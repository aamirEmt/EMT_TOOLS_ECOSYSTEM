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
        self._download_endpoints = {
            "flight": ("GET", "https://mybookings.easemytrip.com/MyBooking/GetdownLodingPdf"),
            "train": ("GET", "https://mybookings.easemytrip.com/Train/DownloadPdf/"),
            "hotels": ("GET", "https://mybookings.easemytrip.com/Hotels/DownloadPdf/"),
            "bus": ("POST", "https://mybookings.easemytrip.com/Bus/GetPdf/"),
        }

    async def send_otp(self, booking_id: str, email: str) -> Dict[str, Any]:
        """Call EMT guest login API to trigger OTP and retrieve BID."""
        async with self._lock:
            try:
                async with MyBookingsApiClient() as client:
                    data = await client.guest_login(booking_id, email)
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
            async with MyBookingsApiClient() as client:
                data = await client.verify_guest_login_otp(
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

    async def fetch_download_url(self, bid: str, transaction_type: str | None) -> Dict[str, Any]:
        """Fetch download PDF link based on transaction type."""
        tx = (transaction_type or "flight").strip().lower()
        method, base_url = self._download_endpoints.get(tx, self._download_endpoints["flight"])

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                if method == "GET":
                    separator = "&" if "?" in base_url else "?"
                    url = f"{base_url}{separator}bid={bid}"
                    response = await client.get(url)
                else:  # POST (bus)
                    response = await client.post(base_url, json={"bid": bid})

                response.raise_for_status()
                data = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        except httpx.HTTPError as exc:
            logger.error("Download fetch failed for %s: %s", tx, exc, exc_info=True)
            return {
                "success": False,
                "message": "Failed to fetch download link.",
            }

        if isinstance(data, dict):
            download_url = data.get("url") or data.get("Url") or data.get("download_url") or data.get("DownloadUrl")
        else:
            download_url = data

        if not download_url:
            return {
                "success": False,
                "message": "Download link not found in response.",
                "raw": data,
            }

        return {
            "success": True,
            "download_url": download_url,
            "raw": data,
        }
