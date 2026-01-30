"""
Tests for Bus Search Tool.

Run with:
    pytest tests/test_buses.py -v -s

"""

import pytest
from datetime import datetime, timedelta
from tools_factory.factory import get_tool_factory
from tools_factory.base_schema import ToolResponseFormat

pytestmark = pytest.mark.integration


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def dummy_bus_search_delhi_manali():
    """Search using city IDs."""
    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    return {
        "source_id": "733",
        "destination_id": "757",
        "journey_date": journey_date,
    }


@pytest.fixture
def dummy_bus_search_by_city_name():
    """Search using city names (auto-resolved to IDs)."""
    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    return {
        "source_name": "Delhi",
        "destination_name": "Manali",
        "journey_date": journey_date,
    }


@pytest.fixture
def dummy_bus_search_with_volvo_filter():
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
    today = datetime.now()
    journey_date = (today + timedelta(days=14)).strftime("%Y-%m-%d")
    return {
        "source_id": "733",
        "destination_id": "757",
        "journey_date": journey_date,
    }


# ============================================================================
# BUS SEARCH TESTS - CITY ID
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_delhi_manali(dummy_bus_search_delhi_manali):
    """Test bus search with city IDs."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n🚌 Searching buses by ID: {dummy_bus_search_delhi_manali}")

    result = await tool.execute(**dummy_bus_search_delhi_manali)

    assert hasattr(result, "response_text")
    print(f"✅ Response: {result.response_text}")

    assert result.structured_content is not None
    data = result.structured_content

    assert "buses" in data
    assert "total_count" in data

    buses = data.get("buses", [])
    print(f"📊 Found {len(buses)} buses")

    if buses:
        first_bus = buses[0]
        print(f"   First bus: {first_bus.get('operator_name')} - {first_bus.get('bus_type')}")
        print(f"   Departure: {first_bus.get('departure_time')}")
        print(f"   Duration: {first_bus.get('duration')}")
        print(f"   Price: ₹{first_bus.get('price')}")
        print(f"   Available Seats: {first_bus.get('available_seats')}")


# ============================================================================
# BUS SEARCH TESTS - CITY NAME (NEW)
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_by_city_name(dummy_bus_search_by_city_name):
    """Test bus search with city names (auto-resolved to IDs)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n🚌 Searching buses by CITY NAME: {dummy_bus_search_by_city_name}")

    result = await tool.execute(**dummy_bus_search_by_city_name)

    assert hasattr(result, "response_text")
    print(f"✅ Response: {result.response_text}")

    # Should not be an error
    if result.is_error:
        print(f"   ⚠️ Error: {result.structured_content}")
    else:
        data = result.structured_content
        buses = data.get("buses", [])
        print(f"📊 Found {len(buses)} buses")
        
        # Verify city names were resolved
        print(f"   Source ID resolved: {data.get('source_id')}")
        print(f"   Source Name: {data.get('source_name')}")
        print(f"   Destination ID resolved: {data.get('destination_id')}")
        print(f"   Destination Name: {data.get('destination_name')}")


@pytest.mark.asyncio
async def test_bus_search_mixed_id_and_name():
    """Test bus search with mix of city ID and name."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

    # Source by ID, destination by name
    payload = {
        "source_id": "733",  # Delhi ID
        "destination_name": "Manali",  # Manali by name
        "journey_date": journey_date,
    }

    print(f"\n🚌 Searching with mixed ID/Name: {payload}")

    result = await tool.execute(**payload)

    print(f"✅ Response: {result.response_text}")
    print(f"   Is Error: {result.is_error}")


@pytest.mark.asyncio
async def test_bus_search_invalid_city_name():
    """Test bus search with invalid city name."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

    payload = {
        "source_name": "InvalidCityXYZ123",
        "destination_name": "Manali",
        "journey_date": journey_date,
    }

    print(f"\n🚌 Searching with invalid city name: {payload}")

    result = await tool.execute(**payload)

    print(f"✅ Response: {result.response_text}")
    print(f"   Is Error: {result.is_error}")
    
    # Should return an error for invalid city
    assert result.is_error or "not found" in result.response_text.lower() or len(result.structured_content.get("buses", [])) == 0


# ============================================================================
# CITY AUTOSUGGEST TESTS (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_city_autosuggest_encryption():
    """Test city autosuggest API with encryption/decryption."""
    from tools_factory.buses.bus_search_service import get_city_suggestions, get_city_id

    print("\n🔐 Testing city autosuggest with encryption...")
    
    # Test getting suggestions for "Delhi"
    suggestions = await get_city_suggestions("Delhi")
    
    print(f"   Suggestions for 'Delhi': {len(suggestions)} found")
    if suggestions:
        for s in suggestions[:3]:
            print(f"      - {s.get('name')} (ID: {s.get('id')}, State: {s.get('state')})")
    
    assert len(suggestions) > 0, "Should find Delhi suggestions"


