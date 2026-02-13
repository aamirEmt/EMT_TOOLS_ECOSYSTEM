"""
Test script for train search WhatsApp dual formats.
Tests both class-mentioned and class-not-mentioned response formats.
"""

import pytest
from datetime import datetime, timedelta
from tools_factory.factory import get_tool_factory
import json


@pytest.mark.asyncio
async def test_whatsapp_with_class_mentioned():
    """Test WhatsApp response when class IS mentioned (with availability check)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="NDLS",
        toStation="UDZ",
        journeyDate=journey_date,
        travelClass="3A",  # Class mentioned
        _user_type="whatsapp"
    )

    # Assertions
    assert not result.is_error, f"Should not have errors. Error: {result.response_text}"
    assert result.whatsapp_response is not None, "Should have WhatsApp response"

    # Check WhatsApp response structure
    wa_response = result.whatsapp_response
    assert wa_response.get("whatsapp_json") is not None, "Should have whatsapp_json"

    wa_json = wa_response["whatsapp_json"]

    # Verify class-mentioned format
    assert wa_json.get("is_class_mentioned") is True, "is_class_mentioned should be True"
    assert wa_json.get("trains") is not None, "Should have 'trains' key"
    assert wa_json.get("options") is None, "Should NOT have 'options' key"

    # Verify search_context
    search_context = wa_json.get("search_context", {})
    assert search_context.get("source") == "NDLS"
    assert search_context.get("destination") == "UDZ"
    assert search_context.get("class") == "3A", "Class should be in search_context"
    assert search_context.get("search_id") is not None, "Should have search_id"

    # Verify trains structure
    trains = wa_json.get("trains", [])
    if len(trains) > 0:
        train = trains[0]
        assert "option_id" in train
        assert "train_no" in train
        assert "train_name" in train
        assert "classes" in train, "Should have classes list"
        assert "booking_link" in train, "Should have booking_link"

        # Verify class info
        classes = train.get("classes", [])
        assert len(classes) == 1, "Should have exactly one class (the requested one)"
        class_info = classes[0]
        assert class_info.get("class") == "3A", "Class should match requested"
        assert "status" in class_info, "Should have availability status"
        assert "fare" in class_info, "Should have fare"

        print(f"\n[PASS] WhatsApp + Class Mentioned Test")
        print(f"   Found {len(trains)} bookable trains")
        print(f"   Sample train: {train['train_name']} ({train['train_no']})")
        print(f"   Status: {class_info['status']}")
        print(f"   Fare: Rs.{class_info['fare']}")
        print(f"   Booking: {train['booking_link'][:60]}...")
    else:
        print(f"\n[INFO] No bookable trains found for 3A class (this is OK if none available)")

    # Save response for inspection
    with open("test_whatsapp_class_mentioned.json", "w", encoding="utf-8") as f:
        json.dump(result.whatsapp_response, f, indent=2, ensure_ascii=False)
    print(f"   Response saved to: test_whatsapp_class_mentioned.json")


@pytest.mark.asyncio
async def test_whatsapp_without_class():
    """Test WhatsApp response when class NOT mentioned (no availability check)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="NDLS",
        toStation="UDZ",
        journeyDate=journey_date,
        # NO travelClass parameter
        _user_type="whatsapp"
    )

    # Assertions
    assert not result.is_error, f"Should not have errors. Error: {result.response_text}"
    assert result.whatsapp_response is not None, "Should have WhatsApp response"

    # Check WhatsApp response structure
    wa_response = result.whatsapp_response
    assert wa_response.get("whatsapp_json") is not None, "Should have whatsapp_json"

    wa_json = wa_response["whatsapp_json"]

    # Verify class-NOT-mentioned format
    assert wa_json.get("is_class_mentioned") is False, "is_class_mentioned should be False"
    assert wa_json.get("options") is not None, "Should have 'options' key"
    assert wa_json.get("trains") is None, "Should NOT have 'trains' key"

    # Verify search_context
    search_context = wa_json.get("search_context", {})
    assert search_context.get("source") == "NDLS"
    assert search_context.get("destination") == "UDZ"
    assert search_context.get("class") is None, "Class should be None"
    assert search_context.get("search_id") is not None, "Should have search_id"

    # Verify options structure
    options = wa_json.get("options", [])
    assert len(options) > 0, "Should have at least one train option"

    option = options[0]
    assert "option_id" in option
    assert "train_no" in option
    assert "train_name" in option
    assert "classes" in option, "Should have classes list"
    assert "booking_link" not in option, "Should NOT have booking_link"

    # Verify classes list has multiple classes
    classes = option.get("classes", [])
    assert len(classes) > 0, "Should have at least one class"
    class_info = classes[0]
    assert "class" in class_info, "Should have class code"
    assert "fare" in class_info, "Should have fare"
    assert "status" not in class_info, "Should NOT have status (no availability check)"

    print(f"\n[PASS] WhatsApp + No Class Test")
    print(f"   Found {len(options)} trains")
    print(f"   Sample train: {option['train_name']} ({option['train_no']})")
    print(f"   Classes available: {len(classes)}")
    for cls in classes[:3]:  # Show first 3 classes
        print(f"   - {cls['class']}: Rs.{cls.get('fare', 'N/A')}")

    # Save response for inspection
    with open("test_whatsapp_no_class.json", "w", encoding="utf-8") as f:
        json.dump(result.whatsapp_response, f, indent=2, ensure_ascii=False)
    print(f"   Response saved to: test_whatsapp_no_class.json")


