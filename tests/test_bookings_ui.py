"""
UI Tests for Booking Renderers (Flight, Bus, Train, Hotel).

Run with:
    pytest tests/test_bookings_ui.py -v -s

Generate HTML only:
    python tests/test_bookings_ui.py

"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from typing import Dict, Any

from tools_factory.bookings.flight_bookings_renderer import render_flight_bookings
from tools_factory.bookings.bus_bookings_renderer import render_bus_bookings
from tools_factory.bookings.train_bookings_renderer import render_train_bookings
from tools_factory.bookings.hotel_bookings_renderer import render_hotel_bookings

pytestmark = [pytest.mark.ui]


# ============================================================================
# HTML HELPERS
# ============================================================================

def wrap_html_page(content: str, title: str = "Bookings UI Test") -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ background: #f5f5f5; padding: 20px; margin: 0; }}
        .test-section {{ margin-bottom: 40px; padding: 20px; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .test-title {{ font-family: sans-serif; font-size: 18px; font-weight: 600; color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #ef6614; }}
        .test-meta {{ font-family: sans-serif; font-size: 12px; color: #666; margin-bottom: 15px; }}
    </style>
</head>
<body>{content}</body>
</html>"""


def save_html_file(html_content: str, filename: str, output_dir: str = None) -> str:
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    return filepath


# ============================================================================
# SAMPLE API DATA (from real EaseMyTrip product search response)
# ============================================================================

