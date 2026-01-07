"""Real API tests with dummy input payloads.

These tests make actual API calls and verify real responses.
NO MOCKING - Real API integration tests.

File: tool_factory/tests/test_tools_real_api.py

Run with:
    pytest tool_factory/tests/test_tools_real_api.py -v -s
    
Mark as integration tests:
    pytest -m integration
"""

import pytest
import json
from datetime import datetime, timedelta
from tools_factory.factory import get_tool_factory


# Mark all tests in this file as integration tests (slow)
pytestmark = pytest.mark.integration


# ============================================================================
# TEST FIXTURES - DUMMY PAYLOADS
# ============================================================================

@pytest.fixture
def dummy_flight_oneway():
    """Dummy payload for one-way flight search."""
    today = datetime.now()
    outbound = (today + timedelta(days=30)).strftime("%Y-%m-%d")  # 30 days from now
    
    return {
        "origin": "DEL",
        "destination": "BOM",
        "outbound_date": outbound,
        "adults": 1,
        "children": 0,
        "infants": 0
    }

@pytest.fixture
def dummy_flight_oneway_with_limit():
    """Dummy payload for one-way flight search."""
    today = datetime.now()
    outbound = (today + timedelta(days=30)).strftime("%Y-%m-%d")  # 30 days from now
    
    return {
        "origin": "DEL",
        "destination": "BOM",
        "outbound_date": outbound,
        "adults": 1,
        "children": 0,
        "infants": 0,
        "_limit": 2
    }

@pytest.fixture
def dummy_flight_roundtrip_with_limit():
    today = datetime.now()
    outbound = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    return_date = (today + timedelta(days=37)).strftime("%Y-%m-%d")

    return {
        "origin": "DEL",
        "destination": "BOM",
        "outbound_date": outbound,
        "return_date": return_date,
        "adults": 1,
        "_limit": 2
    }


@pytest.fixture
def dummy_flight_international_oneway_with_limit():
    today = datetime.now()
    outbound = (today + timedelta(days=30)).strftime("%Y-%m-%d")

    return {
        "origin": "DEL",
        "destination": "DXB",
        "outbound_date": outbound,
        "adults": 1,
        "_limit": 2
    }


@pytest.fixture
def dummy_flight_international_roundtrip_with_limit():
    today = datetime.now()
    outbound = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    return_date = (today + timedelta(days=37)).strftime("%Y-%m-%d")

    return {
        "origin": "DEL",
        "destination": "DXB",
        "outbound_date": outbound,
        "return_date": return_date,
        "adults": 1,
        "_limit": 2
    }


@pytest.fixture
def dummy_flight_roundtrip():
    """Dummy payload for round-trip flight search."""
    today = datetime.now()
    outbound = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    return_date = (today + timedelta(days=37)).strftime("%Y-%m-%d")  # 7 days later
    
    return {
        "origin": "DEL",
        "destination": "BOM",
        "outbound_date": outbound,
        "return_date": return_date,
        "adults": 2,
        "children": 1,
        "infants": 0
    }


@pytest.fixture
def dummy_flight_popular_route():
    """Dummy payload for popular route (likely to have results)."""
    today = datetime.now()
    outbound = (today + timedelta(days=21)).strftime("%Y-%m-%d")
    
    return {
        "origin": "BLR",  # Bangalore
        "destination": "DEL",  # Delhi
        "outbound_date": outbound,
        "adults": 1
    }


@pytest.fixture
def dummy_hotel_basic():
    """Dummy payload for basic hotel search."""
    today = datetime.now()
    checkin = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=32)).strftime("%Y-%m-%d")
    
    return {
        "city_name": "Mumbai",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 1,
        "num_adults": 2,
        "num_children": 0
    }


@pytest.fixture
def dummy_hotel_with_filters():
    """Dummy payload for hotel search with filters."""
    today = datetime.now()
    checkin = (today + timedelta(days=14)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=16)).strftime("%Y-%m-%d")
    
    return {
        "city_name": "Goa",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 2,
        "num_adults": 4,
        "num_children": 2,
        "min_price": 2000,
        "max_price": 10000,
        "rating": ["4", "5"],
        "amenities": ["Wi-Fi", "Swimming Pool"]
    }


