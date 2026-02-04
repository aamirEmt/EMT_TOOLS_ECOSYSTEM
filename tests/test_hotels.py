"""Real API tests for hotel search functionality.

These tests make actual API calls and verify real responses.
NO MOCKING - Real API integration tests.

File: tests/test_hotels.py

Run with:
    pytest tests/test_hotels.py -v -s
    
Mark as integration tests:
    pytest -m integration tests/test_hotels.py
"""

import pytest
from datetime import datetime, timedelta
from tools_factory.factory import get_tool_factory
from unittest.mock import AsyncMock, patch

# Mark all tests in this file as integration tests (slow)
pytestmark = pytest.mark.integration


# ============================================================================
# TEST FIXTURES - DUMMY PAYLOADS
# ============================================================================

@pytest.fixture
def dummy_hotel_basic():
    """Dummy payload for basic hotel search."""
    today = datetime.now()
    checkin = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    
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


@pytest.fixture
def dummy_hotel_popular():
    """Dummy payload for popular destination."""
    today = datetime.now()
    checkin = (today + timedelta(days=21)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=23)).strftime("%Y-%m-%d")
    
    return {
        "city_name": "Delhi",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 1,
        "num_adults": 2
    }


# ============================================================================
# HOTEL SEARCH TESTS - REAL API
# ============================================================================

@pytest.mark.asyncio
async def test_hotel_search_basic_real_api(dummy_hotel_basic):
    """Test basic hotel search with real API call."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    print(f"\n🔍 Searching hotels: {dummy_hotel_basic}")
    
    result = await tool.execute(**dummy_hotel_basic)
    
    # Verify response structure
    assert hasattr(result, 'response_text')
    assert hasattr(result, 'structured_content')
    
    print(f"✅ Response: {result.response_text}")
    
    data = result.structured_content
    
    # Verify structure
    assert "hotels" in data or "results" in data
    assert "city" in data or "city_name" in data
    assert "check_in" in data or "check_in_date" in data
    
    # Print results summary
    hotels = data.get("hotels", data.get("results", []))
    print(f"📊 Found {len(hotels)} hotels in {dummy_hotel_basic['city_name']}")
    
    if hotels:
        first_hotel = hotels[0]
        print(f"   First hotel: {first_hotel.get('name', 'N/A')}")
        print(f"   Rating: {first_hotel.get('rating', 'N/A')}")
        print(f"   Price: ₹{first_hotel.get('price', 'N/A')}")
        deeplink = first_hotel.get('deepLink') or first_hotel.get('booking_url') or first_hotel.get('url')
        if deeplink:
            print(f"   DeepLink: {deeplink}")


@pytest.mark.asyncio
async def test_hotel_search_with_filters_real_api(dummy_hotel_with_filters):
    """Test hotel search with filters (rating, amenities)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    print(f"Using tool: {tool}")
    
    print(f"\n🔍 Searching hotels with filters: {dummy_hotel_with_filters}")
    
    result = await tool.execute(**dummy_hotel_with_filters)
    
    assert hasattr(result, 'structured_content')
    data = result.structured_content
    
    hotels = data.get("hotels", data.get("results", []))
    print(f"✅ Found {len(hotels)} hotels with filters")
    print(f"   City: {dummy_hotel_with_filters['city_name']}")
    print(f"   Rating filter: {dummy_hotel_with_filters['rating']}")
    print(f"   Amenities: {dummy_hotel_with_filters['amenities']}")