SAMPLE_FLIGHT_DATA = {
    "Upcoming": [
        {
            "FlightDetailUI": [{
                "canPolicy": None, "faretype": "Oneway", "IsDomestic": True,
                "DepartureCity": "New Delhi", "ArrivalCity": "Jaipur",
                "DepartureDate": "Sun-03May2026", "ArrivalDate": "Sun-03May2026",
                "DepartureTime": "06:00", "ArrivalTime": "06:45",
                "AirLineName": "6E", "FlightNumber": "6483", "FlightStops": "0",
                "ClassOfFlight": "R", "FlightDuration": "00h 45m",
                "GDSPnr": "tester", "AirLinePnr": "tester",
                "SourceTerminal": "Terminal 1", "DestinationalTerminal": "Terminal 2",
                "DepartureName": "Indira Gandhi International Airport",
                "ArrivalName": "Jaipur Airport",
                "DepartureCityCode": "DEL", "ArrivalCityCode": "JAI",
                "ClassType": "Economy", "BaggageWeight": "15Kgs",
                "CabinBaggageWeight": "7Kgs", "FullAirLineName": "Indigo",
                "BrandFareName": "Saver",
                "TransactionScreenId": "EMT162759795",
            }],
            "fltDetails": {
                "passengerDetails": [{
                    "title": "Mr", "firstName": "Rikant", "lastName": "Test",
                    "status": "Confirmed", "airLinePnr": "tester",
                    "bookingAmt": 3021.0, "origin": "DEL", "destination": "JAI",
                    "cabinClass": "Economy", "paxType": "ADT",
                }],
                "bookingDate": "2026-02-12T16:14:59",
                "transactionScreenId": "EMT162759795",
                "FareType": "Oneway", "emtFee": 300,
            },
            "BookingRefNo": "EMT162759795", "TripDetails": "New Delhi-Jaipur",
            "TravelDate": "Sun-03May2026", "BookingDate": "Thu - 12 Feb 2026",
            "Travellers": "1", "TripStatus": "Upcoming Trip",
            "Status": "Upcoming Trip", "TripType": "OneWay",
            "SourceFullCityName": "Delhi", "DestinationFullCityName": "Jaipur",
            "Currency": "INR",
        },
        {
            "FlightDetailUI": [{
                "DepartureCity": "Hyderabad", "ArrivalCity": "Goa",
                "DepartureDate": "Sat-21Mar2026", "ArrivalDate": "Sat-21Mar2026",
                "DepartureTime": "15:40", "ArrivalTime": "16:55",
                "AirLineName": "6E", "FlightNumber": " 121", "FlightStops": "0",
                "FlightDuration": "01h 15m",
                "SourceTerminal": "", "DestinationalTerminal": "",
                "DepartureCityCode": "HYD", "ArrivalCityCode": "GOX",
                "DepartureName": "Rajiv Gandhi International Airport",
                "ArrivalName": "North Goa -MOPA Airport",
                "ClassType": "Economy", "BaggageWeight": "15Kgs",
                "CabinBaggageWeight": "7Kgs", "FullAirLineName": "Indigo",
                "BrandFareName": "Saver",
            }],
            "fltDetails": {
                "passengerDetails": [{
                    "title": "Mr", "firstName": "Rikant", "lastName": "Test",
                    "status": "Confirmed", "airLinePnr": "Tespnr",
                    "bookingAmt": 2638.0,
                }],
                "bookingDate": "2026-02-12T15:53:07",
                "FareType": "Oneway",
            },
            "BookingRefNo": "EMT162758999", "TripDetails": "Hyderabad-Goa",
            "TravelDate": "Sat-21Mar2026", "BookingDate": "Thu - 12 Feb 2026",
            "Travellers": "1", "TripStatus": "Upcoming Trip",
            "Status": "Upcoming Trip", "TripType": "OneWay",
            "Currency": "INR",
        },
    ],
    "Cancelled": [
        {
            "FlightDetailUI": [{
                "DepartureCity": "New Delhi", "ArrivalCity": "Jaipur",
                "DepartureDate": "Sun-01Mar2026", "ArrivalDate": "Sun-01Mar2026",
                "DepartureTime": "04:45", "ArrivalTime": "05:40",
                "AirLineName": "6E", "FlightNumber": "5037", "FlightStops": "0",
                "FlightDuration": "00h 55m",
                "SourceTerminal": "Terminal 3", "DestinationalTerminal": "Terminal 2",
                "DepartureCityCode": "DEL", "ArrivalCityCode": "JAI",
                "ClassType": "Economy", "BaggageWeight": "15Kgs",
                "CabinBaggageWeight": "7Kgs", "FullAirLineName": "Indigo",
                "BrandFareName": "Saver",
            }],
            "fltDetails": {
                "passengerDetails": [{
                    "title": "Mr", "firstName": "Rikant", "lastName": "Test",
                    "status": "Cancel Requested", "airLinePnr": "tester",
                    "bookingAmt": 2699.0,
                    "cancelRequestedDate": "2/17/2026 5:07:56 PM",
                }],
                "bookingDate": "2026-02-12T15:30:22",
                "FareType": "Oneway",
            },
            "BookingRefNo": "EMT162758223", "TripDetails": "New Delhi-Jaipur",
            "TravelDate": "Sun-01Mar2026", "BookingDate": "Thu - 12 Feb 2026",
            "Travellers": "1", "TripStatus": "Cancelled Requested",
            "Status": "Cancelled Requested", "TripType": "OneWay",
            "Currency": "INR",
            "CancelListStrip": "Your flight cancellation request has been sent !",
            "CanReqDate": "Tue - 17 Feb 2026 05:07:56 PM",
        },
    ],
    "Completed": None,
    "Locked": None,
    "Rejected": None,
}

