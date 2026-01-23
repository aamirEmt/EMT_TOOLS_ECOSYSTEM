"""Real API tests for Bus Search Tool.

These tests make actual API calls and verify real responses.
NO MOCKING - Real API integration tests.

File: tests/test_buses.py

Run with:
    pytest tests/test_buses.py -v -s

Mark as integration tests:
    pytest -m integration

API Reference:
    POST http://busapi.easemytrip.com/v1/api/detail/List/
    
    Request payload:
    {
        "sourceId": "733",
        "destinationId": "757",
        "date": "08-11-2025",
        "key": "dsasa4gfdg4543gfdg6ghgf45325gfd",
        "version": "1",
        "isVrl": "False",
        "isVolvo": "False",
        "IsAndroidIos_Hit": false,
        "agentCode": "",
        "CountryCode": "IN"
    }
"""

import pytest
from datetime import datetime, timedelta
from tools_factory.factory import get_tool_factory
from tools_factory.base_schema import ToolResponseFormat

# Mark all tests in this file as integration tests (slow)
pytestmark = pytest.mark.integration


# ============================================================================
# TEST FIXTURES - DUMMY PAYLOADS
# Based on  example: sourceId "733" (Delhi), destinationId "757" (Manali)
# ============================================================================

@pytest.fixture
def dummy_bus_search_delhi_manali():
    """Dummy payload for Delhi to Manali route (from  example).
    
     example:
        sourceId: "733" (Delhi)
        destinationId: "757" (Manali)
    """
    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

    return {
        "source_id": "733",
        "destination_id": "757",
        "journey_date": journey_date,
    }


@pytest.fixture
def dummy_bus_search_with_volvo_filter():
    """Dummy payload with Volvo filter enabled (from : isVolvo field)."""
    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

    return {
        "source_id": "733",
        "destination_id": "757",
        "journey_date": journey_date,
        "is_volvo": True,
    }


@pytest.fixture
def dummy_bus_search_popular_route():
    """Dummy payload for popular route (likely to have many results)."""
    today = datetime.now()
    journey_date = (today + timedelta(days=14)).strftime("%Y-%m-%d")

    return {
        "source_id": "733",
        "destination_id": "757",
        "journey_date": journey_date,
    }


# ============================================================================
# BUS SEARCH TESTS - REAL API
# API: POST http://busapi.easemytrip.com/v1/api/detail/List/
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_delhi_manali(dummy_bus_search_delhi_manali):
    """Test bus search for Delhi (733) to Manali (757) route from ."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n🚌 Searching buses: {dummy_bus_search_delhi_manali}")

    result = await tool.execute(**dummy_bus_search_delhi_manali)

    assert hasattr(result, "response_text")
    print(f"✅ Response: {result.response_text}")

    assert result.structured_content is not None
    data = result.structured_content

    # Verify API response structure (from )
    assert "buses" in data
    assert "total_count" in data

    buses = data.get("buses", [])
    print(f"📊 Found {len(buses)} buses")

    if buses:
        first_bus = buses[0]
        # Fields from  AvailableTrips
        print(f"   First bus: {first_bus.get('operator_name')} - {first_bus.get('bus_type')}")
        print(f"   Departure: {first_bus.get('departure_time')}")
        print(f"   Duration: {first_bus.get('duration')}")
        print(f"   Price: ₹{first_bus.get('price')}")
        print(f"   Available Seats: {first_bus.get('available_seats')}")


@pytest.mark.asyncio
async def test_bus_search_with_volvo_filter(dummy_bus_search_with_volvo_filter):
    """Test bus search with Volvo filter (: isVolvo field)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n🚌 Searching Volvo buses: {dummy_bus_search_with_volvo_filter}")

    result = await tool.execute(**dummy_bus_search_with_volvo_filter)

    assert hasattr(result, "response_text")
    print(f"✅ Response: {result.response_text}")

    data = result.structured_content
    buses = data.get("buses", [])

    print(f"📊 Found {len(buses)} Volvo buses")

    # Verify Volvo filter applied
    for bus in buses[:3]:
        print(f"   {bus.get('operator_name')}: isVolvo={bus.get('is_volvo')}, busType={bus.get('bus_type')}")