@pytest.mark.asyncio
async def test_website_mode_unaffected():
    """Test that website mode is unaffected by changes (no availability check)."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="NDLS",
        toStation="UDZ",
        journeyDate=journey_date,
        travelClass="3A",  # Class mentioned but website mode
        _user_type="website"
    )

    # Assertions
    assert not result.is_error, f"Should not have errors. Error: {result.response_text}"
    assert result.html is not None, "Website should return HTML"
    assert result.whatsapp_response is None, "Website should NOT have WhatsApp response"
    assert result.structured_content is not None, "Website should have structured content"

    print(f"\n[PASS] Website Mode Test")
    print(f"   HTML length: {len(result.html)} chars")
    print(f"   Trains in result: {len(result.structured_content.get('trains', []))}")
    print(f"   Website mode unaffected by WhatsApp changes")


@pytest.mark.asyncio
async def test_whatsapp_ladies_quota_delhi_jaipur_3ac():
    """Test WhatsApp response with Ladies quota, Delhi to Jaipur, 3AC."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="Delhi",
        toStation="Jaipur",
        journeyDate=journey_date,
        travelClass="3A",
        quota="LD",
        _user_type="whatsapp"
    )

    assert not result.is_error, f"Should not error. Got: {result.response_text}"
    assert result.whatsapp_response is not None, "Should have WhatsApp response"

    wa_response = result.whatsapp_response
    wa_json = wa_response.get("whatsapp_json", {})

    # Verify class-mentioned format
    assert wa_json.get("is_class_mentioned") is True, "is_class_mentioned should be True"
    assert wa_json.get("trains") is not None, "Should have 'trains' key"
    assert wa_json.get("options") is None, "Should NOT have 'options' key"

    # Verify search_context has Ladies quota
    search_context = wa_json.get("search_context", {})
    assert search_context.get("class") == "3A", "Class should be 3A"
    assert search_context.get("quota") == "LD", "Quota should be LD (Ladies)"

    trains = wa_json.get("trains", [])

    if len(trains) > 0:
        # Trains found with available seats
        train = trains[0]
        assert "booking_link" in train, "Should have booking_link"
        assert "classes" in train, "Should have classes"

        class_info = train["classes"][0]
        assert class_info.get("class") == "3A"
        assert "status" in class_info

        # Booking link should contain LD quota
        assert "/LD/" in train["booking_link"], "Booking link should use Ladies quota"

        print(f"\n[PASS] Ladies Quota Delhi-Jaipur 3AC")
        print(f"   Found {len(trains)} bookable trains")
        print(f"   Sample: {train['train_name']} ({train['train_no']})")
        print(f"   Status: {class_info['status']}, Fare: Rs.{class_info.get('fare', 'N/A')}")
        print(f"   Booking: {train['booking_link'][:70]}...")
    else:
        # No seats available - verify response text
        response_text = wa_response.get("response_text", "")
        assert "No trains found" in response_text, \
            f"Should say 'No trains found' when empty. Got: {response_text}"
        assert "3A" in response_text, "Should mention class 3A in no-seats message"

        print(f"\n[PASS] Ladies Quota Delhi-Jaipur 3AC - No seats available")
        print(f"   Response: {response_text}")

    # Save response
    with open("test_whatsapp_ladies_quota.json", "w", encoding="utf-8") as f:
        json.dump(result.whatsapp_response, f, indent=2, ensure_ascii=False)
    print(f"   Response saved to: test_whatsapp_ladies_quota.json")


@pytest.mark.asyncio
async def test_whatsapp_delhi_chandigarh_3a_booking_links():
    """Test WhatsApp response Delhi to Chandigarh 3AC - print booking links."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_trains")

    journey_date = (datetime.now() + timedelta(days=3)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="Delhi",
        toStation="Chandigarh",
        journeyDate=journey_date,
        travelClass="3A",
        _user_type="whatsapp"
    )

    assert not result.is_error, f"Should not error. Got: {result.response_text}"
    assert result.whatsapp_response is not None, "Should have WhatsApp response"

    wa_response = result.whatsapp_response
    wa_json = wa_response.get("whatsapp_json", {})

    assert wa_json.get("is_class_mentioned") is True
    trains = wa_json.get("trains", [])

    print(f"\n[TEST] Delhi → Chandigarh | 3A | {journey_date}")
    print(f"  Response: {wa_response.get('response_text', '')}")
    print(f"  Total trains: {len(trains)}")
    print(f"  {'─' * 60}")

    for train in trains:
        class_info = train.get("classes", [{}])[0]
        print(f"  {train['train_name']} ({train['train_no']})")
        print(f"    Dep: {train['departure_time']} → Arr: {train['arrival_time']} | {train['duration']}")
        print(f"    Status: {class_info.get('status', 'N/A')} | Fare: Rs.{class_info.get('fare', 'N/A')}")
        print(f"    Booking: {train.get('booking_link', 'N/A')}")
        print()

    if not trains:
        print(f"  No bookable trains found.")

    with open("test_whatsapp_delhi_chandigarh.json", "w", encoding="utf-8") as f:
        json.dump(result.whatsapp_response, f, indent=2, ensure_ascii=False)
    print(f"  Response saved to: test_whatsapp_delhi_chandigarh.json")


if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("TRAIN SEARCH WHATSAPP DUAL FORMAT TESTS")
    print("=" * 70)

    async def run_all_tests():
        print("\n1. Testing WhatsApp with class mentioned...")
        await test_whatsapp_with_class_mentioned()

        print("\n2. Testing WhatsApp without class...")
        await test_whatsapp_without_class()

        print("\n3. Testing website mode unaffected...")
        await test_website_mode_unaffected()

        print("\n4. Testing Ladies quota Delhi-Jaipur 3AC...")
        await test_whatsapp_ladies_quota_delhi_jaipur_3ac()

        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETED!")
        print("=" * 70)

    asyncio.run(run_all_tests())