SAMPLE_BUS_DATA = {
    "UpComing": [
        {
            "BookingRefNo": "EMT162787700",
            "TripDetails": "Rajkot-Jamnagar",
            "BookingDate": "Friday, February 13, 2026",
            "Travellers": "1",
            "Status": "UpcomingTrip",
            "DateOfJourney": "2/26/2026 7:00:00 PM",
            "JourneyDate": "2/26/2026 7:00:00 PM",
            "BookedOn": "Friday, February 13, 2026",
            "Details": {
                "DepartureDate": "Thursday, February 26, 2026",
                "DepartureTime": "06:30 PM",
                "DepartureTime1": "19:00",
                "BusDuration": "01h 30m",
                "ArrivalTime": "20:30",
                "ArrivalDate": "Thursday, February 26, 2026",
                "TravelsOperator": "SHYAM TRAVELS",
                "BusType": "NONAC Sleeper ( + ) ",
                "Source": "Rajkot",
                "Destination": "Jamnagar",
                "BPLocation": "Main Bus Stand, Greenland Chowkadi",
                "BdTime": "06:30 PM",
                "Droptime": "08:30 PM",
            },
        },
    ],
    "Cancelled": [
        {
            "BookingRefNo": "EMT162787610",
            "TripDetails": "Rajkot-Jamnagar",
            "BookingDate": "Friday, February 13, 2026",
            "Travellers": "1",
            "Status": "Refunded",
            "DateOfJourney": "2/27/2026 7:00:00 PM",
            "Details": {
                "DepartureDate": "Friday, February 27, 2026",
                "DepartureTime": "06:30 PM",
                "DepartureTime1": "19:00",
                "BusDuration": "01h 30m",
                "ArrivalTime": "20:30",
                "ArrivalDate": "Friday, February 27, 2026",
                "TravelsOperator": "Shyam Travels",
                "BusType": "NONAC Sleeper ( + ) ",
                "Source": "Rajkot",
                "Destination": "Jamnagar",
                "BPLocation": "Main Bus Stand, Greenland Chowkadi",
            },
            "canRequestDate": "2/13/2026 2:58:49 PM",
            "RefundAmt": 118,
            "RefunUpdatedON": "2/13/2026 10:57:40 PM",
        },
        {
            "BookingRefNo": "EMT162787451",
            "TripDetails": "Rajkot-Jamnagar",
            "BookingDate": "Friday, February 13, 2026",
            "Travellers": "1",
            "Status": "Refunded",
            "DateOfJourney": "2/28/2026 7:00:00 PM",
            "Details": {
                "DepartureDate": "Saturday, February 28, 2026",
                "DepartureTime": "06:30 PM",
                "DepartureTime1": "19:00",
                "BusDuration": "01h 30m",
                "ArrivalTime": "20:30",
                "ArrivalDate": "Saturday, February 28, 2026",
                "TravelsOperator": "Shyam Travels",
                "BusType": "NONAC Sleeper ( + ) ",
                "Source": "Rajkot",
                "Destination": "Jamnagar",
                "BPLocation": "Main Bus Stand, Greenland Chowkadi",
            },
            "canRequestDate": "2/13/2026 12:43:02 PM",
            "RefundAmt": 126,
            "RefunUpdatedON": "2/13/2026 10:55:21 PM",
        },
    ],
    "Completed": None,
    "Refunded": [
        {
            "BookingRefNo": "EMT162787610",
            "TripDetails": "Rajkot-Jamnagar",
            "BookingDate": "Friday, February 13, 2026",
            "Travellers": "1",
            "Status": "Refunded",
            "DateOfJourney": "2/27/2026 7:00:00 PM",
            "Details": {
                "DepartureDate": "Friday, February 27, 2026",
                "DepartureTime": "06:30 PM",
                "DepartureTime1": "19:00",
                "BusDuration": "01h 30m",
                "ArrivalTime": "20:30",
                "ArrivalDate": "Friday, February 27, 2026",
                "TravelsOperator": "Shyam Travels",
                "BusType": "NONAC Sleeper ( + ) ",
                "Source": "Rajkot",
                "Destination": "Jamnagar",
            },
            "RefundAmt": 118,
            "RefunUpdatedON": "2/13/2026 10:57:40 PM",
        },
    ],
}