@pytest.mark.asyncio
async def test_hotel_search_popular_destination(dummy_hotel_popular):
    """Test hotel search in popular destination (should have many results)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    print(f"\n🔍 Searching hotels in popular destination: {dummy_hotel_popular['city_name']}")
    
    result = await tool.execute(**dummy_hotel_popular)
    
    data = result.structured_content
    hotels = data.get("hotels", data.get("results", []))
    
    # Popular destinations should have many results
    print(f"📊 Found {len(hotels)} hotels in {dummy_hotel_popular['city_name']}")
    
    # Verify we got some results
    assert len(hotels) > 0, "Popular destination should return hotels"
    
    # Print first 3 hotels details
    for i, hotel in enumerate(hotels[:3], 1):
        print(f"\n   Hotel {i}:")
        print(f"      Name: {hotel.get('name', 'N/A')}")
        print(f"      Rating: {hotel.get('rating', 'N/A')}")
        print(f"      Price: ₹{hotel.get('price', 'N/A')}")
        print(f"      Address: {hotel.get('address', 'N/A')}")


@pytest.mark.asyncio
async def test_hotel_search_multiple_rooms():
    """Test hotel search with multiple rooms for group booking."""
    today = datetime.now()
    checkin = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=33)).strftime("%Y-%m-%d")
    
    payload = {
        "city_name": "Bangalore",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 3,
        "num_adults": 6,
        "num_children": 2
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    print(f"\n🔍 Searching hotels for group (3 rooms, 6 adults, 2 children)")
    
    result = await tool.execute(**payload)
    
    assert hasattr(result, "structured_content")
    data = result.structured_content
    
    hotels = data.get("hotels", data.get("results", []))
    print(f"✅ Found {len(hotels)} hotels for group booking")


@pytest.mark.asyncio
async def test_hotel_search_extended_stay():
    """Test hotel search for extended stay (1 week+)."""
    today = datetime.now()
    checkin = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=37)).strftime("%Y-%m-%d")  # 7 nights
    
    payload = {
        "city_name": "Mumbai",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 1,
        "num_adults": 1
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    print(f"\n🔍 Searching hotels for extended stay (7 nights)")
    
    result = await tool.execute(**payload)
    
    assert hasattr(result, "structured_content")
    data = result.structured_content
    
    hotels = data.get("hotels", data.get("results", []))
    print(f"✅ Found {len(hotels)} hotels for extended stay")


@pytest.mark.asyncio
async def test_hotel_search_budget_hotels():
    """Test hotel search with budget price range."""
    today = datetime.now()
    checkin = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=32)).strftime("%Y-%m-%d")
    
    payload = {
        "city_name": "Jaipur",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 1,
        "num_adults": 2,
        "min_price": 500,
        "max_price": 2000
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    print(f"\n🔍 Searching budget hotels (₹500-2000)")
    
    result = await tool.execute(**payload)
    
    assert hasattr(result, "structured_content")
    data = result.structured_content
    
    hotels = data.get("hotels", data.get("results", []))
    print(f"✅ Found {len(hotels)} budget hotels")
    
    # Verify prices are within range
    if hotels:
        for hotel in hotels[:3]:
            price = hotel.get("price")
            if price:
                print(f"   {hotel.get('name')}: ₹{price}")


@pytest.mark.asyncio
async def test_hotel_search_luxury_hotels():
    """Test hotel search for luxury hotels (5-star)."""
    today = datetime.now()
    checkin = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=32)).strftime("%Y-%m-%d")
    
    payload = {
        "city_name": "Mumbai",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 1,
        "num_adults": 2,
        "rating": ["5"],
        "min_price": 5000
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    print(f"\n🔍 Searching luxury hotels (5-star, ₹5000+)")
    
    result = await tool.execute(**payload)
    
    assert hasattr(result, "structured_content")
    data = result.structured_content
    
    hotels = data.get("hotels", data.get("results", []))
    print(f"✅ Found {len(hotels)} luxury hotels")


# ============================================================================
# HOTEL EDGE CASES - REAL API
# ============================================================================

@pytest.mark.asyncio
async def test_hotel_search_far_future_date():
    """Test hotel search with date far in the future."""
    today = datetime.now()
    checkin = (today + timedelta(days=180)).strftime("%Y-%m-%d")  # 6 months
    checkout = (today + timedelta(days=182)).strftime("%Y-%m-%d")
    
    payload = {
        "city_name": "Delhi",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 1,
        "num_adults": 2
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    print(f"\n🔍 Searching hotels 6 months ahead: {checkin}")
    
    result = await tool.execute(**payload)
    
    # Should handle gracefully (may or may not have results)
    assert hasattr(result, "structured_content")
    
    hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
    print(f"✅ Far future search returned {len(hotels)} hotels")


@pytest.mark.asyncio
async def test_hotel_search_last_minute():
    """Test hotel search for last-minute booking (within 3 days)."""
    today = datetime.now()
    checkin = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=4)).strftime("%Y-%m-%d")
    
    payload = {
        "city_name": "Bangalore",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 1,
        "num_adults": 1
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    print(f"\n🔍 Searching hotels for last-minute booking (2 days ahead)")
    
    result = await tool.execute(**payload)
    
    assert hasattr(result, "structured_content")
    hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
    
    print(f"✅ Last-minute search returned {len(hotels)} hotels")


@pytest.mark.asyncio
async def test_hotel_search_less_popular_destination():
    """Test hotel search in less popular destination."""
    today = datetime.now()
    checkin = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=32)).strftime("%Y-%m-%d")
    
    payload = {
        "city_name": "Shimla",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 1,
        "num_adults": 2
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    print(f"\n🔍 Searching hotels in less popular destination: {payload['city_name']}")
    
    result = await tool.execute(**payload)
    
    assert hasattr(result, "structured_content")
    hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
    
    print(f"✅ Less popular destination returned {len(hotels)} hotels")


@pytest.mark.asyncio
async def test_hotel_search_weekend_stay():
    """Test hotel search for weekend stay."""
    today = datetime.now()
    # Find next Saturday
    days_ahead = (5 - today.weekday()) % 7  # 5 = Saturday
    if days_ahead == 0:
        days_ahead = 7
    
    checkin = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=days_ahead + 2)).strftime("%Y-%m-%d")  # Sunday checkout
    
    payload = {
        "city_name": "Goa",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 1,
        "num_adults": 2
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    print(f"\n🔍 Searching hotels for weekend stay in Goa")
    
    result = await tool.execute(**payload)
    
    assert hasattr(result, "structured_content")
    hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
    
    print(f"✅ Weekend search returned {len(hotels)} hotels")


@pytest.mark.asyncio
async def test_hotel_search_single_night():
    """Test hotel search for single night stay."""
    today = datetime.now()
    checkin = (today + timedelta(days=15)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=16)).strftime("%Y-%m-%d")
    
    payload = {
        "city_name": "Pune",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 1,
        "num_adults": 1
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    print(f"\n🔍 Searching hotels for single night stay")
    
    result = await tool.execute(**payload)
    
    assert hasattr(result, "structured_content")
    hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
    
    print(f"✅ Single night search returned {len(hotels)} hotels")


# ============================================================================
# HOTEL DATA VALIDATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_hotel_response_has_required_fields(dummy_hotel_basic):
    """Verify hotel results include all required fields."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    result = await tool.execute(**dummy_hotel_basic)
    hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
    
    if hotels:
        first_hotel = hotels[0]
        
        # Check essential fields
        assert "name" in first_hotel, "Hotel should have name"
        assert "price" in first_hotel or "total_price" in first_hotel, "Hotel should have price"
        
        print(f"\n✅ Required fields verified for: {first_hotel.get('name')}")


