"""Tool orchestrator for flight post-booking actions (seat, meal, baggage)."""
from typing import Dict, Tuple
import asyncio
import time
import logging

from ..base import BaseTool, ToolMetadata
from ..base_schema import ToolResponseFormat
from .post_booking_schema import FlightPostBookingInput
from .post_booking_service import FlightPostBookingService
from .post_booking_renderer import render_otp_verification_view

logger = logging.getLogger(__name__)

# =====================================
# Simple in-memory per-user service bag
# =====================================
_sessions: Dict[str, Tuple[FlightPostBookingService, float]] = {}
_sessions_lock = asyncio.Lock()
_SESSION_TTL_SECONDS = 1800  # 30 minutes

POST_BOOKING_BASE_URLS = {
    "flight": "https://mybookings.easemytrip.com/MyBooking/FlightDetails",
    "bus": "https://mybookings.easemytrip.com/Bus/bookingDetail",
    "train": "https://mybookings.easemytrip.com/Train/Index",
    "hotels": "https://mybookings.easemytrip.com/Hotels/Detail",
}


def _resolve_post_booking_url(transaction_type: str | None) -> str:
    """Return the correct post-booking base URL for the given transaction type."""
    tx = (transaction_type or "flight").strip().lower()
    return POST_BOOKING_BASE_URLS.get(tx, POST_BOOKING_BASE_URLS["flight"])


def _session_key(booking_id: str, email: str) -> str:
    return f"{booking_id.strip().upper()}:{email.strip().lower()}"


async def _cleanup_expired_sessions(now: float) -> None:
    """Remove stale session objects."""
    expired_keys = [
        key for key, (_, ts) in _sessions.items()
        if now - ts > _SESSION_TTL_SECONDS
    ]
    for key in expired_keys:
        _sessions.pop(key, None)


async def get_user_service(booking_id: str, email: str) -> FlightPostBookingService:
    """Get or create a service instance for a booking/email pair."""
    key = _session_key(booking_id, email)
    async with _sessions_lock:
        now = time.time()
        await _cleanup_expired_sessions(now)

        if key in _sessions:
            _sessions[key] = (_sessions[key][0], now)  # refresh TTL
            return _sessions[key][0]

        service = FlightPostBookingService()
        _sessions[key] = (service, now)
        return service


class FlightPostBookingTool(BaseTool):
    """
    Actions:
      - start      : send OTP for the provided booking/email
      - verify_otp : validate OTP and return redirect URL with BID attached
    """

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="flight_post_booking",
            description=(
                "Tool for add seat, meal, baggage, reschedule flight (post-booking actions.) "
                "Takes booking ID and email to send OTP, then verifies OTP and returns a redirect URL with BID for post-booking management. "
                "Send OTP for post-booking flight actions (add seat, meal, baggage), "
                "verify it, and return a redirect URL containing the BID."
            ),
            input_schema=FlightPostBookingInput.model_json_schema(),
            output_template=None,
            category="flights",
            tags=["flight", "post-booking", "otp", "seat", "meal", "baggage"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        try:
            input_data = FlightPostBookingInput(**kwargs)
        except Exception as exc:
            return ToolResponseFormat(response_text=str(exc), is_error=True)

        action = input_data.action

        if action == "start":
            return await self._handle_start(input_data)
        if action == "verify_otp":
            return await self._handle_verify(input_data)

        return ToolResponseFormat(
            response_text="Invalid action. Use 'start' or 'verify_otp'.",
            is_error=True,
        )

    # -----------------------
    # action = "start"
    # -----------------------
    async def _handle_start(self, input_data: FlightPostBookingInput) -> ToolResponseFormat:
        service = await get_user_service(input_data.booking_id, input_data.email)

        try:
            result = await service.send_otp(
                booking_id=input_data.booking_id,
                email=input_data.email,
            )
        except Exception:
            logger.error("Post-booking OTP send failed", exc_info=True)
            return ToolResponseFormat(
                response_text="Could not send OTP. Please try again.",
                is_error=True,
            )

        if not result.get("success"):
            return ToolResponseFormat(
                response_text=f"OTP send failed: {result.get('message')}",
                structured_content=result,
                is_error=True,
            )

        # Persist BID and transaction type on the service for later URL creation
        service._bid = result.get("bid")
        service._transaction_type = result.get("transaction_type") or "Flight"
        service._download_requested = bool(input_data.download)

        # Build HTML for OTP entry UI
        html = render_otp_verification_view(
            booking_id=input_data.booking_id,
            email=input_data.email,
            is_otp_send=result.get("is_otp_sent", True),
            download=bool(input_data.download),
            api_endpoint="/tools/flight_post_booking",
        )

        return ToolResponseFormat(
            response_text="OTP sent. Please verify to continue post-booking actions.",
            structured_content={
                "otp_sent": result.get("is_otp_sent", True),
                "bid": result.get("bid"),
                "transaction_type": result.get("transaction_type") or "Flight",
                "message": result.get("message"),
                "download": bool(input_data.download),
            },
            html=html,
        )

    # -----------------------
    # action = "verify_otp"
    # -----------------------
    async def _handle_verify(self, input_data: FlightPostBookingInput) -> ToolResponseFormat:
        if not input_data.otp:
            return ToolResponseFormat(
                response_text="Please provide the OTP received on your email/phone.",
                is_error=True,
            )

        service = await get_user_service(input_data.booking_id, input_data.email)

        try:
            result = await service.verify_otp(otp=input_data.otp)
        except Exception:
            logger.error("Post-booking OTP verification failed", exc_info=True)
            return ToolResponseFormat(
                response_text="OTP verification failed. Please try again.",
                is_error=True,
            )

        if not result.get("success"):
            return ToolResponseFormat(
                response_text=f"Invalid OTP: {result.get('message')}",
                structured_content=result,
                is_error=True,
            )

        bid = result.get("bid") or getattr(service, "_bid", None)
        transaction_type = getattr(service, "_transaction_type", None) or "Flight"
        if not bid:
            return ToolResponseFormat(
                response_text="OTP verified but BID was not found.",
                is_error=True,
            )

        base_url = _resolve_post_booking_url(transaction_type)
        redirect_url = f"{base_url}?bid={bid}"
        download_requested = getattr(service, "_download_requested", False)
        download_url = None
        if download_requested:
            download_result = await service.fetch_download_url(bid, transaction_type)
            if not download_result.get("success"):
                return ToolResponseFormat(
                    response_text=f"OTP verified but failed to fetch download link: {download_result.get('message')}",
                    structured_content={
                        "bid": bid,
                        "transaction_type": transaction_type,
                        "redirect_url": redirect_url,
                        "download_error": download_result,
                        "download": download_requested,
                    },
                    is_error=True,
                )
            download_url = download_result.get("download_url")

        return ToolResponseFormat(
            response_text="OTP verified. Continue with seat/meal/baggage selection.",
            structured_content={
                "bid": bid,
                "transaction_type": transaction_type,
                "redirect_url": redirect_url,
                "actions": ["add_seat", "add_meal", "add_baggage"],
                "message": result.get("message"),
                "download": download_requested,
                "download_url": download_url,
            },
        )