# ============================================================================
# FLIGHT SEARCH TESTS - REAL API
# ============================================================================

@pytest.mark.asyncio
async def test_flight_search_oneway_real_api(dummy_flight_oneway):
    """Test one-way flight search with real API call."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")
    
    print(f"\n🔍 Searching flights: {dummy_flight_oneway}")
    
    result = await tool.execute(**dummy_flight_oneway)
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    
    # Verify response structure
    assert "text" in result
    assert "structured_content" in result
    
    print(f"✅ Response: {result['text']}")
    
    data = result["structured_content"]
    
    # Verify API response structure
    assert "outbound_flights" in data
    assert "is_roundtrip" in data
    assert data["is_roundtrip"] == False
    assert "origin" in data
    assert "destination" in data
    
    # Print results summary
    flights = data.get("outbound_flights", [])
    print(f"📊 Found {len(flights)} outbound flights")
    
    if flights:
        first_flight = flights[0]
        print(f"   First flight: {first_flight.get('origin')} → {first_flight.get('destination')}")
        print(f"   Stops: {first_flight.get('total_stops')}")
        print(f"   Journey time: {first_flight.get('journey_time')}")

@pytest.mark.asyncio
async def test_flight_search_oneway_real_api_with_limit(dummy_flight_oneway_with_limit):
    """Test one-way flight search with real API call."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")
    
    print(f"\n🔍 Searching flights: {dummy_flight_oneway_with_limit}")
    
    result = await tool.execute(**dummy_flight_oneway_with_limit)
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    
    # Verify response structure
    assert "text" in result
    assert "structured_content" in result
    
    print(f"✅ Response: {result['text']}")
    
    data = result["structured_content"]
    
    # Verify API response structure
    assert "outbound_flights" in data
    assert "is_roundtrip" in data
    assert data["is_roundtrip"] == False
    assert "origin" in data
    assert "destination" in data
    
    # Print results summary
    flights = data.get("outbound_flights", [])
    print(f"📊 Found {len(flights)} outbound flights")
    
    if flights:
        first_flight = flights[0]
        print(f"   First flight: {first_flight.get('origin')} → {first_flight.get('destination')}")
        print(f"   Stops: {first_flight.get('total_stops')}")
        print(f"   Journey time: {first_flight.get('journey_time')}")

@pytest.mark.asyncio
async def test_flight_search_roundtrip_real_api_with_limit(dummy_flight_roundtrip_with_limit):
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")

    print(f"\n🔍 Searching round-trip flights with limit: {dummy_flight_roundtrip_with_limit}")

    result = await tool.execute(**dummy_flight_roundtrip_with_limit)

    data = result["structured_content"]

    assert data["is_roundtrip"] is True
    assert len(data.get("outbound_flights", [])) <= 2
    assert len(data.get("return_flights", [])) <= 2

    print("✅ Roundtrip limit applied correctly")


@pytest.mark.asyncio
async def test_flight_search_international_oneway_with_limit(dummy_flight_international_oneway_with_limit):
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")

    print(f"\n🌍 Searching international oneway with limit: {dummy_flight_international_oneway_with_limit}")

    result = await tool.execute(**dummy_flight_international_oneway_with_limit)

    data = result["structured_content"]

    assert data["is_roundtrip"] is False
    assert len(data.get("outbound_flights", [])) <= 2

    print("✅ International oneway limit applied")


@pytest.mark.asyncio
async def test_flight_search_international_roundtrip_with_limit(dummy_flight_international_roundtrip_with_limit):
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")

    print(f"\n🌍 Searching international roundtrip with limit: {dummy_flight_international_roundtrip_with_limit}")

    result = await tool.execute(**dummy_flight_international_roundtrip_with_limit)

    data = result["structured_content"]

    assert data["is_roundtrip"] is True
    assert len(data.get("outbound_flights", [])) <= 2
    assert len(data.get("return_flights", [])) <= 2

    print("✅ International roundtrip limit applied")

