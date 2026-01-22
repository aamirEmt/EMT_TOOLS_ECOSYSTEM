"""Real API tests for Train Search Tool.

These tests make actual API calls and verify real responses.
NO MOCKING - Real API integration tests.

File: tests/test_trains.py

Run with:
    pytest tests/test_trains.py -v -s

Mark as integration tests:
    pytest -m integration
"""

import pytest
from datetime import datetime, timedelta
from tools_factory.factory import get_tool_factory
from tools_factory.base_schema import ToolResponseFormat
from emt_client.utils import fetch_train_station_suggestions, resolve_train_station

# Mark all tests in this file as integration tests (slow)
pytestmark = pytest.mark.integration


# ============================================================================
# TEST FIXTURES - DUMMY PAYLOADS
# ============================================================================

@pytest.fixture
def dummy_train_search_with_codes():
    """Dummy payload with pre-formatted station codes."""
    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

    return {
        "from_station": "New Delhi (NDLS)",
        "to_station": "Mumbai Central (MMCT)",
        "journey_date": journey_date,
    }


@pytest.fixture
def dummy_train_search_without_codes():
    """Dummy payload with just city names (no codes)."""
    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

    return {
        "from_station": "Delhi",
        "to_station": "Mumbai",
        "journey_date": journey_date,
    }


@pytest.fixture
def dummy_train_search_jammu_delhi():
    """Dummy payload for Jammu to Delhi route."""
    today = datetime.now()
    journey_date = (today + timedelta(days=10)).strftime("%Y-%m-%d")

    return {
        "from_station": "Jammu",
        "to_station": "Delhi",
        "journey_date": journey_date,
    }


@pytest.fixture
def dummy_train_search_with_class():
    """Dummy payload with preferred travel class."""
    today = datetime.now()
    journey_date = (today + timedelta(days=14)).strftime("%Y-%m-%d")

    return {
        "from_station": "Delhi",
        "to_station": "Jaipur",
        "journey_date": journey_date,
        "travel_class": "3A",
    }


@pytest.fixture
def dummy_train_search_with_quota():
    """Dummy payload with specific quota."""
    today = datetime.now()
    journey_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")

    return {
        "from_station": "Delhi",
        "to_station": "Lucknow",
        "journey_date": journey_date,
        "quota": "TQ",  # Tatkal
    }


@pytest.fixture
def dummy_train_search_popular_route():
    """Dummy payload for popular route (likely to have many results)."""
    today = datetime.now()
    journey_date = (today + timedelta(days=21)).strftime("%Y-%m-%d")

    return {
        "from_station": "New Delhi (NDLS)",
        "to_station": "Varanasi Junction (BSB)",
        "journey_date": journey_date,
    }


# ============================================================================
# TRAIN STATION AUTOSUGGEST TESTS - REAL API
# ============================================================================

@pytest.mark.asyncio
async def test_train_autosuggest_jammu():
    """Test train station autosuggest for Jammu."""
    print("\n🔍 Testing autosuggest for 'Jammu'")

    suggestions = await fetch_train_station_suggestions("Jammu")

    assert suggestions is not None
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0

    first = suggestions[0]
    assert "Code" in first
    assert "Name" in first

    print(f"✅ Found {len(suggestions)} suggestions")
    print(f"   First suggestion: {first['Name']} ({first['Code']})")

    # Jammu Tawi should be the first result
    assert first["Code"] == "JAT", f"Expected JAT, got {first['Code']}"


@pytest.mark.asyncio
async def test_train_autosuggest_delhi():
    """Test train station autosuggest for Delhi."""
    print("\n🔍 Testing autosuggest for 'Delhi'")

    suggestions = await fetch_train_station_suggestions("Delhi")

    assert suggestions is not None
    assert len(suggestions) > 0

    print(f"✅ Found {len(suggestions)} Delhi stations:")
    for s in suggestions[:5]:
        print(f"   - {s['Name']} ({s['Code']})")