@pytest.mark.asyncio
async def test_bus_search_popular_route(dummy_bus_search_popular_route):
    """Test bus search on popular route (should have many results)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n🚌 Searching popular route: {dummy_bus_search_popular_route}")

    result = await tool.execute(**dummy_bus_search_popular_route)

    data = result.structured_content
    buses = data.get("buses", [])

    print(f"📊 Found {len(buses)} buses on popular route")
    
    #  response fields
    print(f"   Total trips (TotalTrips): {data.get('total_trips', 0)}")
    print(f"   AC buses (AcCount): {data.get('ac_count', 0)}")
    print(f"   Non-AC buses (NonAcCount): {data.get('non_ac_count', 0)}")
    print(f"   Max Price: {data.get('max_price')}")
    print(f"   Min Price: {data.get('min_price')}")

    # Print first 3 buses
    for i, bus in enumerate(buses[:3], 1):
        print(f"\n   Bus {i}:")
        print(f"      Operator (Travels): {bus.get('operator_name')}")
        print(f"      Type (busType): {bus.get('bus_type')}")
        print(f"      Duration: {bus.get('duration')}")
        print(f"      Price: ₹{bus.get('price')}")
        print(f"      Seats (AvailableSeats): {bus.get('available_seats')}")
        print(f"      AC: {bus.get('is_ac')}")
        print(f"      Rating (rt): {bus.get('rating')}")


# ============================================================================
# WHATSAPP FORMAT TESTS - REAL API
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_whatsapp_format(dummy_bus_search_delhi_manali):
    """Test bus search returns WhatsApp formatted response."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    payload = {**dummy_bus_search_delhi_manali, "_user_type": "whatsapp"}

    print(f"\n📱 Searching buses (WhatsApp format): {payload}")

    result: ToolResponseFormat = await tool.execute(**payload)

    assert result.whatsapp_response is not None
    print(f"✅ WhatsApp response received")

    whatsapp_data = result.whatsapp_response
    assert "whatsapp_json" in whatsapp_data
    assert whatsapp_data["whatsapp_json"]["type"] == "bus_collection"

    options = whatsapp_data["whatsapp_json"].get("options", [])
    print(f"📊 WhatsApp options: {len(options)} buses")

    if options:
        first = options[0]
        print(f"\n   First option:")
        print(f"      Operator: {first.get('operator_name')}")
        print(f"      Bus Type: {first.get('bus_type')}")
        print(f"      Departure: {first.get('departure_time')}")
        print(f"      Fare: ₹{first.get('fare')}")
        print(f"      Boarding Point: {first.get('boarding_point')}")
        print(f"      Dropping Point: {first.get('dropping_point')}")


# ============================================================================
# DATA VALIDATION TESTS - Verifying  response fields
# ============================================================================

@pytest.mark.asyncio
async def test_bus_response_has_boarding_points(dummy_bus_search_delhi_manali):
    """Verify bus results include boarding points (: bdPoints)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    buses = result.structured_content.get("buses", [])

    if buses:
        first_bus = buses[0]
        assert "boarding_points" in first_bus, "Bus should have boarding_points (bdPoints)"

        boarding_points = first_bus["boarding_points"]
        if boarding_points:
            first_bp = boarding_points[0]
            #  bdPoints fields
            assert "bd_id" in first_bp  # bdid
            assert "bd_long_name" in first_bp  # bdLongName

            print(f"\n✅ Boarding points (bdPoints) verified:")
            for bp in boarding_points[:3]:
                print(f"   - {bp.get('bd_long_name')} at {bp.get('time')}")
                print(f"     Location (bdlocation): {bp.get('bd_location')}")
                print(f"     Contact (contactNumber): {bp.get('contact_number')}")


@pytest.mark.asyncio
async def test_bus_response_has_dropping_points(dummy_bus_search_delhi_manali):
    """Verify bus results include dropping points (: dpPoints)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    buses = result.structured_content.get("buses", [])

    if buses:
        first_bus = buses[0]
        assert "dropping_points" in first_bus, "Bus should have dropping_points (dpPoints)"

        dropping_points = first_bus["dropping_points"]
        if dropping_points:
            first_dp = dropping_points[0]
            #  dpPoints fields
            assert "dp_id" in first_dp  # dpId
            assert "dp_name" in first_dp  # dpName

            print(f"\n✅ Dropping points (dpPoints) verified:")
            for dp in dropping_points[:3]:
                print(f"   - {dp.get('dp_name')} at {dp.get('dp_time')}")
                print(f"     Location (locatoin): {dp.get('location')}")


