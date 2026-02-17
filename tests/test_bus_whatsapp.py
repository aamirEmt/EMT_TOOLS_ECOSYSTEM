"""Real API tests for bus search WhatsApp JSON functionality.

These tests make actual API calls and verify real responses.
NO MOCKING - Real API integration tests.

File: tests/test_bus_whatsapp.py

Run with:
    pytest tests/test_bus_whatsapp.py -v -s
    
Or run directly:
    python tests/test_bus_whatsapp.py
"""

import sys
import os

# ============================================================================
# PATH SETUP - Required for direct python execution
# ============================================================================
# Add project root to Python path so 'tools_factory' can be imported
# This handles running from tests/ directory or project root
current_dir = os.path.dirname(os.path.abspath(__file__))
# If we're in tests/, go up one level; otherwise assume we're at project root
if os.path.basename(current_dir) == 'tests':
    project_root = os.path.dirname(current_dir)
else:
    project_root = current_dir

if project_root not in sys.path:
    sys.path.insert(0, project_root)
# ============================================================================

import pytest
import asyncio
import json
from datetime import datetime, timedelta

# Mark all tests in this file as integration tests (slow)
pytestmark = pytest.mark.integration


# ============================================================================
# TEST FIXTURES - DUMMY PAYLOADS
# ============================================================================

@pytest.fixture
def dummy_bus_basic():
    """Dummy payload for basic bus search."""
    today = datetime.now()
    journey_date = (today + timedelta(days=3)).strftime("%d-%m-%Y")
    
    return {
        "source_name": "Gurugram",
        "destination_name": "Jaipur",
        "journey_date": journey_date,
    }


@pytest.fixture
def dummy_bus_with_ac_filter():
    """Dummy payload for AC bus search."""
    today = datetime.now()
    journey_date = (today + timedelta(days=5)).strftime("%d-%m-%Y")
    
    return {
        "source_name": "Delhi",
        "destination_name": "Jaipur",
        "journey_date": journey_date,
        "is_ac": True,
    }


@pytest.fixture
def dummy_bus_with_sleeper_filter():
    """Dummy payload for sleeper bus search."""
    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%d-%m-%Y")
    
    return {
        "source_name": "Kanpur",
        "destination_name": "Varanasi",
        "journey_date": journey_date,
        "is_sleeper": True,
    }


@pytest.fixture
def dummy_bus_with_time_filter():
    """Dummy payload for bus search with departure time filter."""
    today = datetime.now()
    journey_date = (today + timedelta(days=5)).strftime("%d-%m-%Y")
    
    return {
        "source_name": "Delhi",
        "destination_name": "Jaipur",
        "journey_date": journey_date,
        "departure_time_from": "18:00",  # Evening buses
    }


@pytest.fixture
def dummy_bus_combined_filters():
    """Dummy payload for bus search with combined filters."""
    today = datetime.now()
    journey_date = (today + timedelta(days=10)).strftime("%d-%m-%Y")
    
    return {
        "source_name": "Delhi",
        "destination_name": "Jaipur",
        "journey_date": journey_date,
        "is_ac": True,
        "is_sleeper": True,
        "departure_time_from": "20:00",
        "departure_time_to": "06:00",  # Overnight range
    }


# ============================================================================
# BUS SEARCH WHATSAPP JSON TESTS - REAL API
# ============================================================================