@pytest.mark.asyncio
async def test_train_autosuggest_mumbai():
    """Test train station autosuggest for Mumbai."""
    print("\n🔍 Testing autosuggest for 'Mumbai'")

    suggestions = await fetch_train_station_suggestions("Mumbai")

    assert suggestions is not None
    assert len(suggestions) > 0

    print(f"✅ Found {len(suggestions)} Mumbai stations:")
    for s in suggestions[:5]:
        print(f"   - {s['Name']} ({s['Code']})")


@pytest.mark.asyncio
async def test_resolve_train_station_jammu():
    """Test resolve_train_station converts 'Jammu' to proper format."""
    print("\n🔍 Testing resolve_train_station for 'Jammu'")

    result = await resolve_train_station("Jammu")

    assert result is not None
    assert "(" in result and ")" in result
    assert "JAT" in result

    print(f"✅ Resolved: 'Jammu' → '{result}'")


@pytest.mark.asyncio
async def test_resolve_train_station_delhi():
    """Test resolve_train_station converts 'Delhi' to proper format."""
    print("\n🔍 Testing resolve_train_station for 'Delhi'")

    result = await resolve_train_station("Delhi")

    assert result is not None
    assert "(" in result and ")" in result

    print(f"✅ Resolved: 'Delhi' → '{result}'")


@pytest.mark.asyncio
async def test_resolve_train_station_already_formatted():
    """Test that already formatted stations are returned as-is."""
    print("\n🔍 Testing resolve_train_station with pre-formatted input")

    # This should be passed through without API call
    # (checked in _needs_station_resolution)
    input_station = "New Delhi (NDLS)"

    # The function will still call API, but that's okay
    # The important thing is the service layer skips resolution
    from tools_factory.trains.train_search_service import _needs_station_resolution

    needs_resolution = _needs_station_resolution(input_station)
    assert needs_resolution is False, "Pre-formatted station should not need resolution"

    print(f"✅ '{input_station}' correctly identified as not needing resolution")


# ============================================================================
# TRAIN SEARCH TESTS - REAL API
# ============================================================================

@pytest.mark.asyncio
async def test_train_search_with_codes(dummy_train_search_with_codes):
    """Test train search with pre-formatted station codes."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    print(f"\n🔍 Searching trains: {dummy_train_search_with_codes}")

    result = await tool.execute(**dummy_train_search_with_codes)

    assert hasattr(result, "response_text")
    print(f"✅ Response: {result.response_text}")

    assert result.structured_content is not None
    data = result.structured_content

    # Verify API response structure
    assert "trains" in data
    assert "total_count" in data

    trains = data.get("trains", [])
    print(f"📊 Found {len(trains)} trains")

    if trains:
        first_train = trains[0]
        print(f"   First train: {first_train.get('train_number')} - {first_train.get('train_name')}")
        print(f"   Departure: {first_train.get('departure_time')}")
        print(f"   Duration: {first_train.get('duration')}")


@pytest.mark.asyncio
async def test_train_search_without_codes(dummy_train_search_without_codes):
    """Test train search with just city names (auto-resolution)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    print(f"\n🔍 Searching trains (auto-resolve): {dummy_train_search_without_codes}")

    result = await tool.execute(**dummy_train_search_without_codes)

    assert hasattr(result, "response_text")
    print(f"✅ Response: {result.response_text}")

    assert result.structured_content is not None
    data = result.structured_content

    assert "trains" in data
    trains = data.get("trains", [])
    print(f"📊 Found {len(trains)} trains (with auto station resolution)")