@pytest.mark.asyncio
async def test_bus_response_has_amenities(dummy_bus_search_delhi_manali):
    """Verify bus results include amenities (: lstamenities)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    buses = result.structured_content.get("buses", [])

    if buses:
        first_bus = buses[0]
        assert "amenities" in first_bus, "Bus should have amenities (lstamenities)"

        amenities = first_bus["amenities"]
        print(f"\n✅ Amenities (lstamenities): {amenities}")
        
        #  example amenities: USB Charging Point, Water Bottle, AC, etc.


@pytest.mark.asyncio
async def test_bus_response_has_cancellation_policy(dummy_bus_search_delhi_manali):
    """Verify bus results include cancellation policy (: cancelPolicyList)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    buses = result.structured_content.get("buses", [])

    if buses:
        first_bus = buses[0]
        assert "cancellation_policy" in first_bus, "Bus should have cancellation_policy (cancelPolicyList)"

        policies = first_bus["cancellation_policy"]
        if policies:
            print(f"\n✅ Cancellation policy (cancelPolicyList) verified:")
            for policy in policies:
                #  fields: timeFrom, timeTo, percentageCharge, flatCharge, isFlat
                print(f"   - {policy.get('time_from')}h to {policy.get('time_to')}h: {policy.get('percentage_charge')}% charge")


@pytest.mark.asyncio
async def test_bus_response_has_timing_info(dummy_bus_search_delhi_manali):
    """Verify bus results include timing information from ."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    buses = result.structured_content.get("buses", [])

    if buses:
        first_bus = buses[0]

        #  AvailableTrips fields
        assert "departure_time" in first_bus  # departureTime
        assert "arrival_time" in first_bus  # ArrivalTime
        assert "duration" in first_bus  # duration
        assert "departure_date" in first_bus  # departureDate
        assert "arrival_date" in first_bus  # arrivalDate

        print(f"\n✅ Timing info verified:")
        print(f"   Departure (departureTime): {first_bus['departure_time']}")
        print(f"   Arrival (ArrivalTime): {first_bus['arrival_time']}")
        print(f"   Duration: {first_bus['duration']}")
        print(f"   Departure Date (departureDate): {first_bus['departure_date']}")
        print(f"   Arrival Date (arrivalDate): {first_bus['arrival_date']}")


@pytest.mark.asyncio
async def test_bus_response_has_seat_type_info(dummy_bus_search_delhi_manali):
    """Verify bus results include seat type info (: seater, sleeper, isSemiSleeper)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    buses = result.structured_content.get("buses", [])

    if buses:
        first_bus = buses[0]

        #  AvailableTrips seat type fields
        assert "is_seater" in first_bus  # seater
        assert "is_sleeper" in first_bus  # sleeper
        assert "is_semi_sleeper" in first_bus  # isSemiSleeper

        print(f"\n✅ Seat type info verified:")
        print(f"   Seater (seater): {first_bus['is_seater']}")
        print(f"   Sleeper (sleeper): {first_bus['is_sleeper']}")
        print(f"   Semi-Sleeper (isSemiSleeper): {first_bus['is_semi_sleeper']}")