@pytest.mark.asyncio
async def test_bus_search_whatsapp_basic(dummy_bus_basic):
    """Test basic bus search with real API call for WhatsApp JSON response."""
    from tools_factory.factory import get_tool_factory
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n{'='*80}")
    print(f"🔍 BASIC BUS SEARCH - WhatsApp JSON Test")
    print(f"{'='*80}")
    print(f"Payload: {json.dumps(dummy_bus_basic, indent=2)}")

    result = await tool.execute(
        **dummy_bus_basic,
        _user_type="whatsapp",
        _limit=5
    )

    # Extract WhatsApp response
    whatsapp_response = result.whatsapp_response
    assert whatsapp_response is not None, "Response must have 'whatsapp_response'"
    
    print(f"\n📋 FULL WHATSAPP RESPONSE:")
    print(json.dumps(whatsapp_response, indent=2, default=str))
    
    # Validate structure
    whatsapp_data = whatsapp_response.get("whatsapp_json")
    assert whatsapp_data is not None, "Must have 'whatsapp_json'"
    assert "options" in whatsapp_data, "Must have 'options'"
    assert "view_all_buses_url" in whatsapp_data, "Must have 'view_all_buses_url'"
    
    # Validate each bus option
    print(f"\n📊 BUS OPTIONS ({len(whatsapp_data['options'])} buses):")
    print("-" * 60)
    
    for bus in whatsapp_data["options"]:
        print(f"\nOption {bus.get('option_id')}:")
        print(f"   Operator: {bus.get('operator_name')}")
        print(f"   Bus Type: {bus.get('bus_type')}")
        print(f"   Time: {bus.get('departure_time')} → {bus.get('arrival_time')}")
        print(f"   Duration: {bus.get('duration')}")
        print(f"   💰 FARE: ₹{bus.get('fare')}")
        print(f"   Seats: {bus.get('available_seats')}")
        print(f"   AC: {bus.get('is_ac')} | Non-AC: {bus.get('is_non_ac', 'N/A')}")
        print(f"   Seater: {bus.get('is_seater', 'N/A')} | Sleeper: {bus.get('is_sleeper', 'N/A')}")
        print(f"   Rating: {bus.get('rating')}")
        print(f"   Boarding: {bus.get('boarding_point')}")
        print(f"   Dropping: {bus.get('dropping_point')}")
        
        # Validate required fields
        assert "option_id" in bus
        assert "operator_name" in bus
        assert "fare" in bus
        assert bus.get("fare") is not None, "Fare should not be None"
        assert isinstance(bus.get("fare"), (int, float)), f"Fare should be numeric, got {type(bus.get('fare'))}"
    
    print(f"\n✅ Test passed with {len(whatsapp_data['options'])} buses")


@pytest.mark.asyncio
async def test_bus_search_whatsapp_ac_filter(dummy_bus_with_ac_filter):
    """Test AC bus search for WhatsApp JSON response."""
    from tools_factory.factory import get_tool_factory
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n{'='*80}")
    print(f"🔍 AC BUS SEARCH - WhatsApp JSON Test")
    print(f"{'='*80}")
    print(f"Payload: {json.dumps(dummy_bus_with_ac_filter, indent=2)}")

    result = await tool.execute(
        **dummy_bus_with_ac_filter,
        _user_type="whatsapp",
        _limit=5
    )

    whatsapp_response = result.whatsapp_response
    assert whatsapp_response is not None
    
    print(f"\n📋 FULL WHATSAPP RESPONSE:")
    print(json.dumps(whatsapp_response, indent=2, default=str))
    
    whatsapp_data = whatsapp_response.get("whatsapp_json")
    
    # Verify all buses are AC
    print(f"\n📊 AC FILTER VERIFICATION:")
    for bus in whatsapp_data["options"]:
        print(f"   {bus.get('operator_name')}: AC={bus.get('is_ac')}, Fare=₹{bus.get('fare')}")
        # All results should be AC when filter is applied
        assert bus.get("is_ac") == True, f"Bus should be AC but got is_ac={bus.get('is_ac')}"
    
    print(f"\n✅ AC filter test passed")