@pytest.mark.asyncio
async def test_train_search_jammu_to_delhi(dummy_train_search_jammu_delhi):
    """Test train search from Jammu to Delhi with auto-resolution."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    print(f"\n🔍 Searching Jammu to Delhi: {dummy_train_search_jammu_delhi}")

    result = await tool.execute(**dummy_train_search_jammu_delhi)

    assert hasattr(result, "response_text")
    print(f"✅ Response: {result.response_text}")

    assert result.structured_content is not None
    data = result.structured_content

    # Verify the station resolution happened
    assert "from_station" in data
    assert "to_station" in data

    # Check that codes are now present in the response
    print(f"   From: {data.get('from_station')}")
    print(f"   To: {data.get('to_station')}")

    trains = data.get("trains", [])
    print(f"📊 Found {len(trains)} trains from Jammu to Delhi")

    if trains:
        for i, train in enumerate(trains[:3], 1):
            print(f"\n   Train {i}: {train.get('train_number')} - {train.get('train_name')}")
            print(f"      {train.get('from_station_name')} → {train.get('to_station_name')}")
            print(f"      Departure: {train.get('departure_time')} | Arrival: {train.get('arrival_time')}")
            print(f"      Duration: {train.get('duration')}")


@pytest.mark.asyncio
async def test_train_search_with_class_filter(dummy_train_search_with_class):
    """Test train search with specific travel class filter."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    print(f"\n🔍 Searching trains with 3A class: {dummy_train_search_with_class}")

    result = await tool.execute(**dummy_train_search_with_class)

    assert result.structured_content is not None
    data = result.structured_content

    trains = data.get("trains", [])
    print(f"📊 Found {len(trains)} trains with 3A class available")

    # Verify trains have 3A class
    for train in trains[:3]:
        classes = train.get("classes", [])
        class_codes = [c.get("class_code") for c in classes]
        print(f"   {train.get('train_name')}: Classes = {class_codes}")

        # Should only have 3A class (filtered)
        assert "3A" in class_codes or len(class_codes) == 0


@pytest.mark.asyncio
async def test_train_search_popular_route(dummy_train_search_popular_route):
    """Test train search on popular route (should have many results)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    print(f"\n🔍 Searching popular route: {dummy_train_search_popular_route}")

    result = await tool.execute(**dummy_train_search_popular_route)

    data = result.structured_content
    trains = data.get("trains", [])

    print(f"📊 Found {len(trains)} trains on popular route")

    # Popular routes should have results
    assert len(trains) > 0, "Popular route should return trains"

    # Print first 3 trains
    for i, train in enumerate(trains[:3], 1):
        print(f"\n   Train {i}:")
        print(f"      {train.get('train_number')} - {train.get('train_name')}")
        print(f"      Duration: {train.get('duration')}")
        print(f"      Running days: {train.get('running_days')}")

        classes = train.get("classes", [])
        if classes:
            cheapest = min(classes, key=lambda c: float(c.get("fare", 0) or 0))
            print(f"      Cheapest fare: ₹{cheapest.get('fare')} ({cheapest.get('class_name')})")


# ============================================================================
# WHATSAPP FORMAT TESTS - REAL API
# ============================================================================

@pytest.mark.asyncio
async def test_train_search_whatsapp_format(dummy_train_search_with_codes):
    """Test train search returns WhatsApp formatted response."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    payload = {**dummy_train_search_with_codes, "_user_type": "whatsapp"}

    print(f"\n📱 Searching trains (WhatsApp format): {payload}")

    result: ToolResponseFormat = await tool.execute(**payload)

    assert result.whatsapp_response is not None
    print(f"✅ WhatsApp response received")

    whatsapp_data = result.whatsapp_response
    assert "whatsapp_json" in whatsapp_data
    assert whatsapp_data["whatsapp_json"]["type"] == "train_collection"

    options = whatsapp_data["whatsapp_json"].get("options", [])
    print(f"📊 WhatsApp options: {len(options)} trains")

    if options:
        first = options[0]
        print(f"\n   First option:")
        print(f"      Train: {first.get('train_number')} - {first.get('train_name')}")
        print(f"      Departure: {first.get('departure_time')}")
        print(f"      Cheapest fare: ₹{first.get('cheapest_fare')}")


