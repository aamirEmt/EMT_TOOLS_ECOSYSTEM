"""Cancellation Tool - Unified tool with action-based dispatch"""
from typing import Dict, Tuple
import asyncio
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
    render_train_booking_details, render_bus_booking_details,
    render_flight_booking_details,
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
                "NEVER ASK PNR ALWAYS ASK FOR EMT BOOKING ID."
                "Booking cancellation tool for Hotel, Train, Bus, and Flight bookings. "
                "Supports all EaseMyTrip booking types — the system auto-detects the module from the booking ID. "
                "Use action='start' with booking_id and email to login and fetch booking details (login OTP is auto-sent). "
                "Use action='verify_otp' with otp to verify the guest login OTP. "
                "Use action='send_otp' to send cancellation OTP. "
                "Use action='confirm' with otp to complete cancellation. "
                "For hotel: also pass room_id and transaction_id. "
                "For train: also pass pax_ids, reservation_id, pnr_number. "
                "For bus: also pass seats (comma-separated seat numbers). "
                "For flight: also pass outbound_pax_ids and/or inbound_pax_ids (comma-separated)."
            ),
            input_schema=CancellationInput.model_json_schema(),
            category="cancellation",
            tags=["cancellation", "hotel", "train", "bus", "flight", "flow"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        user_type = kwargs.pop("_user_type", "chatbot")
        kwargs.pop("_limit", None)
        kwargs.pop("_session_id", None)

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
            return await self._handle_verify_otp(input_data, user_type)
        elif action == "send_otp":
            return await self._handle_send_otp(input_data, user_type)
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
        if transaction_type == "Flight":
            return await self._handle_start_flight(
                input_data, login_result, bid, user_type, render_html, is_whatsapp, service
            )

        if transaction_type == "Train":
            return await self._handle_start_train(
                input_data, login_result, bid, user_type, render_html, is_whatsapp, service
            )

        if transaction_type == "Bus":
            return await self._handle_start_bus(
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
        # WhatsApp: Stop after sending login OTP, don't fetch details yet
        otp_sent = login_result.get("ids", {}).get("is_otp_send")
        if is_whatsapp and otp_sent:
            otp_text = (
                "📧 An OTP has been sent to your registered email/phone.\n\n"
                "🔐 Please enter the OTP to verify your identity and view booking details.\n\n"
                "Type the OTP like: \"123456\" or \"My OTP is ABC123\""
            )
            from .cancellation_schema import (
                WhatsappCancellationFormat,
                WhatsappCancellationFinalResponse,
            )
            whatsapp_response = WhatsappCancellationFinalResponse(
                response_text=otp_text,
                whatsapp_json=WhatsappCancellationFormat(
                    type="cancellation",
                    status="otp_sent_for_login",
                    message=otp_text,
                    booking_id=input_data.booking_id,
                    transaction_type="Hotel",
                ),
            )
            return ToolResponseFormat(
                response_text=otp_text,
                structured_content={"login": login_result, "bid": bid, "transaction_type": "Hotel"},
                whatsapp_response=whatsapp_response.model_dump(),
            )

        # Website/Chatbot: Continue with current flow (fetch details immediately)
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
        # WhatsApp: Stop after sending login OTP, don't fetch details yet
        otp_sent = login_result.get("ids", {}).get("is_otp_send")
        if is_whatsapp and otp_sent:
            otp_text = (
                "📧 An OTP has been sent to your registered email/phone.\n\n"
                "🔐 Please enter the OTP to verify your identity and view booking details.\n\n"
                "Type the OTP like: \"123456\" or \"My OTP is ABC123\""
            )
            from .cancellation_schema import (
                WhatsappCancellationFormat,
                WhatsappCancellationFinalResponse,
            )
            whatsapp_response = WhatsappCancellationFinalResponse(
                response_text=otp_text,
                whatsapp_json=WhatsappCancellationFormat(
                    type="cancellation",
                    status="otp_sent_for_login",
                    message=otp_text,
                    booking_id=input_data.booking_id,
                    transaction_type="Train",
                ),
            )
            return ToolResponseFormat(
                response_text=otp_text,
                structured_content={"login": login_result, "bid": bid, "transaction_type": "Train"},
                whatsapp_response=whatsapp_response.model_dump(),
            )

        # Website/Chatbot: Continue with current flow (fetch details immediately)
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
    async def _handle_verify_otp(self, input_data: CancellationInput, user_type: str) -> ToolResponseFormat:
        is_whatsapp = user_type.lower() == "whatsapp"

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
            error_text = (
                f"❌ {result['message']}\n\n"
                f"Please check the OTP and try again."
            )
            whatsapp_response = None
            if is_whatsapp:
                from .cancellation_schema import (
                    WhatsappCancellationFormat,
                    WhatsappCancellationFinalResponse,
                )
                whatsapp_response = WhatsappCancellationFinalResponse(
                    response_text=error_text,
                    whatsapp_json=WhatsappCancellationFormat(
                        type="cancellation",
                        status="error",
                        message=error_text,
                        booking_id=input_data.booking_id,
                    ),
                )
            return ToolResponseFormat(
                response_text=error_text,
                structured_content=result,
                is_error=True,
                whatsapp_response=(
                    whatsapp_response.model_dump() if whatsapp_response else None
                ),
            )

        # For WhatsApp: After OTP verification, fetch and show booking details
        if is_whatsapp:
            tx_type = service._transaction_type
            bid = service._bid

            # Fetch booking details based on transaction type
            try:
                if tx_type == "Flight":
                    return await self._fetch_and_show_flight_details(input_data, bid, service)
                elif tx_type == "Train":
                    return await self._fetch_and_show_train_details(input_data, bid, service)
                elif tx_type == "Bus":
                    return await self._fetch_and_show_bus_details(input_data, bid, service)
                else:  # Hotel
                    return await self._fetch_and_show_hotel_details(input_data, bid, service)
            except Exception as exc:
                logger.error(f"Error fetching details after OTP verification: {exc}", exc_info=True)
                return ToolResponseFormat(
                    response_text="OTP verified, but failed to fetch booking details. Please try again.",
                    is_error=True,
                )

        # For Website/Chatbot: Just confirm OTP verification
        success_text = (
            f"✅ OTP verified successfully!\n\n"
            f"Your identity has been confirmed. Would you like to proceed with the cancellation?"
        )

        return ToolResponseFormat(
            response_text=success_text,
            structured_content=result,
        )

    # ----------------------------------------------------------
    # Helper methods to fetch and show booking details (for WhatsApp after OTP verification)
    # ----------------------------------------------------------
    async def _fetch_and_show_hotel_details(self, input_data, bid, service) -> ToolResponseFormat:
        """Fetch and show hotel booking details for WhatsApp after OTP verification"""
        details_result = await service.fetch_booking_details(bid=bid)

        if not details_result["success"]:
            return ToolResponseFormat(
                response_text=f"OTP verified, but failed to fetch booking details: {details_result.get('error')}",
                is_error=True,
            )

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
        cancellation_params = []  # Store params for LLM to use

        for idx, r in enumerate(rooms, 1):
            room_type = r.get('room_type', 'Room')
            room_no = r.get('room_no')
            room_id = r.get('room_id')
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

            # Store cancellation parameters for this room
            if room_id:
                cancellation_params.append(f"room_{idx}_id: {room_id}")

            if policy:
                for line in policy.split('\n'):
                    if line.strip():
                        room_descriptions.append(f"   {line}")

        # Get transaction_id from booking details
        transaction_id = details_result.get("transaction_id") or details_result.get("booking_details", {}).get("transaction_id")

        # Store cancellation metadata in service for WhatsApp (auto-populate later)
        service._cancellation_room_ids = [r.get("room_id") for r in rooms if r.get("room_id")]
        service._cancellation_transaction_id = transaction_id

        text = (
            f"✅ OTP verified successfully!\n\n"
            f"I've pulled up your booking details for {hotel_name}.\n\n"
            + "\n".join(booking_summary) + "\n"
            + "\n".join(room_descriptions)
            + "\n\n📋 Cancellation Details:"
            + f"\n- Booking ID: {input_data.booking_id}"
        )

        # Add transaction_id if available
        if transaction_id:
            text += f"\n- Transaction ID: {transaction_id}"

        # Add room IDs for reference
        if len(rooms) == 1 and rooms[0].get('room_id'):
            text += f"\n- Room ID: {rooms[0].get('room_id')}"
        elif len(rooms) > 1:
            for idx, r in enumerate(rooms, 1):
                if r.get('room_id'):
                    text += f"\n- Room {idx} ID: {r.get('room_id')}"

        text += "\n\nWould you like to proceed with the cancellation?"

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
            structured_content={"booking_details": details_result, "bid": bid, "transaction_type": "Hotel"},
            whatsapp_response=whatsapp_response.model_dump(),
        )

    async def _fetch_and_show_train_details(self, input_data, bid, service) -> ToolResponseFormat:
        """Fetch and show train booking details for WhatsApp after OTP verification"""
        details_result = await service.fetch_train_booking_details(bid=bid)

        if not details_result["success"]:
            return ToolResponseFormat(
                response_text=f"OTP verified, but failed to fetch train details: {details_result.get('error')}",
                is_error=True,
            )

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

        # Store cancellation metadata in service for WhatsApp (auto-populate later)
        service._cancellation_pax_ids = [p.get("pax_id") for p in passengers if p.get("pax_id")]
        service._cancellation_reservation_id = details_result.get("reservation_id")
        service._cancellation_pnr_number = pnr_number
        service._cancellation_total_passenger = len(passengers)

        text = (
            f"✅ OTP verified successfully!\n\n"
            f"I've pulled up your train booking details.\n\n"
            + "\n".join(booking_summary)
            + "\n\n👥 Passengers:"
            + "\n".join(pax_descriptions)
            + "\n\nWould you like to proceed with the cancellation?"
        )

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
            structured_content={"booking_details": details_result, "bid": bid, "transaction_type": "Train"},
            whatsapp_response=whatsapp_response.model_dump(),
        )

    async def _fetch_and_show_bus_details(self, input_data, bid, service) -> ToolResponseFormat:
        """Fetch and show bus booking details for WhatsApp after OTP verification"""
        details_result = await service.fetch_bus_booking_details(bid=bid)

        if not details_result["success"]:
            return ToolResponseFormat(
                response_text=f"OTP verified, but failed to fetch bus details: {details_result.get('error')}",
                is_error=True,
            )

        bus_info = details_result.get("bus_info", {})
        passengers = details_result.get("passengers", [])

        source = bus_info.get("source", "")
        destination = bus_info.get("destination", "")
        journey_date = bus_info.get("date_of_journey", "")
        departure_time = bus_info.get("departure_time", "")
        bus_type = bus_info.get("bus_type", "")
        operator = bus_info.get("travels_operator", "")
        ticket_no = bus_info.get("ticket_no", "")
        total_fare = bus_info.get("total_fare", "")

        booking_summary = []
        if operator:
            booking_summary.append(f"🚌 {operator}")
        if source and destination:
            booking_summary.append(f"📍 {source} → {destination}")
        if journey_date and departure_time:
            booking_summary.append(f"📅 {journey_date} at {departure_time}")
        if bus_type:
            booking_summary.append(f"🎫 {bus_type.strip()}")
        if ticket_no:
            booking_summary.append(f"🔢 Ticket: {ticket_no}")
        if total_fare:
            booking_summary.append(f"💰 Total Fare: ₹{total_fare}")

        pax_descriptions = []
        for idx, pax in enumerate(passengers, 1):
            name = f"{pax.get('title', '')} {pax.get('first_name', '')} {pax.get('last_name', '')}".strip()
            seat = pax.get('seat_no', '')
            fare = pax.get('fare', '')
            status = pax.get('status', '')

            desc = f"\n{idx}. {name}"
            if seat:
                desc += f" - Seat {seat}"
            if fare:
                desc += f" (₹{fare})"
            if status:
                desc += f" - {status}"
            pax_descriptions.append(desc)

        # Store cancellation metadata in service for WhatsApp (auto-populate later)
        service._cancellation_seats = ",".join([p.get("seat_no", "") for p in passengers if p.get("seat_no")])

        text = (
            f"✅ OTP verified successfully!\n\n"
            f"Here are the details for your bus booking **{input_data.booking_id}**:\n\n"
            + "\n".join(booking_summary)
            + "\n\n👥 **Passengers:**"
            + "".join(pax_descriptions)
            + "\n\nWould you like to proceed with the cancellation?"
        )

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
                transaction_type="Bus",
                seats=[
                    {
                        "seat_no": p.get("seat_no"),
                        "name": f"{p.get('title', '')} {p.get('first_name', '')} {p.get('last_name', '')}".strip(),
                        "fare": p.get("fare"),
                        "status": p.get("status"),
                    }
                    for p in passengers
                ],
            ),
        )

        return ToolResponseFormat(
            response_text=text,
            structured_content={"booking_details": details_result, "bid": bid, "transaction_type": "Bus"},
            whatsapp_response=whatsapp_response.model_dump(),
        )

    async def _fetch_and_show_flight_details(self, input_data, bid, service) -> ToolResponseFormat:
        """Fetch and show flight booking details for WhatsApp after OTP verification"""
        details_result = await service.fetch_flight_booking_details(bid=bid)

        if not details_result["success"]:
            return ToolResponseFormat(
                response_text=f"OTP verified, but failed to fetch flight details: {details_result.get('error')}",
                is_error=True,
            )

        # Store total cancellable for partial cancel computation
        service._total_cancellable = details_result.get("total_cancellable", 0)

        flight_segments = details_result.get("flight_segments", [])
        outbound_pax = details_result.get("outbound_passengers", [])
        inbound_pax = details_result.get("inbound_passengers", [])
        price_info = details_result.get("price_info", {})
        pnr_info = details_result.get("pnr_info", [])

        booking_summary = []

        # Flight segments info
        for seg in flight_segments:
            airline = seg.get("airline_code") or seg.get("airline_name", "")
            flight_no = seg.get("flight_number", "")
            origin = seg.get("origin", "")
            destination = seg.get("destination", "")
            dep_date = seg.get("departure_date", "")
            dep_time = seg.get("departure_time", "")
            arr_time = seg.get("arrival_time", "")
            duration = seg.get("duration", "")
            cabin = seg.get("cabin_class", "")
            bound = seg.get("bound_type", "")

            bound_label = ""
            if bound:
                bound_lower = str(bound).lower()
                if "out" in bound_lower:
                    bound_label = "Outbound"
                elif "in" in bound_lower:
                    bound_label = "Inbound"

            seg_line = f"✈️ {airline} {flight_no} — {origin} → {destination}"
            if dep_date:
                seg_line += f" | {dep_date}"
            if dep_time and arr_time:
                seg_line += f" ({dep_time} - {arr_time})"
            if duration:
                seg_line += f" | {duration}"
            if cabin:
                seg_line += f" | {cabin}"
            if bound_label:
                seg_line = f"[{bound_label}] {seg_line}"
            booking_summary.append(seg_line)

        # PNR info
        for pnr in pnr_info:
            airline_pnr = pnr.get("airline_pnr", "")
            gds_pnr = pnr.get("gds_pnr", "")
            if airline_pnr:
                booking_summary.append(f"🔢 Airline PNR: {airline_pnr}")
            if gds_pnr:
                booking_summary.append(f"🔢 GDS PNR: {gds_pnr}")

        # Price info
        total_fare = price_info.get("total_fare", "")
        if total_fare:
            booking_summary.append(f"💰 Total Fare: ₹{total_fare}")

        # Passengers
        pax_descriptions = []
        all_pax = []
        for pax in outbound_pax:
            all_pax.append({**pax, "_bound": "Outbound"})
        for pax in inbound_pax:
            all_pax.append({**pax, "_bound": "Inbound"})

        for idx, pax in enumerate(all_pax, 1):
            name = f"{pax.get('title', '')} {pax.get('first_name', '')} {pax.get('last_name', '')}".strip()
            pax_type = pax.get("pax_type", "")
            status = pax.get("status", "")
            ticket = pax.get("ticket_number", "")
            bound_label = pax.get("_bound", "")
            charge = pax.get("cancellation_charge", "")

            desc = f"\n{idx}. {name}"
            if pax_type:
                desc += f" ({pax_type})"
            if bound_label:
                desc += f" [{bound_label}]"
            if ticket:
                desc += f" - Ticket: {ticket}"
            if status:
                desc += f" - {status}"
            if charge:
                desc += f" - Cancel charge: ₹{charge}"
            pax_descriptions.append(desc)

        # Store cancellation metadata in service for WhatsApp (auto-populate later)
        outbound_ids = [p.get("pax_id", "") for p in outbound_pax if p.get("pax_id")]
        inbound_ids = [p.get("pax_id", "") for p in inbound_pax if p.get("pax_id")]
        service._cancellation_outbound_pax_ids = ",".join(outbound_ids) if outbound_ids else None
        service._cancellation_inbound_pax_ids = ",".join(inbound_ids) if inbound_ids else None

        text = (
            f"✅ OTP verified successfully!\n\n"
            f"Here are the details for your flight booking **{input_data.booking_id}**:\n\n"
            + "\n".join(booking_summary)
            + "\n\n👥 **Passengers:**"
            + "".join(pax_descriptions)
            + "\n\nWould you like to proceed with the cancellation?"
        )

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
                transaction_type="Flight",
                flight_passengers=[
                    {
                        "pax_id": p.get("pax_id"),
                        "name": f"{p.get('title', '')} {p.get('first_name', '')} {p.get('last_name', '')}".strip(),
                        "pax_type": p.get("pax_type"),
                        "status": p.get("status"),
                        "bound_type": p.get("bound_type"),
                    }
                    for p in all_pax
                ],
            ),
        )

        return ToolResponseFormat(
            response_text=text,
            structured_content={"booking_details": details_result, "bid": bid, "transaction_type": "Flight"},
            whatsapp_response=whatsapp_response.model_dump(),
        )

    # ----------------------------------------------------------
    # action = "send_otp"
    # ----------------------------------------------------------
    async def _handle_send_otp(self, input_data: CancellationInput, user_type: str) -> ToolResponseFormat:
        is_whatsapp = user_type.lower() == "whatsapp"
        service = await get_user_service(input_data.booking_id, input_data.email)

        # Route based on transaction type
        tx_type = service._transaction_type

        try:
            if tx_type == "Flight":
                result = await service.send_flight_cancellation_otp(
                    booking_id=input_data.booking_id,
                    email=input_data.email,
                )
            elif tx_type == "Train":
                result = await service.send_train_cancellation_otp(
                    booking_id=input_data.booking_id,
                    email=input_data.email,
                )
            elif tx_type == "Bus":
                result = await service.send_bus_cancellation_otp(
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

        otp_text = (
            f"📧 An OTP (One-Time Password) has been sent to your registered email/phone.\n\n"
            f"🔐 Please provide the OTP to confirm the cancellation.\n\n"
            f"⏱️ Note: The OTP is valid for 10 minutes only."
        )

        whatsapp_response = None
        if is_whatsapp:
            from .cancellation_schema import (
                WhatsappCancellationFormat,
                WhatsappCancellationFinalResponse,
            )
            whatsapp_response = WhatsappCancellationFinalResponse(
                response_text=otp_text,
                whatsapp_json=WhatsappCancellationFormat(
                    type="cancellation",
                    status="otp_sent",
                    message=otp_text,
                    booking_id=input_data.booking_id,
                    transaction_type=tx_type,
                ),
            )

        return ToolResponseFormat(
            response_text=otp_text,
            structured_content=result,
            whatsapp_response=(
                whatsapp_response.model_dump() if whatsapp_response else None
            ),
        )

    # ----------------------------------------------------------
    # action = "confirm" — submit cancellation with OTP
    # ----------------------------------------------------------
    async def _handle_confirm(self, input_data: CancellationInput, user_type: str) -> ToolResponseFormat:
        render_html = user_type.lower() == "website"
        is_whatsapp = user_type.lower() == "whatsapp"
        service = await get_user_service(input_data.booking_id, input_data.email)
        tx_type = service._transaction_type

        if tx_type == "Flight":
            return await self._handle_confirm_flight(input_data, render_html, is_whatsapp, service)
        if tx_type == "Train":
            return await self._handle_confirm_train(input_data, render_html, is_whatsapp, service)
        if tx_type == "Bus":
            return await self._handle_confirm_bus(input_data, render_html, is_whatsapp, service)
        return await self._handle_confirm_hotel(input_data, render_html, is_whatsapp, service)

    # ----------------------------------------------------------
    # _handle_confirm — Hotel branch
    # ----------------------------------------------------------
    async def _handle_confirm_hotel(self, input_data, render_html, is_whatsapp, service) -> ToolResponseFormat:
        # Auto-populate parameters for WhatsApp users from service session
        room_id = input_data.room_id
        transaction_id = input_data.transaction_id

        if is_whatsapp:
            # Auto-fill from service session if not provided
            if not room_id and hasattr(service, '_cancellation_room_ids') and service._cancellation_room_ids:
                room_id = service._cancellation_room_ids[0]  # Default to first room
            if not transaction_id and hasattr(service, '_cancellation_transaction_id'):
                transaction_id = service._cancellation_transaction_id

        # Validate required fields
        if not input_data.otp:
            return ToolResponseFormat(
                response_text="Please provide the OTP to confirm the cancellation.",
                is_error=True,
            )

        if not room_id or not transaction_id:
            return ToolResponseFormat(
                response_text="Missing required cancellation details. Please start the cancellation process again.",
                is_error=True,
            )

        try:
            result = await service.request_cancellation(
                booking_id=input_data.booking_id,
                email=input_data.email,
                otp=input_data.otp,
                room_id=room_id,  # Use auto-populated value
                transaction_id=transaction_id,  # Use auto-populated value
                is_pay_at_hotel=input_data.is_pay_at_hotel,
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

        whatsapp_response = None
        if is_whatsapp:
            from .cancellation_schema import (
                WhatsappCancellationFormat,
                WhatsappCancellationFinalResponse,
            )
            whatsapp_response = WhatsappCancellationFinalResponse(
                response_text=success_text,
                whatsapp_json=WhatsappCancellationFormat(
                    type="cancellation",
                    status="cancelled",
                    message=success_text,
                    booking_id=input_data.booking_id,
                    transaction_type="Hotel",
                    refund_info=result.get("refund_info"),
                ),
            )

        return ToolResponseFormat(
            response_text=success_text,
            structured_content=result,
            html=html,
            whatsapp_response=(
                whatsapp_response.model_dump() if whatsapp_response else None
            ),
        )

    # ----------------------------------------------------------
    # _handle_confirm — Train branch
    # ----------------------------------------------------------
    async def _handle_confirm_train(self, input_data, render_html, is_whatsapp, service) -> ToolResponseFormat:
        # Auto-populate parameters for WhatsApp users from service session
        pax_ids = input_data.pax_ids
        reservation_id = input_data.reservation_id
        pnr_number = input_data.pnr_number
        total_passenger = input_data.total_passenger

        if is_whatsapp:
            # Auto-fill from service session if not provided
            if not pax_ids and hasattr(service, '_cancellation_pax_ids'):
                pax_ids = service._cancellation_pax_ids
            if not reservation_id and hasattr(service, '_cancellation_reservation_id'):
                reservation_id = service._cancellation_reservation_id
            if not pnr_number and hasattr(service, '_cancellation_pnr_number'):
                pnr_number = service._cancellation_pnr_number
            if not total_passenger and hasattr(service, '_cancellation_total_passenger'):
                total_passenger = service._cancellation_total_passenger

        # Validate required fields
        if not input_data.otp:
            return ToolResponseFormat(
                response_text="Please provide the OTP to confirm the cancellation.",
                is_error=True,
            )

        if not pax_ids or not reservation_id or not pnr_number:
            return ToolResponseFormat(
                response_text="Missing required cancellation details. Please start the cancellation process again.",
                is_error=True,
            )

        try:
            result = await service.request_train_cancellation(
                booking_id=input_data.booking_id,
                email=input_data.email,
                otp=input_data.otp,
                pax_ids=pax_ids,  # Use auto-populated value
                reservation_id=reservation_id,  # Use auto-populated value
                pnr_number=pnr_number,  # Use auto-populated value
                total_passenger=total_passenger or len(pax_ids),
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

        whatsapp_response = None
        if is_whatsapp:
            from .cancellation_schema import (
                WhatsappCancellationFormat,
                WhatsappCancellationFinalResponse,
            )
            whatsapp_response = WhatsappCancellationFinalResponse(
                response_text=success_text,
                whatsapp_json=WhatsappCancellationFormat(
                    type="cancellation",
                    status="cancelled",
                    message=success_text,
                    booking_id=input_data.booking_id,
                    transaction_type="Train",
                    refund_info=result.get("refund_info"),
                ),
            )

        return ToolResponseFormat(
            response_text=success_text,
            structured_content=result,
            html=html,
            whatsapp_response=(
                whatsapp_response.model_dump() if whatsapp_response else None
            ),
        )

    # ----------------------------------------------------------
    # _handle_start — Bus branch
    # ----------------------------------------------------------
    async def _handle_start_bus(
        self, input_data, login_result, bid, user_type, render_html, is_whatsapp, service
    ) -> ToolResponseFormat:
        # WhatsApp: Stop after sending login OTP, don't fetch details yet
        otp_sent = login_result.get("ids", {}).get("is_otp_send")
        if is_whatsapp and otp_sent:
            otp_text = (
                "📧 An OTP has been sent to your registered email/phone.\n\n"
                "🔐 Please enter the OTP to verify your identity and view booking details.\n\n"
                "Type the OTP like: \"123456\" or \"My OTP is ABC123\""
            )
            from .cancellation_schema import (
                WhatsappCancellationFormat,
                WhatsappCancellationFinalResponse,
            )
            whatsapp_response = WhatsappCancellationFinalResponse(
                response_text=otp_text,
                whatsapp_json=WhatsappCancellationFormat(
                    type="cancellation",
                    status="otp_sent_for_login",
                    message=otp_text,
                    booking_id=input_data.booking_id,
                    transaction_type="Bus",
                ),
            )
            return ToolResponseFormat(
                response_text=otp_text,
                structured_content={"login": login_result, "bid": bid, "transaction_type": "Bus"},
                whatsapp_response=whatsapp_response.model_dump(),
            )

        # Website/Chatbot: Continue with current flow (fetch details immediately)
        try:
            details_result = await service.fetch_bus_booking_details(bid=bid)
        except Exception as exc:
            logger.error(f"Service error during fetch bus details: {exc}", exc_info=True)
            return ToolResponseFormat(
                response_text="Something went wrong while fetching bus booking details. Please try again.",
                is_error=True,
            )

        combined = {
            "login": login_result,
            "booking_details": details_result,
            "bid": bid,
            "transaction_type": "Bus",
        }

        if not details_result["success"]:
            return ToolResponseFormat(
                response_text=f"Login succeeded but failed to fetch bus details: {details_result.get('error')}",
                structured_content=combined,
                is_error=True,
            )

        # Website mode: render interactive HTML
        if render_html:
            api_base_url = CHATBOT_API_BASE_URL
            is_otp_send = login_result.get("ids", {}).get("is_otp_send", False)
            html = render_bus_booking_details(
                booking_details=details_result,
                booking_id=input_data.booking_id,
                email=input_data.email,
                bid=bid,
                api_base_url=api_base_url,
                is_otp_send=is_otp_send,
            )
            return ToolResponseFormat(
                response_text=f"Bus booking details for {input_data.booking_id}",
                structured_content={
                    "booking_details": details_result,
                    "bid": bid,
                    "transaction_type": "Bus",
                },
                html=html,
            )

        # Chatbot / WhatsApp mode: build friendly text
        bus_info = details_result.get("bus_info", {})
        passengers = details_result.get("passengers", [])

        source = bus_info.get("source", "")
        destination = bus_info.get("destination", "")
        journey_date = bus_info.get("date_of_journey", "")
        departure_time = bus_info.get("departure_time", "")
        bus_type = bus_info.get("bus_type", "")
        operator = bus_info.get("travels_operator", "")
        ticket_no = bus_info.get("ticket_no", "")
        total_fare = bus_info.get("total_fare", "")

        booking_summary = []
        if operator:
            booking_summary.append(f"🚌 {operator}")
        if source and destination:
            booking_summary.append(f"📍 {source} → {destination}")
        if journey_date and departure_time:
            booking_summary.append(f"📅 {journey_date} at {departure_time}")
        if bus_type:
            booking_summary.append(f"🎫 {bus_type.strip()}")
        if ticket_no:
            booking_summary.append(f"🔢 Ticket: {ticket_no}")
        if total_fare:
            booking_summary.append(f"💰 Total Fare: ₹{total_fare}")

        pax_descriptions = []
        for idx, pax in enumerate(passengers, 1):
            name = f"{pax.get('title', '')} {pax.get('first_name', '')} {pax.get('last_name', '')}".strip()
            seat = pax.get('seat_no', '')
            fare = pax.get('fare', '')
            status = pax.get('status', '')

            desc = f"\n{idx}. {name}"
            if seat:
                desc += f" - Seat {seat}"
            if fare:
                desc += f" (₹{fare})"
            if status:
                desc += f" - {status}"
            pax_descriptions.append(desc)

        otp_sent = login_result.get("ids", {}).get("is_otp_send")
        otp_notice = ""
        if otp_sent:
            otp_notice = "\n\n🔐 An OTP has been sent to your registered email/phone. Please verify to proceed."

        friendly_text = (
            f"Here are the details for your bus booking **{input_data.booking_id}**:\n\n"
            + "\n".join(booking_summary)
            + "\n\n👥 **Passengers:**"
            + "".join(pax_descriptions)
            + otp_notice
            + "\n\nWould you like to proceed with the cancellation?"
        )

        whatsapp_response = None
        if is_whatsapp:
            from .cancellation_schema import (
                WhatsappCancellationFormat,
                WhatsappCancellationFinalResponse,
            )
            whatsapp_response = WhatsappCancellationFinalResponse(
                response_text=friendly_text,
                whatsapp_json=WhatsappCancellationFormat(
                    type="cancellation",
                    status="booking_details",
                    message=friendly_text,
                    booking_id=input_data.booking_id,
                    transaction_type="Bus",
                    seats=[
                        {
                            "seat_no": p.get("seat_no"),
                            "name": f"{p.get('title', '')} {p.get('first_name', '')} {p.get('last_name', '')}".strip(),
                            "fare": p.get("fare"),
                            "status": p.get("status"),
                        }
                        for p in passengers
                    ],
                ),
            )

        return ToolResponseFormat(
            response_text=friendly_text,
            structured_content=combined,
            whatsapp_response=(
                whatsapp_response.model_dump() if whatsapp_response else None
            ),
        )

    # ----------------------------------------------------------
    # _handle_confirm — Bus branch
    # ----------------------------------------------------------
    async def _handle_confirm_bus(self, input_data, render_html, is_whatsapp, service) -> ToolResponseFormat:
        # Auto-populate parameters for WhatsApp users from service session
        seats = input_data.seats

        if is_whatsapp:
            # Auto-fill from service session if not provided
            if not seats and hasattr(service, '_cancellation_seats'):
                seats = service._cancellation_seats

        # Validate required fields
        if not input_data.otp:
            return ToolResponseFormat(
                response_text="Please provide the OTP to confirm the cancellation.",
                is_error=True,
            )

        if not seats:
            return ToolResponseFormat(
                response_text="Missing required cancellation details. Please start the cancellation process again.",
                is_error=True,
            )

        try:
            result = await service.request_bus_cancellation(
                booking_id=input_data.booking_id,
                email=input_data.email,
                otp=input_data.otp,
                seats=seats,  # Use auto-populated value
                transaction_id=input_data.transaction_id or "",
                reason=input_data.reason or "",
                remark=input_data.remark or "",
            )
        except Exception as exc:
            logger.error(f"Service error during bus cancellation: {exc}", exc_info=True)
            return ToolResponseFormat(
                response_text="Something went wrong while submitting bus cancellation. Please try again.",
                is_error=True,
            )

        if not result["success"]:
            return ToolResponseFormat(
                response_text=f"Bus cancellation failed: {result['message']}\n\nPlease try again or contact customer support.",
                structured_content=result,
                is_error=True,
            )

        refund_info = result.get("refund_info")
        if refund_info:
            refund_amount = refund_info.get('refund_amount', 'N/A')
            cancellation_charges = refund_info.get('cancellation_charges', 'N/A')
            remarks = refund_info.get('remarks', '')
            success_text = (
                f"Your bus booking has been successfully cancelled!\n\n"
                f"Refund Details:\n"
                f"   • Refund Amount: ₹{refund_amount}\n"
                f"   • Cancellation Charges: ₹{cancellation_charges}\n"
            )
            if remarks:
                success_text += f"   • {remarks}\n"
            success_text += (
                f"\nYou will receive a cancellation confirmation email shortly.\n"
                f"The refund will be processed within 5-7 business days.\n\n"
                f"Thank you for using EaseMyTrip. We hope to serve you again!"
            )
        else:
            success_text = (
                f"Your bus booking has been successfully cancelled!\n\n"
                f"You will receive a cancellation confirmation email shortly.\n\n"
                f"Thank you for using EaseMyTrip. We hope to serve you again!"
            )

        html = None
        if render_html:
            result["booking_id"] = input_data.booking_id
            html = render_cancellation_success(result)

        whatsapp_response = None
        if is_whatsapp:
            from .cancellation_schema import (
                WhatsappCancellationFormat,
                WhatsappCancellationFinalResponse,
            )
            whatsapp_response = WhatsappCancellationFinalResponse(
                response_text=success_text,
                whatsapp_json=WhatsappCancellationFormat(
                    type="cancellation",
                    status="cancelled",
                    message=success_text,
                    booking_id=input_data.booking_id,
                    transaction_type="Bus",
                    refund_info=result.get("refund_info"),
                ),
            )

        return ToolResponseFormat(
            response_text=success_text,
            structured_content=result,
            html=html,
            whatsapp_response=(
                whatsapp_response.model_dump() if whatsapp_response else None
            ),
        )

    # ----------------------------------------------------------
    # _handle_start — Flight branch
    # ----------------------------------------------------------
    async def _handle_start_flight(
        self, input_data, login_result, bid, user_type, render_html, is_whatsapp, service
    ) -> ToolResponseFormat:
        # WhatsApp: Stop after sending login OTP, don't fetch details yet
        otp_sent = login_result.get("ids", {}).get("is_otp_send")
        if is_whatsapp and otp_sent:
            otp_text = (
                "📧 An OTP has been sent to your registered email/phone.\n\n"
                "🔐 Please enter the OTP to verify your identity and view booking details.\n\n"
                "Type the OTP like: \"123456\" or \"My OTP is ABC123\""
            )
            from .cancellation_schema import (
                WhatsappCancellationFormat,
                WhatsappCancellationFinalResponse,
            )
            whatsapp_response = WhatsappCancellationFinalResponse(
                response_text=otp_text,
                whatsapp_json=WhatsappCancellationFormat(
                    type="cancellation",
                    status="otp_sent_for_login",
                    message=otp_text,
                    booking_id=input_data.booking_id,
                    transaction_type="Flight",
                ),
            )
            return ToolResponseFormat(
                response_text=otp_text,
                structured_content={"login": login_result, "bid": bid, "transaction_type": "Flight"},
                whatsapp_response=whatsapp_response.model_dump(),
            )

        # Website/Chatbot: Continue with current flow (fetch details immediately)
        try:
            details_result = await service.fetch_flight_booking_details(bid=bid)
        except Exception as exc:
            logger.error(f"Service error during fetch flight details: {exc}", exc_info=True)
            return ToolResponseFormat(
                response_text="Something went wrong while fetching flight booking details. Please try again.",
                is_error=True,
            )

        combined = {
            "login": login_result,
            "booking_details": details_result,
            "bid": bid,
            "transaction_type": "Flight",
        }

        if not details_result["success"]:
            return ToolResponseFormat(
                response_text=f"Login succeeded but failed to fetch flight details: {details_result.get('error')}",
                structured_content=combined,
                is_error=True,
            )

        # Store total cancellable for partial cancel computation
        service._total_cancellable = details_result.get("total_cancellable", 0)

        # Website mode: render interactive HTML
        if render_html:
            api_base_url = CHATBOT_API_BASE_URL
            is_otp_send = login_result.get("ids", {}).get("is_otp_send", False)
            html = render_flight_booking_details(
                booking_details=details_result,
                booking_id=input_data.booking_id,
                email=input_data.email,
                bid=bid,
                api_base_url=api_base_url,
                is_otp_send=is_otp_send,
            )
            return ToolResponseFormat(
                response_text=f"Flight booking details for {input_data.booking_id}",
                structured_content={
                    "booking_details": details_result,
                    "bid": bid,
                    "transaction_type": "Flight",
                },
                html=html,
            )

        # Chatbot / WhatsApp mode: build friendly text
        flight_segments = details_result.get("flight_segments", [])
        outbound_pax = details_result.get("outbound_passengers", [])
        inbound_pax = details_result.get("inbound_passengers", [])
        price_info = details_result.get("price_info", {})
        pnr_info = details_result.get("pnr_info", [])

        booking_summary = []

        # Flight segments info
        for seg in flight_segments:
            airline = seg.get("airline_code") or seg.get("airline_name", "")
            flight_no = seg.get("flight_number", "")
            origin = seg.get("origin", "")
            destination = seg.get("destination", "")
            dep_date = seg.get("departure_date", "")
            dep_time = seg.get("departure_time", "")
            arr_time = seg.get("arrival_time", "")
            duration = seg.get("duration", "")
            cabin = seg.get("cabin_class", "")
            bound = seg.get("bound_type", "")

            bound_label = ""
            if bound:
                bound_lower = str(bound).lower()
                if "out" in bound_lower:
                    bound_label = "Outbound"
                elif "in" in bound_lower:
                    bound_label = "Inbound"

            seg_line = f"✈️ {airline} {flight_no} — {origin} → {destination}"
            if dep_date:
                seg_line += f" | {dep_date}"
            if dep_time and arr_time:
                seg_line += f" ({dep_time} - {arr_time})"
            if duration:
                seg_line += f" | {duration}"
            if cabin:
                seg_line += f" | {cabin}"
            if bound_label:
                seg_line = f"[{bound_label}] {seg_line}"
            booking_summary.append(seg_line)

        # PNR info
        for pnr in pnr_info:
            airline_pnr = pnr.get("airline_pnr", "")
            gds_pnr = pnr.get("gds_pnr", "")
            if airline_pnr:
                booking_summary.append(f"🔢 Airline PNR: {airline_pnr}")
            if gds_pnr:
                booking_summary.append(f"🔢 GDS PNR: {gds_pnr}")

        # Price info
        total_fare = price_info.get("total_fare", "")
        if total_fare:
            booking_summary.append(f"💰 Total Fare: ₹{total_fare}")

        # Passengers
        pax_descriptions = []
        all_pax = []
        for pax in outbound_pax:
            all_pax.append({**pax, "_bound": "Outbound"})
        for pax in inbound_pax:
            all_pax.append({**pax, "_bound": "Inbound"})

        for idx, pax in enumerate(all_pax, 1):
            name = f"{pax.get('title', '')} {pax.get('first_name', '')} {pax.get('last_name', '')}".strip()
            pax_type = pax.get("pax_type", "")
            status = pax.get("status", "")
            ticket = pax.get("ticket_number", "")
            bound_label = pax.get("_bound", "")
            charge = pax.get("cancellation_charge", "")

            desc = f"\n{idx}. {name}"
            if pax_type:
                desc += f" ({pax_type})"
            if bound_label:
                desc += f" [{bound_label}]"
            if ticket:
                desc += f" - Ticket: {ticket}"
            if status:
                desc += f" - {status}"
            if charge:
                desc += f" - Cancel charge: ₹{charge}"
            pax_descriptions.append(desc)

        otp_sent = login_result.get("ids", {}).get("is_otp_send")
        otp_notice = ""
        if otp_sent:
            otp_notice = "\n\n📧 An OTP has been sent to your registered email/phone. Please provide it to verify your identity before proceeding."

        text = (
            f"Here are the details for your flight booking **{input_data.booking_id}**:\n\n"
            + "\n".join(booking_summary)
            + "\n\n👥 **Passengers:**"
            + "".join(pax_descriptions)
            + otp_notice
            + "\n\nWould you like to proceed with the cancellation?"
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
                    transaction_type="Flight",
                    flight_passengers=[
                        {
                            "pax_id": p.get("pax_id"),
                            "name": f"{p.get('title', '')} {p.get('first_name', '')} {p.get('last_name', '')}".strip(),
                            "pax_type": p.get("pax_type"),
                            "status": p.get("status"),
                            "bound_type": p.get("bound_type"),
                        }
                        for p in all_pax
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
    # _handle_confirm — Flight branch
    # ----------------------------------------------------------
    async def _handle_confirm_flight(self, input_data, render_html, is_whatsapp, service) -> ToolResponseFormat:
        # Auto-populate parameters for WhatsApp users from service session
        outbound_pax_ids = input_data.outbound_pax_ids
        inbound_pax_ids = input_data.inbound_pax_ids

        if is_whatsapp:
            # Auto-fill from service session if not provided
            if not outbound_pax_ids and hasattr(service, '_cancellation_outbound_pax_ids'):
                outbound_pax_ids = service._cancellation_outbound_pax_ids
            if not inbound_pax_ids and hasattr(service, '_cancellation_inbound_pax_ids'):
                inbound_pax_ids = service._cancellation_inbound_pax_ids

        # Validate required fields
        if not input_data.otp:
            return ToolResponseFormat(
                response_text="Please provide the OTP to confirm the cancellation.",
                is_error=True,
            )

        if not outbound_pax_ids and not inbound_pax_ids:
            return ToolResponseFormat(
                response_text="Missing required cancellation details. Please start the cancellation process again.",
                is_error=True,
            )

        # Extract mode (default to "1" for backward compatibility)
        mode = input_data.mode or "1"

        try:
            result = await service.request_flight_cancellation(
                booking_id=input_data.booking_id,
                email=input_data.email,
                otp=input_data.otp,
                outbound_pax_ids=outbound_pax_ids or "",  # Use auto-populated value
                inbound_pax_ids=inbound_pax_ids or "",  # Use auto-populated value
                mode=mode,  # Pass mode to service
            )
        except Exception as exc:
            logger.error(f"Service error during flight cancellation: {exc}", exc_info=True)
            return ToolResponseFormat(
                response_text="Something went wrong while submitting flight cancellation. Please try again.",
                is_error=True,
            )

        if not result["success"]:
            return ToolResponseFormat(
                response_text=f"❌ Flight cancellation failed: {result['message']}\n\nPlease try again or contact customer support.",
                structured_content=result,
                is_error=True,
            )

        refund_info = result.get("refund_info")
        if refund_info:
            refund_amount = refund_info.get('refund_amount', 'N/A')
            cancellation_charges = refund_info.get('cancellation_charges', 'N/A')
            success_text = (
                f"Your flight booking has been successfully cancelled!\n\n"
                f"Refund Details:\n"
                f"   • Refund Amount: ₹{refund_amount}\n"
                f"   • Cancellation Charges: ₹{cancellation_charges}\n"
                f"   • Refund Mode: {refund_info.get('refund_mode', 'Original payment method')}\n\n"
                f"You will receive a cancellation confirmation email shortly.\n"
                f"The refund will be processed within 5-7 business days.\n\n"
                f"Thank you for using EaseMyTrip. We hope to serve you again!"
            )
        else:
            success_text = (
                f"Your flight booking has been successfully cancelled!\n\n"
                f"{result.get('message', '')}\n\n"
                f"You will receive a cancellation confirmation email shortly.\n\n"
                f"Thank you for using EaseMyTrip. We hope to serve you again!"
            )

        html = None
        if render_html:
            result["booking_id"] = input_data.booking_id
            html = render_cancellation_success(result)

        whatsapp_response = None
        if is_whatsapp:
            from .cancellation_schema import (
                WhatsappCancellationFormat,
                WhatsappCancellationFinalResponse,
            )
            whatsapp_response = WhatsappCancellationFinalResponse(
                response_text=success_text,
                whatsapp_json=WhatsappCancellationFormat(
                    type="cancellation",
                    status="cancelled",
                    message=success_text,
                    booking_id=input_data.booking_id,
                    transaction_type="Flight",
                    refund_info=result.get("refund_info"),
                ),
            )

        return ToolResponseFormat(
            response_text=success_text,
            structured_content=result,
            html=html,
            whatsapp_response=(
                whatsapp_response.model_dump() if whatsapp_response else None
            ),
        )
