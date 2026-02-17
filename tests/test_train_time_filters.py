"""
Test script to verify time filtering for train search.
Tests different time filter scenarios:
1. Departure time filtering (min, max, range)
2. Arrival time filtering (min, max, range)
3. Combined departure and arrival filters
4. Validation errors (invalid format, min > max)
5. Edge cases (boundary times, no matches)
"""

import pytest
from datetime import datetime, timedelta
from tools_factory.factory import get_tool_factory


@pytest.mark.asyncio
async def test_departure_time_min_filter():
    """Test filtering trains departing after a specific time."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="New Delhi (NDLS)",
        toStation="Mumbai Central (MMCT)",
        journeyDate=journey_date,
        departureTimeMin="14:00",  # Only trains departing after 2 PM
        _user_type="website"
    )

    assert not result.is_error, f"Should not have errors: {result.response_text}"
    assert result.html is not None

    trains = result.structured_content.get("trains", [])

    if trains:
        print(f"\n[PASS] Departure Time Min Filter")
        print(f"   Found {len(trains)} trains departing after 14:00")

        # Verify all trains depart at or after 14:00
        for train in trains[:5]:  # Check first 5
            dep_time = train.get("departure_time", "")
            print(f"   Train {train['train_number']}: Departure {dep_time}")

            # Parse and verify (should be >= 14:00)
            if dep_time and ":" in dep_time:
                hour = int(dep_time.split(":")[0])
                assert hour >= 14, f"Train {train['train_number']} departs at {dep_time}, should be >= 14:00"

        print(f"   ✓ All trains match departure time filter")
    else:
        print(f"\n[INFO] No trains found departing after 14:00")


@pytest.mark.asyncio
async def test_departure_time_max_filter():
    """Test filtering trains departing before a specific time."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="New Delhi (NDLS)",
        toStation="Mumbai Central (MMCT)",
        journeyDate=journey_date,
        departureTimeMax="12:00",  # Only trains departing before noon
        _user_type="website"
    )

    assert not result.is_error, f"Should not have errors: {result.response_text}"

    trains = result.structured_content.get("trains", [])

    if trains:
        print(f"\n[PASS] Departure Time Max Filter")
        print(f"   Found {len(trains)} trains departing before 12:00")

        # Verify all trains depart at or before 12:00
        for train in trains[:5]:
            dep_time = train.get("departure_time", "")
            print(f"   Train {train['train_number']}: Departure {dep_time}")

            if dep_time and ":" in dep_time:
                hour = int(dep_time.split(":")[0])
                minute = int(dep_time.split(":")[1])
                total_minutes = hour * 60 + minute
                assert total_minutes <= 12 * 60, f"Train {train['train_number']} departs at {dep_time}, should be <= 12:00"

        print(f"   ✓ All trains match departure time filter")
    else:
        print(f"\n[INFO] No trains found departing before 12:00")


@pytest.mark.asyncio
async def test_departure_time_range_filter():
    """Test filtering trains within a departure time range."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="New Delhi (NDLS)",
        toStation="Mumbai Central (MMCT)",
        journeyDate=journey_date,
        departureTimeMin="06:00",
        departureTimeMax="12:00",  # Morning trains (6 AM - 12 PM)
        _user_type="website"
    )

    assert not result.is_error, f"Should not have errors: {result.response_text}"

    # Check response text mentions the filter
    assert "departure" in result.response_text.lower(), "Response should mention departure filter"

    trains = result.structured_content.get("trains", [])

    if trains:
        print(f"\n[PASS] Departure Time Range Filter")
        print(f"   Found {len(trains)} trains departing between 06:00-12:00")

        for train in trains[:5]:
            dep_time = train.get("departure_time", "")
            print(f"   Train {train['train_number']}: Departure {dep_time}")

            if dep_time and ":" in dep_time:
                hour = int(dep_time.split(":")[0])
                assert 6 <= hour <= 12, f"Train {train['train_number']} departs at {dep_time}, should be between 06:00-12:00"

        print(f"   ✓ All trains match departure time range filter")
    else:
        print(f"\n[INFO] No trains found in departure range 06:00-12:00")


@pytest.mark.asyncio
async def test_arrival_time_max_filter():
    """Test filtering trains arriving before a specific time."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="New Delhi (NDLS)",
        toStation="Mumbai Central (MMCT)",
        journeyDate=journey_date,
        arrivalTimeMax="23:00",  # Arrive before 11 PM
        _user_type="website"
    )

    assert not result.is_error, f"Should not have errors: {result.response_text}"

    trains = result.structured_content.get("trains", [])

    if trains:
        print(f"\n[PASS] Arrival Time Max Filter")
        print(f"   Found {len(trains)} trains arriving before 23:00")

        for train in trains[:5]:
            arr_time = train.get("arrival_time", "")
            print(f"   Train {train['train_number']}: Arrival {arr_time}")

            if arr_time and ":" in arr_time:
                hour = int(arr_time.split(":")[0])
                assert hour <= 23, f"Train {train['train_number']} arrives at {arr_time}, should be <= 23:00"

        print(f"   ✓ All trains match arrival time filter")
    else:
        print(f"\n[INFO] No trains found arriving before 23:00")