@pytest.mark.asyncio
async def test_train_search_whatsapp_jammu_delhi(dummy_train_search_jammu_delhi):
    """Test WhatsApp format for Jammu to Delhi with auto-resolution."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    payload = {**dummy_train_search_jammu_delhi, "_user_type": "whatsapp"}

    print(f"\n📱 Searching Jammu to Delhi (WhatsApp): {payload}")

    result: ToolResponseFormat = await tool.execute(**payload)

    assert result.whatsapp_response is not None

    whatsapp_data = result.whatsapp_response
    options = whatsapp_data["whatsapp_json"].get("options", [])

    print(f"✅ Found {len(options)} train options for WhatsApp")

    # Print WhatsApp JSON structure
    print(f"\n📱 WhatsApp JSON:\n{whatsapp_data['whatsapp_json']}")


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_train_response_has_classes(dummy_train_search_with_codes):
    """Verify train results include class availability."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    result = await tool.execute(**dummy_train_search_with_codes)
    trains = result.structured_content.get("trains", [])

    if trains:
        first_train = trains[0]
        assert "classes" in first_train, "Train should have classes"

        classes = first_train["classes"]
        if classes:
            first_class = classes[0]
            assert "class_code" in first_class
            assert "class_name" in first_class
            assert "fare" in first_class
            assert "availability_status" in first_class

            print(f"\n✅ Class data verified:")
            for cls in classes:
                print(f"   {cls['class_code']} ({cls['class_name']}): ₹{cls['fare']} - {cls['availability_status']}")


@pytest.mark.asyncio
async def test_train_response_has_running_days(dummy_train_search_with_codes):
    """Verify train results include running days."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    result = await tool.execute(**dummy_train_search_with_codes)
    trains = result.structured_content.get("trains", [])

    if trains:
        first_train = trains[0]
        assert "running_days" in first_train, "Train should have running_days"

        running_days = first_train["running_days"]
        print(f"\n✅ Running days: {running_days}")

        # Should be a list of day abbreviations
        assert isinstance(running_days, list)


@pytest.mark.asyncio
async def test_train_response_has_timing_info(dummy_train_search_with_codes):
    """Verify train results include timing information."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    result = await tool.execute(**dummy_train_search_with_codes)
    trains = result.structured_content.get("trains", [])

    if trains:
        first_train = trains[0]

        assert "departure_time" in first_train
        assert "arrival_time" in first_train
        assert "duration" in first_train
        assert "departure_date" in first_train
        assert "arrival_date" in first_train

        print(f"\n✅ Timing info verified:")
        print(f"   Departure: {first_train['departure_time']} on {first_train['departure_date']}")
        print(f"   Arrival: {first_train['arrival_time']} on {first_train['arrival_date']}")
        print(f"   Duration: {first_train['duration']}")


# ============================================================================
# EDGE CASES - REAL API
# ============================================================================

@pytest.mark.asyncio
async def test_train_search_far_future_date():
    """Test train search with date far in the future."""
    today = datetime.now()
    journey_date = (today + timedelta(days=90)).strftime("%Y-%m-%d")

    payload = {
        "from_station": "Delhi",
        "to_station": "Mumbai",
        "journey_date": journey_date,
    }

    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    print(f"\n🔍 Searching trains 90 days ahead: {journey_date}")

    result = await tool.execute(**payload)

    assert result.structured_content is not None
    trains = result.structured_content.get("trains", [])

    print(f"✅ Far future search returned {len(trains)} trains")


@pytest.mark.asyncio
async def test_train_search_near_date():
    """Test train search with date very soon (tomorrow)."""
    today = datetime.now()
    journey_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")

    payload = {
        "from_station": "Delhi",
        "to_station": "Agra",
        "journey_date": journey_date,
    }

    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    print(f"\n🔍 Searching trains for tomorrow: {journey_date}")

    result = await tool.execute(**payload)

    assert result.structured_content is not None
    trains = result.structured_content.get("trains", [])

    print(f"✅ Near date search returned {len(trains)} trains")


@pytest.mark.asyncio
async def test_train_search_short_route():
    """Test train search on short route."""
    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

    payload = {
        "from_station": "Delhi",
        "to_station": "Agra",
        "journey_date": journey_date,
    }

    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    print(f"\n🔍 Searching short route Delhi-Agra")

    result = await tool.execute(**payload)

    assert result.structured_content is not None
    trains = result.structured_content.get("trains", [])

    print(f"✅ Short route search returned {len(trains)} trains")

    if trains:
        # Short route trains should have short duration
        first = trains[0]
        print(f"   Duration: {first.get('duration')}")


