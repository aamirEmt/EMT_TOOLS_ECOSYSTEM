"""Interactive terminal test for Hotel Cancellation Flow"""
import asyncio
import logging
from tools_factory.hotel_cancellation.hotel_cancellation_service import HotelCancellationService

# Enable logging to see debug messages
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')


async def main():
    # Use async context manager to ensure proper cleanup
    async with HotelCancellationService() as svc:
        print("=" * 50)
        print("  Hotel Booking Cancellation - Test")
        print("=" * 50)

        # Step 1: Guest Login
        booking_id = input("\nBooking ID (e.g. EMT1624718): ").strip()
        email = input("Email: ").strip()

        print("\n[Step 1] Logging in...")
        login = await svc.guest_login(booking_id, email)

        if not login["success"]:
            print(f"Login failed: {login['message']}")
            return

        bid = login["ids"]["bid"]
        print(f"Login successful! Transaction ID: {login['ids'].get('transaction_id')}")

        # Step 2: Fetch Booking Details
        print("\n[Step 2] Fetching booking details...")
        details = await svc.fetch_booking_details(bid)

        if not details["success"]:
            print(f"Failed to fetch details: {details['error']}")
            return

        rooms = details["rooms"]
        print(f"\nFound {len(rooms)} room(s):")
        for i, r in enumerate(rooms):
            print(f"  [{i}] {r.get('room_type', 'N/A')} - Room {r.get('room_no', 'N/A')}")
            print(f"      ID: {r.get('room_id')}")
            print(f"      Hotel: {r.get('hotel_name', 'N/A')}")
            print(f"      Check-in: {r.get('check_in', 'N/A')}")
            print(f"      Check-out: {r.get('check_out', 'N/A')}")
            print(f"      Policy: {r.get('cancellation_policy', 'N/A')}")
            print(f"      Amount: {r.get('amount', 'N/A')}")
            print(f"      Pay at hotel: {r.get('is_pay_at_hotel')}")

        proceed = input("\nProceed to cancel? (y/n): ").strip().lower()
        if proceed != "y":
            print("Cancelled by user.")
            return

        # Select room
        if len(rooms) == 1:
            room_idx = 0
        else:
            room_idx = int(input(f"Select room index (0-{len(rooms)-1}): ").strip())

        room = rooms[room_idx]

        # Debug: Print room details including IDs
        print(f"\nSelected room details:")
        print(f"  room_id: {room.get('room_id')}")
        print(f"  transaction_id: {room.get('transaction_id')}")

        # Validate room_id exists
        if not room.get("room_id") or room.get("room_id") == "undefined":
            print("\nERROR: Room ID is missing or invalid!")
            print(f"Available room data: {room}")
            return

        reason = input("\nReason (or press Enter for 'Change of plans'): ").strip()
        if not reason:
            reason = "Change of plans"
        remark = input("Remark (optional, press Enter to skip): ").strip()

        # Step 3: Send OTP (auto-refreshes session internally)
        print("\n[Step 3] Sending cancellation OTP...")
        otp_result = await svc.send_cancellation_otp(
            booking_id=booking_id,
            email=email,
        )

        if not otp_result["success"]:
            print(f"Failed to send OTP: {otp_result['message']}")
            print(f"Raw response: {otp_result.get('raw_response')}")
            return

        print(f"OTP sent: {otp_result['message']}")

        # Step 4: Request Cancellation (auto-refreshes session internally)
        otp = input("\nEnter OTP: ").strip()

        print("\n[Step 4] Submitting cancellation request...")
        cancel = await svc.request_cancellation(
            booking_id=booking_id,
            email=email,
            otp=otp,
            room_id=room["room_id"],
            transaction_id=room["transaction_id"],
            is_pay_at_hotel=room["is_pay_at_hotel"],
            payment_url=details.get("payment_url", ""),
            reason=reason,
            remark=remark,
        )

        if cancel["success"]:
            print(f"\nCancellation successful! {cancel['message']}")
            if cancel.get("refund_info"):
                ri = cancel["refund_info"]
                print(f"  Refund: {ri.get('refund_amount', 'N/A')}")
                print(f"  Charges: {ri.get('cancellation_charges', 'N/A')}")
        else:
            print(f"\nCancellation failed: {cancel['message']}")

        print("\nRaw response:", cancel.get("raw_response"))


if __name__ == "__main__":
    asyncio.run(main())