@pytest.mark.asyncio
async def test_bus_search_whatsapp_sleeper_filter(dummy_bus_with_sleeper_filter):
    """Test sleeper bus search for WhatsApp JSON response."""
    from tools_factory.factory import get_tool_factory
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n{'='*80}")
    print(f"🔍 SLEEPER BUS SEARCH - WhatsApp JSON Test")
    print(f"{'='*80}")
    print(f"Payload: {json.dumps(dummy_bus_with_sleeper_filter, indent=2)}")

    result = await tool.execute(
        **dummy_bus_with_sleeper_filter,
        _user_type="whatsapp",
        _limit=5
    )

    whatsapp_response = result.whatsapp_response
    assert whatsapp_response is not None
    
    print(f"\n📋 FULL WHATSAPP RESPONSE:")
    print(json.dumps(whatsapp_response, indent=2, default=str))
    
    whatsapp_data = whatsapp_response.get("whatsapp_json")
    
    # Verify all buses are sleeper
    print(f"\n📊 SLEEPER FILTER VERIFICATION:")
    for bus in whatsapp_data["options"]:
        print(f"   {bus.get('operator_name')}: Sleeper={bus.get('is_sleeper')}, Fare=₹{bus.get('fare')}")
        assert bus.get("is_sleeper") == True, f"Bus should be sleeper but got is_sleeper={bus.get('is_sleeper')}"
    
    print(f"\n✅ Sleeper filter test passed")


@pytest.mark.asyncio
async def test_bus_search_whatsapp_time_filter(dummy_bus_with_time_filter):
    """Test bus search with departure time filter for WhatsApp JSON response."""
    from tools_factory.factory import get_tool_factory
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n{'='*80}")
    print(f"🔍 TIME FILTER BUS SEARCH - WhatsApp JSON Test")
    print(f"{'='*80}")
    print(f"Payload: {json.dumps(dummy_bus_with_time_filter, indent=2)}")

    result = await tool.execute(
        **dummy_bus_with_time_filter,
        _user_type="whatsapp",
        _limit=5
    )

    whatsapp_response = result.whatsapp_response
    assert whatsapp_response is not None
    
    print(f"\n📋 FULL WHATSAPP RESPONSE:")
    print(json.dumps(whatsapp_response, indent=2, default=str))
    
    whatsapp_data = whatsapp_response.get("whatsapp_json")
    
    # Verify departure times
    print(f"\n📊 TIME FILTER VERIFICATION (after 18:00):")
    for bus in whatsapp_data["options"]:
        dep_time = bus.get("departure_time", "00:00")
        print(f"   {bus.get('operator_name')}: Departs {dep_time}, Fare=₹{bus.get('fare')}")
        
        # Parse time and verify it's after 18:00
        if dep_time and ":" in dep_time:
            hours = int(dep_time.split(":")[0])
            assert hours >= 18, f"Departure time {dep_time} should be after 18:00"
    
    print(f"\n✅ Time filter test passed")


@pytest.mark.asyncio
async def test_bus_search_whatsapp_combined_filters(dummy_bus_combined_filters):
    """Test bus search with combined filters for WhatsApp JSON response."""
    from tools_factory.factory import get_tool_factory
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")

    print(f"\n{'='*80}")
    print(f"🔍 COMBINED FILTERS BUS SEARCH - WhatsApp JSON Test")
    print(f"{'='*80}")
    print(f"Payload: {json.dumps(dummy_bus_combined_filters, indent=2)}")

    result = await tool.execute(
        **dummy_bus_combined_filters,
        _user_type="whatsapp",
        _limit=5
    )

    whatsapp_response = result.whatsapp_response
    assert whatsapp_response is not None
    
    print(f"\n📋 FULL WHATSAPP RESPONSE:")
    print(json.dumps(whatsapp_response, indent=2, default=str))
    
    whatsapp_data = whatsapp_response.get("whatsapp_json")
    
    # Verify combined filters
    print(f"\n📊 COMBINED FILTER VERIFICATION (AC + Sleeper + Night):")
    for bus in whatsapp_data["options"]:
        print(f"   {bus.get('operator_name')}:")
        print(f"      AC: {bus.get('is_ac')}, Sleeper: {bus.get('is_sleeper')}")
        print(f"      Departs: {bus.get('departure_time')}, Fare: ₹{bus.get('fare')}")
        
        # Verify filters
        assert bus.get("is_ac") == True, "Should be AC"
        assert bus.get("is_sleeper") == True, "Should be sleeper"
    
    print(f"\n✅ Combined filters test passed")