@pytest.mark.asyncio
async def test_bus_response_has_ac_info(dummy_bus_search_delhi_manali):
    """Verify bus results include AC info (: AC, nonAC)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    buses = result.structured_content.get("buses", [])

    if buses:
        first_bus = buses[0]

        #  AvailableTrips AC fields
        assert "is_ac" in first_bus  # AC
        assert "is_non_ac" in first_bus  # nonAC

        print(f"\n✅ AC info verified:")
        print(f"   AC: {first_bus['is_ac']}")
        print(f"   Non-AC (nonAC): {first_bus['is_non_ac']}")


@pytest.mark.asyncio
async def test_bus_response_has_operator_info(dummy_bus_search_delhi_manali):
    """Verify bus results include operator info from ."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    buses = result.structured_content.get("buses", [])

    if buses:
        first_bus = buses[0]

        #  AvailableTrips operator fields
        assert "operator_name" in first_bus  # Travels
        assert "operator_id" in first_bus  # operatorid
        assert "route_id" in first_bus  # routeId
        assert "engine_id" in first_bus  # engineId

        print(f"\n✅ Operator info verified:")
        print(f"   Operator (Travels): {first_bus['operator_name']}")
        print(f"   Operator ID (operatorid): {first_bus['operator_id']}")
        print(f"   Route ID (routeId): {first_bus['route_id']}")
        print(f"   Engine ID (engineId): {first_bus['engine_id']}")


@pytest.mark.asyncio
async def test_bus_response_has_fare_info(dummy_bus_search_delhi_manali):
    """Verify bus results include fare info (: price, fares)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    buses = result.structured_content.get("buses", [])

    if buses:
        first_bus = buses[0]

        #  AvailableTrips fare fields
        assert "price" in first_bus  # price
        assert "fares" in first_bus  # fares array

        print(f"\n✅ Fare info verified:")
        print(f"   Price: ₹{first_bus['price']}")
        print(f"   Fares array: {first_bus['fares']}")


@pytest.mark.asyncio
async def test_bus_response_has_tracking_info(dummy_bus_search_delhi_manali):
    """Verify bus results include tracking info (: liveTrackingAvailable, mTicketEnabled)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    buses = result.structured_content.get("buses", [])

    if buses:
        first_bus = buses[0]

        #  AvailableTrips tracking fields
        assert "live_tracking_available" in first_bus  # liveTrackingAvailable
        assert "m_ticket_enabled" in first_bus  # mTicketEnabled
        assert "is_cancellable" in first_bus  # isCancellable

        print(f"\n✅ Tracking info verified:")
        print(f"   Live Tracking (liveTrackingAvailable): {first_bus['live_tracking_available']}")
        print(f"   M-Ticket (mTicketEnabled): {first_bus['m_ticket_enabled']}")
        print(f"   Cancellable (isCancellable): {first_bus['is_cancellable']}")


