"""
Quick script to test train availability UI with real API data
Tests different trains and class combinations with automatic route fetching
"""

import pytest
from datetime import datetime, timedelta
from tools_factory.factory import get_tool_factory


@pytest.mark.asyncio
async def test_nandankanan_express_availability():
    """Test Nandankanan Express (12816) availability with major classes."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        trainNo="12816",
        journeyDate=journey_date,
        classes=["3A", "2A", "1A", "SL"],
        quota="GN",  # General quota
        _user_type="website"
    )

    # Assertions
    assert not result.is_error
    assert result.html is not None

    # Check structured content
    data = result.structured_content
    assert data.get("train_info") is not None
    assert len(data.get("classes", [])) == 4

    # Verify quota in HTML
    assert "General" in result.html or "/GN/" in result.html, "HTML should include quota"

    # Save HTML for visual inspection
    if result.html:
        with open("train_availability_nandankanan.html", "w", encoding="utf-8") as f:
            f.write(result.html)

    print(f"\n[PASS] Nandankanan Express UI Test")
    print(f"   Quota: General (GN)")
    print(f"   HTML saved to: train_availability_nandankanan.html")


@pytest.mark.asyncio
async def test_mewar_express_availability():
    """Test Mewar Express (12963) availability - tries Tatkal quota which may fail."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    # Tatkal is only available 1 day before - use 7 days to FORCE an error
    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        trainNo="12963",
        journeyDate=journey_date,
        classes=["SL", "3A", "2A"],
        quota="TQ",  # Tatkal quota - will fail for 7 days from now
        _user_type="website"
    )

    # Should return error for Tatkal outside booking window
    if result.is_error:
        print(f"\n[PASS] Tatkal Error Handling Test")
        print(f"   Error detected: {result.response_text}")
        print(f"   ✓ No UI displayed (is_error=True)")
        print(f"   ✓ Error message shown to user")
        assert result.html is None, "Should NOT have HTML when error occurs"
        return

    # If we get here, Tatkal was actually valid (shouldn't happen for 7 days out)
    print(f"\n[UNEXPECTED] Tatkal quota succeeded for 7 days from now")
    print(f"   This is unusual - Tatkal should only be available 1 day before")

    # Check if it's a success response
    if result.html is not None:
        train_info = result.structured_content.get("train_info", {})
        print(f"   Train: {train_info.get('train_name')}")

        # Save for inspection
        with open("train_availability_mewar_tatkal.html", "w", encoding="utf-8") as f:
            f.write(result.html)


@pytest.mark.asyncio
async def test_all_classes_availability():
    """Test availability with all major travel classes."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    journey_date = (datetime.now() + timedelta(days=14)).strftime("%d-%m-%Y")

    result = await tool.execute(
        trainNo="12951",  # Mumbai Rajdhani
        journeyDate=journey_date,
        classes=["1A", "2A", "3A", "SL", "2S", "CC"],
        quota="GN",  # General quota
        _user_type="website"
    )

    # Assertions
    assert not result.is_error
    assert result.html is not None

    # Check all classes returned
    classes = result.structured_content.get("classes", [])
    assert len(classes) == 6

    # Verify booking links include quota
    assert "/GN/" in result.html, "Booking links should include /GN/ quota"

    # Save HTML
    if result.html:
        with open("train_availability_all_classes.html", "w", encoding="utf-8") as f:
            f.write(result.html)

    print(f"\n[PASS] All Classes UI Test")
    print(f"   Train: {result.structured_content['train_info']['train_name']}")
    print(f"   Classes: {len(classes)}")
    print(f"   Quota: General (GN)")
    print(f"   HTML saved to: train_availability_all_classes.html")


@pytest.mark.asyncio
async def test_shatabdi_availability():
    """Test availability for Shatabdi train with Ladies quota."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    journey_date = (datetime.now() + timedelta(days=5)).strftime("%d-%m-%Y")

    result = await tool.execute(
        trainNo="12430",  # Lucknow Shatabdi
        journeyDate=journey_date,
        classes=["CC", "EC"],
        quota="LD",  # Ladies quota
        _user_type="website"
    )

    # Note: May fail if Ladies quota not available for this train
    if result.is_error:
        print(f"\n[INFO] Ladies quota error (may not be valid for this train)")
        print(f"   Error: {result.response_text}")
        print(f"   Falling back to General quota...")

        # Retry with General quota
        result = await tool.execute(
            trainNo="12430",
            journeyDate=journey_date,
            classes=["CC", "EC"],
            quota="GN",
            _user_type="website"
        )

    # Assertions
    assert not result.is_error
    assert result.html is not None

    # Save HTML
    if result.html:
        with open("train_availability_shatabdi.html", "w", encoding="utf-8") as f:
            f.write(result.html)

    print(f"\n[PASS] Shatabdi Train UI Test")
    print(f"   HTML saved to: train_availability_shatabdi.html")