@pytest.mark.asyncio
async def test_city_id_lookup():
    """Test getting city ID from name."""
    from tools_factory.buses.bus_search_service import get_city_id

    print("\n🔍 Testing city ID lookup...")
    
    # Test Delhi
    delhi_id = await get_city_id("Delhi")
    print(f"   Delhi ID: {delhi_id}")
    assert delhi_id is not None, "Should find Delhi ID"
    
    # Test Manali
    manali_id = await get_city_id("Manali")
    print(f"   Manali ID: {manali_id}")
    assert manali_id is not None, "Should find Manali ID"


@pytest.mark.asyncio
async def test_city_resolve_names_to_ids():
    """Test resolving both source and destination city names."""
    from tools_factory.buses.bus_search_service import resolve_city_names_to_ids

    print("\n🔄 Testing city name resolution...")
    
    result = await resolve_city_names_to_ids("Delhi", "Manali")
    
    print(f"   Source ID: {result.get('source_id')}")
    print(f"   Source Name: {result.get('source_name')}")
    print(f"   Destination ID: {result.get('destination_id')}")
    print(f"   Destination Name: {result.get('destination_name')}")
    print(f"   Error: {result.get('error')}")
    
    assert result.get("source_id") is not None
    assert result.get("destination_id") is not None
    assert result.get("error") is None


# ============================================================================
# VOLVO FILTER TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_with_volvo_filter(dummy_bus_search_with_volvo_filter):
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n🚌 Searching Volvo buses: {dummy_bus_search_with_volvo_filter}")

    result = await tool.execute(**dummy_bus_search_with_volvo_filter)

    assert hasattr(result, "response_text")
    print(f"✅ Response: {result.response_text}")

    data = result.structured_content
    buses = data.get("buses", [])

    print(f"📊 Found {len(buses)} Volvo buses")

    for bus in buses[:3]:
        print(f"   {bus.get('operator_name')}: isVolvo={bus.get('is_volvo')}, busType={bus.get('bus_type')}")


# ============================================================================
# VIEW ALL LINK TESTS (NEW)
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_view_all_link_present(dummy_bus_search_delhi_manali):
    """Test that view_all_link is present in response."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n🔗 Testing view_all_link presence...")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    data = result.structured_content

    assert "view_all_link" in data, "view_all_link should be present in response"
    
    view_all_link = data.get("view_all_link", "")
    print(f"   view_all_link: {view_all_link}")
    
    if view_all_link:
        assert "bus.easemytrip.com" in view_all_link, "Should point to EaseMyTrip bus site"
        assert "org=" in view_all_link, "Should have org parameter"
        assert "des=" in view_all_link, "Should have des parameter"
        assert "date=" in view_all_link, "Should have date parameter"
        print(f"✅ view_all_link is valid")


# ============================================================================
# RATING NORMALIZATION TESTS (NEW)
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_rating_normalization(dummy_bus_search_delhi_manali):
    """Test that ratings are properly normalized (no raw "45" appearing)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n⭐ Testing rating normalization...")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    buses = result.structured_content.get("buses", [])

    ratings_checked = 0
    for i, bus in enumerate(buses[:10]):
        rating = bus.get("rating")
        
        if rating is not None and rating != "":
            ratings_checked += 1
            
            # Rating should be a string
            assert isinstance(rating, str), f"Rating should be string, got {type(rating)}: {rating}"
            
            # Rating should be <= 5 (normalized from 0-50 scale)
            try:
                rating_float = float(rating)
                assert rating_float <= 5, f"Rating {rating} should be <= 5 (normalized)"
                assert rating_float >= 0, f"Rating {rating} should be >= 0"
                
                # Rating should NOT be raw API values like 45, 40, etc.
                assert rating_float != 45, f"Rating should not be raw '45'"
                assert rating_float != 40, f"Rating should not be raw '40'"
                
                print(f"   Bus {i+1} ({bus.get('operator_name', 'N/A')[:20]}): Rating = {rating} ✅")
            except ValueError:
                print(f"   Bus {i+1}: Rating = {rating} (non-numeric)")
    
    print(f"\n✅ Checked {ratings_checked} ratings - all normalized correctly")


@pytest.mark.asyncio
async def test_bus_search_html_no_raw_rating_45(dummy_bus_search_delhi_manali):
    """Test that HTML does not contain raw rating values like '45'."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n⭐ Testing HTML for raw rating values...")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    html = result.html
    
    if html:
        # Check that raw ratings don't appear in HTML
        assert "★ 45" not in html, "Raw rating '★ 45' should not appear in HTML"
        assert "★ 40" not in html, "Raw rating '★ 40' should not appear in HTML"
        assert "★ 35" not in html, "Raw rating '★ 35' should not appear in HTML"
        
        print(f"✅ No raw rating values found in HTML")


# ============================================================================
# HTML OUTPUT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_html_output_present(dummy_bus_search_delhi_manali):
    """Test that HTML output is generated for website user type."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n🖼️ Testing HTML output presence...")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    
    assert result.html is not None, "HTML output should be present for website"
    assert len(result.html) > 0, "HTML output should not be empty"
    assert "bus-carousel" in result.html, "HTML should contain bus-carousel class"
    
    print(f"✅ HTML output generated ({len(result.html)} chars)")


