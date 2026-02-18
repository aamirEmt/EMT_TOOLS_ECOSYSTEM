"""Service layer for flight post-booking OTP flow."""
import asyncio
import logging
import random
from typing import Dict, Any

logger = logging.getLogger(__name__)


class FlightPostBookingService:
    """Encapsulates OTP send/verify and BID handling for post-booking actions."""

    def __init__(self) -> None:
        self._otp: str | None = None
        self._bid: str | None = None
        # Simple lock to avoid concurrent OTP generation for the same service instance
        self._lock = asyncio.Lock()

    async def send_otp(self, booking_id: str, email: str) -> Dict[str, Any]:
        """Simulate sending OTP and preparing BID for downstream link building."""
        async with self._lock:
            self._otp = self._generate_otp()
            self._bid = self._build_bid(booking_id)

        logger.info("OTP generated for booking %s sent to %s", booking_id, email)

        return {
            "success": True,
            "message": "OTP has been sent to your registered email/phone.",
            "is_otp_sent": True,
            "bid": self._bid,
            "otp_hint": "Use the OTP shared via your registered contact.",
        }

    async def verify_otp(self, otp: str) -> Dict[str, Any]:
        """Verify OTP that was generated during send_otp."""
        if not self._otp:
            return {
                "success": False,
                "message": "No OTP session found. Please start again.",
            }

        if otp != self._otp:
            return {
                "success": False,
                "message": "Invalid OTP. Please check and try again.",
            }

        logger.info("OTP verified for BID %s", self._bid)
        return {
            "success": True,
            "message": "OTP verified successfully.",
            "bid": self._bid,
        }

    def _generate_otp(self) -> str:
        """Generate a 6-digit numeric OTP."""
        return f"{random.randint(0, 999999):06d}"

    def _build_bid(self, booking_id: str) -> str:
        """Derive a BID placeholder from booking id (can be replaced with API value)."""
        token = booking_id.strip().upper()
        suffix = token[-6:] if token else "UNKNOWN"
        return f"BID-{suffix}"