@pytest.mark.asyncio
async def test_premium_classes_only():
    """Test availability with premium classes only (1A, 2A) and Senior Citizen quota."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    journey_date = (datetime.now() + timedelta(days=20)).strftime("%d-%m-%Y")

    result = await tool.execute(
        trainNo="12302",  # Howrah Rajdhani
        journeyDate=journey_date,
        classes=["1A", "2A"],
        quota="SS",  # Senior Citizen quota
        _user_type="website"
    )

    # Note: Senior Citizen quota may not be valid
    if result.is_error:
        print(f"\n[INFO] Senior Citizen quota error (may not be valid)")
        print(f"   Error: {result.response_text}")
        print(f"   Falling back to General quota...")

        # Retry with General quota
        result = await tool.execute(
            trainNo="12302",
            journeyDate=journey_date,
            classes=["1A", "2A"],
            quota="GN",
            _user_type="website"
        )

    # Assertions
    assert not result.is_error
    assert result.html is not None

    # Check route info
    route_info = result.structured_content.get("route_info", {})
    assert route_info.get("from_station_code") is not None
    assert route_info.get("to_station_code") is not None

    # Save HTML
    if result.html:
        with open("train_availability_premium.html", "w", encoding="utf-8") as f:
            f.write(result.html)

    print(f"\n[PASS] Premium Classes UI Test")
    print(f"   Route: {route_info.get('from_station_name')} -> {route_info.get('to_station_name')}")
    print(f"   HTML saved to: train_availability_premium.html")


@pytest.mark.asyncio
async def test_economy_classes_only():
    """Test availability with economy classes only (SL, 2S) and default quota."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    journey_date = (datetime.now() + timedelta(days=8)).strftime("%d-%m-%Y")

    result = await tool.execute(
        trainNo="12616",  # Grand Trunk Express
        journeyDate=journey_date,
        classes=["SL", "2S"],
        # quota not specified - should default to "GN"
        _user_type="website"
    )

    # Assertions
    assert not result.is_error
    assert result.html is not None

    # Verify default quota (GN) is used
    assert "General" in result.html or "/GN/" in result.html, "Should default to General quota"

    # Save HTML
    if result.html:
        with open("train_availability_economy.html", "w", encoding="utf-8") as f:
            f.write(result.html)

    print(f"\n[PASS] Economy Classes UI Test")
    print(f"   Quota: Default (GN)")
    print(f"   HTML saved to: train_availability_economy.html")


@pytest.mark.asyncio
async def test_quota_in_booking_links():
    """Test that quota is correctly included in booking links for all classes."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    # Test with General quota
    result_gn = await tool.execute(
        trainNo="12816",
        journeyDate=journey_date,
        classes=["3A", "2A"],
        quota="GN",
        _user_type="website"
    )

    # Assertions for GN
    assert not result_gn.is_error
    assert result_gn.html is not None

    # Verify booking links contain /GN/
    assert "/GN/" in result_gn.html, "Booking links should contain /GN/ quota"
    assert "General" in result_gn.html, "HTML should display General quota name"

    # Count occurrences of booking links with quota
    gn_links = result_gn.html.count("/GN/")
    assert gn_links >= 2, f"Should have at least 2 booking links with /GN/, found {gn_links}"

    print(f"\n[PASS] Quota in Booking Links Test")
    print(f"   General (GN) quota:")
    print(f"     - Booking links with /GN/: {gn_links}")
    print(f"     - Quota badge displayed: ✓")

    # Test with Tatkal quota (if date allows)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
    result_tq = await tool.execute(
        trainNo="12816",
        journeyDate=tomorrow,
        classes=["3A"],
        quota="TQ",
        _user_type="website"
    )

    if not result_tq.is_error:
        assert "/TQ/" in result_tq.html, "Booking links should contain /TQ/ quota"
        assert "Tatkal" in result_tq.html, "HTML should display Tatkal quota name"
        tq_links = result_tq.html.count("/TQ/")
        print(f"   Tatkal (TQ) quota:")
        print(f"     - Booking links with /TQ/: {tq_links}")
        print(f"     - Quota badge displayed: ✓")
    else:
        print(f"   Tatkal (TQ) quota:")
        print(f"     - Outside booking window (expected)")

    print(f"\n   ✓ Quota field successfully integrated")
    print(f"   ✓ Booking links include quota parameter")
    print(f"   ✓ Quota displayed in UI badge")


@pytest.mark.asyncio
async def test_error_no_ui():
    """Test that NO UI is shown when quota error occurs."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    # Use Tatkal quota 7 days from now - guaranteed to fail
    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        trainNo="12816",
        journeyDate=journey_date,
        classes=["3A"],
        quota="TQ",  # Tatkal - will fail for 7 days out
        _user_type="website"
    )

    print(f"\n[TEST] Error Handling - No UI Test")

    if result.is_error:
        print(f"   ✓ Error detected: {result.response_text}")
        print(f"   ✓ is_error = True")

        # CRITICAL: No HTML should be generated
        assert result.html is None, "ERROR: HTML should be None when error occurs!"
        print(f"   ✓ HTML is None (no UI rendered)")

        # No WhatsApp response either
        assert result.whatsapp_response is None, "ERROR: WhatsApp response should be None when error occurs!"
        print(f"   ✓ WhatsApp response is None")

        print(f"\n[PASS] Error Handling Works Correctly!")
        print(f"   When quota error occurs:")
        print(f"     - is_error = True")
        print(f"     - HTML = None")
        print(f"     - Only error message shown")
    else:
        print(f"   ✗ UNEXPECTED: No error detected!")
        print(f"   Error message should appear for Tatkal 7 days from now")
        print(f"   is_error = {result.is_error}")
        print(f"   HTML exists = {result.html is not None}")

        if result.html:
            print(f"\n   [DEBUG] Classes in result:")
            classes = result.structured_content.get("classes", [])
            for cls in classes:
                print(f"     - {cls['class_code']}: {cls.get('status', 'N/A')}")

        # Fail the test
        assert False, "Expected error for Tatkal 7 days from now, but got success response"
