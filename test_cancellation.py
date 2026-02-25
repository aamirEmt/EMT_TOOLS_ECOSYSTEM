"""Interactive terminal test for Hotel Cancellation Flow (unified tool)"""
import asyncio
import logging
from tools_factory.factory import get_tool_factory

# Enable logging to see debug messages
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')


async def main():
    factory = get_tool_factory()
    tool = factory.get_tool("hotel_cancellation")

    if not tool:
        print("ERROR: hotel_cancellation tool not found in factory!")
        return

    print("=" * 50)
    print("  Hotel Booking Cancellation - Test")
    print("=" * 50)

    # Step 1: Start (login + fetch details)
    booking_id = input("\nBooking ID (e.g. EMT1624718): ").strip()
    email = input("Email: ").strip()

    print("\n[Action: start] Logging in and fetching details...")
    result = await tool.execute(
        action="start",
        booking_id=booking_id,
        email=email,
    )

    print(f"\nResponse: {result.response_text}")

    if result.is_error:
        print("Flow stopped due to error.")
        return

    # Show rooms from structured content
    details = result.structured_content.get("booking_details", {})
    rooms = details.get("rooms", [])
    print(f"\nFound {len(rooms)} room(s):")
    for i, r in enumerate(rooms):
        print(f"  [{i}] {r.get('room_type', 'N/A')} - Room {r.get('room_no', 'N/A')}")
        print(f"      ID: {r.get('room_id')}")
        print(f"      Transaction ID: {r.get('transaction_id')}")
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

    if not room.get("room_id") or room.get("room_id") == "undefined":
        print(f"\nERROR: Room ID is missing or invalid! Room data: {room}")
        return

    reason = input("\nReason (or press Enter for 'Change of plans'): ").strip()
    if not reason:
        reason = "Change of plans"
    remark = input("Remark (optional, press Enter to skip): ").strip()

    # Step 2: Send OTP
    print("\n[Action: send_otp] Sending cancellation OTP...")
    otp_result = await tool.execute(
        action="send_otp",
        booking_id=booking_id,
        email=email,
    )

    print(f"\nResponse: {otp_result.response_text}")

    if otp_result.is_error:
        print("Flow stopped due to error.")
        return

    # Step 3: Confirm cancellation
    otp = input("\nEnter OTP: ").strip()

    print("\n[Action: confirm] Submitting cancellation request...")
    cancel_result = await tool.execute(
        action="confirm",
        booking_id=booking_id,
        email=email,
        otp=otp,
        room_id=room["room_id"],
        transaction_id=room["transaction_id"],
        is_pay_at_hotel=room.get("is_pay_at_hotel", False),
        payment_url=details.get("payment_url", ""),
        reason=reason,
        remark=remark,
    )

    print(f"\nResponse: {cancel_result.response_text}")

    if cancel_result.is_error:
        print("Cancellation failed.")
    else:
        print("Cancellation successful!")

    print("\nRaw structured content:", cancel_result.structured_content)


if __name__ == "__main__":
    asyncio.run(main())