#HTML tests

@pytest.mark.asyncio
async def test_flight_search_oneway_real_api_with_html(dummy_flight_oneway):
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")

    payload = {**dummy_flight_oneway, "_html": True}

    result = await tool.execute(**payload)

    assert result["html"] is not None
    assert "flight-card" in result["html"]

    print("✅ Oneway HTML rendered")


@pytest.mark.asyncio
async def test_flight_search_roundtrip_real_api_with_html(dummy_flight_roundtrip):
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")

    payload = {**dummy_flight_roundtrip, "_html": True}

    result = await tool.execute(**payload)

    assert result["html"] is not None
    assert "flight-card" in result["html"]

    print("✅ Roundtrip HTML rendered")
'''
@pytest.mark.asyncio
async def test_flight_search_international_oneway_with_html(
    dummy_flight_international_oneway_with_limit
):
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")

    payload = {
        k: v for k, v in dummy_flight_international_oneway_with_limit.items()
        if k != "_limit"
    }
    payload["_html"] = True

    result = await tool.execute(**payload)

    assert result["html"] is not None

    html = result["html"]

    if "flight-card" in html:
        assert "flight-card" in html
    else:
        assert "No flights available" in html
'''
@pytest.mark.asyncio
async def test_flight_search_international_oneway_with_html(dummy_flight_international_oneway_with_limit):
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")

    payload = {k: v for k, v in dummy_flight_international_oneway_with_limit.items() if k != "_limit"}
    payload["_html"] = True

    result = await tool.execute(**payload)

    assert result["html"] is not None
    assert "flight-card" in result["html"]

    print("✅ International oneway HTML rendered")


@pytest.mark.asyncio
async def test_flight_search_international_roundtrip_with_html(dummy_flight_international_roundtrip_with_limit):
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")

    payload = {k: v for k, v in dummy_flight_international_roundtrip_with_limit.items() if k != "_limit"}
    payload["_html"] = True

    result = await tool.execute(**payload)

    assert result["html"] is not None
    assert "flight-card" in result["html"]

    print("✅ International roundtrip HTML rendered")


@pytest.mark.asyncio
async def test_flight_search_roundtrip_real_api(dummy_flight_roundtrip):
    """Test round-trip flight search with real API call."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")
    
    print(f"\n🔍 Searching round-trip flights: {dummy_flight_roundtrip}")
    
    result = await tool.execute(**dummy_flight_roundtrip)
    
    assert "structured_content" in result
    data = result["structured_content"]
    
    # Verify round-trip structure
    assert data["is_roundtrip"] == True
    assert "outbound_flights" in data
    assert "return_flights" in data
    
    # Print results
    outbound_count = len(data.get("outbound_flights", []))
    return_count = len(data.get("return_flights", []))
    
    print(f"✅ Found {outbound_count} outbound, {return_count} return flights")


@pytest.mark.asyncio
async def test_flight_search_popular_route(dummy_flight_popular_route):
    """Test flight search on popular route (should have many results)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")
    
    print(f"\n🔍 Searching popular route: {dummy_flight_popular_route}")
    
    result = await tool.execute(**dummy_flight_popular_route)
    
    data = result["structured_content"]
    flights = data.get("outbound_flights", [])
    
    # Popular routes should have results
    print(f"📊 Found {len(flights)} flights on popular route")
    
    # Verify we got some results
    assert len(flights) > 0, "Popular route should return flights"
    
    # Print first 3 flights details
    for i, flight in enumerate(flights[:3], 1):
        print(f"\n   Flight {i}:")
        print(f"      Journey: {flight.get('journey_time')}")
        print(f"      Stops: {flight.get('total_stops')}")
        print(f"      Refundable: {flight.get('is_refundable')}")
        
        # Print fare if available
        fares = flight.get("fare_options", [])
        if fares:
            cheapest = fares[0]
            print(f"      Fare: ₹{cheapest.get('total_fare')}")


