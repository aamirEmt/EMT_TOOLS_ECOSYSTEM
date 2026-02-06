"""Hotel Cancellation Service - Business logic for 4-step cancellation flow"""
from typing import Dict, Any
import logging
import re

from emt_client.clients.mybookings_client import MyBookingsApiClient

logger = logging.getLogger(__name__)


def _strip_html_tags(text: str) -> str:
    """
    Remove HTML tags from text and clean up formatting.

    Example:
        Input: "<ul><li>Free cancellation (Rs.0) before 25-Feb-2026 </li><li> 100% Deduction From: 25-Feb-2026 till check-in </li>"
        Output: "• Free cancellation (Rs.0) before 25-Feb-2026\n• 100% Deduction From: 25-Feb-2026 till check-in"
    """
    if not text:
        return text

    # Replace </li> with newline for list items
    text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)

    # Replace <li> with bullet point
    text = re.sub(r'<li[^>]*>', '• ', text, flags=re.IGNORECASE)

    # Remove all other HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Clean up whitespace
    text = re.sub(r'\n\s*\n', '\n', text)  # Remove empty lines
    text = re.sub(r'[ \t]+', ' ', text)  # Normalize spaces
    text = text.strip()

    return text


class HotelCancellationService:
    """
    Service layer for hotel booking cancellation operations.

    Uses a persistent HTTP client with session/cookie management.
    Remember to call close() when done, or use as async context manager:

        async with HotelCancellationService() as svc:
            await svc.guest_login(...)
    """

    def __init__(self):
        self.client = MyBookingsApiClient()
        # Store session state to avoid unnecessary re-logins
        self._bid = None
        self._transaction_screen_id = None
        self._booking_id = None
        self._email = None

    async def guest_login(self, booking_id: str, email: str) -> Dict[str, Any]:
        """
        Step 1: Authenticate guest user with booking ID + email.

        Returns dict with keys: success, ids, error, message
        """
        try:
            response = await self.client.guest_login(booking_id, email)

            ids = response.get("Ids") or response
            bid = ids.get("bid") or ids.get("Bid") or ids.get("BID")

            # Try multiple field name variations for screen ID
            transaction_screen_id = (
                ids.get("TransactionScreenId")
                or ids.get("TransactionScreenID")
                or ids.get("EmtScreenID")
                or ids.get("EmtScreenId")
                or ids.get("ScreenID")
                or ids.get("ScreenId")
            )

            # Log available fields for debugging if screen ID is missing
            if not transaction_screen_id:
                logger.warning(
                    f"Screen ID not found in login response. Available fields: {list(ids.keys())}"
                )

            if not bid:
                return {
                    "success": False,
                    "error": "LOGIN_FAILED",
                    "message": ids.get("Message") or "Guest login failed - no bid token returned",
                    "ids": None,
                }

            # Store session state for reuse (now that we have persistent cookies)
            self._bid = bid
            self._transaction_screen_id = transaction_screen_id
            self._booking_id = booking_id
            self._email = email

            return {
                "success": True,
                "ids": {
                    "bid": bid,
                    "transaction_id": ids.get("TransactionId"),
                    "transaction_screen_id": transaction_screen_id,
                    "transaction_type": ids.get("TransactionType"),
                    "is_otp_send": ids.get("IsOtpSend"),
                    "message": ids.get("Message"),
                },
                "error": None,
                "message": "Guest login successful",
            }
        except Exception as e:
            logger.error(f"Guest login failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Guest login failed due to an unexpected error",
                "ids": None,
            }

    async def fetch_booking_details(self, bid: str) -> Dict[str, Any]:
        """
        Step 2: Fetch room and booking details using the bid token.

        Returns dict with keys: success, rooms, payment_url, hotel_info, guest_info, error, raw_response
        """
        try:
            response = await self.client.fetch_booking_details(bid)

            rooms_raw = response.get("Room") or response.get("Rooms") or []
            if not isinstance(rooms_raw, list):
                rooms_raw = [rooms_raw] if rooms_raw else []

            # Extract hotel-level info from first room (same for all rooms)
            hotel_info = {}
            if rooms_raw:
                first_room = rooms_raw[0]
                hotel_info = {
                    "hotel_name": first_room.get("name"),
                    "address": first_room.get("Address_Description"),
                    "check_in": first_room.get("CheckIn"),
                    "check_out": first_room.get("checkOut"),
                    "duration": first_room.get("Duration"),
                    "total_fare": first_room.get("TotalFare"),
                    "number_of_rooms": first_room.get("NumberOfRoomsBooked"),
                }

            # Extract guest info from PaxDetails
            pax_details = response.get("PaxDetails", [])
            guest_info = []
            if pax_details:
                # Get unique guests (API may have duplicates)
                seen_guests = set()
                for pax in pax_details:
                    guest_key = (pax.get("FirstName"), pax.get("LastName"), pax.get("Title"))
                    if guest_key not in seen_guests:
                        seen_guests.add(guest_key)
                        guest_info.append({
                            "title": pax.get("Title"),
                            "first_name": pax.get("FirstName"),
                            "last_name": pax.get("LastName"),
                            "pax_type": pax.get("PaxType"),
                            "mobile": pax.get("CustomerMobile"),
                        })

            rooms = []
            for r in rooms_raw:
                # Log available fields in first room for debugging
                if not rooms:
                    logger.info(f"First room fields: {list(r.keys())}")

                # Try multiple field name variations for room_id
                room_id = (
                    r.get("RoomID")
                    or r.get("RoomId")
                    or r.get("roomId")
                    or r.get("Id")
                    or r.get("ID")
                )

                if not room_id:
                    logger.warning(f"Room ID not found! Available fields: {list(r.keys())}")

                # Get and clean cancellation policy (strip HTML tags)
                cancellation_policy = r.get("CancellationPolicy", "")
                if cancellation_policy:
                    cancellation_policy = _strip_html_tags(cancellation_policy)

                rooms.append({
                    "room_id": room_id,
                    "room_type": r.get("RoomType"),
                    "room_no": r.get("RoomNo"),
                    "transaction_id": r.get("TransactionId"),
                    "cancellation_policy": cancellation_policy,
                    "is_pay_at_hotel": bool(r.get("isPayAtHotel")),
                    "total_adults": r.get("TotalAdult"),
                    "check_in": r.get("CheckIn"),
                    "check_out": r.get("checkOut"),
                    "hotel_name": r.get("name"),
                    "amount": r.get("TotalFare"),
                    "meal_type": r.get("mealtype"),
                    "confirmation_no": r.get("ConfirmationNo"),
                    "payment_due_date": r.get("PaymentDueDate"),
                    "payment_remaining_days": r.get("PaymentRemainingDays"),
                })

            links = response.get("Links") or {}
            payment_url = links.get("PaymentURL") or links.get("PaymentUrl") or ""

            return {
                "success": True,
                "rooms": rooms,
                "hotel_info": hotel_info,
                "guest_info": guest_info,
                "payment_url": payment_url,
                "error": None,
                "raw_response": response,
            }
        except Exception as e:
            logger.error(f"Fetch booking details failed: {e}", exc_info=True)
            return {
                "success": False,
                "rooms": [],
                "hotel_info": {},
                "guest_info": [],
                "payment_url": None,
                "error": str(e),
                "raw_response": {},
            }

    async def _refresh_session(self, booking_id: str, email: str) -> Dict[str, Any]:
        """
        Re-login and re-fetch booking details to get a fresh bid with
        the server-side session advanced to the correct state.

        Returns dict with fresh bid + transaction_screen_id, or raises on failure.
        """
        login = await self.guest_login(booking_id, email)
        if not login["success"]:
            raise Exception(f"Session refresh login failed: {login['message']}")

        bid = login["ids"]["bid"]
        transaction_screen_id = login["ids"].get("transaction_screen_id")

        # Must also fetch details so server advances session state
        await self.client.fetch_booking_details(bid)

        return {
            "bid": bid,
            "transaction_screen_id": transaction_screen_id,
        }

    async def send_cancellation_otp(
        self,
        booking_id: str,
        email: str,
    ) -> Dict[str, Any]:
        """
        Step 3: Request OTP for cancellation using existing session.

        Uses stored session from guest_login (with persistent cookies).
        Only refreshes if no stored session exists.
        Returns dict with keys: success, message, error, bid, raw_response
        """
        try:
            # Use stored session if available, otherwise refresh
            if not self._bid or booking_id != self._booking_id or email != self._email:
                logger.info("No stored session or credentials changed, refreshing session...")
                session = await self._refresh_session(booking_id, email)
                bid = session["bid"]
            else:
                logger.info("Using stored session from login...")
                bid = self._bid

            # IMPORTANT: Always use bid as EmtScreenID for OTP request
            # (NOT transaction_screen_id - that's for different purposes)
            logger.info(f"Sending cancellation OTP with bid as EmtScreenID: {bid[:10]}...")
            response = await self.client.send_cancellation_otp(bid)

            # Log full response for debugging
            logger.info(f"OTP Response: {response}")

            is_status = response.get("isStatus", False)
            msg = response.get("Msg") or response.get("Message") or ""

            # Special case: If isStatus is False but Msg is None/empty and no error,
            # the OTP might still be sent (API quirk). Check for explicit error indicators.
            has_error = (
                response.get("Error")
                or response.get("error")
                or (msg and ("error" in msg.lower() or "fail" in msg.lower() or "expired" in msg.lower()))
            )

            # Consider success if isStatus is True, OR if there's no explicit error
            is_success = is_status or (not has_error and msg != "Failed")

            if not is_success:
                logger.error(f"OTP send failed. Response: {response}")

            return {
                "success": is_success,
                "message": msg if msg else ("OTP sent successfully" if is_success else "Failed to send OTP"),
                "error": None if is_success else "OTP_SEND_FAILED",
                "bid": bid,
                "transaction_screen_id": self._transaction_screen_id,
                "raw_response": response,
            }
        except Exception as e:
            logger.error(f"Send cancellation OTP failed: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to send cancellation OTP: {e}",
                "error": str(e),
                "bid": None,
                "raw_response": {},
            }

    async def request_cancellation(
        self,
        booking_id: str,
        email: str,
        otp: str,
        room_id: str,
        transaction_id: str,
        is_pay_at_hotel: bool,
        payment_url: str,
        reason: str = "Change of plans",
        remark: str = "",
    ) -> Dict[str, Any]:
        """
        Step 4: Submit the cancellation request using existing session.

        Uses stored session from guest_login (with persistent cookies).
        Only refreshes if no stored session exists.
        Returns dict with keys: success, message, refund_info, error, raw_response
        """
        try:
            # Use stored session if available, otherwise refresh
            if not self._bid or booking_id != self._booking_id or email != self._email:
                logger.info("No stored session or credentials changed, refreshing session...")
                session = await self._refresh_session(booking_id, email)
                bid = session["bid"]
            else:
                logger.info("Using stored session from login...")
                bid = self._bid

            response = await self.client.request_cancellation(
                bid=bid,
                otp=otp,
                room_id=room_id,
                transaction_id=transaction_id,
                is_pay_at_hotel=is_pay_at_hotel,
                payment_url=payment_url,
                reason=reason,
                remark=remark,
            )

            # Log response for debugging
            logger.info(f"Cancellation Response: {response}")

            # Handle string response (API sometimes returns plain strings)
            if isinstance(response, str):
                # API returned a string instead of JSON object
                is_success = "success" in response.lower() or "cancel" in response.lower()
                msg = response
                refund_info = None
            else:
                # Normal JSON object response
                # API uses "Status" field (boolean) and "LogMessage" for success indicator
                is_success = response.get("Status", False) or response.get("isStatus", False)
                msg = response.get("LogMessage") or response.get("Message") or response.get("Msg") or ""

                # Get cancellation details from Data object
                data = response.get("Data", {})
                if data and isinstance(data, dict):
                    cancellation_text = data.get("Text", "")
                    if cancellation_text:
                        msg = f"{msg} - {cancellation_text}" if msg else cancellation_text

                refund_info = None
                # Check for refund info in response or Data
                if response.get("RefundAmount") or response.get("CancellationCharges"):
                    refund_info = {
                        "refund_amount": response.get("RefundAmount"),
                        "cancellation_charges": response.get("CancellationCharges"),
                        "refund_mode": response.get("RefundMode"),
                    }
                elif data and (data.get("charge") or data.get("currency")):
                    refund_info = {
                        "refund_amount": None,
                        "cancellation_charges": data.get("charge"),
                        "refund_mode": data.get("currency"),
                    }

            return {
                "success": bool(is_success),
                "message": msg if is_success else (msg or "Cancellation request failed"),
                "refund_info": refund_info,
                "error": None if is_success else "CANCELLATION_FAILED",
                "raw_response": response,
            }
        except Exception as e:
            logger.error(f"Request cancellation failed: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Cancellation request failed",
                "refund_info": None,
                "error": str(e),
                "raw_response": {},
            }

    async def close(self):
        """Close the underlying HTTP client. Call this when done using the service."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        """Async context manager exit - ensures client is closed"""
        await self.close()