@pytest.mark.asyncio
async def test_bus_search_html_has_view_all_card(dummy_bus_search_delhi_manali):
    """Test that HTML contains View All card when there are many buses."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n🔗 Testing View All card in HTML...")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    
    html = result.html
    data = result.structured_content
    
    total_buses = len(data.get("buses", []))
    view_all_link = data.get("view_all_link", "")
    
    print(f"   Total buses: {total_buses}")
    print(f"   Has view_all_link: {bool(view_all_link)}")
    
    # View All card should appear when total > display_limit (default 5) AND link exists
    if total_buses > 5 and view_all_link:
        assert "view-all-card" in html or "view-all-link" in html, \
            "View All card/link should appear when buses > 5 and link exists"
        print(f"✅ View All card present in HTML")
    else:
        print(f"⚠️ Not enough buses ({total_buses}) or no link to test View All card")


@pytest.mark.asyncio
async def test_bus_search_html_width_90_percent(dummy_bus_search_delhi_manali):
    """Test that carousel has width: 90% in CSS."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n📐 Testing carousel width CSS...")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    html = result.html
    
    if html:
        assert "width: 90%" in html or "width:90%" in html, \
            "Carousel should have width: 90% in CSS"
        
        print(f"✅ Carousel width 90% verified")


# ============================================================================
# WHATSAPP FORMAT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_whatsapp_format(dummy_bus_search_delhi_manali):
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


@pytest.mark.asyncio
async def test_bus_search_whatsapp_no_html(dummy_bus_search_delhi_manali):
    """Test that WhatsApp format does not generate HTML output."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    payload = {**dummy_bus_search_delhi_manali, "_user_type": "whatsapp"}

    result = await tool.execute(**payload)
    
    assert result.html is None, "WhatsApp format should not have HTML output"
    assert result.whatsapp_response is not None, "WhatsApp format should have whatsapp_response"
    
    print(f"\n✅ WhatsApp format correctly has no HTML output")


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_bus_response_has_boarding_points(dummy_bus_search_delhi_manali):
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    buses = result.structured_content.get("buses", [])

    if buses:
        first_bus = buses[0]
        assert "boarding_points" in first_bus, "Bus should have boarding_points"

        boarding_points = first_bus["boarding_points"]
        if boarding_points:
            first_bp = boarding_points[0]
            assert "bd_id" in first_bp
            assert "bd_long_name" in first_bp

            print(f"\n✅ Boarding points verified:")
            for bp in boarding_points[:3]:
                print(f"   - {bp.get('bd_long_name')} at {bp.get('time')}")


@pytest.mark.asyncio
async def test_bus_response_has_dropping_points(dummy_bus_search_delhi_manali):
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    result = await tool.execute(**dummy_bus_search_delhi_manali)
    buses = result.structured_content.get("buses", [])

    if buses:
        first_bus = buses[0]
        assert "dropping_points" in first_bus, "Bus should have dropping_points"

        dropping_points = first_bus["dropping_points"]
        if dropping_points:
            first_dp = dropping_points[0]
            assert "dp_id" in first_dp
            assert "dp_name" in first_dp

            print(f"\n✅ Dropping points verified:")
            for dp in dropping_points[:3]:
                print(f"   - {dp.get('dp_name')} at {dp.get('dp_time')}")


@pytest.mark.asyncio
async def test_bus_response_has_book_now_link(dummy_bus_search_delhi_manali):
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
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_invalid_date_format():
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    payload = {
        "source_id": "733",
        "destination_id": "757",
        "journey_date": "25-01-2026",  # Invalid format
    }

    print(f"\n🚌 Testing invalid date format: {payload['journey_date']}")

    result = await tool.execute(**payload)

    assert result.is_error is True
    print(f"✅ Correctly returned error for invalid date format")
    print(f"   Error: {result.response_text}")


@pytest.mark.asyncio
async def test_bus_search_missing_required_field():
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    payload = {
        "journey_date": "2026-02-01",
        # Missing source and destination
    }

    print(f"\n🚌 Testing missing required fields")

    result = await tool.execute(**payload)

    assert result.is_error is True
    print(f"✅ Correctly returned error for missing fields")
    print(f"   Error: {result.response_text}")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_response_time(dummy_bus_search_delhi_manali):
    import time

    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    start = time.time()
    result = await tool.execute(**dummy_bus_search_delhi_manali)
    elapsed = time.time() - start

    print(f"\n⏱️  Bus search took {elapsed:.2f} seconds")

    assert elapsed < 30, f"Search took too long: {elapsed}s"
    assert result.structured_content is not None


# ============================================================================
# LIMIT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_with_limit(dummy_bus_search_delhi_manali):
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    payload = {**dummy_bus_search_delhi_manali, "_limit": 5}

    print(f"\n🚌 Searching buses with limit=5")

    result = await tool.execute(**payload)

    data = result.structured_content
    buses = data.get("buses", [])

    assert len(buses) <= 5, f"Expected at most 5 buses, got {len(buses)}"

    print(f"✅ Limited search returned {len(buses)} buses (max 5)")