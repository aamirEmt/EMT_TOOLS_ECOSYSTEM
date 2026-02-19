"""
Test HTML Generator - Generates UI using hotel_cancellation_renderer.py with dummy data.
Opens both Booking Details and Cancellation Success templates in the browser.
"""
import webbrowser
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from tools_factory.hotel_cancellation.hotel_cancellation_renderer import (
    render_booking_details,
    render_cancellation_success,
)


# ===================================================================
# Dummy data matching the real API response structure
# ===================================================================

DUMMY_BOOKING_DETAILS = {
    "booking_id": "EMT162477218",
    "payment_url": "https://emt.bio/myeIn4",
    "hotel_info": {
        "hotel_name": "ZIP BY SPREE HOTELS BROOKEFIELD",
        "address": "Site 627, Aecs Layout, Kundalahalli, Brookefield, Bengaluru, Karnataka 560037",
        "check_in": "2026-02-27T00:00:00",
        "check_out": "2026-03-25T00:00:00",
        "duration": "26",
        "total_fare": "59328.00",
        "number_of_rooms": "1",
    },
    "guest_info": [
        {
            "title": "Mr.",
            "first_name": "Rahul",
            "last_name": "Sharma",
            "pax_type": "Adult",
            "mobile": "9876543210",
        },
        {
            "title": "Mrs.",
            "first_name": "Priya",
            "last_name": "Sharma",
            "pax_type": "Adult",
            "mobile": "9876543210",
        },
    ],
    "rooms": [
        {
            "room_id": "6146385",
            "room_type": "Deluxe King Or Twin Bed Room",
            "room_no": "1",
            "transaction_id": "162477218",
            "cancellation_policy": "\u2022 Free cancellation (Rs.0) before 26-Feb-2026\n\u2022 100% Deduction From: 26-Feb-2026 till check-in",
            "is_pay_at_hotel": True,
            "total_adults": "2",
            "amount": "59328.00",
            "meal_type": "Breakfast not included, Welcome Drink, Free Wi-Fi",
            "is_refundable": True,
        },
    ],
}

DUMMY_BOOKING_MULTI_ROOM = {
    "booking_id": "EMT162499001",
    "hotel_info": {
        "hotel_name": "The Oberoi Grand, Kolkata",
        "address": "15, Jawaharlal Nehru Road, Kolkata, West Bengal 700013",
        "check_in": "2026-03-10T00:00:00",
        "check_out": "2026-03-14T00:00:00",
        "duration": "4",
        "total_fare": "48500.00",
        "number_of_rooms": "2",
    },
    "guest_info": [
        {
            "title": "Mr.",
            "first_name": "Amit",
            "last_name": "Patel",
            "pax_type": "Adult",
            "mobile": "9123456789",
        },
    ],
    "rooms": [
        {
            "room_id": "7001001",
            "room_type": "Premier Suite",
            "room_no": "501",
            "transaction_id": "162499001",
            "cancellation_policy": "\u2022 Free cancellation before 08-Mar-2026\n\u2022 50% charge from 08-Mar to 09-Mar-2026\n\u2022 100% charge from 09-Mar-2026 onwards",
            "is_pay_at_hotel": False,
            "total_adults": "2",
            "amount": "28500.00",
            "meal_type": "Breakfast included, Airport Pickup",
            "is_refundable": True,
        },
        {
            "room_id": "7001002",
            "room_type": "Deluxe Double Room",
            "room_no": "302",
            "transaction_id": "162499001",
            "cancellation_policy": "\u2022 Non-refundable booking",
            "is_pay_at_hotel": False,
            "total_adults": "1",
            "amount": "20000.00",
            "meal_type": "Breakfast included",
            "is_refundable": False,
        },
    ],
}

DUMMY_CANCELLATION_WITH_REFUND = {
    "booking_id": "EMT162477218",
    "hotel_name": "ZIP BY SPREE HOTELS BROOKEFIELD",
    "room_type": "Deluxe King Or Twin Bed Room",
    "refund_info": {
        "refund_amount": "59328.00",
        "cancellation_charges": "0.00",
        "refund_mode": "Original Payment Method",
    },
}

