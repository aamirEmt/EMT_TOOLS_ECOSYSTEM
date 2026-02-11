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
        _user_type="website"
    )

    # Assertions
    assert not result.is_error
    assert result.html is not None

    # Check structured content
    data = result.structured_content
    assert data.get("train_info") is not None
    assert len(data.get("classes", [])) == 4

    # Save HTML for visual inspection
    if result.html:
        with open("train_availability_nandankanan.html", "w", encoding="utf-8") as f:
            f.write(result.html)

    print(f"\n[PASS] Nandankanan Express UI Test")
    print(f"   HTML saved to: train_availability_nandankanan.html")


@pytest.mark.asyncio
async def test_mewar_express_availability():
    """Test Mewar Express (12963) availability with economy classes."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    journey_date = (datetime.now() + timedelta(days=10)).strftime("%d-%m-%Y")

    result = await tool.execute(
        trainNo="12963",
        journeyDate=journey_date,
        classes=["SL", "3A", "2A"],
        _user_type="website"
    )

    # Assertions
    assert not result.is_error
    assert result.html is not None

    # Check train info
    train_info = result.structured_content.get("train_info", {})
    assert train_info.get("train_name") == "MEWAR EXPRESS"
    assert train_info.get("train_no") == "12963"

    # Save HTML
    if result.html:
        with open("train_availability_mewar.html", "w", encoding="utf-8") as f:
            f.write(result.html)

    print(f"\n[PASS] Mewar Express UI Test")
    print(f"   HTML saved to: train_availability_mewar.html")


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
        _user_type="website"
    )

    # Assertions
    assert not result.is_error
    assert result.html is not None

    # Check all classes returned
    classes = result.structured_content.get("classes", [])
    assert len(classes) == 6

    # Save HTML
    if result.html:
        with open("train_availability_all_classes.html", "w", encoding="utf-8") as f:
            f.write(result.html)

    print(f"\n[PASS] All Classes UI Test")
    print(f"   Train: {result.structured_content['train_info']['train_name']}")
    print(f"   Classes: {len(classes)}")
    print(f"   HTML saved to: train_availability_all_classes.html")


@pytest.mark.asyncio
async def test_shatabdi_availability():
    """Test availability for Shatabdi train."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    journey_date = (datetime.now() + timedelta(days=5)).strftime("%d-%m-%Y")

    result = await tool.execute(
        trainNo="12430",  # Lucknow Shatabdi
        journeyDate=journey_date,
        classes=["CC", "EC"],
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
    """Test availability with premium classes only (1A, 2A)."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    journey_date = (datetime.now() + timedelta(days=20)).strftime("%d-%m-%Y")

    result = await tool.execute(
        trainNo="12302",  # Howrah Rajdhani
        journeyDate=journey_date,
        classes=["1A", "2A"],
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
    """Test availability with economy classes only (SL, 2S)."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    journey_date = (datetime.now() + timedelta(days=8)).strftime("%d-%m-%Y")

    result = await tool.execute(
        trainNo="12616",  # Grand Trunk Express
        journeyDate=journey_date,
        classes=["SL", "2S"],
        _user_type="website"
    )

    # Assertions
    assert not result.is_error
    assert result.html is not None

    # Save HTML
    if result.html:
        with open("train_availability_economy.html", "w", encoding="utf-8") as f:
            f.write(result.html)

    print(f"\n[PASS] Economy Classes UI Test")
    print(f"   HTML saved to: train_availability_economy.html")
