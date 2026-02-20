"""Service layer for flight post-booking OTP flow."""
import asyncio
import logging
from typing import Dict, Any

import httpx
from emt_client.clients.mybookings_client import MyBookingsApiClient

logger = logging.getLogger(__name__)


class FlightPostBookingService:
    """Encapsulates OTP send/verify and BID handling for post-booking actions."""

    def __init__(self) -> None:
        self._bid: str | None = None
        self._transaction_type: str | None = None
        # lock to avoid concurrent requests per service instance
        self._lock = asyncio.Lock()
        self._eticket_url = "https://emtservice-ln.easemytrip.com/api/Partials/GetETicketByBETID"
        # Persistent client with cookie jar — shared across send_otp, verify_otp, fetch_download_url
        self.client = MyBookingsApiClient()

    async def send_otp(self, booking_id: str, email: str) -> Dict[str, Any]:
        """Call EMT guest login API to trigger OTP and retrieve BID."""
        async with self._lock:
            try:
                data = await self.client.guest_login(booking_id, email)
            except Exception as exc:
                logger.error("guest_login failed: %s", exc, exc_info=True)
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

    async def send_flight_post_booking_otp(self, booking_id: str, email: str) -> Dict[str, Any]:
        """Send post-booking OTP for a flight booking."""
        return await self.send_otp(booking_id, email)

    async def send_bus_post_booking_otp(self, booking_id: str, email: str) -> Dict[str, Any]:
        """Send post-booking OTP for a bus booking."""
        return await self.send_otp(booking_id, email)

    async def send_train_post_booking_otp(self, booking_id: str, email: str) -> Dict[str, Any]:
        """Send post-booking OTP for a train booking."""
        return await self.send_otp(booking_id, email)

    async def send_hotel_post_booking_otp(self, booking_id: str, email: str) -> Dict[str, Any]:
        """Send post-booking OTP for a hotel booking."""
        return await self.send_otp(booking_id, email)

    async def verify_otp(self, otp: str) -> Dict[str, Any]:
        """Verify OTP using EMT verify API."""
        if not self._bid:
            return {
                "success": False,
                "message": "No BID stored. Please start the flow again.",
            }

        try:
            data = await self.client.verify_guest_login_otp(
                self._bid, otp, self._transaction_type or "Flight"
            )
        except Exception as exc:
            logger.error("verify_guest_login_otp failed: %s", exc, exc_info=True)
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

    async def fetch_download_url(self, bid: str, email: str) -> Dict[str, Any]:
        """Fetch e-ticket PDF link using the unified EMT eticket API."""
        try:
            response = await self.client.client.post(
                self._eticket_url,
                json={"bid": bid},
                headers={"auth": email},
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            logger.error("E-ticket fetch failed: %s", exc, exc_info=True)
            return {
                "success": False,
                "message": "Failed to fetch e-ticket link.",
            }

        is_success = data.get("Status") is True
        download_url = data.get("Url") or data.get("url")

        if not is_success or not download_url:
            return {
                "success": False,
                "message": data.get("Error") or data.get("Msg") or "E-ticket link not found in response.",
                "raw": data,
            }

        return {
            "success": True,
            "download_url": download_url,
            "raw": data,
        }