DUMMY_CANCELLATION_NO_REFUND = {
    "booking_id": "EMT162499001",
    "hotel_name": "The Oberoi Grand, Kolkata",
    "room_type": "Deluxe Double Room",
    "refund_info": None,
}


# ===================================================================
# Generate HTML and write to file
# ===================================================================

def generate_test_page():
    booking_html_1 = render_booking_details(DUMMY_BOOKING_DETAILS)
    booking_html_2 = render_booking_details(DUMMY_BOOKING_MULTI_ROOM)
    success_html_1 = render_cancellation_success(DUMMY_CANCELLATION_WITH_REFUND)
    success_html_2 = render_cancellation_success(DUMMY_CANCELLATION_NO_REFUND)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hotel Cancellation Renderer - UI Test</title>
    <style>
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: #f0f2f5;
            margin: 0;
            padding: 20px;
        }}
        .test-section {{
            max-width: 800px;
            margin: 0 auto 40px;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            overflow: hidden;
        }}
        .test-header {{
            background: linear-gradient(135deg, #1a237e, #283593);
            color: #fff;
            padding: 16px 24px;
            font-size: 16px;
            font-weight: 600;
        }}
        .test-header span {{
            font-size: 12px;
            opacity: 0.7;
            display: block;
            margin-top: 4px;
            font-weight: 400;
        }}
        .test-body {{
            padding: 20px;
        }}
        h1 {{
            text-align: center;
            color: #1a237e;
            margin-bottom: 30px;
            font-size: 28px;
        }}
        .dark-toggle {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .dark-toggle button {{
            padding: 10px 24px;
            border: 2px solid #1a237e;
            background: #fff;
            color: #1a237e;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
        }}
        .dark-toggle button:hover {{
            background: #1a237e;
            color: #fff;
        }}
    </style>
</head>
<body>

<h1>Hotel Cancellation Renderer - UI Test</h1>

<div class="dark-toggle">
    <button onclick="document.querySelectorAll('.booking-details-carousel, .cancellation-success').forEach(el => el.classList.toggle('dark')); document.body.style.background = document.body.style.background === 'rgb(26, 26, 26)' ? '#f0f2f5' : '#1a1a1a';">
        Toggle Dark Mode
    </button>
</div>

<!-- Test 1: Single Room Booking Details -->
<div class="test-section">
    <div class="test-header">
        Test 1: Booking Details - Single Room (Pay at Hotel)
        <span>ZIP BY SPREE HOTELS BROOKEFIELD - 26 nights - 2 guests</span>
    </div>
    <div class="test-body">
        {booking_html_1}
    </div>
</div>

<!-- Test 2: Multi Room Booking Details -->
<div class="test-section">
    <div class="test-header">
        Test 2: Booking Details - Multiple Rooms (Prepaid)
        <span>The Oberoi Grand - 4 nights - 1 Refundable + 1 Non-Refundable</span>
    </div>
    <div class="test-body">
        {booking_html_2}
    </div>
</div>

<!-- Test 3: Cancellation Success with Refund -->
<div class="test-section">
    <div class="test-header">
        Test 3: Cancellation Success - With Full Refund
        <span>Shows refund amount, charges, and refund mode</span>
    </div>
    <div class="test-body">
        {success_html_1}
    </div>
</div>

<!-- Test 4: Cancellation Success without Refund -->
<div class="test-section">
    <div class="test-header">
        Test 4: Cancellation Success - No Refund Info
        <span>Non-refundable booking cancellation</span>
    </div>
    <div class="test-body">
        {success_html_2}
    </div>
</div>

</body>
</html>"""

    output_path = os.path.join(os.path.dirname(__file__), "test_renderer_output.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"HTML generated: {output_path}")
    webbrowser.open(f"file:///{output_path.replace(os.sep, '/')}")
    print("Opened in browser.")


if __name__ == "__main__":
    generate_test_page()