@pytest.mark.asyncio
async def test_bus_price_matches_website():
    """
    Test that the fare in WhatsApp response matches the website price (not strikethrough).
    This specifically tests the price fix.
    """
    from tools_factory.factory import get_tool_factory
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")
    
    today = datetime.now()
    journey_date = (today + timedelta(days=3)).strftime("%d-%m-%Y")
    
    payload = {
        "source_name": "Gurugram",
        "destination_name": "Jaipur",
        "journey_date": journey_date,
    }

    print(f"\n{'='*80}")
    print(f"🔍 PRICE VERIFICATION TEST")
    print(f"{'='*80}")
    print(f"Testing that WhatsApp fare = Website price (not strikethrough)")

    # Get WhatsApp response
    whatsapp_result = await tool.execute(
        **payload,
        _user_type="whatsapp",
        _limit=5
    )
    
    # Get Website response (for comparison)
    website_result = await tool.execute(
        **payload,
        _user_type="website",
        _limit=5
    )
    
    whatsapp_data = whatsapp_result.whatsapp_response.get("whatsapp_json")
    website_buses = website_result.structured_content.get("buses", [])
    
    print(f"\n📊 PRICE COMPARISON:")
    print("-" * 70)
    print(f"{'Operator':<30} {'WhatsApp Fare':>15} {'Website Price':>15}")
    print("-" * 70)
    
    for i, wa_bus in enumerate(whatsapp_data["options"][:5]):
        wa_fare = wa_bus.get("fare")
        
        # Find matching bus in website results
        matching_website_bus = None
        for wb in website_buses:
            if wb.get("bus_id") == wa_bus.get("bus_id"):
                matching_website_bus = wb
                break
        
        if matching_website_bus:
            website_price = matching_website_bus.get("price")
            operator = wa_bus.get("operator_name", "Unknown")[:28]
            print(f"{operator:<30} ₹{wa_fare:>13} ₹{website_price:>13}")
            
            # They should match! Compare as floats to handle int/float differences
            try:
                wa_fare_num = float(wa_fare) if wa_fare else 0
                website_price_num = float(website_price) if website_price else 0
                assert wa_fare_num == website_price_num, \
                    f"WhatsApp fare (₹{wa_fare}) should match website price (₹{website_price})"
            except (ValueError, TypeError):
                assert str(wa_fare) == str(website_price), \
                    f"WhatsApp fare (₹{wa_fare}) should match website price (₹{website_price})"
        else:
            print(f"{wa_bus.get('operator_name', 'Unknown')[:28]:<30} ₹{wa_fare:>13} {'(no match)':>15}")
    
    print("-" * 70)
    print(f"\n✅ Price verification passed - WhatsApp fares match website prices!")


@pytest.mark.asyncio  
async def test_bus_whatsapp_has_all_new_fields():
    """Test that WhatsApp response includes all new filter fields."""
    from tools_factory.factory import get_tool_factory
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")
    
    today = datetime.now()
    journey_date = (today + timedelta(days=5)).strftime("%d-%m-%Y")
    
    payload = {
        "source_name": "Delhi",
        "destination_name": "Jaipur",
        "journey_date": journey_date,
    }

    print(f"\n{'='*80}")
    print(f"🔍 NEW FIELDS VERIFICATION TEST")
    print(f"{'='*80}")

    result = await tool.execute(
        **payload,
        _user_type="whatsapp",
        _limit=3
    )
    
    whatsapp_data = result.whatsapp_response.get("whatsapp_json")
    
    required_fields = [
        "option_id",
        "bus_id", 
        "operator_name",
        "bus_type",
        "departure_time",
        "arrival_time",
        "duration",
        "date",
        "available_seats",
        "fare",
        "is_ac",
        "is_non_ac",      # NEW
        "is_seater",      # NEW
        "is_sleeper",     # NEW
        "is_volvo",
        "rating",
        "boarding_point",
        "dropping_point",
        "amenities_count",
        "book_now",
    ]
    
    print(f"\n📋 Checking for required fields in WhatsApp response:")
    
    for bus in whatsapp_data["options"]:
        print(f"\n🚌 {bus.get('operator_name')}:")
        missing_fields = []
        
        for field in required_fields:
            if field in bus:
                value = bus[field]
                print(f"   ✅ {field}: {value}")
            else:
                print(f"   ❌ {field}: MISSING")
                missing_fields.append(field)
        
        assert len(missing_fields) == 0, f"Missing fields: {missing_fields}"
    
    print(f"\n✅ All required fields present in WhatsApp response!")