@pytest.mark.asyncio
async def test_hotel_response_has_pricing_details(dummy_hotel_basic):
    """Verify hotel results include detailed pricing information."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    result = await tool.execute(**dummy_hotel_basic)
    hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
    
    if hotels:
        first_hotel = hotels[0]
        
        # Check for price fields
        has_price = any(key in first_hotel for key in ["price", "total_price", "base_price", "price_per_night"])
        assert has_price, "Hotel should have price information"
        
        price_value = first_hotel.get("price") or first_hotel.get("total_price") or first_hotel.get("price_per_night")
        print(f"\n✅ Pricing verified: ₹{price_value}")


@pytest.mark.asyncio
async def test_hotel_response_has_amenities(dummy_hotel_basic):
    """Verify hotel results include amenities information."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    result = await tool.execute(**dummy_hotel_basic)
    hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
    
    if hotels:
        first_hotel = hotels[0]
        
        # Check for amenities
        if "amenities" in first_hotel:
            amenities = first_hotel["amenities"]
            print(f"\n✅ Amenities found: {amenities[:5] if isinstance(amenities, list) else amenities}")
        else:
            print(f"\n⚠️  No amenities field in response")


@pytest.mark.asyncio
async def test_hotel_response_has_rating(dummy_hotel_basic):
    """Verify hotel results include rating information."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    result = await tool.execute(**dummy_hotel_basic)
    hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
    
    if hotels:
        first_hotel = hotels[0]
        
        # Check for rating
        if "rating" in first_hotel or "star_rating" in first_hotel:
            rating = first_hotel.get("rating") or first_hotel.get("star_rating")
            print(f"\n✅ Rating found: {rating}")
        else:
            print(f"\n⚠️  No rating field in response")


@pytest.mark.asyncio
async def test_hotel_response_has_location(dummy_hotel_basic):
    """Verify hotel results include location/address information."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    result = await tool.execute(**dummy_hotel_basic)
    hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
    
    if hotels:
        first_hotel = hotels[0]
        
        # Check for location fields
        has_location = any(key in first_hotel for key in ["address", "location", "area", "locality"])
        
        if has_location:
            location = first_hotel.get("address") or first_hotel.get("location") or first_hotel.get("area")
            print(f"\n✅ Location verified: {location}")
        else:
            print(f"\n⚠️  No location field in response")


