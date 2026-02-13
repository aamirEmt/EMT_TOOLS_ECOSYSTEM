"""Cancellation Tool - Unified tool with action-based dispatch"""
from typing import Dict, Tuple
import asyncio
import os
import time
import logging
from pydantic import ValidationError

from ..base import BaseTool, ToolMetadata
from ..base_schema import ToolResponseFormat
from .cancellation_schema import CancellationInput
from .cancellation_service import CancellationService
from emt_client.config import CHATBOT_API_BASE_URL
from .cancellation_renderer import (
    render_booking_details, render_cancellation_success,
    render_train_booking_details, render_already_cancelled,
)

logger = logging.getLogger(__name__)


# ============================================================
# Per-User Session Registry (isolates concurrent users)
# ============================================================
_sessions: Dict[str, Tuple[CancellationService, float]] = {}
_sessions_lock = asyncio.Lock()
_SESSION_TTL_SECONDS = 1800  # 30 minutes
_MAX_SESSIONS = 500


def _session_key(booking_id: str, email: str) -> str:
    """Create a unique session key from booking_id + email"""
    return f"{booking_id.strip().upper()}:{email.strip().lower()}"


async def get_user_service(booking_id: str, email: str) -> CancellationService:
    """Get or create a per-user service instance with TTL cleanup"""
    key = _session_key(booking_id, email)
    now = time.monotonic()
    expired_services = []

    async with _sessions_lock:
        # Collect expired sessions (don't close yet — avoid I/O inside lock)
        expired = [k for k, (svc, ts) in _sessions.items() if now - ts > _SESSION_TTL_SECONDS]
        for k in expired:
            svc, _ = _sessions.pop(k)
            expired_services.append(svc)

        if key in _sessions:
            svc, _ = _sessions[key]
            _sessions[key] = (svc, now)  # refresh TTL
            result = svc
        elif len(_sessions) >= _MAX_SESSIONS:
            # Evict oldest session to make room
            oldest_key = min(_sessions, key=lambda k: _sessions[k][1])
            old_svc, _ = _sessions.pop(oldest_key)
            expired_services.append(old_svc)
            logger.warning(f"Session limit reached, evicted: {oldest_key}")
            svc = CancellationService()
            _sessions[key] = (svc, now)
            result = svc
        else:
            svc = CancellationService()
            _sessions[key] = (svc, now)
            logger.info(f"Created new session for: {key}")
            result = svc

    # Close expired services OUTSIDE the lock (non-blocking for other users)
    for svc in expired_services:
        try:
            await svc.close()
        except Exception:
            logger.warning("Failed to close expired session", exc_info=True)

    return result