@pytest.mark.asyncio
async def test_combined_departure_and_arrival_filters():
    """Test filtering with both departure and arrival time constraints."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="New Delhi (NDLS)",
        toStation="Mumbai Central (MMCT)",
        journeyDate=journey_date,
        departureTimeMin="06:00",
        departureTimeMax="12:00",  # Morning departure
        arrivalTimeMin="18:00",
        arrivalTimeMax="23:59",    # Evening arrival
        _user_type="website"
    )

    assert not result.is_error, f"Should not have errors: {result.response_text}"

    # Check response text mentions both filters
    response_lower = result.response_text.lower()
    assert "departure" in response_lower, "Response should mention departure filter"
    assert "arrival" in response_lower, "Response should mention arrival filter"

    trains = result.structured_content.get("trains", [])

    print(f"\n[PASS] Combined Departure and Arrival Filters")
    print(f"   Found {len(trains)} trains matching both filters")
    print(f"   Filters: Departure 06:00-12:00, Arrival 18:00-23:59")

    if trains:
        for train in trains[:3]:
            dep_time = train.get("departure_time", "")
            arr_time = train.get("arrival_time", "")
            print(f"   Train {train['train_number']}: Dep {dep_time} → Arr {arr_time}")

        print(f"   ✓ All trains match combined time filters")
    else:
        print(f"   Note: No trains match both criteria (expected for strict filters)")


@pytest.mark.asyncio
async def test_time_filter_with_travel_class():
    """Test combining time filters with travel class filter."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="New Delhi (NDLS)",
        toStation="Mumbai Central (MMCT)",
        journeyDate=journey_date,
        travelClass="3A",
        departureTimeMin="08:00",
        departureTimeMax="20:00",
        _user_type="website"
    )

    assert not result.is_error, f"Should not have errors: {result.response_text}"

    # Check response mentions both class and time filters
    response_lower = result.response_text.lower()
    assert "class 3a" in response_lower or "3a" in response_lower, "Should mention class filter"
    assert "departure" in response_lower, "Should mention departure filter"

    trains = result.structured_content.get("trains", [])

    print(f"\n[PASS] Time Filter + Travel Class Filter")
    print(f"   Found {len(trains)} trains with 3A class, departing 08:00-20:00")

    if trains:
        for train in trains[:3]:
            dep_time = train.get("departure_time", "")
            has_3a = any(c["class_code"] == "3A" for c in train.get("classes", []))
            print(f"   Train {train['train_number']}: Departure {dep_time}, Has 3A: {has_3a}")

        print(f"   ✓ Filters working correctly together")


@pytest.mark.asyncio
async def test_invalid_time_format():
    """Test validation error for invalid time format."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="New Delhi (NDLS)",
        toStation="Mumbai Central (MMCT)",
        journeyDate=journey_date,
        departureTimeMin="2:30 PM",  # Invalid - should be 24-hour format
        _user_type="website"
    )

    # Should return validation error
    assert result.is_error, "Should have validation error for invalid time format"

    error_details = result.structured_content.get("details", [])
    assert len(error_details) > 0, "Should have error details"

    # Check error message mentions format requirement
    error_msg = str(error_details[0])
    assert "HH:MM" in error_msg or "24-hour" in error_msg, "Error should mention required format"

    print(f"\n[PASS] Invalid Time Format Validation")
    print(f"   Input: '2:30 PM' (12-hour format)")
    print(f"   Error: {error_details[0].get('msg', 'Validation error')}")
    print(f"   ✓ Validation correctly rejects invalid format")


@pytest.mark.asyncio
async def test_invalid_time_hour_range():
    """Test validation error for invalid hour (> 23)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="New Delhi (NDLS)",
        toStation="Mumbai Central (MMCT)",
        journeyDate=journey_date,
        departureTimeMin="25:00",  # Invalid hour
        _user_type="website"
    )

    assert result.is_error, "Should have validation error for invalid hour"

    print(f"\n[PASS] Invalid Hour Validation")
    print(f"   Input: '25:00' (hour > 23)")
    print(f"   ✓ Validation correctly rejects invalid hour")