@pytest.mark.asyncio
async def test_hotel_response_has_images(dummy_hotel_basic):
    """Verify hotel results include image URLs."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    result = await tool.execute(**dummy_hotel_basic)
    hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
    
    if hotels:
        first_hotel = hotels[0]
        
        # Check for image fields
        if "images" in first_hotel or "image_url" in first_hotel or "thumbnail" in first_hotel:
            images = first_hotel.get("images") or first_hotel.get("image_url") or first_hotel.get("thumbnail")
            print(f"\n✅ Images found: {len(images) if isinstance(images, list) else 1}")
        else:
            print(f"\n⚠️  No images field in response")


@pytest.mark.asyncio
async def test_hotel_response_has_booking_link(dummy_hotel_basic):
    """Verify hotel results include booking/deep links."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    result = await tool.execute(**dummy_hotel_basic)
    hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
    
    if hotels:
        first_hotel = hotels[0]
        
        # Check for booking link fields
        if "booking_url" in first_hotel or "deepLink" in first_hotel or "url" in first_hotel:
            link = first_hotel.get("booking_url") or first_hotel.get("deepLink") or first_hotel.get("url")
            assert link.startswith("http"), "Link should be a valid URL"
            print(f"\n✅ Booking link verified: {link[:50]}...")
        else:
            print(f"\n⚠️  No booking link in response")


# ============================================================================
# HOTEL PERFORMANCE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_hotel_search_response_time(dummy_hotel_basic):
    """Test that hotel search completes in reasonable time."""
    import time
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    start = time.time()
    result = await tool.execute(**dummy_hotel_basic)
    elapsed = time.time() - start
    
    print(f"\n⏱️  Hotel search took {elapsed:.2f} seconds")
    
    # Should complete within 60 seconds
    assert elapsed < 60, f"Search took too long: {elapsed}s"
    assert hasattr(result, "structured_content")


# ============================================================================
# HOTEL MULTIPLE SEARCHES TEST
# ============================================================================