@pytest.mark.asyncio
async def test_flight_search_with_multiple_passengers():
    """Test flight search with family (multiple passengers)."""
    today = datetime.now()
    outbound = (today + timedelta(days=45)).strftime("%Y-%m-%d")
    
    payload = {
        "origin": "BOM",
        "destination": "GOI",  # Mumbai to Goa
        "outbound_date": outbound,
        "adults": 2,
        "children": 2,
        "infants": 1
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")
    
    print(f"\n🔍 Searching flights for family: {payload}")
    
    result = await tool.execute(**payload)
    
    assert "structured_content" in result
    data = result["structured_content"]
    
    flights = data.get("outbound_flights", [])
    print(f"✅ Found {len(flights)} flights for 2 adults, 2 children, 1 infant")


# ============================================================================
# HOTEL SEARCH TESTS - REAL API
# ============================================================================

# @pytest.mark.asyncio
# async def test_hotel_search_basic_real_api(dummy_hotel_basic):
#     """Test basic hotel search with real API call."""
#     factory = get_tool_factory()
#     tool = factory.get_tool("search_hotels")
    
#     print(f"\n🔍 Searching hotels: {dummy_hotel_basic}")
    
#     result = await tool.execute(**dummy_hotel_basic)
    
#     # Verify response structure
#     assert "text" in result
#     assert "structured_content" in result
    
#     print(f"✅ Response: {result['text']}")
    
#     data = result["structured_content"]
    
#     # Verify structure (exact fields depend on your hotel_search implementation)
#     assert "hotels" in data or "results" in data
    
#     print(f"📊 Hotel search completed for {dummy_hotel_basic['city_name']}")


# @pytest.mark.asyncio
# async def test_hotel_search_with_filters_real_api(dummy_hotel_with_filters):
#     """Test hotel search with filters (rating, amenities)."""
#     factory = get_tool_factory()
#     tool = factory.get_tool("search_hotels")
    
#     print(f"\n🔍 Searching hotels with filters: {dummy_hotel_with_filters}")
    
#     result = await tool.execute(**dummy_hotel_with_filters)
    
#     assert "structured_content" in result
#     data = result["structured_content"]
    
#     print(f"✅ Hotel search with filters completed")
#     print(f"   City: {dummy_hotel_with_filters['city_name']}")
#     print(f"   Rating filter: {dummy_hotel_with_filters['rating']}")
#     print(f"   Amenities: {dummy_hotel_with_filters['amenities']}")


# ============================================================================
# EDGE CASES - REAL API
# ============================================================================

@pytest.mark.asyncio
async def test_flight_search_far_future_date():
    """Test flight search with date far in the future."""
    today = datetime.now()
    outbound = (today + timedelta(days=180)).strftime("%Y-%m-%d")  # 6 months
    
    payload = {
        "origin": "DEL",
        "destination": "BOM",
        "outbound_date": outbound,
        "adults": 1
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")
    
    print(f"\n🔍 Searching flights 6 months ahead: {outbound}")
    
    result = await tool.execute(**payload)
    
    # Should handle gracefully (may or may not have results)
    assert "structured_content" in result
    
    flights = result["structured_content"].get("outbound_flights", [])
    print(f"✅ Far future search returned {len(flights)} flights")


@pytest.mark.asyncio
async def test_flight_search_near_date():
    """Test flight search with date very soon (within 3 days)."""
    today = datetime.now()
    outbound = (today + timedelta(days=3)).strftime("%Y-%m-%d")
    
    payload = {
        "origin": "DEL",
        "destination": "BOM",
        "outbound_date": outbound,
        "adults": 1
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")
    
    print(f"\n🔍 Searching flights in 3 days: {outbound}")
    
    result = await tool.execute(**payload)
    
    assert "structured_content" in result
    flights = result["structured_content"].get("outbound_flights", [])
    
    # Near date might have fewer flights
    print(f"✅ Near date search returned {len(flights)} flights")


@pytest.mark.asyncio
async def test_flight_search_uncommon_route():
    """Test flight search on less common route."""
    today = datetime.now()
    outbound = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    
    payload = {
        "origin": "IXC",  # Chandigarh
        "destination": "CCU",  # Kolkata
        "outbound_date": outbound,
        "adults": 1
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")
    
    print(f"\n🔍 Searching uncommon route: {payload['origin']} → {payload['destination']}")
    
    result = await tool.execute(**payload)
    
    assert "structured_content" in result
    flights = result["structured_content"].get("outbound_flights", [])
    
    print(f"✅ Uncommon route returned {len(flights)} flights")


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_flight_response_has_deeplinks(dummy_flight_oneway):
    """Verify flight results include deeplinks."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")
    
    result = await tool.execute(**dummy_flight_oneway)
    flights = result["structured_content"].get("outbound_flights", [])
    
    if flights:
        first_flight = flights[0]
        assert "deepLink" in first_flight, "Flight should have deepLink"
        assert first_flight["deepLink"].startswith("http"), "deepLink should be URL"
        
        print(f"\n✅ DeepLink verified: {first_flight['deepLink'][:50]}...")


@pytest.mark.asyncio
async def test_flight_response_has_fare_options(dummy_flight_oneway):
    """Verify flight results include fare options."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")
    
    result = await tool.execute(**dummy_flight_oneway)
    flights = result["structured_content"].get("outbound_flights", [])
    
    if flights:
        first_flight = flights[0]
        assert "fare_options" in first_flight, "Flight should have fare_options"
        
        fares = first_flight["fare_options"]
        if fares:
            first_fare = fares[0]
            assert "total_fare" in first_fare
            assert "base_fare" in first_fare
            
            print(f"\n✅ Fare data verified: ₹{first_fare.get('total_fare')}")


@pytest.mark.asyncio
async def test_flight_response_has_legs(dummy_flight_oneway):
    """Verify flight results include leg details."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")
    
    result = await tool.execute(**dummy_flight_oneway)
    flights = result["structured_content"].get("outbound_flights", [])
    
    if flights:
        first_flight = flights[0]
        assert "legs" in first_flight, "Flight should have legs"
        
        legs = first_flight["legs"]
        assert len(legs) > 0, "Should have at least one leg"
        
        first_leg = legs[0]
        assert "airline_code" in first_leg
        assert "flight_number" in first_leg
        assert "origin" in first_leg
        assert "destination" in first_leg
        
        print(f"\n✅ Leg data verified: {first_leg['airline_code']} {first_leg['flight_number']}")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_flight_search_response_time(dummy_flight_oneway):
    """Test that flight search completes in reasonable time."""
    import time
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")
    
    start = time.time()
    result = await tool.execute(**dummy_flight_oneway)
    elapsed = time.time() - start
    
    print(f"\n⏱️  Flight search took {elapsed:.2f} seconds")
    
    # Should complete within 60 seconds
    assert elapsed < 60, f"Search took too long: {elapsed}s"
    assert "structured_content" in result


# ============================================================================
# MULTIPLE SEARCHES TEST
# ============================================================================

@pytest.mark.asyncio
async def test_multiple_consecutive_searches():
    """Test multiple searches in sequence (like a real user)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")
    
    today = datetime.now()
    
    routes = [
        ("DEL", "BOM"),
        ("BOM", "DEL"),
        ("BLR", "HYD"),
    ]
    
    print("\n🔍 Testing multiple consecutive searches...")
    
    for origin, destination in routes:
        outbound = (today + timedelta(days=30)).strftime("%Y-%m-%d")
        
        payload = {
            "origin": origin,
            "destination": destination,
            "outbound_date": outbound,
            "adults": 1
        }
        
        result = await tool.execute(**payload)
        assert "structured_content" in result
        
        flights = result["structured_content"].get("outbound_flights", [])
        print(f"   {origin} → {destination}: {len(flights)} flights")
    
    print("✅ All consecutive searches completed")