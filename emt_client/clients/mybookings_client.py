"""MyBookings API Client for Cancellation Flow (Hotel, Train, etc.)"""
import httpx
from typing import Dict, Any
import logging
import json

from emt_client.config import MYBOOKINGS_BASE_URL

logger = logging.getLogger(__name__)


class MyBookingsApiClient:
    """
    Client for mybookings.easemytrip.com cancellation APIs (Hotel, Train, etc.).

    Uses a persistent HTTP client with cookie jar to maintain session state
    across the multi-step cancellation flow. Remember to call close() when done,
    or use as async context manager.
    """

    def __init__(self):
        self.base_url = MYBOOKINGS_BASE_URL
        self.timeout = httpx.Timeout(
        connect=10.0,   # connection should fail fast
        read=60.0,      # wait longer for slow cancellation response
        write=30.0,
        pool=10.0,
        )
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0",
        }
        # Persistent client with automatic cookie handling
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self.headers,
            follow_redirects=True,
        )

    async def guest_login(self, booking_id: str, email: str) -> Dict[str, Any]:
        """Step 1: POST /Mybooking/LoginGuestUser?app=null"""
        url = f"{self.base_url}/Mybooking/LoginGuestUser?app=null"
        payload = {
            "BetId": booking_id,
            "Emailid": email,
        }
        return await self._post(url, payload)

    async def verify_guest_login_otp(self, bid: str, otp: str, transaction_type: str = "Hotel") -> Dict[str, Any]:
        """Step 1b: POST /Mybooking/VerifyGuestLoginOtp"""
        url = f"{self.base_url}/Mybooking/VerifyGuestLoginOtp"
        payload = {
            "BetId": bid,
            "otp": otp,
            "transactionType": transaction_type,
        }
        return await self._post(url, payload)

    async def fetch_booking_details(self, bid: str) -> Dict[str, Any]:
        """Step 2: POST /Hotels/BookingDetails"""
        url = f"{self.base_url}/Hotels/BookingDetails"
        payload = {
            "bid": bid,
            "whiteListedCode": "EMT",
        }
        return await self._post(url, payload)

    async def send_cancellation_otp(self, screen_id: str) -> Dict[str, Any]:
        """Step 3: POST /Hotels/CancellationOtp"""
        url = f"{self.base_url}/Hotels/CancellationOtp"
        payload = {
            "EmtScreenID": screen_id,
        }
        logger.info(f"OTP request payload: {payload}")
        return await self._post(url, payload)

    async def request_cancellation(
        self,
        bid: str,
        otp: str,
        room_id: str,
        transaction_id: str,
        is_pay_at_hotel: bool,
        payment_url: str,
        reason: str = "Change of plans",
        remark: str = "",
    ) -> Dict[str, Any]:
        """Step 4: POST /Hotels/RequestCancellation"""
        url = f"{self.base_url}/Hotels/RequestCancellation"
        payload = {
            "Remark": remark or "",
            "Reason": reason or "Change of plans",
            "OTP": str(otp),
            # API expects literal string "undefined" for RoomId
            "RoomId": "undefined",
            "TransactionId": str(transaction_id) if transaction_id else "",
            "IsPayHotel": str(is_pay_at_hotel).lower(),
            "PaymentUrl": payment_url or "",
            "ApplicationType": "false",
            "Bid": bid,
        }
        logger.info(f"Cancellation payload: {payload}")
        return await self._post(url, payload)

    # ==================================================================
    # Train-specific API methods
    # ==================================================================

    async def fetch_train_booking_details(self, bid: str) -> Dict[str, Any]:
        """POST /Train/BookingDetail/"""
        url = f"{self.base_url}/Train/BookingDetail/"
        payload = {"bid": bid}
        return await self._post(url, payload)

    async def send_train_cancellation_otp(self, screen_id: str) -> Dict[str, Any]:
        """POST /Train/CancellationOtp/"""
        url = f"{self.base_url}/Train/CancellationOtp/"
        payload = {"EmtScreenID": screen_id}
        logger.info(f"Train OTP request payload: {payload}")
        return await self._post(url, payload)
   
    async def cancel_train(
        self,
        bid: str,
        otp: str,
        reservation_id: str,
        pax_ids: list,
        all_pax_ids:list,
        total_passenger: int,
        pnr_number: str,
    ) -> Dict[str, Any]:
        """POST /Train/CancelTrain"""
        url = f"{self.base_url}/Train/CancelTrain"
        def build_payload(all_pax_ids, selected_ids):
            ary = ["Y" if pid in selected_ids else "N"
                for pid in all_pax_ids]

            return {
                "ArycheckedValue": ary,
                "id": "",
                "_reservationId": reservation_id,
                "_PaxID": selected_ids,
                "totalPassenger": len(all_pax_ids),
                "PnrNumber": pnr_number,
                "OTP": otp,
                "bid": bid,
            }
        payload = build_payload(
        all_pax_ids,
        pax_ids)
    
        logger.info(f"Train cancellation payload: {payload}")
        print(f"Train cancellation payload: {payload}")
        return await self._post(url, payload)

    # ==================================================================
    # Bus-specific API methods
    # ==================================================================

    async def fetch_bus_booking_details(self, bid: str) -> Dict[str, Any]:
        """POST /Bus/BookingDetails/"""
        url = f"{self.base_url}/Bus/BookingDetails/"
        payload = {"bid": bid}
        return await self._post(url, payload)

    async def send_bus_cancellation_otp(self, screen_id: str) -> Dict[str, Any]:
        """POST /Bus/CancellationOtp/"""
        url = f"{self.base_url}/Bus/CancellationOtp/"
        payload = {"EmtScreenID": screen_id}
        logger.info(f"Bus OTP request payload: {payload}")
        return await self._post(url, payload)

    async def cancel_bus(
        self,
        bid: str,
        otp: str,
        seats: str,
        transaction_id: str = "",
        reason: str = "",
        remark: str = "",
    ) -> Dict[str, Any]:
        """POST /bus/RequestCancellation/"""
        url = f"{self.base_url}/bus/RequestCancellation/"
        payload = {
            "Remark": remark or "",
            "Reason": reason or "",
            "OTP": otp,
            "Seats": seats,
            "TransactionId": transaction_id or "",
            "Bid": bid,
        }
        logger.info(f"Bus cancellation payload: {payload}")
        return await self._post(url, payload)

    # ==================================================================
    # Flight-specific API methods
    # ==================================================================

    async def fetch_flight_booking_details(
        self, bid: str, transaction_screen_id: str, email: str
    ) -> Dict[str, Any]:
        """POST to GetFlightDetails (emtservice-ln)"""
        url = "https://emtservice-ln.easemytrip.com/api/Flight/GetFlightDetails"
        payload = {
            "emailId": email,
            "authentication": {"userName": "EMT", "password": "123"},
            "bid": bid,
            "transactionScreenId": transaction_screen_id,
        }
        return await self._post_flight(url, payload, email)

    async def send_flight_cancellation_otp(
        self, transaction_id: str, transaction_screen_id: str, email: str
    ) -> Dict[str, Any]:
        """POST to SendOtpOnCancellation (emtservice)"""
        url = "http://emtservice.easemytrip.com/emtapp.svc/SendOtpOnCancellation"
        payload = {
            "Authentication": {"Password": "123", "UserName": "emt"},
            "TransctionId": transaction_id,
            "TransctionScreenId": transaction_screen_id,
            "EmailID": email,
        }
        return await self._post_flight(url, payload, email)

    async def cancel_flight(
        self,
        transaction_screen_id: str,
        email: str,
        otp: str,
        outbound_pax_ids: str = "",
        inbound_pax_ids: str = "",
        mode: str = "1",
        is_partial_cancel: str = "false",
    ) -> Dict[str, Any]:
        """POST to FlightCancellation (emtservice-ln)"""
        url = "https://emtservice-ln.easemytrip.com/api/Flight/FlightCancellation"
        payload = {
            "Authentication": {
                "IpAddress": "::1",
                "Password": "123",
                "UserName": "EMT",
            },
            "TransactionScreenId": transaction_screen_id,
            "mode": mode,
            "EmailId": email,
            "VerfyOTP": otp,
            "inBoundPaxIds": inbound_pax_ids,
            "isPartialCancel": is_partial_cancel,
            "outBoundPaxIds": outbound_pax_ids,
        }
        logger.info(f"Flight cancellation payload: {payload}")
        return await self._post_flight(url, payload, email)

    async def close(self):
        """Close the persistent HTTP client. Call this when done using the client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - ensures client is closed"""
        await self.close()

    async def _post_flight(self, url: str, payload: dict, email: str = "") -> Dict[str, Any]:
        """POST for flight APIs (different base URLs, email header)."""
        extra_headers = {}
        if email:
            extra_headers["auth"] = email
        try:
            response = await self.client.post(url, json=payload, headers=extra_headers)
            response.raise_for_status()

            if response.status_code == 204 or not response.text:
                return {}

            result = response.json()

            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    pass

            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling {url}: {e}")
            raise

    async def _post(self, url: str, payload: dict) -> Dict[str, Any]:
        """
        Generic POST with error handling.
        Uses persistent client to maintain cookies/session across requests.
        """
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            if response.status_code == 204 or not response.text:
                return {}

            result = response.json()

            # Handle double-encoded JSON (API returns JSON string instead of object)
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                    logger.debug(f"Decoded double-encoded JSON response")
                except json.JSONDecodeError:
                    # It's just a plain string, not JSON
                    logger.debug(f"Response is a plain string: {result}")

            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling {url}: {e}")
            raise