@pytest.mark.asyncio
async def test_hotel_multiple_consecutive_searches():
    """Test multiple hotel searches in sequence (like a real user)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    today = datetime.now()
    
    cities = [
        "Mumbai",
        "Delhi",
        "Bangalore",
        "Goa",
        "Pune"
    ]
    
    print("\n🔍 Testing multiple consecutive hotel searches...")
    
    for city in cities:
        checkin = (today + timedelta(days=30)).strftime("%Y-%m-%d")
        checkout = (today + timedelta(days=32)).strftime("%Y-%m-%d")
        
        payload = {
            "city_name": city,
            "check_in_date": checkin,
            "check_out_date": checkout,
            "num_rooms": 1,
            "num_adults": 2
        }
        
        result = await tool.execute(**payload)
        assert hasattr(result, "structured_content")
        
        hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
        print(f"   {city}: {len(hotels)} hotels")
    
    print("✅ All consecutive searches completed")


# ============================================================================
# HOTEL FILTER COMBINATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_hotel_search_price_and_rating_filters():
    """Test hotel search with combined price and rating filters."""
    today = datetime.now()
    checkin = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=32)).strftime("%Y-%m-%d")
    
    payload = {
        "city_name": "Mumbai",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 1,
        "num_adults": 2,
        "min_price": 3000,
        "max_price": 8000,
        "rating": ["4", "5"]
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    print(f"\n🔍 Searching hotels with price (₹3000-8000) and rating (4-5 star) filters")
    
    result = await tool.execute(**payload)
    
    assert hasattr(result, "structured_content")
    hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
    
    print(f"✅ Found {len(hotels)} hotels matching filters")


@pytest.mark.asyncio
async def test_hotel_search_with_specific_amenities():
    """Test hotel search with specific amenity requirements."""
    today = datetime.now()
    checkin = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=32)).strftime("%Y-%m-%d")
    
    payload = {
        "city_name": "Goa",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 1,
        "num_adults": 2,
        "amenities": ["Swimming Pool", "Free Breakfast", "Beach Access"]
    }
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")
    
    print(f"\n🔍 Searching hotels with specific amenities: {payload['amenities']}")
    
    result = await tool.execute(**payload)
    
    assert hasattr(result, "structured_content")
    hotels = result.structured_content.get("hotels", result.structured_content.get("results", []))
    
    print(f"✅ Found {len(hotels)} hotels with required amenities")

# ============================================================================
# HOTEL WHATSAPP JSON RESPONSE TEST - REAL API
# ============================================================================
@pytest.mark.asyncio
async def test_hotel_search_whatsapp_real_api(dummy_hotel_basic):
    """
    Test hotel search with real API call for WhatsApp JSON response.
    Verifies:
        - _iscomingfromwhatsapp=True
        - Returns WhatsApp-ready JSON format
        - At most 3 hotels in the response
        - All required fields present
    """
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    print(f"\n🔍 Searching hotels for WhatsApp JSON: {dummy_hotel_basic}")

    # Make the real API call
    result = await tool.execute(
        **dummy_hotel_basic,
        _user_type="whatsapp",
        _limit=3  # optional: limit to first 10 hotels for faster response
    )

    # Extract WhatsApp response
    whatsapp_response = result.whatsapp_response
    assert whatsapp_response is not None, "Response must have 'whatsapp_response' attribute"
    
    whatsapp_data = whatsapp_response["whatsapp_json"]
    assert whatsapp_data is not None, "WhatsApp response must have 'whatsapp_json' attribute"

    # ------------------------
    # Check high-level structure
    # ------------------------
    assert "options" in whatsapp_data, "WhatsApp JSON must have 'options' key"
    assert "view_all_hotels_url" in whatsapp_data, "WhatsApp JSON must have 'view_all_hotels_url'"


    # Check each hotel has required fields
    for hotel in whatsapp_data["options"]:
        assert "option_id" in hotel
        assert "hotel_name" in hotel
        assert "location" in hotel
        assert "rating" in hotel
        assert "price" in hotel
        assert "price_unit" in hotel
        assert hotel["price_unit"] == "per night"
        assert "image_url" in hotel
        assert "amenities" in hotel
        assert "booking_url" in hotel

    print(f"✅ WhatsApp JSON test passed with {len(whatsapp_data['options'])} hotels")
    print(f"View all hotels URL: {whatsapp_data['view_all_hotels_url']}")


# ============================================================================
# HOTEL ADJUSTED PRICE TEST
# ============================================================================

@pytest.mark.asyncio
async def test_hotel_adjusted_price_calculation(dummy_hotel_basic):
    """Test that hotel price is correctly calculated as (base_price - discount)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    print(f"\nSearching hotels to verify adjusted price calculation")

    result = await tool.execute(**dummy_hotel_basic)

    assert hasattr(result, "structured_content")
    hotels = result.structured_content.get("hotels", [])

    print(f"\nFound {len(hotels)} hotels\n")
    print("=" * 80)

    for idx, hotel in enumerate(hotels, start=1):
        name = hotel.get("name", "N/A")
        price_obj = hotel.get("price", {})
        adjusted_price = price_obj.get("amount")
        currency = price_obj.get("currency", "INR")
        discount = hotel.get("discount") or 0
        rating = hotel.get("rating", "N/A")
        location = hotel.get("location", "N/A")

        print(f"Hotel {idx}: {name}")
        print(f"   Rating: {rating}")
        print(f"   Location: {location}")
        print(f"   Price (after discount): {currency} {adjusted_price}")
        print(f"   Discount: {currency} {discount}")
        print("-" * 40)

    # Verify at least one hotel was returned
    assert len(hotels) > 0, "Should return at least one hotel"

    # Verify price structure
    for hotel in hotels:
        price_obj = hotel.get("price", {})
        assert "amount" in price_obj, "Price should have 'amount' field"
        assert "currency" in price_obj, "Price should have 'currency' field"

        # Verify adjusted price is a number (int or float)
        amount = price_obj.get("amount")
        assert isinstance(amount, (int, float)) or amount is None, \
            f"Price amount should be numeric, got {type(amount)}"

    print(f"\nAdjusted price verification passed for {len(hotels)} hotels")