@pytest.mark.asyncio
async def test_train_search_long_route():
    """Test train search on long route."""
    today = datetime.now()
    journey_date = (today + timedelta(days=14)).strftime("%Y-%m-%d")

    payload = {
        "from_station": "Delhi",
        "to_station": "Chennai",
        "journey_date": journey_date,
    }

    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    print(f"\n🔍 Searching long route Delhi-Chennai")

    result = await tool.execute(**payload)

    assert result.structured_content is not None
    trains = result.structured_content.get("trains", [])

    print(f"✅ Long route search returned {len(trains)} trains")

    if trains:
        first = trains[0]
        print(f"   Train: {first.get('train_name')}")
        print(f"   Duration: {first.get('duration')}")
        print(f"   Distance: {first.get('distance')}")


# ============================================================================
# LIMIT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_train_search_with_limit(dummy_train_search_with_codes):
    """Test train search with result limit."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    payload = {**dummy_train_search_with_codes, "_limit": 3}

    print(f"\n🔍 Searching trains with limit=3")

    result = await tool.execute(**payload)

    data = result.structured_content
    trains = data.get("trains", [])

    assert len(trains) <= 3, f"Expected at most 3 trains, got {len(trains)}"

    print(f"✅ Limited search returned {len(trains)} trains (max 3)")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_train_search_response_time(dummy_train_search_with_codes):
    """Test that train search completes in reasonable time."""
    import time

    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    start = time.time()
    result = await tool.execute(**dummy_train_search_with_codes)
    elapsed = time.time() - start

    print(f"\n⏱️  Train search took {elapsed:.2f} seconds")

    # Should complete within 30 seconds
    assert elapsed < 30, f"Search took too long: {elapsed}s"
    assert result.structured_content is not None


@pytest.mark.asyncio
async def test_train_autosuggest_response_time():
    """Test that autosuggest completes quickly."""
    import time

    start = time.time()
    result = await resolve_train_station("Mumbai")
    elapsed = time.time() - start

    print(f"\n⏱️  Autosuggest took {elapsed:.2f} seconds")

    # Should complete within 5 seconds
    assert elapsed < 5, f"Autosuggest took too long: {elapsed}s"
    assert result is not None


# ============================================================================
# MULTIPLE SEARCHES TEST
# ============================================================================

@pytest.mark.asyncio
async def test_multiple_consecutive_train_searches():
    """Test multiple train searches in sequence."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    today = datetime.now()
    journey_date = (today + timedelta(days=14)).strftime("%Y-%m-%d")

    routes = [
        ("Delhi", "Mumbai"),
        ("Mumbai", "Pune"),
        ("Bangalore", "Chennai"),
    ]

    print("\n🔍 Testing multiple consecutive train searches...")

    for from_station, to_station in routes:
        payload = {
            "from_station": from_station,
            "to_station": to_station,
            "journey_date": journey_date,
        }

        result = await tool.execute(**payload)
        assert result.structured_content is not None

        trains = result.structured_content.get("trains", [])
        print(f"   {from_station} → {to_station}: {len(trains)} trains")

    print("✅ All consecutive searches completed")


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_train_search_invalid_date_format():
    """Test train search with invalid date format."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    payload = {
        "from_station": "Delhi",
        "to_station": "Mumbai",
        "journey_date": "25-01-2026",  # Wrong format (should be YYYY-MM-DD)
    }

    print(f"\n🔍 Testing invalid date format: {payload['journey_date']}")

    result = await tool.execute(**payload)

    # Should return an error response
    assert result.is_error is True
    print(f"✅ Correctly returned error for invalid date format")
    print(f"   Error: {result.response_text}")


@pytest.mark.asyncio
async def test_train_search_missing_required_field():
    """Test train search with missing required field."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    payload = {
        "from_station": "Delhi",
        # Missing to_station and journey_date
    }

    print(f"\n🔍 Testing missing required fields")

    result = await tool.execute(**payload)

    # Should return an error response
    assert result.is_error is True
    print(f"✅ Correctly returned error for missing fields")
    print(f"   Error: {result.response_text}")