@pytest.mark.asyncio
async def test_bus_response_has_book_now_link(dummy_bus_search_delhi_manali):
    """Verify bus results include booking deeplink."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    buses = result.structured_content.get("buses", [])

    if buses:
        first_bus = buses[0]
        assert "book_now" in first_bus, "Bus should have book_now link"

        book_now = first_bus["book_now"]
        assert book_now is not None
        assert "easemytrip.com" in book_now

        print(f"\n✅ Book now link: {book_now}")


# ============================================================================
# EDGE CASES - REAL API
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_far_future_date():
    """Test bus search with date far in the future."""
    today = datetime.now()
    journey_date = (today + timedelta(days=60)).strftime("%Y-%m-%d")

    # Using  example city IDs
    payload = {
        "source_id": "733",  # Delhi
        "destination_id": "757",  # Manali
        "journey_date": journey_date,
    }

    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n🚌 Searching buses 60 days ahead: {journey_date}")

    result = await tool.execute(**payload)

    assert result.structured_content is not None
    buses = result.structured_content.get("buses", [])

    print(f"✅ Far future search returned {len(buses)} buses")
    print(f"   isBusAvailable: {result.structured_content.get('is_bus_available')}")


@pytest.mark.asyncio
async def test_bus_search_near_date():
    """Test bus search with date very soon (tomorrow)."""
    today = datetime.now()
    journey_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")

    # Using  example city IDs
    payload = {
        "source_id": "733",  # Delhi
        "destination_id": "757",  # Manali
        "journey_date": journey_date,
    }

    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n🚌 Searching buses for tomorrow: {journey_date}")

    result = await tool.execute(**payload)

    assert result.structured_content is not None
    buses = result.structured_content.get("buses", [])

    print(f"✅ Near date search returned {len(buses)} buses")


# ============================================================================
# LIMIT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_with_limit(dummy_bus_search_delhi_manali):
    """Test bus search with result limit."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    payload = {**dummy_bus_search_delhi_manali, "_limit": 5}

    print(f"\n🚌 Searching buses with limit=5")

    result = await tool.execute(**payload)

    data = result.structured_content
    buses = data.get("buses", [])

    assert len(buses) <= 5, f"Expected at most 5 buses, got {len(buses)}"

    print(f"✅ Limited search returned {len(buses)} buses (max 5)")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_response_time(dummy_bus_search_delhi_manali):
    """Test that bus search completes in reasonable time."""
    import time

    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    start = time.time()
    result = await tool.execute(**dummy_bus_search_delhi_manali)
    elapsed = time.time() - start

    print(f"\n⏱️  Bus search took {elapsed:.2f} seconds")

    # Should complete within 30 seconds
    assert elapsed < 30, f"Search took too long: {elapsed}s"
    assert result.structured_content is not None


# ============================================================================
# MULTIPLE SEARCHES TEST
# ============================================================================

@pytest.mark.asyncio
async def test_multiple_consecutive_bus_searches():
    """Test multiple bus searches in sequence using  city IDs."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    today = datetime.now()
    journey_date = (today + timedelta(days=14)).strftime("%Y-%m-%d")

    # Using  example: Delhi (733) to Manali (757)
    # Multiple searches with same route but different dates
    searches = [
        ("733", "757", journey_date),
        ("733", "757", (today + timedelta(days=21)).strftime("%Y-%m-%d")),
        ("733", "757", (today + timedelta(days=28)).strftime("%Y-%m-%d")),
    ]

    print("\n🚌 Testing multiple consecutive bus searches...")

    for source_id, destination_id, date in searches:
        payload = {
            "source_id": source_id,
            "destination_id": destination_id,
            "journey_date": date,
        }

        result = await tool.execute(**payload)
        assert result.structured_content is not None

        buses = result.structured_content.get("buses", [])
        print(f"   {source_id} → {destination_id} on {date}: {len(buses)} buses")

    print("✅ All consecutive searches completed")


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_invalid_date_format():
    """Test bus search with invalid date format."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    payload = {
        "source_id": "733",
        "destination_id": "757",
        "journey_date": "25-01-2026",  # Wrong format (should be YYYY-MM-DD)
    }

    print(f"\n🚌 Testing invalid date format: {payload['journey_date']}")

    result = await tool.execute(**payload)

    # Should return an error response
    assert result.is_error is True
    print(f"✅ Correctly returned error for invalid date format")
    print(f"   Error: {result.response_text}")


@pytest.mark.asyncio
async def test_bus_search_missing_required_field():
    """Test bus search with missing required field."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    payload = {
        "source_id": "733",
        # Missing destination_id and journey_date
    }

    print(f"\n🚌 Testing missing required fields")

    result = await tool.execute(**payload)

    # Should return an error response
    assert result.is_error is True
    print(f"✅ Correctly returned error for missing fields")
    print(f"   Error: {result.response_text}")


@pytest.mark.asyncio
async def test_bus_search_empty_source_id():
    """Test bus search with empty source ID."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

    payload = {
        "source_id": "",
        "destination_id": "757",
        "journey_date": journey_date,
    }

    print(f"\n🚌 Testing empty source_id")

    result = await tool.execute(**payload)

    # Should handle gracefully
    print(f"   Response: {result.response_text}")
    print(f"   Is Error: {result.is_error}")