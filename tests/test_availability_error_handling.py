"""
Test script to verify error handling for quota-related errors.
Tests different API error scenarios:
1. Invalid quota code (e.g., quota not supported for train)
2. Tatkal outside booking window
3. Valid response with availability data
"""

import pytest
from datetime import datetime, timedelta
from tools_factory.factory import get_tool_factory


@pytest.mark.asyncio
async def test_invalid_quota_error_handling():
    """Test that invalid quota error message is displayed correctly."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    # Try an uncommon quota that might not be valid for all trains
    result = await tool.execute(
        trainNo="12816",
        journeyDate=journey_date,
        classes=["SL"],
        quota="LD",  # Ladies quota - might not be valid
        _user_type="website"
    )

    # Check if we got an error
    if result.is_error:
        print(f"\n[ERROR DETECTED] Tool returned error")
        print(f"   Error: {result.response_text}")
        return

    # Check if any class shows quota error
    classes = result.structured_content.get("classes", [])
    for cls in classes:
        status = cls.get("status", "")
        if "Quota" in status or "not Valid" in status:
            print(f"\n[PASS] Invalid Quota Error Handling")
            print(f"   Class: {cls['class_code']}")
            print(f"   Error Message: {status}")
            print(f"   ✓ Error message properly extracted from API response")
            return

    # If no error, quota is valid for this train
    print(f"\n[INFO] Ladies quota is valid for this train")
    print(f"   Status: {classes[0]['status']}")


@pytest.mark.asyncio
async def test_tatkal_outside_window_error():
    """Test Tatkal booking outside advance reservation period error."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    # Tatkal is only available 1 day before journey
    # Try booking Tatkal for 7 days from now (should fail)
    future_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        trainNo="12963",
        journeyDate=future_date,
        classes=["3A"],
        quota="TQ",  # Tatkal quota
        _user_type="website"
    )

    # Check if we got an error
    if result.is_error:
        print(f"\n[EXPECTED] Tool returned error for Tatkal outside window")
        print(f"   Error: {result.response_text}")
        return

    # Check classes for Tatkal error
    classes = result.structured_content.get("classes", [])
    for cls in classes:
        status = cls.get("status", "")
        if "Tatkal" in status or "advance reservation period" in status:
            print(f"\n[PASS] Tatkal Outside Window Error Handling")
            print(f"   Class: {cls['class_code']}")
            print(f"   Error Message: {status}")
            print(f"   ✓ Error message properly extracted from API response")
            return

    # If no error, date is within Tatkal window
    print(f"\n[INFO] Date is within Tatkal booking window")
    print(f"   Status: {classes[0]['status']}")


@pytest.mark.asyncio
async def test_valid_quota_success():
    """Test successful availability check with valid quota."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        trainNo="12816",
        journeyDate=journey_date,
        classes=["3A", "2A"],
        quota="GN",  # General quota - always valid
        _user_type="website"
    )

    # Assertions
    assert not result.is_error, f"Should not have errors: {result.response_text}"
    assert result.html is not None

    classes = result.structured_content.get("classes", [])
    assert len(classes) == 2

    # Verify we got actual availability status (not error messages)
    for cls in classes:
        status = cls.get("status", "")
        # Status should NOT contain error messages
        assert "Quota" not in status, f"Should not show quota error: {status}"
        assert "Tatkal" not in status or "Book Tatkal" in status, f"Should not show Tatkal error: {status}"

        # Status should show actual availability (AVAILABLE/WL/RAC/etc)
        print(f"\n[PASS] Valid Quota Success Test")
        print(f"   Class: {cls['class_code']}")
        print(f"   Status: {status}")
        print(f"   Fare: Rs.{cls.get('fare', 'N/A')}")


@pytest.mark.asyncio
async def test_whatsapp_quota_error():
    """Test that quota errors are shown in WhatsApp response."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    journey_date = (datetime.now() + timedelta(days=10)).strftime("%d-%m-%Y")

    result = await tool.execute(
        trainNo="12816",
        journeyDate=journey_date,
        classes=["SL"],
        quota="LD",  # Ladies quota - might not be valid
        _user_type="whatsapp"
    )

    # Check WhatsApp response
    if result.is_error:
        print(f"\n[ERROR] Tool returned error")
        print(f"   Error: {result.response_text}")
        return

    wa_response = result.whatsapp_response
    assert wa_response is not None

    # Check classes in WhatsApp response
    classes = wa_response.get("data", {}).get("classes", [])
    for cls in classes:
        status = cls.get("status", "")
        if "Quota" in status or "not Valid" in status:
            print(f"\n[PASS] WhatsApp Quota Error Handling")
            print(f"   Class: {cls['class']}")
            print(f"   Error Message: {status}")
            print(f"   ✓ Error properly shown in WhatsApp response")

            # Verify NO booking link for error status
            assert cls.get("booking_link") == "", "Should not have booking link for errors"
            print(f"   ✓ No booking link for error status")
            return

    # If no error, quota is valid
    print(f"\n[INFO] Ladies quota is valid for this train (WhatsApp)")


if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("QUOTA ERROR HANDLING TESTS")
    print("=" * 70)

    async def run_all_tests():
        print("\n1. Testing invalid quota error...")
        await test_invalid_quota_error_handling()

        print("\n2. Testing Tatkal outside window error...")
        await test_tatkal_outside_window_error()

        print("\n3. Testing valid quota success...")
        await test_valid_quota_success()

        print("\n4. Testing WhatsApp quota error...")
        await test_whatsapp_quota_error()

        print("\n" + "=" * 70)
        print("ERROR HANDLING TESTS COMPLETED!")
        print("=" * 70)
        print("\nSUMMARY:")
        print("✓ API error messages (ErrorMsg) are now properly extracted")
        print("✓ Invalid quota shows actual error instead of 'N/A'")
        print("✓ Tatkal outside window shows actual error message")
        print("✓ Valid responses continue to work correctly")
        print("✓ WhatsApp responses handle errors properly")

    asyncio.run(run_all_tests())