SAMPLE_TRAIN_DATA = {
    "trainJourneyDetails": [
        {
            "BookingRefNo": "EMT162790845",
            "TripDetails": "RJPB-PNBE",
            "TravelDate": "Wed-08 Apr 2026",
            "ArrivalDate": "Wed-08 Apr 2026",
            "DepartureDate": "Wed-08 Apr 2026",
            "Travellers": "1",
            "TripStatus": "Refunded",
            "BookingDate": "Fri-13 Feb 2026",
            "TrainName": "Intercity Exp",
            "TrainNo": "13401",
            "FromStn": "Rajendranagar T",
            "ToStn": "Patna Jn",
            "Class": "2S",
            "Quota": "GN",
            "BoardingStation": "RJPB",
            "BoardingTime": "10:43",
            "BoardingDate": "Wed-08 Apr 2026",
            "TrainDuration": "00h 10m",
            "DepartureTime": "10:45",
            "ArrivalTime": "10:55",
            "RefundAmt": 0,
            "RefundDate": "Sat - 14 Feb 2026",
            "CanReqDate": "Fri - 13 Feb 2026",
        },
        {
            "BookingRefNo": "EMT162795704",
            "TripDetails": "SGG-BGP",
            "TravelDate": "Mon-13 Apr 2026",
            "ArrivalDate": "Mon-13 Apr 2026",
            "DepartureDate": "Mon-13 Apr 2026",
            "Travellers": "1",
            "TripStatus": "Refunded",
            "BookingDate": "Fri-13 Feb 2026",
            "TrainName": "Kaviguru Expres",
            "TrainNo": "13016",
            "FromStn": "Sultanganj",
            "ToStn": "Bhagalpur",
            "Class": "2S",
            "Quota": "GN",
            "BoardingStation": "SGG",
            "BoardingTime": "06:54",
            "BoardingDate": "Mon-13 Apr 2026",
            "TrainDuration": "00h 49m",
            "DepartureTime": "06:56",
            "ArrivalTime": "07:45",
            "RefundAmt": 0,
            "RefundDate": "Sat - 14 Feb 2026",
            "CanReqDate": "Fri - 13 Feb 2026",
        },
    ],
    "Upcoming": None,
    "Completed": None,
    "Cancelled": None,
    "Refunded": [
        {
            "BookingRefNo": "EMT162790845",
            "TripDetails": "RJPB-PNBE",
            "TravelDate": "Wed-08 Apr 2026",
            "Travellers": "1",
            "TripStatus": "Refunded",
            "BookingDate": "Fri-13 Feb 2026",
            "TrainName": "Intercity Exp",
            "TrainNo": "13401",
            "FromStn": "Rajendranagar T",
            "ToStn": "Patna Jn",
            "Class": "2S",
            "Quota": "GN",
            "BoardingStation": "RJPB",
            "BoardingTime": "10:43",
            "TrainDuration": "00h 10m",
            "DepartureTime": "10:45",
            "ArrivalTime": "10:55",
            "RefundAmt": 0,
            "RefundDate": "Sat - 14 Feb 2026",
        },
        {
            "BookingRefNo": "EMT162795704",
            "TripDetails": "SGG-BGP",
            "TravelDate": "Mon-13 Apr 2026",
            "Travellers": "1",
            "TripStatus": "Refunded",
            "BookingDate": "Fri-13 Feb 2026",
            "TrainName": "Kaviguru Expres",
            "TrainNo": "13016",
            "FromStn": "Sultanganj",
            "ToStn": "Bhagalpur",
            "Class": "2S",
            "Quota": "GN",
            "BoardingStation": "SGG",
            "BoardingTime": "06:54",
            "TrainDuration": "00h 49m",
            "DepartureTime": "06:56",
            "ArrivalTime": "07:45",
            "RefundAmt": 0,
            "RefundDate": "Sat - 14 Feb 2026",
        },
    ],
}

SAMPLE_HOTEL_DATA = {
    "Upcoming": [
        {
            "BookingRefNo": "EMT162800001",
            "HotelName": "Taj Mahal Palace",
            "CheckInDate": "Sat-15 Mar 2026",
            "CheckOutDate": "Mon-17 Mar 2026",
            "NoOfRooms": 1,
            "NoOfGuests": 2,
            "Night": 2,
            "RoomType": "Deluxe Room",
            "TripDetails": "Mumbai",
            "BookingDate": "Thu - 12 Feb 2026",
            "TripStatus": "Upcoming",
            "Travellers": "2",
            "Address_Description": "Apollo Bunder, Colaba, Mumbai, Maharashtra 400001",
        },
    ],
    "Completed": [
        {
            "BookingRefNo": "EMT162800002",
            "HotelName": "The Oberoi Udaivilas",
            "CheckInDate": "Mon-01 Jan 2026",
            "CheckOutDate": "Thu-04 Jan 2026",
            "NoOfRooms": 1,
            "NoOfGuests": 2,
            "Night": 3,
            "RoomType": "Premier Room",
            "TripDetails": "Udaipur",
            "BookingDate": "Mon - 20 Dec 2025",
            "TripStatus": "Completed",
            "Travellers": "2",
        },
    ],
    "Cancelled": None,
    "Pending": None,
}


