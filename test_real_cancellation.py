"""
Test script: Runs the real cancellation flow (login + fetch details),
renders the interactive HTML using the actual renderer, and saves it
to test_output.html. Open that file in Chrome (with CORS disabled) to
test the full OTP + cancellation flow against real EaseMyTrip APIs.

Usage:
    python test_real_cancellation.py <booking_id> <email>

Example:
    python test_real_cancellation.py EMT1624718 user@example.com

Then open test_output.html in Chrome launched with:
    chrome.exe --disable-web-security --disable-gpu --user-data-dir="%TEMP%\chrome-cors-test"
"""
import asyncio
import sys
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from tools_factory.hotel_cancellation.hotel_cancellation_service import HotelCancellationService
from tools_factory.hotel_cancellation.hotel_cancellation_renderer import render_booking_details


async def main(booking_id: str, email: str):
    service = HotelCancellationService()

    try:
        # Step 1: Guest login
        print(f"\n[1/2] Logging in with booking_id={booking_id}, email={email} ...")
        login_result = await service.guest_login(booking_id=booking_id, email=email)

        if not login_result["success"]:
            print(f"Login failed: {login_result['message']}")
            return

        bid = login_result["ids"]["bid"]
        print(f"  Login OK. BID = {bid}")

        # Step 2: Fetch booking details
        print(f"\n[2/2] Fetching booking details ...")
        details = await service.fetch_booking_details(bid=bid)

        if not details["success"]:
            print(f"  Fetch failed: {details.get('error')}")
            return

        print(f"  Found {len(details.get('rooms', []))} room(s)")
        print(f"  Hotel: {details.get('hotel_info', {}).get('hotel_name', 'N/A')}")

        # Render interactive HTML (exact same code path as production)
        details["booking_id"] = booking_id
        html = render_booking_details(
            booking_details=details,
            booking_id=booking_id,
            email=email,
            bid=bid,
        )

        # Wrap in a full HTML page
        output = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hotel Cancellation Test — {booking_id}</title>
  <style>
    body {{ margin: 0; padding: 20px; background: #f5f5f5; font-family: sans-serif; }}
    .wrapper {{ max-width: 750px; margin: 0 auto; }}
    .info-banner {{ background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px;
                    padding: 12px 16px; margin-bottom: 20px; font-size: 13px; color: #856404; }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="info-banner">
      Testing with real APIs. BID: <code>{bid}</code> | Booking: <code>{booking_id}</code><br>
      Open this in Chrome with <code>--disable-web-security</code> to avoid CORS errors.
    </div>
    {html}
  </div>
</body>
</html>"""

        output_path = "test_output.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"\nDone! Open {output_path} in Chrome (with CORS disabled).")
        print(f'  chrome.exe --disable-web-security --disable-gpu --user-data-dir="%TEMP%\\chrome-cors-test"')

    finally:
        await service.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_real_cancellation.py <booking_id> <email>")
        print("Example: python test_real_cancellation.py EMT1624718 user@example.com")
        sys.exit(1)

    asyncio.run(main(sys.argv[1], sys.argv[2]))
