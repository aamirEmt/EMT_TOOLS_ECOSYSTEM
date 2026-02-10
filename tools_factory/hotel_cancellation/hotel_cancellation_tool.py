"""Hotel Cancellation Tool - Unified tool with action-based dispatch"""
from typing import Dict, Tuple
import asyncio
import time
import logging
from pydantic import ValidationError

from ..base import BaseTool, ToolMetadata
from ..base_schema import ToolResponseFormat
from .hotel_cancellation_schema import HotelCancellationInput
from .hotel_cancellation_service import HotelCancellationService
from .hotel_cancellation_renderer import render_booking_details, render_cancellation_success

logger = logging.getLogger(__name__)


# ============================================================
# Per-User Session Registry (isolates concurrent users)
# ============================================================
_sessions: Dict[str, Tuple[HotelCancellationService, float]] = {}
_sessions_lock = asyncio.Lock()
_SESSION_TTL_SECONDS = 1800  # 30 minutes
_MAX_SESSIONS = 500


def _session_key(booking_id: str, email: str) -> str:
    """Create a unique session key from booking_id + email"""
    return f"{booking_id.strip().upper()}:{email.strip().lower()}"


async def get_user_service(booking_id: str, email: str) -> HotelCancellationService:
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
            svc = HotelCancellationService()
            _sessions[key] = (svc, now)
            result = svc
        else:
            svc = HotelCancellationService()
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
# Unified Hotel Cancellation Tool
# ============================================================
class HotelCancellationTool(BaseTool):
    """
    Single tool for the entire hotel cancellation flow.

    Actions:
      - "start"    : Login + fetch booking details → returns room list
      - "send_otp" : Send cancellation OTP to user's email
      - "confirm"  : Submit cancellation with OTP, room_id, transaction_id
    """

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="hotel_cancellation",
            description=(
                "Hotel booking cancellation tool. "
                "Use action='start' with booking_id and email to fetch booking details. "
                "Use action='send_otp' to send cancellation OTP. "
                "Use action='confirm' with otp, room_id, and transaction_id to complete cancellation."
            ),
            input_schema=HotelCancellationInput.model_json_schema(),
            category="cancellation",
            tags=["hotel", "cancellation", "flow"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        user_type = kwargs.pop("_user_type", "chatbot")
        api_base_url = kwargs.pop("_api_base_url", None)
        kwargs.pop("_limit", None)

        try:
            input_data = HotelCancellationInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid input for hotel cancellation",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        action = input_data.action.lower().strip()

        if action == "start":
            return await self._handle_start(input_data, user_type, api_base_url)
        elif action == "send_otp":
            return await self._handle_send_otp(input_data)
        elif action == "confirm":
            return await self._handle_confirm(input_data, user_type)
        else:
            return ToolResponseFormat(
                response_text=f"Unknown action '{input_data.action}'. Use 'start', 'send_otp', or 'confirm'.",
                is_error=True,
            )

    # ----------------------------------------------------------
    # action = "start" — login + fetch booking details
    # ----------------------------------------------------------
    async def _handle_start(self, input_data: HotelCancellationInput, user_type: str, api_base_url: str = None) -> ToolResponseFormat:
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

        # Step 2: Fetch booking details
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
            html = render_booking_details(
                booking_details=details_result,
                api_base_url=api_base_url or "",
                booking_id=input_data.booking_id,
                email=input_data.email,
            )
            return ToolResponseFormat(
                response_text=f"Booking details for {input_data.booking_id}",
                structured_content={
                    "booking_details": details_result,
                    "bid": bid,
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

        if len(rooms) == 1:
            text = (
                f"I've pulled up your booking details for {hotel_name}.\n\n"
                + "\n".join(booking_summary) + "\n"
                + "\n".join(room_descriptions) + "\n\n"
                f"Would you like to cancel this booking?"
            )
        else:
            text = (
                f"I've pulled up your booking details for {hotel_name}.\n\n"
                + "\n".join(booking_summary) + "\n"
                + "\n".join(room_descriptions) + "\n\n"
                f"Which room would you like to cancel?"
            )

        whatsapp_response = None
        if is_whatsapp:
            from .hotel_cancellation_schema import (
                WhatsappCancellationFormat,
                WhatsappCancellationFinalResponse,
            )
            whatsapp_response = WhatsappCancellationFinalResponse(
                response_text=text,
                whatsapp_json=WhatsappCancellationFormat(
                    type="hotel_cancellation",
                    status="booking_details",
                    message=text,
                    booking_id=input_data.booking_id,
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
    # action = "send_otp"
    # ----------------------------------------------------------
    async def _handle_send_otp(self, input_data: HotelCancellationInput) -> ToolResponseFormat:
        service = await get_user_service(input_data.booking_id, input_data.email)
        try:
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
                f"📧 An OTP (One-Time Password) has been sent to your registered email address.\n\n"
                f"🔐 Please check your email and provide the OTP to confirm the cancellation.\n\n"
                f"⏱️ Note: The OTP is valid for 10 minutes only.\n\n"
                f"Type the OTP like: \"123456\" or \"My OTP is ABC123\""
            ),
            structured_content=result,
        )

    # ----------------------------------------------------------
    # action = "confirm" — submit cancellation with OTP
    # ----------------------------------------------------------
    async def _handle_confirm(self, input_data: HotelCancellationInput, user_type: str) -> ToolResponseFormat:
        render_html = user_type.lower() == "website"

        # Validate required fields
        if not input_data.otp or not input_data.room_id or not input_data.transaction_id:
            return ToolResponseFormat(
                response_text="Missing required fields for confirm: otp, room_id, transaction_id",
                is_error=True,
            )

        service = await get_user_service(input_data.booking_id, input_data.email)
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