# ============================================================================
# RENDERER TESTS
# ============================================================================

class TestFlightBookingsRenderer:

    def test_renders_html(self):
        html = render_flight_bookings(SAMPLE_FLIGHT_DATA)
        assert html is not None
        assert len(html) > 0

    def test_contains_status_tabs(self):
        html = render_flight_bookings(SAMPLE_FLIGHT_DATA)
        assert "bkng-tab" in html
        assert "Upcoming" in html
        assert "Cancelled" in html

    def test_upcoming_tab_active_by_default(self):
        html = render_flight_bookings(SAMPLE_FLIGHT_DATA)
        # The Upcoming tab should have the active class
        assert 'data-status="Upcoming"' in html

    def test_contains_booking_cards(self):
        html = render_flight_bookings(SAMPLE_FLIGHT_DATA)
        assert "bkng-card" in html
        assert "EMT162759795" in html
        assert "EMT162758999" in html
        assert "EMT162758223" in html

    def test_contains_flight_details(self):
        html = render_flight_bookings(SAMPLE_FLIGHT_DATA)
        assert "Indigo" in html
        assert "6E" in html
        assert "DEL" in html
        assert "JAI" in html
        assert "06:00" in html
        assert "06:45" in html

    def test_contains_passenger_info(self):
        html = render_flight_bookings(SAMPLE_FLIGHT_DATA)
        assert "Rikant" in html
        assert "Confirmed" in html

    def test_contains_cancel_strip(self):
        html = render_flight_bookings(SAMPLE_FLIGHT_DATA)
        assert "cancellation request has been sent" in html

    def test_empty_data(self):
        html = render_flight_bookings({})
        assert "No flight bookings" in html

    def test_none_data(self):
        html = render_flight_bookings(None)
        assert "No flight bookings" in html

    def test_tab_counts(self):
        html = render_flight_bookings(SAMPLE_FLIGHT_DATA)
        assert "(2)" in html  # 2 upcoming
        assert "(1)" in html  # 1 cancelled


class TestBusBookingsRenderer:

    def test_renders_html(self):
        html = render_bus_bookings(SAMPLE_BUS_DATA)
        assert html is not None
        assert len(html) > 0

    def test_contains_status_tabs(self):
        html = render_bus_bookings(SAMPLE_BUS_DATA)
        assert "bkng-tab" in html
        assert "Upcoming" in html
        assert "Cancelled" in html

    def test_upcoming_tab_active_by_default(self):
        html = render_bus_bookings(SAMPLE_BUS_DATA)
        assert 'data-status="UpComing"' in html

    def test_contains_booking_cards(self):
        html = render_bus_bookings(SAMPLE_BUS_DATA)
        assert "bkng-card" in html
        assert "EMT162787700" in html

    def test_contains_bus_details(self):
        html = render_bus_bookings(SAMPLE_BUS_DATA)
        assert "SHYAM TRAVELS" in html
        assert "Rajkot" in html
        assert "Jamnagar" in html
        assert "19:00" in html

    def test_contains_refund_info(self):
        html = render_bus_bookings(SAMPLE_BUS_DATA)
        assert "118" in html

    def test_empty_data(self):
        html = render_bus_bookings({})
        assert "No bus bookings" in html


