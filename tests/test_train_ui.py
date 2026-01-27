"""
Quick script to test train UI with real API data
Tests train search with HTML rendering
"""

import pytest
from datetime import datetime, timedelta
from tools_factory.trains.train_search_tool import TrainSearchTool


@pytest.mark.asyncio
async def test_train_search_delhi_to_agra():
    """Test train search from Delhi to Agra with UI rendering"""
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    result = await tool.execute(
        fromStation="Delhi",
        toStation="Agra",
        journeyDate=journey_date,
        _limit=5,
        _user_type="website"
    )

    assert not result.is_error

    data = result.structured_content
    assert data is not None
    assert len(data.get("trains", [])) > 0

    # Check that trains have classes with book_now links
    trains = data.get("trains", [])
    if trains:
        first_train = trains[0]
        assert "classes" in first_train
        classes = first_train.get("classes", [])
        if classes:
            first_class = classes[0]
            assert "book_now" in first_class
            assert first_class["book_now"].startswith("https://railways.easemytrip.com/TrainInfo/")

    if result.html:
        with open("train_search_results.html", "w", encoding="utf-8") as f:
            f.write(result.html)


@pytest.mark.asyncio
async def test_train_search_mumbai_to_pune():
    """Test train search from Mumbai to Pune"""
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")

    result = await tool.execute(
        fromStation="Mumbai",
        toStation="Pune",
        journeyDate=journey_date,
        _limit=8,
        _user_type="website"
    )

    assert not result.is_error

    data = result.structured_content
    assert data is not None

    if result.html:
        with open("train_mumbai_pune_results.html", "w", encoding="utf-8") as f:
            f.write(result.html)


@pytest.mark.asyncio
async def test_train_search_with_class_filter():
    """Test train search with specific travel class filter"""
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

    result = await tool.execute(
        fromStation="New Delhi",
        toStation="Varanasi",
        journeyDate=journey_date,
        travelClass="3A",
        _limit=5,
        _user_type="website"
    )

    assert not result.is_error

    data = result.structured_content
    if data and data.get("trains"):
        # If class filter works, all classes should be 3A
        for train in data.get("trains", []):
            for cls in train.get("classes", []):
                assert cls.get("class_code") == "3A"

    if result.html:
        with open("train_class_filter_results.html", "w", encoding="utf-8") as f:
            f.write(result.html)


@pytest.mark.asyncio
async def test_train_search_tatkal_quota():
    """Test train search with Tatkal quota"""
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

    result = await tool.execute(
        fromStation="Delhi",
        toStation="Jaipur",
        journeyDate=journey_date,
        quota="TQ",
        _limit=5,
        _user_type="website"
    )

    assert not result.is_error

    data = result.structured_content
    if data:
        assert data.get("quota") == "TQ"

    if result.html:
        with open("train_tatkal_results.html", "w", encoding="utf-8") as f:
            f.write(result.html)


@pytest.mark.asyncio
async def test_train_search_whatsapp_response():
    """Test train search with WhatsApp response format"""
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    result = await tool.execute(
        fromStation="Chennai",
        toStation="Bangalore",
        journeyDate=journey_date,
        _limit=3,
        _user_type="whatsapp"
    )

    assert not result.is_error

    # WhatsApp response should not have HTML
    assert result.html is None

    # Should have whatsapp_response
    assert result.whatsapp_response is not None
