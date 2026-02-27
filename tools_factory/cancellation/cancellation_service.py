"""Cancellation Service - Business logic for 4-step cancellation flow"""
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


class CancellationService:
    """
    Service layer for booking cancellation operations (Hotel, Train, etc.).

    Uses a persistent HTTP client with session/cookie management.
    Detects module type from TransactionType after login and routes accordingly.
    Remember to call close() when done, or use as async context manager:

        async with CancellationService() as svc:
            await svc.guest_login(...)
    """

    def __init__(self):
        self.client = MyBookingsApiClient()
        # Store session state to avoid unnecessary re-logins
        self._bid = None
        self._transaction_screen_id = None
        self._booking_id = None
        self._email = None
        self._transaction_type = None  # "Hotel", "Train", "Flight", etc.
        self._emt_screen_id = None  # For train: ID field from PaxList
        # Flight-specific state
        self._flight_transaction_id = None  # Numeric ID e.g. "162759795"
        self._flight_transaction_screen_id = None  # e.g. "EMT162759795"

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
            self._transaction_type = ids.get("TransactionType")

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

    async def verify_otp(self, otp: str) -> Dict[str, Any]:
        """
        Step 1b: Verify guest login OTP.

        Uses stored bid from guest_login.
        Returns dict with keys: success, message, error
        """
        if not self._bid:
            return {
                "success": False,
                "message": "No active session. Please start the cancellation flow first.",
                "error": "NO_SESSION",
            }

        try:
            response = await self.client.verify_guest_login_otp(
                self._bid, otp, transaction_type=self._transaction_type or "Hotel"
            )

            is_verified = str(response.get("isVerify", "")).lower() == "true"
            msg = response.get("Message") or response.get("Msg") or ""

            return {
                "success": is_verified,
                "message": msg if msg else ("OTP verified successfully" if is_verified else "Invalid OTP"),
                "error": None if is_verified else "OTP_INVALID",
            }
        except Exception as e:
            logger.error(f"OTP verification failed: {e}", exc_info=True)
            return {
                "success": False,
                "message": "OTP verification failed due to an unexpected error",
                "error": str(e),
            }

    async def fetch_booking_details(self, bid: str) -> Dict[str, Any]:
        """
        Step 2: Fetch room and booking details using the bid token.

        Returns dict with keys: success, rooms, hotel_info, guest_info, error, raw_response
        """
        try:
            response = await self.client.fetch_booking_details(bid)

            rooms_raw = response.get("Room") or response.get("Rooms") or []
            if not isinstance(rooms_raw, list):
                rooms_raw = [rooms_raw] if rooms_raw else []

            # Check cancellation status from PaymentDetails
            payment_details = response.get("PaymentDetails") or []
            if not isinstance(payment_details, list):
                payment_details = [payment_details] if payment_details else []

            # Build a map of room_id -> cancelled status
            cancelled_room_ids = set()
            for pd in payment_details:
                status = (pd.get("Status") or "").strip()
                if status.lower() == "cancelled":
                    room_id = pd.get("RoomID") or pd.get("RoomId") or pd.get("ID") or pd.get("Id")
                    if room_id:
                        cancelled_room_ids.add(str(room_id))

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

                is_cancelled = str(room_id) in cancelled_room_ids if room_id else False

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
                    "is_cancelled": is_cancelled,
                })

            # Check if all rooms are cancelled
            all_cancelled = bool(rooms) and all(r.get("is_cancelled") for r in rooms)

            return {
                "success": True,
                "rooms": rooms,
                "hotel_info": hotel_info,
                "guest_info": guest_info,
                "all_cancelled": all_cancelled,
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
                "error": str(e),
                "raw_response": {},
            }

    async def _refresh_session(self, booking_id: str, email: str) -> Dict[str, Any]:
        """
        Re-login and re-fetch booking details to get a fresh bid with
        the server-side session advanced to the correct state.

        Routes to the correct booking details endpoint based on transaction type
        to avoid triggering cross-module OTP sends.

        Returns dict with fresh bid + transaction_screen_id, or raises on failure.
        """
        login = await self.guest_login(booking_id, email)
        if not login["success"]:
            raise Exception(f"Session refresh login failed: {login['message']}")

        bid = login["ids"]["bid"]
        transaction_screen_id = login["ids"].get("transaction_screen_id")

        # Fetch details using module-specific endpoint to avoid cross-module OTP triggers
        # The server auto-sends OTP when booking details are fetched for certain modules
        transaction_type = self._transaction_type or "Hotel"

        logger.info(f"Refreshing session for {transaction_type} booking...")

        if transaction_type == "Flight":
            # Flight uses different parameters and endpoint
            await self.client.fetch_flight_booking_details(
                bid=bid,
                transaction_screen_id=self._booking_id or booking_id,
                email=email
            )
        elif transaction_type == "Train":
            await self.client.fetch_train_booking_details(bid)
        elif transaction_type == "Bus":
            await self.client.fetch_bus_booking_details(bid)
        else:  # Hotel or unknown - default to hotel
            if transaction_type != "Hotel":
                logger.warning(f"Unknown transaction type '{transaction_type}', defaulting to hotel endpoint")
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

        THIS METHOD IS FOR HOTEL BOOKINGS ONLY.
        For other booking types, use the module-specific methods.

        Uses stored session from guest_login (with persistent cookies).
        Only refreshes if no stored session exists.
        Returns dict with keys: success, message, error, bid, raw_response
        """
        try:
            # Safety check: Warn if called for non-hotel booking
            if self._transaction_type and self._transaction_type != "Hotel":
                logger.warning(
                    f"send_cancellation_otp() called for {self._transaction_type} booking. "
                    f"This should use send_{self._transaction_type.lower()}_cancellation_otp() instead."
                )

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

    # ==================================================================
    # Train-specific methods
    # ==================================================================

    async def fetch_train_booking_details(self, bid: str) -> Dict[str, Any]:
        """
        Fetch train booking details using the bid token.

        Returns dict with keys: success, passengers, train_info, price_info,
        cancel_price_info, reservation_id, pnr_number, emt_screen_id, error, raw_response
        """
        try:
            response = await self.client.fetch_train_booking_details(bid)

            pax_list = response.get("PaxList") or []
            train_details = response.get("TrainDetails") or {}
            price_details = response.get("TrainPriceDetails") or {}
            cancel_price = response.get("TrainCancelPriceDetails") or {}

            # Extract EMT Screen ID from first passenger (same for all)
            emt_screen_id = None
            if pax_list:
                emt_screen_id = pax_list[0].get("ID")
                self._emt_screen_id = emt_screen_id

            # Parse passengers
            passengers = []
            cancelled_statuses = {"cancelled", "can", "refunded"}
            for pax in pax_list:
                current_status = pax.get("TicketCurrentStatus") or ""
                is_cancelled = current_status.strip().lower() in cancelled_statuses
                passengers.append({
                    "pax_id": pax.get("PaxId"),
                    "title": pax.get("PaxTitle"),
                    "name": pax.get("FirstName"),
                    "age": pax.get("Age"),
                    "gender": pax.get("Gender"),
                    "pax_type": pax.get("PaxType"),
                    "seat_no": pax.get("SeatNo"),
                    "seat_type": pax.get("SeatType"),
                    "coach_number": pax.get("CoachNumber"),
                    "booking_status": pax.get("BookingStatus"),
                    "current_status": current_status,
                    "is_cancelled": is_cancelled,
                    "pnr_number": pax.get("PnrNumber"),
                    "transaction_id": pax.get("TransactionId"),
                    "cancel_request": pax.get("CancelRequest"),
                })

            # Parse train info
            train_info = {
                "train_name": train_details.get("TrainName"),
                "train_number": train_details.get("TrainNumber"),
                "from_station": train_details.get("FromStation"),
                "from_station_name": train_details.get("FromStationName"),
                "to_station": train_details.get("ToStation"),
                "to_station_name": train_details.get("ToStationName"),
                "departure_date": train_details.get("DepartureDate"),
                "departure_time": train_details.get("DepartureTime"),
                "arrival_date": train_details.get("ArrivalDate"),
                "arrival_time": train_details.get("ArrivalTime"),
                "boarding_station": train_details.get("BoardingStation"),
                "boarding_date": train_details.get("BoardingDate"),
                "boarding_time": train_details.get("BoardingTime"),
                "duration": train_details.get("Duration"),
                "travel_class": train_details.get("Class"),
                "quota": train_details.get("Quota"),
                "distance": train_details.get("Distance"),
                "num_adults": train_details.get("NumberOfAdult"),
                "num_children": train_details.get("NumberOfChild"),
                "num_infants": train_details.get("NumberOfInfant"),
                "reservation_id": train_details.get("ReservationId"),
                "booking_date": train_details.get("BookingDate"),
            }

            # Parse price info
            price_info = {
                "base_fare": price_details.get("BaseFare"),
                "tax": price_details.get("Tax"),
                "total_fare": price_details.get("TotalFare"),
                "insurance_charges": price_details.get("InsuranceCharges"),
                "is_free_cancellation": price_details.get("IsFreeCancellation"),
                "free_cancellation_amount": price_details.get("FreeCancellationAmount"),
            }

            # Parse cancellation price info
            cancel_price_info = {
                "total_amount_paid": cancel_price.get("TotalAmountPaid"),
                "total_fare": cancel_price.get("TotalFare"),
                "base_fare": cancel_price.get("BaseFare"),
                "irctc_charges": cancel_price.get("IRCTCCharges"),
                "irctc_convenience_fee": cancel_price.get("IRCTCConvenienceFee"),
                "agent_service_charge": cancel_price.get("AgentServiceCharge"),
                "reservation_charge": cancel_price.get("ReservationCharge"),
                "superfast_charge": cancel_price.get("SuperfastCharge"),
                "free_cancellation_amount": cancel_price.get("FreeCancellationAmount"),
            }

            # Get PNR and reservation ID
            pnr_number = pax_list[0].get("PnrNumber") if pax_list else None
            reservation_id = train_details.get("ReservationId")

            # Check if all passengers are cancelled
            all_cancelled = bool(passengers) and all(p.get("is_cancelled") for p in passengers)

            return {
                "success": True,
                "passengers": passengers,
                "train_info": train_info,
                "price_info": price_info,
                "cancel_price_info": cancel_price_info,
                "reservation_id": reservation_id,
                "pnr_number": pnr_number,
                "emt_screen_id": emt_screen_id,
                "bet_id": response.get("BetId"),
                "all_cancelled": all_cancelled,
                "error": None,
                "raw_response": response,
            }
        except Exception as e:
            logger.error(f"Fetch train booking details failed: {e}", exc_info=True)
            return {
                "success": False,
                "passengers": [],
                "train_info": {},
                "price_info": {},
                "cancel_price_info": {},
                "reservation_id": None,
                "pnr_number": None,
                "emt_screen_id": None,
                "bet_id": None,
                "error": str(e),
                "raw_response": {},
            }

    async def send_train_cancellation_otp(
        self,
        booking_id: str,
        email: str,
    ) -> Dict[str, Any]:
        """
        Send cancellation OTP for train booking.

        Uses the EMT Screen ID (ID field from PaxList in booking details).
        Returns dict with keys: success, message, error, raw_response
        """
        try:
            if not self._emt_screen_id:
                return {
                    "success": False,
                    "message": "No EMT Screen ID found. Please fetch booking details first.",
                    "error": "NO_SCREEN_ID",
                    "raw_response": {},
                }

            logger.info(f"Sending train cancellation OTP with EmtScreenID: {self._emt_screen_id[:10]}...")
            response = await self.client.send_train_cancellation_otp(self._emt_screen_id)

            logger.info(f"Train OTP Response: {response}")

            is_status = response.get("isStatus", False)
            msg = response.get("Msg") or response.get("Message") or ""

            has_error = (
                response.get("Error")
                or response.get("error")
                or (msg and ("error" in msg.lower() or "fail" in msg.lower() or "expired" in msg.lower()))
            )

            is_success = is_status or (not has_error and msg != "Failed")

            if not is_success:
                logger.error(f"Train OTP send failed. Response: {response}")

            return {
                "success": is_success,
                "message": msg if msg else ("OTP sent successfully" if is_success else "Failed to send OTP"),
                "error": None if is_success else "OTP_SEND_FAILED",
                "raw_response": response,
            }
        except Exception as e:
            logger.error(f"Send train cancellation OTP failed: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to send cancellation OTP: {e}",
                "error": str(e),
                "raw_response": {},
            }

    async def request_train_cancellation(
        self,
        booking_id: str,
        email: str,
        otp: str,
        pax_ids: list,
        all_pax_ids:list,
        reservation_id: str,
        pnr_number: str,
        total_passenger: int,
    ) -> Dict[str, Any]:
        """
        Submit train cancellation request.

        Returns dict with keys: success, message, refund_info, error, raw_response
        """
        try:
            if not self._emt_screen_id:
                return {
                    "success": False,
                    "message": "No EMT Screen ID found. Please fetch booking details first.",
                    "refund_info": None,
                    "error": "NO_SCREEN_ID",
                    "raw_response": {},
                }

            response = await self.client.cancel_train(
                bid=self._emt_screen_id,
                otp=otp,
                reservation_id=reservation_id,
                pax_ids=pax_ids,
                all_pax_ids =all_pax_ids,
                total_passenger=total_passenger,
                pnr_number=pnr_number,
            )

            logger.info(f"Train Cancellation Response: {response}")

            # Handle string response
            if isinstance(response, str):
                is_success = "success" in response.lower() or "cancel" in response.lower()
                msg = response
                refund_info = None
            else:
                is_success = response.get("Status", False) or response.get("isStatus", False)
                msg = response.get("LogMessage") or response.get("Message") or response.get("Msg") or ""

                data = response.get("Data", {})
                if data and isinstance(data, dict):
                    cancellation_text = data.get("Text", "")
                    if cancellation_text:
                        msg = f"{msg} - {cancellation_text}" if msg else cancellation_text

                refund_info = None
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
                "message": msg if is_success else (msg or "Train cancellation request failed"),
                "refund_info": refund_info,
                "error": None if is_success else "CANCELLATION_FAILED",
                "raw_response": response,
            }
        except Exception as e:
            logger.error(f"Train cancellation failed: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Train cancellation request failed",
                "refund_info": None,
                "error": str(e),
                "raw_response": {},
            }

    # ==================================================================
    # Bus-specific methods
    # ==================================================================

    async def fetch_bus_booking_details(self, bid: str) -> Dict[str, Any]:
        """
        Fetch bus booking details using the bid token.

        Returns dict with keys: success, passengers, bus_info, price_info,
        ticket_no, all_cancelled, error, raw_response
        """
        try:
            response = await self.client.fetch_bus_booking_details(bid)

            bus_detail = response.get("BusbookingDetail") or {}
            pax_list = response.get("BuspaxDetail") or []

            # Parse passengers with cancellation status
            passengers = []
            cancelled_statuses = {"cancelled", "cancel"}
            for pax in pax_list:
                status = pax.get("Status") or ""
                is_cancelled = status.strip().lower() in cancelled_statuses
                passengers.append({
                    "title": pax.get("Title"),
                    "first_name": pax.get("FirstName"),
                    "last_name": pax.get("LastName"),
                    "gender": pax.get("Gender"),
                    "age": pax.get("Age"),
                    "seat_no": pax.get("SeatNo"),
                    "fare": pax.get("Fare"),
                    "status": status,
                    "is_cancelled": is_cancelled,
                    "is_cancel_req": pax.get("IsCancelReq", False),
                    "journey_status": pax.get("JourneyStatus"),
                    "refund_amount": pax.get("RefundAmount"),
                    "cancellation_charge": pax.get("CancellationCharge"),
                    "total_fare": pax.get("Totalfare"),
                    "base_fare": pax.get("BaseFare"),
                })

            # Parse bus info
            cancellation_policy_raw = bus_detail.get("BusCancellationPolicy", "")
            cancellation_policy = ""
            if cancellation_policy_raw:
                cancellation_policy = _strip_html_tags(cancellation_policy_raw)

            bus_info = {
                "transaction_id": bus_detail.get("TransactionId"),
                "ticket_no": bus_detail.get("TicketNo"),
                "ticket_status": bus_detail.get("TicketStatus"),
                "source": bus_detail.get("Source"),
                "destination": bus_detail.get("Destination"),
                "departure_time": bus_detail.get("DepartureTime"),
                "date_of_journey": bus_detail.get("DateOfJourney"),
                "bus_type": bus_detail.get("BusType"),
                "num_passengers": bus_detail.get("NoOfPassenger"),
                "travels_operator": bus_detail.get("TravelsOperator"),
                "bp_location": bus_detail.get("BPLocation"),
                "bp_time": bus_detail.get("BPTime"),
                "bus_duration": bus_detail.get("BusDuration"),
                "arrival_time": bus_detail.get("ArrivalTime"),
                "arrival_date": bus_detail.get("ArrivalDate"),
                "total_fare": bus_detail.get("TotalFare"),
                "total_base_fare": bus_detail.get("TotalBaseFare"),
                "total_tax": bus_detail.get("TotalTax"),
                "refund_amount": bus_detail.get("RefundAmount"),
                "cancellation_charge": bus_detail.get("CancellationCharge"),
                "cancellation_policy": cancellation_policy,
                "cancellation_policy_html": cancellation_policy_raw,
                "booking_date": bus_detail.get("Bookingdate"),
            }

            # Price info
            price_info = {
                "total_fare": bus_detail.get("TotalFare"),
                "base_fare": bus_detail.get("TotalBaseFare"),
                "tax": bus_detail.get("TotalTax"),
                "refund_amount": bus_detail.get("RefundAmount"),
                "card_discount": bus_detail.get("CardDiscount"),
            }

            # Check if all passengers are cancelled
            all_cancelled = bool(passengers) and all(p.get("is_cancelled") for p in passengers)

            return {
                "success": True,
                "passengers": passengers,
                "bus_info": bus_info,
                "price_info": price_info,
                "ticket_no": bus_detail.get("TicketNo"),
                "all_cancelled": all_cancelled,
                "error": None,
                "raw_response": response,
            }
        except Exception as e:
            logger.error(f"Fetch bus booking details failed: {e}", exc_info=True)
            return {
                "success": False,
                "passengers": [],
                "bus_info": {},
                "price_info": {},
                "ticket_no": None,
                "all_cancelled": False,
                "error": str(e),
                "raw_response": {},
            }

    async def send_bus_cancellation_otp(
        self,
        booking_id: str,
        email: str,
    ) -> Dict[str, Any]:
        """
        Send cancellation OTP for bus booking.
        Bus uses bid as EmtScreenID (same as hotel).
        """
        try:
            bid = self._bid
            if not bid:
                return {
                    "success": False,
                    "message": "No bid found. Please login first.",
                    "error": "NO_BID",
                    "raw_response": {},
                }

            response = await self.client.send_bus_cancellation_otp(bid)
            logger.info(f"Bus OTP Response: {response}")

            is_status = response.get("isStatus", False)
            msg = response.get("Msg") or response.get("Message") or ""

            return {
                "success": bool(is_status),
                "message": msg,
                "error": None if is_status else "OTP_FAILED",
                "raw_response": response,
            }
        except Exception as e:
            logger.error(f"Bus OTP send failed: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Failed to send bus cancellation OTP",
                "error": str(e),
                "raw_response": {},
            }

    async def request_bus_cancellation(
        self,
        booking_id: str,
        email: str,
        otp: str,
        seats: str,
        transaction_id: str = "",
        reason: str = "",
        remark: str = "",
    ) -> Dict[str, Any]:
        """
        Submit bus cancellation request.

        Returns dict with keys: success, message, refund_info, error, raw_response
        """
        try:
            bid = self._bid
            if not bid:
                return {
                    "success": False,
                    "message": "No bid found. Please login first.",
                    "refund_info": None,
                    "error": "NO_BID",
                    "raw_response": {},
                }

            response = await self.client.cancel_bus(
                bid=bid,
                otp=otp,
                seats=seats,
                transaction_id=transaction_id,
                reason=reason,
                remark=remark,
            )

            logger.info(f"Bus Cancellation Response: {response}")

            # Handle string response (API sometimes returns double-encoded JSON)
            if isinstance(response, str):
                is_success = "success" in response.lower() or "cancel" in response.lower()
                msg = response
                refund_info = None
            else:
                is_success = response.get("Status", False) or response.get("isStatus", False)
                msg = response.get("Message") or response.get("Msg") or ""

                data = response.get("Data", {})
                refund_info = None
                if data and isinstance(data, dict):
                    refund_info = {
                        "refund_amount": data.get("refundAmount"),
                        "cancellation_charges": data.get("cancellationCharges"),
                        "cancel_status": data.get("cancelStatus"),
                        "is_refunded": data.get("isRefunded"),
                        "pnr_no": data.get("PNRNo"),
                        "cancel_seat_no": data.get("cancelSeatNo"),
                        "remarks": data.get("Remarks"),
                    }

            return {
                "success": bool(is_success),
                "message": msg if is_success else (msg or "Bus cancellation request failed"),
                "refund_info": refund_info,
                "error": None if is_success else "CANCELLATION_FAILED",
                "raw_response": response,
            }
        except Exception as e:
            logger.error(f"Bus cancellation failed: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Bus cancellation request failed",
                "refund_info": None,
                "error": str(e),
                "raw_response": {},
            }

    # ==================================================================
    # Flight-specific methods
    # ==================================================================

    async def fetch_flight_booking_details(self, bid: str) -> Dict[str, Any]:
        """
        Fetch flight booking details using the bid token.

        Returns dict with keys: success, flight_segments, outbound_passengers,
        inbound_passengers, price_info, pnr_info, cancellation_policy,
        trip_status, all_cancelled, error, raw_response
        """
        try:
            # transactionScreenId = booking_id (e.g., "EMT162759795")
            transaction_screen_id = self._booking_id or ""
            email = self._email or ""
            response = await self.client.fetch_flight_booking_details(
                bid=bid,
                transaction_screen_id=transaction_screen_id,
                email=email,
            )

            logger.info(f"Flight API response keys: {list(response.keys()) if isinstance(response, dict) else type(response)}")

            passenger_details = response.get("PassengerDetails") or {}
            booked_passanger = response.get("bookedPassanger") or {}

            logger.info(
                f"Flight parsing: PassengerDetails keys={list(passenger_details.keys())}, "
                f"bookedPassanger keys={list(booked_passanger.keys())}, "
                f"FlightDetail count={len(passenger_details.get('FlightDetail') or [])}, "
                f"outbond pax count={len((booked_passanger.get('outbond') or {}).get('outBondTypePass') or [])}, "
                f"inbond pax count={len((booked_passanger.get('inbound') or {}).get('bookedPaxs') or [])}"
            )

            # Store transaction IDs for OTP and cancellation
            # TransactionId is in FlightPriceDetails, not at root level
            price_details_temp = passenger_details.get("FlightPriceDetails") or {}
            flt_details = passenger_details.get("fltDetails") or {}
            self._flight_transaction_id = str(
                price_details_temp.get("TransactionId") or response.get("TransactionId") or ""
            )
            self._flight_transaction_screen_id = str(
                flt_details.get("transactionScreenId") or response.get("TransactionScreenId") or transaction_screen_id
            )

            trip_status = response.get("TripStatus") or ""

            # Parse flight segments from FlightDetail
            flight_detail = passenger_details.get("FlightDetail") or []
            flight_segments = []
            for seg in flight_detail:
                flight_segments.append({
                    "airline_name": seg.get("AirLineName"),
                    "airline_code": seg.get("AirlineCode") or seg.get("AirLineCode"),
                    "flight_number": seg.get("FlightNumber"),
                    "origin": seg.get("DepartureCityCode") or seg.get("Origin"),
                    "origin_city": seg.get("DepartureCity"),
                    "origin_airport": seg.get("DepartureName") or seg.get("OriginAirportName"),
                    "destination": seg.get("ArrivalCityCode") or seg.get("Destination"),
                    "destination_city": seg.get("ArrivalCity"),
                    "destination_airport": seg.get("ArrivalName") or seg.get("DestinationAirportName"),
                    "departure_date": seg.get("DepartureDate"),
                    "departure_time": seg.get("DepartureTime"),
                    "arrival_date": seg.get("ArrivalDate"),
                    "arrival_time": seg.get("ArrivalTime"),
                    "origin_terminal": seg.get("SourceTerminal") or seg.get("OriginTerminal"),
                    "destination_terminal": seg.get("DestinationalTerminal") or seg.get("DestinationTerminal"),
                    "duration": seg.get("FlightDuration") or seg.get("Duration"),
                    "cabin_class": seg.get("ClassType") or seg.get("CabinClass"),
                    "cabin_baggage": seg.get("CabinBag") or seg.get("CabinBaggage"),
                    "check_in_baggage": seg.get("BaggageWeight") or seg.get("CheckInBaggage"),
                    "bound_type": seg.get("BoundType"),
                    "stops": seg.get("FlightStops") or seg.get("Stops"),
                })

            # Parse outbound passengers
            outbound_passengers = []
            outbond_data = booked_passanger.get("outbond") or {}
            pax_list_out = list(outbond_data.get("outBondTypePass") or [])
            # Fallback: lstOutbond structure (list of groups with bookedPaxs)
            if not pax_list_out:
                for src in [flt_details, passenger_details, response]:
                    lst_outbound = src.get("lstOutbond") or []
                    if lst_outbound:
                        for grp in lst_outbound:
                            pax_list_out.extend(grp.get("bookedPaxs") or [])
                        break
            for pax in pax_list_out:
                is_cancellable = str(pax.get("isCancellable", "")).lower() == "true"
                status = pax.get("paxstatus") or pax.get("Status") or pax.get("status") or ""
                is_cancelled = str(status).lower() in ("cancelled", "cancel")
                outbound_passengers.append({
                    "pax_id": pax.get("paxId"),
                    "title": pax.get("title"),
                    "first_name": pax.get("FirstName") or pax.get("firstName"),
                    "last_name": pax.get("lastName"),
                    "pax_type": pax.get("paxType"),
                    "ticket_number": pax.get("ticketNumber"),
                    "status": status,
                    "is_cancellable": is_cancellable,
                    "is_cancelled": is_cancelled,
                    "cancellation_charge": pax.get("cancellationCharge"),
                    "bound_type": pax.get("tripType") or pax.get("boundType"),
                    "possible_mode": pax.get("possiblemode") or pax.get("possibleMode"),
                })

            # Parse inbound passengers (round-trip)
            inbound_passengers = []
            inbond_data = booked_passanger.get("inbound") or {}
            pax_list_in = list(inbond_data.get("bookedPaxs") or [])# or inbond_data.get("outBondTypePass") or [])
            # Fallback: lstInbound structure (list of groups with bookedPaxs)
            if not pax_list_in:
                for src in [flt_details, passenger_details, response]:
                    lst_inbound = src.get("lstInbound") or []
                    if lst_inbound:
                        for grp in lst_inbound:
                            pax_list_in.extend(grp.get("bookedPaxs") or [])
                        break
            for pax in pax_list_in:
                is_cancellable = str(pax.get("isCancellable", "")).lower() == "true"
                status = pax.get("paxstatus") or pax.get("Status") or pax.get("status") or ""
                is_cancelled = str(status).lower() in ("cancelled", "cancel")
                inbound_passengers.append({
                    "pax_id": pax.get("paxId"),
                    "title": pax.get("title"),
                    "first_name": pax.get("FirstName") or pax.get("firstName"),
                    "last_name": pax.get("lastName"),
                    "pax_type": pax.get("paxType"),
                    "ticket_number": pax.get("ticketNumber"),
                    "status": status,
                    "is_cancellable": is_cancellable,
                    "is_cancelled": is_cancelled,
                    "cancellation_charge": pax.get("cancellationCharge"),
                    "bound_type": pax.get("tripType") or pax.get("boundType"),
                    "possible_mode": pax.get("possiblemode") or pax.get("possibleMode"),
                })

            # Parse price info
            price_details = passenger_details.get("FlightPriceDetails") or {}
            price_info = {
                "total_fare": price_details.get("TotalFare"),
                "total_base_fare": price_details.get("TotalBaseFare"),
                "total_tax": price_details.get("TotalTax"),
                "currency": price_details.get("Currency"),
            }

            # Parse PNR info (PNRList is a dict, not a list)
            pnr_data = passenger_details.get("PNRList") or {}
            pnr_info = []
            if pnr_data and isinstance(pnr_data, dict):
                pnr_info.append({
                    "airline_pnr": pnr_data.get("Airlinepnr"),
                    "gds_pnr": pnr_data.get("Gdspnr"),
                })

            # Parse cancellation policy
            cancellation_policy_data = response.get("FlightCancellationPolicy") or {}
            sectors = cancellation_policy_data.get("Sectors") or []
            cancellation_policy = []
            for sector in sectors:
                # Field name is "CancellationPolicies" not "Policies"
                policies = sector.get("CancellationPolicies") or sector.get("Policies") or []
                policy_items = []
                for pol in policies:
                    policy_items.append({
                        "charge_type": pol.get("ChargeType"),
                        "charge_value": pol.get("ChargeValue") or pol.get("Charge"),
                        "from_date": pol.get("FromDate"),
                        "to_date": pol.get("ToDate"),
                        "policy_text": pol.get("PolicyText") or pol.get("Time"),
                        "is_refundable": pol.get("Refundable"),
                        "is_cancellation": pol.get("IsCancellation"),
                        "policy_detail": pol.get("policydtl") or pol.get("PolicyDetail") or pol.get("Description"),
                    })
                cancellation_policy.append({
                    "sector_name": sector.get("SectorName") or sector.get("Sector"),
                    "bound_type": sector.get("Boundtype"),
                    "departure_date": sector.get("DepartureDate"),
                    "flight_image": sector.get("FlightImage"),
                    "policies": policy_items,
                })

            # Parse pax status
            pax_status_data = response.get("PaxStatus") or {}
            pax_statuses = pax_status_data.get("Pax") or []

            # Check if all passengers are cancelled
            all_pax = outbound_passengers + inbound_passengers
            cancellable_pax = [p for p in all_pax if p.get("is_cancellable")]
            all_cancelled = bool(all_pax) and all(p.get("is_cancelled") for p in all_pax)

            return {
                "success": True,
                "flight_segments": flight_segments,
                "outbound_passengers": outbound_passengers,
                "inbound_passengers": inbound_passengers,
                "price_info": price_info,
                "pnr_info": pnr_info,
                "cancellation_policy": cancellation_policy,
                "pax_statuses": pax_statuses,
                "trip_status": trip_status,
                "transaction_id": self._flight_transaction_id,
                "transaction_screen_id": self._flight_transaction_screen_id,
                "all_cancelled": all_cancelled,
                "total_cancellable": len(cancellable_pax),
                "error": None,
                "raw_response": response,
            }
        except Exception as e:
            logger.error(f"Fetch flight booking details failed: {e}", exc_info=True)
            return {
                "success": False,
                "flight_segments": [],
                "outbound_passengers": [],
                "inbound_passengers": [],
                "price_info": {},
                "pnr_info": [],
                "cancellation_policy": [],
                "pax_statuses": [],
                "trip_status": "",
                "transaction_id": None,
                "transaction_screen_id": None,
                "all_cancelled": False,
                "total_cancellable": 0,
                "error": str(e),
                "raw_response": {},
            }

    async def send_flight_cancellation_otp(
        self,
        booking_id: str,
        email: str,
    ) -> Dict[str, Any]:
        """
        Send cancellation OTP for flight booking.

        Uses stored flight transaction IDs from fetch_flight_booking_details.
        Returns dict with keys: success, message, error, raw_response
        """
        try:
            if not self._flight_transaction_id or not self._flight_transaction_screen_id:
                return {
                    "success": False,
                    "message": "No flight transaction ID found. Please fetch booking details first.",
                    "error": "NO_TRANSACTION_ID",
                    "raw_response": {},
                }

            logger.info(
                f"Sending flight cancellation OTP for TransactionId: {self._flight_transaction_id}, "
                f"TransactionScreenId: {self._flight_transaction_screen_id}"
            )
            response = await self.client.send_flight_cancellation_otp(
                transaction_id=self._flight_transaction_id,
                transaction_screen_id=self._flight_transaction_screen_id,
                email=email,
            )

            logger.info(f"Flight OTP Response: {response}")

            is_status = response.get("IsStatus", False) or response.get("isStatus", False)
            msg = response.get("Msg") or response.get("Message") or ""

            has_error = (
                response.get("Error")
                or response.get("error")
                or (msg and ("error" in msg.lower() or "fail" in msg.lower() or "expired" in msg.lower()))
            )

            is_success = is_status or (not has_error and msg != "Failed")

            if not is_success:
                logger.error(f"Flight OTP send failed. Response: {response}")

            return {
                "success": is_success,
                "message": msg if msg else ("OTP sent successfully" if is_success else "Failed to send OTP"),
                "error": None if is_success else "OTP_SEND_FAILED",
                "raw_response": response,
            }
        except Exception as e:
            logger.error(f"Send flight cancellation OTP failed: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to send cancellation OTP: {e}",
                "error": str(e),
                "raw_response": {},
            }

    async def request_flight_cancellation(
        self,
        booking_id: str,
        email: str,
        otp: str,
        outbound_pax_ids: str = "",
        inbound_pax_ids: str = "",
        mode: str = "1",
    ) -> Dict[str, Any]:
        """
        Submit flight cancellation request.

        Args:
            booking_id: Booking ID
            email: User email
            otp: Cancellation OTP
            outbound_pax_ids: Comma-separated outbound passenger IDs
            inbound_pax_ids: Comma-separated inbound passenger IDs
            mode: Cancellation mode (default "1")

        Returns dict with keys: success, message, refund_info, error, raw_response
        """
        try:
            if not self._flight_transaction_screen_id:
                return {
                    "success": False,
                    "message": "No flight transaction screen ID found. Please fetch booking details first.",
                    "refund_info": None,
                    "error": "NO_TRANSACTION_ID",
                    "raw_response": {},
                }

            # Compute isPartialCancel: "true" if not all cancellable passengers selected
            all_selected_ids = set()
            if outbound_pax_ids:
                all_selected_ids.update(outbound_pax_ids.split(","))
            if inbound_pax_ids:
                all_selected_ids.update(inbound_pax_ids.split(","))
            outbound_pax_ids = "-".join(outbound_pax_ids.split(","))
            inbound_pax_ids = "-".join(inbound_pax_ids.split(","))
            total_cancellable = getattr(self, "_total_cancellable", 0)
            is_partial = "true" if len(all_selected_ids) < total_cancellable else "false"

            response = await self.client.cancel_flight(
                transaction_screen_id=self._flight_transaction_screen_id,
                email=email,
                otp=otp,
                outbound_pax_ids=outbound_pax_ids,
                inbound_pax_ids=inbound_pax_ids,
                mode=mode,
                is_partial_cancel=is_partial,
            )

            logger.info(f"Flight Cancellation Response: {response}")

            if isinstance(response, str):
                is_success = "success" in response.lower() or "cancel" in response.lower()
                msg = response
                refund_info = None
            else:
                is_requested = response.get("isRequested", False)
                is_cancelled = response.get("isCancelled", False)
                is_success = is_requested or is_cancelled or response.get("isValidOTP", False)
                msg = response.get("msg") or response.get("Message") or response.get("Msg") or ""
                status_text = response.get("Status")
                request_id = response.get("RequestId")

                if request_id and not msg:
                    msg = f"Cancellation request submitted (Request ID: {request_id})"

                refund_info = None
                if response.get("RefundAmount") or response.get("CancellationCharges"):
                    refund_info = {
                        "refund_amount": response.get("RefundAmount"),
                        "cancellation_charges": response.get("CancellationCharges"),
                        "refund_mode": response.get("RefundMode"),
                        "request_id": request_id,
                    }

            return {
                "success": bool(is_success),
                "message": msg if is_success else (msg or "Flight cancellation request failed"),
                "refund_info": refund_info,
                "error": None if is_success else "CANCELLATION_FAILED",
                "raw_response": response,
            }
        except Exception as e:
            logger.error(f"Flight cancellation failed: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Flight cancellation request failed",
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