class TestTrainBookingsRenderer:

    def test_renders_html(self):
        html = render_train_bookings(SAMPLE_TRAIN_DATA)
        assert html is not None
        assert len(html) > 0

    def test_contains_status_tabs(self):
        html = render_train_bookings(SAMPLE_TRAIN_DATA)
        assert "bkng-tab" in html
        assert "Refunded" in html

    def test_contains_booking_cards(self):
        html = render_train_bookings(SAMPLE_TRAIN_DATA)
        assert "bkng-card" in html
        assert "EMT162790845" in html
        assert "EMT162795704" in html

    def test_contains_train_details(self):
        html = render_train_bookings(SAMPLE_TRAIN_DATA)
        assert "Intercity Exp" in html
        assert "13401" in html
        assert "Rajendranagar T" in html
        assert "Patna Jn" in html
        assert "10:45" in html

    def test_contains_class_quota(self):
        html = render_train_bookings(SAMPLE_TRAIN_DATA)
        assert "2S" in html
        assert "GN" in html

    def test_empty_data(self):
        html = render_train_bookings({})
        assert "No train bookings" in html


class TestHotelBookingsRenderer:

    def test_renders_html(self):
        html = render_hotel_bookings(SAMPLE_HOTEL_DATA)
        assert html is not None
        assert len(html) > 0

    def test_contains_status_tabs(self):
        html = render_hotel_bookings(SAMPLE_HOTEL_DATA)
        assert "bkng-tab" in html
        assert "Upcoming" in html
        assert "Completed" in html

    def test_upcoming_tab_active_by_default(self):
        html = render_hotel_bookings(SAMPLE_HOTEL_DATA)
        assert 'data-status="Upcoming"' in html

    def test_contains_hotel_details(self):
        html = render_hotel_bookings(SAMPLE_HOTEL_DATA)
        assert "Taj Mahal Palace" in html
        assert "Sat-15 Mar 2026" in html
        assert "Mon-17 Mar 2026" in html

    def test_contains_room_info(self):
        html = render_hotel_bookings(SAMPLE_HOTEL_DATA)
        assert "Deluxe Room" in html

    def test_empty_data(self):
        html = render_hotel_bookings({})
        assert "No hotel bookings" in html


# ============================================================================
# HTML FILE GENERATION TEST
# ============================================================================

def test_generate_all_bookings_html():
    """Generate a combined HTML file with all booking renderers for visual inspection."""
    sections = []

    # Flight bookings
    flight_html = render_flight_bookings(SAMPLE_FLIGHT_DATA)
    sections.append(f"""
    <div class="test-section">
        <div class="test-title">Flight Bookings</div>
        <div class="test-meta">2 Upcoming + 1 Cancelled | Upcoming tab active by default</div>
        {flight_html}
    </div>
    """)

    # Bus bookings
    bus_html = render_bus_bookings(SAMPLE_BUS_DATA)
    sections.append(f"""
    <div class="test-section">
        <div class="test-title">Bus Bookings</div>
        <div class="test-meta">1 Upcoming + 2 Cancelled + 1 Refunded | Upcoming tab active by default</div>
        {bus_html}
    </div>
    """)

    # Train bookings
    train_html = render_train_bookings(SAMPLE_TRAIN_DATA)
    sections.append(f"""
    <div class="test-section">
        <div class="test-title">Train Bookings</div>
        <div class="test-meta">2 Refunded (from trainJourneyDetails) | Refunded tab active (no upcoming)</div>
        {train_html}
    </div>
    """)

    # Hotel bookings
    hotel_html = render_hotel_bookings(SAMPLE_HOTEL_DATA)
    sections.append(f"""
    <div class="test-section">
        <div class="test-title">Hotel Bookings</div>
        <div class="test-meta">1 Upcoming + 1 Completed | Upcoming tab active by default</div>
        {hotel_html}
    </div>
    """)

    full_html = wrap_html_page("\n".join(sections), "Bookings Renderers - UI Test")
    filepath = save_html_file(full_html, "bookings_ui_test.html")
    print(f"\nHTML saved to: {filepath}")
    print(f"Open in browser to inspect the UI.")

    assert os.path.exists(filepath)
    assert os.path.getsize(filepath) > 0


# ============================================================================
# STANDALONE: python tests/test_bookings_ui.py
# ============================================================================

if __name__ == "__main__":
    test_generate_all_bookings_html()
    print("\nRunning unit tests...")
    pytest.main([__file__, "-v", "--tb=short", "-x"])
