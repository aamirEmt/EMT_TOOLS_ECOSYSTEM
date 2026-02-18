"""Service layer for flight post-booking OTP flow."""
import asyncio
import logging
from typing import Dict, Any

import httpx

logger = logging.getLogger(__name__)


# API endpoints (can be moved to config if reused elsewhere)
LOGIN_GUEST_URL = "https://mybookings.easemytrip.com/Mybooking/LoginGuestUser?app=null"
VERIFY_GUEST_URL = "https://mybookings.easemytrip.com/Mybooking/VerifyGuestLoginOtp"


class FlightPostBookingService:
    """Encapsulates OTP send/verify and BID handling for post-booking actions."""

    def __init__(self) -> None:
        self._bid: str | None = None
        self._transaction_type: str | None = None
        # lock to avoid concurrent requests per service instance
        self._lock = asyncio.Lock()

    async def send_otp(self, booking_id: str, email: str) -> Dict[str, Any]:
        """Call EMT guest login API to trigger OTP and retrieve BID."""
        payload = {
            "BetId": booking_id,
            "Emailid": email,
        }

        async with self._lock:
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.post(LOGIN_GUEST_URL, json=payload)
                    response.raise_for_status()
                    data = response.json()
            except httpx.HTTPError as exc:
                logger.error("LoginGuestUser failed: %s", exc, exc_info=True)
                return {
                    "success": False,
                    "message": "Login API failed. Please try again.",
                }

            ids = data.get("Ids") or {}
            bid = ids.get("bid")
            is_otp_sent = str(ids.get("IsOtpSend", "")).lower() == "true"
            transaction_type = ids.get("TransactionType") or "Flight"

            if not bid:
                return {
                    "success": False,
                    "message": "Login API did not return BID.",
                    "raw": data,
                }

            # cache values for verification step
            self._bid = bid
            self._transaction_type = transaction_type

            return {
                "success": True,
                "message": ids.get("Message") or "OTP sent successfully.",
                "is_otp_sent": is_otp_sent,
                "bid": bid,
                "transaction_type": transaction_type,
                "raw": data,
            }

    async def verify_otp(self, otp: str) -> Dict[str, Any]:
        """Verify OTP using EMT verify API."""
        if not self._bid:
            return {
                "success": False,
                "message": "No BID stored. Please start the flow again.",
            }

        payload = {
            "BetId": self._bid,
            "otp": otp,
            "transactionType": self._transaction_type or "Flight",
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(VERIFY_GUEST_URL, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            logger.error("VerifyGuestLoginOtp failed: %s", exc, exc_info=True)
            return {
                "success": False,
                "message": "OTP verification failed. Please try again.",
            }

        is_verified = str(data.get("isVerify", "")).lower() == "true"
        if not is_verified:
            return {
                "success": False,
                "message": data.get("Message") or "Invalid OTP.",
                "raw": data,
            }

        logger.info("OTP verified for BID %s", self._bid)
        return {
            "success": True,
            "message": data.get("Message") or "OTP verified successfully.",
            "bid": self._bid,
            "transaction_type": self._transaction_type or "Flight",
            "raw": data,
        }