# ============================================================================
# MAIN EXECUTION - Run tests directly with python
# ============================================================================

async def run_all_tests():
    """Run all tests when script is executed directly."""
    from tools_factory.factory import get_tool_factory
    
    today = datetime.now()
    
    # Test 1: Basic WhatsApp response
    print("\n" + "="*80)
    print("TEST 1: BASIC WHATSAPP BUS SEARCH")
    print("="*80)
    
    factory = get_tool_factory()
    tool = factory.get_tool("search_buses")
    
    payload = {
        "source_name": "Gurugram",
        "destination_name": "Jaipur",
        "journey_date": (today + timedelta(days=3)).strftime("%d-%m-%Y"),
    }
    
    result = await tool.execute(**payload, _user_type="whatsapp", _limit=5)
    
    print(f"\n📋 WHATSAPP JSON RESPONSE:")
    print(json.dumps(result.whatsapp_response, indent=2, default=str))
    
    # Test 2: AC Filter
    print("\n" + "="*80)
    print("TEST 2: AC BUS SEARCH")
    print("="*80)
    
    payload_ac = {
        "source_name": "Delhi",
        "destination_name": "Jaipur", 
        "journey_date": (today + timedelta(days=5)).strftime("%d-%m-%Y"),
        "is_ac": True,
    }
    
    result_ac = await tool.execute(**payload_ac, _user_type="whatsapp", _limit=5)
    print(f"\n📋 AC BUSES WHATSAPP RESPONSE:")
    print(json.dumps(result_ac.whatsapp_response, indent=2, default=str))
    
    # Test 3: Sleeper Filter
    print("\n" + "="*80)
    print("TEST 3: SLEEPER BUS SEARCH")
    print("="*80)
    
    payload_sleeper = {
        "source_name": "Kanpur",
        "destination_name": "Varanasi",
        "journey_date": (today + timedelta(days=7)).strftime("%d-%m-%Y"),
        "is_sleeper": True,
    }
    
    result_sleeper = await tool.execute(**payload_sleeper, _user_type="whatsapp", _limit=5)
    print(f"\n📋 SLEEPER BUSES WHATSAPP RESPONSE:")
    print(json.dumps(result_sleeper.whatsapp_response, indent=2, default=str))
    
    # Test 4: Time Filter
    print("\n" + "="*80)
    print("TEST 4: EVENING BUS SEARCH (after 6 PM)")
    print("="*80)
    
    payload_time = {
        "source_name": "Delhi",
        "destination_name": "Jaipur",
        "journey_date": (today + timedelta(days=5)).strftime("%d-%m-%Y"),
        "departure_time_from": "18:00",
    }
    
    result_time = await tool.execute(**payload_time, _user_type="whatsapp", _limit=5)
    print(f"\n📋 EVENING BUSES WHATSAPP RESPONSE:")
    print(json.dumps(result_time.whatsapp_response, indent=2, default=str))
    
    # Test 5: Combined Filters
    print("\n" + "="*80)
    print("TEST 5: COMBINED FILTERS (AC + Sleeper + Night)")
    print("="*80)
    
    payload_combined = {
        "source_name": "Delhi",
        "destination_name": "Jaipur",
        "journey_date": (today + timedelta(days=10)).strftime("%d-%m-%Y"),
        "is_ac": True,
        "is_sleeper": True,
        "departure_time_from": "20:00",
    }
    
    result_combined = await tool.execute(**payload_combined, _user_type="whatsapp", _limit=5)
    print(f"\n📋 COMBINED FILTERS WHATSAPP RESPONSE:")
    print(json.dumps(result_combined.whatsapp_response, indent=2, default=str))
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED!")
    print("="*80)


if __name__ == "__main__":
    # Run tests directly
    asyncio.run(run_all_tests())