# ============================================================
# Unified Cancellation Tool
# ============================================================
class CancellationTool(BaseTool):
    """
    Single tool for the entire cancellation flow.

    Actions:
      - "start"      : Login + fetch booking details (login OTP auto-sent)
      - "verify_otp" : Verify guest login OTP before proceeding
      - "send_otp"   : Send cancellation OTP to user's email
      - "confirm"    : Submit cancellation with cancellation OTP, room_id, transaction_id
    """

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="cancellation",
            description=(
                "Booking cancellation tool. "
                "Use action='start' with booking_id and email to login and fetch booking details (login OTP is auto-sent). "
                "Use action='verify_otp' with otp to verify the guest login OTP. "
                "Use action='send_otp' to send cancellation OTP. "
                "Use action='confirm' with otp, room_id, and transaction_id to complete cancellation."
            ),
            input_schema=CancellationInput.model_json_schema(),
            category="cancellation",
            tags=["cancellation", "flow"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        user_type = kwargs.pop("_user_type", "chatbot")
        kwargs.pop("_limit", None)

        try:
            input_data = CancellationInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid input for cancellation",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        action = input_data.action.lower().strip()

        if action == "start":
            return await self._handle_start(input_data, user_type)
        elif action == "verify_otp":
            return await self._handle_verify_otp(input_data)
        elif action == "send_otp":
            return await self._handle_send_otp(input_data)
        elif action == "confirm":
            return await self._handle_confirm(input_data, user_type)
        else:
            return ToolResponseFormat(
                response_text=f"Unknown action '{input_data.action}'. Use 'start', 'verify_otp', 'send_otp', or 'confirm'.",
                is_error=True,
            )

    # ----------------------------------------------------------
    # action = "start" — login + fetch booking details
    # ----------------------------------------------------------
    async def _handle_start(self, input_data: CancellationInput, user_type: str) -> ToolResponseFormat:
        render_html = user_type.lower() == "website"
        is_whatsapp = user_type.lower() == "whatsapp"

        service = await get_user_service(input_data.booking_id, input_data.email)

        # Step 1: Guest login
        try:
            login_result = await service.guest_login(
                booking_id=input_data.booking_id,
                email=input_data.email,
            )
        except Exception as exc:
            logger.error(f"Service error during guest login: {exc}", exc_info=True)
            return ToolResponseFormat(
                response_text="Something went wrong while logging in. Please try again.",
                is_error=True,
            )

        if not login_result["success"]:
            return ToolResponseFormat(
                response_text=f"Guest login failed: {login_result['message']}",
                structured_content=login_result,
                is_error=True,
            )

        bid = login_result["ids"]["bid"]
        transaction_type = login_result["ids"].get("transaction_type", "Hotel")

        # Step 2: Fetch booking details (route based on TransactionType)
        if transaction_type == "Train":
            return await self._handle_start_train(
                input_data, login_result, bid, user_type, render_html, is_whatsapp, service
            )

        return await self._handle_start_hotel(
            input_data, login_result, bid, user_type, render_html, is_whatsapp, service
        )

    # ----------------------------------------------------------
    # _handle_start — Hotel branch
    # ----------------------------------------------------------
    async def _handle_start_hotel(
        self, input_data, login_result, bid, user_type, render_html, is_whatsapp, service
    ) -> ToolResponseFormat:
        try:
            details_result = await service.fetch_booking_details(bid=bid)
        except Exception as exc:
            logger.error(f"Service error during fetch details: {exc}", exc_info=True)
            return ToolResponseFormat(
                response_text="Something went wrong while fetching booking details. Please try again.",
                is_error=True,
            )

        combined = {
            "login": login_result,
            "booking_details": details_result,
            "bid": bid,
            "transaction_type": "Hotel",
        }

        if not details_result["success"]:
            return ToolResponseFormat(
                response_text=f"Login succeeded but failed to fetch details: {details_result.get('error')}",
                structured_content=combined,
                is_error=True,
            )

        # Check if all rooms are already cancelled
        if details_result.get("all_cancelled"):
            if render_html:
                html = render_already_cancelled(
                    booking_id=input_data.booking_id,
                    transaction_type="Hotel",
                    details=details_result,
                )
                return ToolResponseFormat(
                    response_text=f"Booking {input_data.booking_id} has already been cancelled.",
                    html=html,
                )
            return ToolResponseFormat(
                response_text=f"Booking {input_data.booking_id} has already been cancelled. No further action is needed.",
            )

        # Website mode: render interactive HTML
        if render_html:
            details_result["booking_id"] = input_data.booking_id
            api_base_url = CHATBOT_API_BASE_URL
            is_otp_send = login_result.get("ids", {}).get("is_otp_send", False)
            html = render_booking_details(
                booking_details=details_result,
                booking_id=input_data.booking_id,
                email=input_data.email,
                bid=bid,
                api_base_url=api_base_url,
                is_otp_send=is_otp_send,
            )
            return ToolResponseFormat(
                response_text=f"Booking details for {input_data.booking_id}",
                structured_content={
                    "booking_details": details_result,
                    "bid": bid,
                    "transaction_type": "Hotel",
                },
                html=html,
            )

        # Chatbot / WhatsApp mode: build friendly text
        rooms = details_result.get("rooms", [])
        hotel_info = details_result.get("hotel_info", {})
        guest_info = details_result.get("guest_info", [])

        hotel_name = hotel_info.get("hotel_name", "your hotel")
        check_in = hotel_info.get("check_in", "")
        check_out = hotel_info.get("check_out", "")
        duration = hotel_info.get("duration", "")
        total_fare = hotel_info.get("total_fare", "")

        def format_date(date_str):
            if not date_str:
                return ""
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                return dt.strftime("%d %b %Y")
            except:
                return date_str

        check_in_formatted = format_date(check_in)
        check_out_formatted = format_date(check_out)

        guest_names = []
        for guest in guest_info:
            name = f"{guest.get('title', '')} {guest.get('first_name', '')} {guest.get('last_name', '')}".strip()
            if name and name not in guest_names:
                guest_names.append(name)

        booking_summary = []
        if check_in_formatted and check_out_formatted:
            booking_summary.append(f"📅 Check-in: {check_in_formatted} | Check-out: {check_out_formatted}")
        if duration:
            booking_summary.append(f"🌙 Duration: {duration} nights")
        if guest_names:
            booking_summary.append(f"👤 Guests: {', '.join(guest_names)}")
        if total_fare:
            booking_summary.append(f"💰 Total Booking Amount: ₹{total_fare}")

        room_descriptions = []
        for idx, r in enumerate(rooms, 1):
            room_type = r.get('room_type', 'Room')
            room_no = r.get('room_no')
            amount = r.get('amount')
            policy = r.get('cancellation_policy', '')
            adults = r.get('total_adults')

            desc = f"\n{idx}. {room_type}"
            if room_no:
                desc += f" (Room {room_no})"
            if adults:
                desc += f" - {adults} Adult(s)"
            if amount:
                desc += f" - ₹{amount}"
            room_descriptions.append(desc)

            if policy:
                for line in policy.split('\n'):
                    if line.strip():
                        room_descriptions.append(f"   {line}")

        otp_sent = login_result.get("ids", {}).get("is_otp_send")
        otp_notice = ""
        if otp_sent:
            otp_notice = "\n\n📧 An OTP has been sent to your registered email/phone. Please provide it to verify your identity before proceeding."

        text = (
            f"I've pulled up your booking details for {hotel_name}.\n\n"
            + "\n".join(booking_summary) + "\n"
            + "\n".join(room_descriptions)
            + otp_notice
        )

        whatsapp_response = None
        if is_whatsapp:
            from .cancellation_schema import (
                WhatsappCancellationFormat,
                WhatsappCancellationFinalResponse,
            )
            whatsapp_response = WhatsappCancellationFinalResponse(
                response_text=text,
                whatsapp_json=WhatsappCancellationFormat(
                    type="cancellation",
                    status="booking_details",
                    message=text,
                    booking_id=input_data.booking_id,
                    transaction_type="Hotel",
                    rooms=[
                        {
                            "room_id": r.get("room_id"),
                            "room_type": r.get("room_type"),
                            "room_no": r.get("room_no"),
                        }
                        for r in rooms
                    ],
                ),
            )

        return ToolResponseFormat(
            response_text=text,
            structured_content=combined,
            whatsapp_response=(
                whatsapp_response.model_dump() if whatsapp_response else None
            ),
        )

    # ----------------------------------------------------------
    # _handle_start — Train branch
    # ----------------------------------------------------------
    async def _handle_start_train(
        self, input_data, login_result, bid, user_type, render_html, is_whatsapp, service
    ) -> ToolResponseFormat:
        try:
            details_result = await service.fetch_train_booking_details(bid=bid)
        except Exception as exc:
            logger.error(f"Service error during fetch train details: {exc}", exc_info=True)
            return ToolResponseFormat(
                response_text="Something went wrong while fetching train booking details. Please try again.",
                is_error=True,
            )

        combined = {
            "login": login_result,
            "booking_details": details_result,
            "bid": bid,
            "transaction_type": "Train",
        }

        if not details_result["success"]:
            return ToolResponseFormat(
                response_text=f"Login succeeded but failed to fetch train details: {details_result.get('error')}",
                structured_content=combined,
                is_error=True,
            )

        # Check if all passengers are already cancelled
        if details_result.get("all_cancelled"):
            if render_html:
                html = render_already_cancelled(
                    booking_id=input_data.booking_id,
                    transaction_type="Train",
                    details=details_result,
                )
                return ToolResponseFormat(
                    response_text=f"Train booking {input_data.booking_id} has already been cancelled.",
                    html=html,
                )
            return ToolResponseFormat(
                response_text=f"Train booking {input_data.booking_id} has already been cancelled. No further action is needed.",
            )

        # Website mode: render interactive HTML
        if render_html:
            api_base_url = CHATBOT_API_BASE_URL
            is_otp_send = login_result.get("ids", {}).get("is_otp_send", False)
            html = render_train_booking_details(
                booking_details=details_result,
                booking_id=input_data.booking_id,
                email=input_data.email,
                bid=bid,
                api_base_url=api_base_url,
                is_otp_send=is_otp_send,
            )
            return ToolResponseFormat(
                response_text=f"Train booking details for {input_data.booking_id}",
                structured_content={
                    "booking_details": details_result,
                    "bid": bid,
                    "transaction_type": "Train",
                },
                html=html,
            )

        # Chatbot / WhatsApp mode: build friendly text
        train_info = details_result.get("train_info", {})
        passengers = details_result.get("passengers", [])
        price_info = details_result.get("price_info", {})

        train_name = train_info.get("train_name", "your train")
        train_number = train_info.get("train_number", "")
        from_station = train_info.get("from_station_name", train_info.get("from_station", ""))
        to_station = train_info.get("to_station_name", train_info.get("to_station", ""))
        departure_date = train_info.get("departure_date", "")
        departure_time = train_info.get("departure_time", "")
        arrival_date = train_info.get("arrival_date", "")
        arrival_time = train_info.get("arrival_time", "")
        duration = train_info.get("duration", "")
        travel_class = train_info.get("travel_class", "")
        pnr_number = details_result.get("pnr_number", "")
        total_fare = price_info.get("total_fare", "")

        booking_summary = []
        if train_name and train_number:
            booking_summary.append(f"🚆 {train_name} ({train_number})")
        if from_station and to_station:
            booking_summary.append(f"📍 {from_station} → {to_station}")
        if departure_date and departure_time:
            booking_summary.append(f"📅 Departure: {departure_date} at {departure_time}")
        if arrival_date and arrival_time:
            booking_summary.append(f"📅 Arrival: {arrival_date} at {arrival_time}")
        if duration:
            booking_summary.append(f"⏱️ Duration: {duration}")
        if travel_class:
            booking_summary.append(f"🎫 Class: {travel_class}")
        if pnr_number:
            booking_summary.append(f"🔢 PNR: {pnr_number}")
        if total_fare:
            booking_summary.append(f"💰 Total Fare: ₹{total_fare}")

        pax_descriptions = []
        for idx, pax in enumerate(passengers, 1):
            name = f"{pax.get('title', '')} {pax.get('name', '')}".strip()
            pax_type = pax.get('pax_type', '')
            seat_no = pax.get('seat_no', '')
            seat_type = pax.get('seat_type', '')
            coach = pax.get('coach_number', '')
            status = pax.get('booking_status', '')

            desc = f"\n{idx}. {name}"
            if pax_type:
                desc += f" ({pax_type})"
            if coach and seat_no and seat_no != "0":
                desc += f" - Coach {coach}, Seat {seat_no}"
                if seat_type:
                    desc += f" ({seat_type})"
            if status:
                desc += f" - Status: {status}"
            pax_descriptions.append(desc)

        otp_sent = login_result.get("ids", {}).get("is_otp_send")
        otp_notice = ""
        if otp_sent:
            otp_notice = "\n\n📧 An OTP has been sent to your registered email/phone. Please provide it to verify your identity before proceeding."

        text = (
            f"I've pulled up your train booking details.\n\n"
            + "\n".join(booking_summary)
            + "\n\n👥 Passengers:"
            + "\n".join(pax_descriptions)
            + otp_notice
        )

        whatsapp_response = None
        if is_whatsapp:
            from .cancellation_schema import (
                WhatsappCancellationFormat,
                WhatsappCancellationFinalResponse,
            )
            whatsapp_response = WhatsappCancellationFinalResponse(
                response_text=text,
                whatsapp_json=WhatsappCancellationFormat(
                    type="cancellation",
                    status="booking_details",
                    message=text,
                    booking_id=input_data.booking_id,
                    transaction_type="Train",
                    passengers=[
                        {
                            "pax_id": p.get("pax_id"),
                            "name": f"{p.get('title', '')} {p.get('name', '')}".strip(),
                            "pax_type": p.get("pax_type"),
                            "seat_no": p.get("seat_no"),
                            "status": p.get("booking_status"),
                        }
                        for p in passengers
                    ],
                ),
            )

        return ToolResponseFormat(
            response_text=text,
            structured_content=combined,
            whatsapp_response=(
                whatsapp_response.model_dump() if whatsapp_response else None
            ),
        )

    # ----------------------------------------------------------
    # action = "verify_otp" — verify guest login OTP
    # ----------------------------------------------------------
    async def _handle_verify_otp(self, input_data: CancellationInput) -> ToolResponseFormat:
        if not input_data.otp:
            return ToolResponseFormat(
                response_text="Please provide the OTP sent to your registered email/phone.",
                is_error=True,
            )

        service = await get_user_service(input_data.booking_id, input_data.email)
        try:
            result = await service.verify_otp(otp=input_data.otp)
        except Exception as exc:
            logger.error(f"Service error during OTP verification: {exc}", exc_info=True)
            return ToolResponseFormat(
                response_text="Something went wrong while verifying OTP. Please try again.",
                is_error=True,
            )

        if not result["success"]:
            return ToolResponseFormat(
                response_text=(
                    f"❌ {result['message']}\n\n"
                    f"Please check the OTP and try again."
                ),
                structured_content=result,
                is_error=True,
            )

        return ToolResponseFormat(
            response_text=(
                f"✅ OTP verified successfully!\n\n"
                f"Your identity has been confirmed. Would you like to proceed with the cancellation?"
            ),
            structured_content=result,
        )

    # ----------------------------------------------------------
    # action = "send_otp"
    # ----------------------------------------------------------
    async def _handle_send_otp(self, input_data: CancellationInput) -> ToolResponseFormat:
        service = await get_user_service(input_data.booking_id, input_data.email)

        # Route based on transaction type
        is_train = service._transaction_type == "Train"

        try:
            if is_train:
                result = await service.send_train_cancellation_otp(
                    booking_id=input_data.booking_id,
                    email=input_data.email,
                )
            else:
                result = await service.send_cancellation_otp(
                    booking_id=input_data.booking_id,
                    email=input_data.email,
                )
        except Exception as exc:
            logger.error(f"Service error during send OTP: {exc}", exc_info=True)
            return ToolResponseFormat(
                response_text="Something went wrong while sending OTP. Please try again.",
                is_error=True,
            )

        if not result["success"]:
            return ToolResponseFormat(
                response_text=f"Failed to send OTP: {result['message']}",
                structured_content=result,
                is_error=True,
            )

        return ToolResponseFormat(
            response_text=(
                f"📧 An OTP (One-Time Password) has been sent to your registered email/phone.\n\n"
                f"🔐 Please check your email and provide the OTP to confirm the cancellation.\n\n"
                f"⏱️ Note: The OTP is valid for 10 minutes only.\n\n"
                f"Type the OTP like: \"123456\" or \"My OTP is ABC123\""
            ),
            structured_content=result,
        )

    # ----------------------------------------------------------
    # action = "confirm" — submit cancellation with OTP
    # ----------------------------------------------------------
    async def _handle_confirm(self, input_data: CancellationInput, user_type: str) -> ToolResponseFormat:
        render_html = user_type.lower() == "website"
        service = await get_user_service(input_data.booking_id, input_data.email)
        is_train = service._transaction_type == "Train"

        if is_train:
            return await self._handle_confirm_train(input_data, render_html, service)
        return await self._handle_confirm_hotel(input_data, render_html, service)

    # ----------------------------------------------------------
    # _handle_confirm — Hotel branch
    # ----------------------------------------------------------
    async def _handle_confirm_hotel(self, input_data, render_html, service) -> ToolResponseFormat:
        # Validate required fields
        if not input_data.otp or not input_data.room_id or not input_data.transaction_id:
            return ToolResponseFormat(
                response_text="Missing required fields for confirm: otp, room_id, transaction_id",
                is_error=True,
            )

        try:
            result = await service.request_cancellation(
                booking_id=input_data.booking_id,
                email=input_data.email,
                otp=input_data.otp,
                room_id=input_data.room_id,
                transaction_id=input_data.transaction_id,
                is_pay_at_hotel=input_data.is_pay_at_hotel,
                payment_url=input_data.payment_url or "",
                reason=input_data.reason,
                remark=input_data.remark,
            )
        except Exception as exc:
            logger.error(f"Service error during cancellation: {exc}", exc_info=True)
            return ToolResponseFormat(
                response_text="Something went wrong while submitting cancellation. Please try again.",
                is_error=True,
            )

        if not result["success"]:
            return ToolResponseFormat(
                response_text=f"❌ Cancellation failed: {result['message']}\n\nPlease try again or contact customer support.",
                structured_content=result,
                is_error=True,
            )

        # Build success message
        refund_info = result.get("refund_info")
        if refund_info:
            refund_amount = refund_info.get('refund_amount', 'N/A')
            cancellation_charges = refund_info.get('cancellation_charges', 'N/A')
            success_text = (
                f" Your hotel booking has been successfully cancelled!\n\n"
                f" Refund Details:\n"
                f"   • Refund Amount: ₹{refund_amount}\n"
                f"   • Cancellation Charges: ₹{cancellation_charges}\n"
                f"   • Refund Mode: {refund_info.get('refund_mode', 'Original payment method')}\n\n"
                f" You will receive a cancellation confirmation email shortly.\n"
                f" The refund will be processed within 5-7 business days.\n\n"
                f"Thank you for using EaseMyTrip. We hope to serve you again!"
            )
        else:
            success_text = (
                f" Your hotel booking has been successfully cancelled!\n\n"
                f" You will receive a cancellation confirmation email shortly.\n\n"
                f"Thank you for using EaseMyTrip. We hope to serve you again!"
            )

        html = None
        if render_html:
            result["booking_id"] = input_data.booking_id
            html = render_cancellation_success(result)

        return ToolResponseFormat(
            response_text=success_text,
            structured_content=result,
            html=html,
        )

    # ----------------------------------------------------------
    # _handle_confirm — Train branch
    # ----------------------------------------------------------
    async def _handle_confirm_train(self, input_data, render_html, service) -> ToolResponseFormat:
        # Validate required fields
        if not input_data.otp or not input_data.pax_ids or not input_data.reservation_id or not input_data.pnr_number:
            return ToolResponseFormat(
                response_text="Missing required fields for train confirm: otp, pax_ids, reservation_id, pnr_number",
                is_error=True,
            )

        try:
            result = await service.request_train_cancellation(
                booking_id=input_data.booking_id,
                email=input_data.email,
                otp=input_data.otp,
                pax_ids=input_data.pax_ids,
                reservation_id=input_data.reservation_id,
                pnr_number=input_data.pnr_number,
                total_passenger=input_data.total_passenger or len(input_data.pax_ids),
            )
        except Exception as exc:
            logger.error(f"Service error during train cancellation: {exc}", exc_info=True)
            return ToolResponseFormat(
                response_text="Something went wrong while submitting train cancellation. Please try again.",
                is_error=True,
            )

        if not result["success"]:
            return ToolResponseFormat(
                response_text=f"❌ Train cancellation failed: {result['message']}\n\nPlease try again or contact customer support.",
                structured_content=result,
                is_error=True,
            )

        # Build success message
        refund_info = result.get("refund_info")
        if refund_info:
            refund_amount = refund_info.get('refund_amount', 'N/A')
            cancellation_charges = refund_info.get('cancellation_charges', 'N/A')
            success_text = (
                f" Your train booking has been successfully cancelled!\n\n"
                f" Refund Details:\n"
                f"   • Refund Amount: ₹{refund_amount}\n"
                f"   • Cancellation Charges: ₹{cancellation_charges}\n"
                f"   • Refund Mode: {refund_info.get('refund_mode', 'Original payment method')}\n\n"
                f" You will receive a cancellation confirmation email shortly.\n"
                f" The refund will be processed within 5-7 business days.\n\n"
                f"Thank you for using EaseMyTrip. We hope to serve you again!"
            )
        else:
            success_text = (
                f" Your train booking has been successfully cancelled!\n\n"
                f" You will receive a cancellation confirmation email shortly.\n\n"
                f"Thank you for using EaseMyTrip. We hope to serve you again!"
            )

        html = None
        if render_html:
            result["booking_id"] = input_data.booking_id
            html = render_cancellation_success(result)

        return ToolResponseFormat(
            response_text=success_text,
            structured_content=result,
            html=html,
        )