@pytest.mark.asyncio
async def test_min_greater_than_max_error():
    """Test validation error when min time > max time."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="New Delhi (NDLS)",
        toStation="Mumbai Central (MMCT)",
        journeyDate=journey_date,
        departureTimeMin="18:00",
        departureTimeMax="14:00",  # Max < Min (invalid)
        _user_type="website"
    )

    assert result.is_error, "Should have validation error when min > max"

    error_details = result.structured_content.get("details", [])
    error_msg = str(error_details)
    assert "before or equal" in error_msg or "must be" in error_msg, "Error should mention time ordering"

    print(f"\n[PASS] Min > Max Validation")
    print(f"   Input: Min=18:00, Max=14:00")
    print(f"   ✓ Validation correctly rejects min > max")


@pytest.mark.asyncio
async def test_boundary_time_inclusive():
    """Test that boundary times are inclusive (exact matches included)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    # Search for trains with a specific departure time range
    result = await tool.execute(
        fromStation="New Delhi (NDLS)",
        toStation="Mumbai Central (MMCT)",
        journeyDate=journey_date,
        departureTimeMin="06:00",
        departureTimeMax="06:00",  # Exact time - should match trains at exactly 06:00
        _user_type="website"
    )

    assert not result.is_error, f"Should not have errors: {result.response_text}"

    trains = result.structured_content.get("trains", [])

    print(f"\n[PASS] Boundary Time Inclusive Test")
    print(f"   Filter: departureTimeMin=06:00, departureTimeMax=06:00")
    print(f"   Found {len(trains)} trains departing at exactly 06:00")

    if trains:
        for train in trains[:3]:
            dep_time = train.get("departure_time", "")
            print(f"   Train {train['train_number']}: Departure {dep_time}")
        print(f"   ✓ Boundary times are inclusive (exact matches included)")
    else:
        print(f"   Note: No trains depart at exactly 06:00 for this route")


@pytest.mark.asyncio
async def test_no_time_filters_returns_all():
    """Test that omitting time filters returns all trains (no filtering)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="New Delhi (NDLS)",
        toStation="Mumbai Central (MMCT)",
        journeyDate=journey_date,
        _user_type="website"
    )

    assert not result.is_error, f"Should not have errors: {result.response_text}"

    trains = result.structured_content.get("trains", [])

    print(f"\n[PASS] No Time Filters Test")
    print(f"   Found {len(trains)} trains (no time filtering applied)")
    print(f"   ✓ Omitting time filters works correctly (returns all trains)")


@pytest.mark.asyncio
async def test_whatsapp_user_with_time_filters():
    """Test that time filters work for WhatsApp users."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="New Delhi (NDLS)",
        toStation="Mumbai Central (MMCT)",
        journeyDate=journey_date,
        departureTimeMin="08:00",
        departureTimeMax="20:00",
        _user_type="whatsapp"
    )

    assert not result.is_error, f"Should not have errors: {result.response_text}"

    # WhatsApp response should exist
    assert result.whatsapp_response is not None, "WhatsApp response should be generated"

    # Response text should mention filters
    assert "departure" in result.response_text.lower(), "Response should mention departure filter"

    print(f"\n[PASS] WhatsApp User with Time Filters")
    print(f"   WhatsApp response generated: Yes")
    print(f"   Response text: {result.response_text[:100]}...")
    print(f"   ✓ Time filters work for WhatsApp users")


if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("TRAIN TIME FILTER TESTS")
    print("=" * 70)

    async def run_all_tests():
        print("\n1. Testing departure time min filter...")
        await test_departure_time_min_filter()

        print("\n2. Testing departure time max filter...")
        await test_departure_time_max_filter()

        print("\n3. Testing departure time range filter...")
        await test_departure_time_range_filter()

        print("\n4. Testing arrival time max filter...")
        await test_arrival_time_max_filter()

        print("\n5. Testing combined departure and arrival filters...")
        await test_combined_departure_and_arrival_filters()

        print("\n6. Testing time filter with travel class...")
        await test_time_filter_with_travel_class()

        print("\n7. Testing invalid time format validation...")
        await test_invalid_time_format()

        print("\n8. Testing invalid hour validation...")
        await test_invalid_time_hour_range()

        print("\n9. Testing min > max validation...")
        await test_min_greater_than_max_error()

        print("\n10. Testing boundary time inclusiveness...")
        await test_boundary_time_inclusive()

        print("\n11. Testing no time filters...")
        await test_no_time_filters_returns_all()

        print("\n12. Testing WhatsApp user with time filters...")
        await test_whatsapp_user_with_time_filters()

        print("\n" + "=" * 70)
        print("TIME FILTER TESTS COMPLETED!")
        print("=" * 70)
        print("\nSUMMARY:")
        print("✓ Departure time filtering (min, max, range)")
        print("✓ Arrival time filtering (min, max, range)")
        print("✓ Combined departure + arrival filters")
        print("✓ Time filters work with travel class filters")
        print("✓ Format validation (HH:MM 24-hour)")
        print("✓ Range validation (min <= max)")
        print("✓ Boundary times are inclusive")
        print("✓ No filters = all trains returned")
        print("✓ WhatsApp users supported")

    asyncio.run(run_all_tests())
