"""Test cases for Train Status Check tool."""

import pytest
from tools_factory.factory import get_tool_factory


@pytest.mark.asyncio
async def test_train_status_tool_exists():
    """Test that the train status tool is registered in the factory."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_status")
    assert tool is not None
    assert tool.metadata.name == "check_train_status"
    assert tool.metadata.category == "travel"
    assert "train" in tool.metadata.tags


@pytest.mark.asyncio
async def test_train_status_get_available_dates():
    """Test fetching available trackable dates for a train."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_status")

    # Call without date to get available dates
    result = await tool.execute(trainNumber="12618")

    assert result.is_error is False
    assert result.structured_content is not None
    assert "available_dates" in result.structured_content
    assert len(result.structured_content["available_dates"]) > 0

    # Check date structure
    first_date = result.structured_content["available_dates"][0]
    assert "date" in first_date
    assert "day_name" in first_date
    assert "formatted_date" in first_date


@pytest.mark.asyncio
async def test_train_status_with_valid_date():
    """Test getting train status with a valid trackable date."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_status")

    # First get available dates
    dates_result = await tool.execute(trainNumber="12618")
    available_dates = dates_result.structured_content.get("available_dates", [])

    if available_dates:
        # Use the first available date
        valid_date = available_dates[0]["date"]
        result = await tool.execute(trainNumber="12618", journeyDate=valid_date)

        assert result.is_error is False
        assert result.structured_content is not None
        assert "stations" in result.structured_content
        assert len(result.structured_content["stations"]) > 0
        assert "origin_station" in result.structured_content
        assert "destination_station" in result.structured_content


@pytest.mark.asyncio
async def test_train_status_invalid_date():
    """Test that invalid/non-trackable date returns error with suggestions."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_status")

    # Use a date far in the future that won't be trackable
    result = await tool.execute(trainNumber="12618", journeyDate="15-02-2026")

    assert result.is_error is True
    assert "INVALID_DATE" in str(result.structured_content.get("error", ""))
    assert "available_dates" in result.structured_content
    assert "not trackable" in result.response_text.lower()


@pytest.mark.asyncio
async def test_train_status_invalid_train_number_format():
    """Test that invalid train number format returns validation error."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_status")

    # Test with non-numeric train number
    result = await tool.execute(trainNumber="abc")

    assert result.is_error is True
    assert "VALIDATION_ERROR" in str(result.structured_content.get("error", ""))


@pytest.mark.asyncio
async def test_train_status_train_number_too_short():
    """Test that too short train number returns validation error."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_status")

    result = await tool.execute(trainNumber="12")

    assert result.is_error is True
    assert "VALIDATION_ERROR" in str(result.structured_content.get("error", ""))


@pytest.mark.asyncio
async def test_train_status_html_rendering():
    """Test that HTML is generated for website users."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_status")

    # First get available dates
    dates_result = await tool.execute(trainNumber="12618")
    available_dates = dates_result.structured_content.get("available_dates", [])

    if available_dates:
        valid_date = available_dates[0]["date"]
        result = await tool.execute(
            trainNumber="12618",
            journeyDate=valid_date,
            _user_type="website",
        )

        assert result.is_error is False
        assert result.html is not None
        assert len(result.html) > 1000  # Should be substantial HTML
        assert "tst-card" in result.html
        assert "tst-header" in result.html
        assert "tst-dropdown" in result.html


@pytest.mark.asyncio
async def test_train_status_whatsapp_format():
    """Test WhatsApp response format."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_status")

    # First get available dates
    dates_result = await tool.execute(trainNumber="12618")
    available_dates = dates_result.structured_content.get("available_dates", [])

    if available_dates:
        valid_date = available_dates[0]["date"]
        result = await tool.execute(
            trainNumber="12618",
            journeyDate=valid_date,
            _user_type="whatsapp",
        )

        assert result.is_error is False
        assert result.whatsapp_response is not None
        assert result.structured_content is None  # Should be None for WhatsApp
        assert result.html is None  # No HTML for WhatsApp

        # Check WhatsApp response structure
        wa_response = result.whatsapp_response
        assert "whatsapp_json" in wa_response
        assert wa_response["whatsapp_json"]["type"] == "train_status"
        assert "stations" in wa_response["whatsapp_json"]


@pytest.mark.asyncio
async def test_train_status_station_structure():
    """Test that station data has correct structure."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_status")

    dates_result = await tool.execute(trainNumber="12618")
    available_dates = dates_result.structured_content.get("available_dates", [])

    if available_dates:
        valid_date = available_dates[0]["date"]
        result = await tool.execute(trainNumber="12618", journeyDate=valid_date)

        if not result.is_error:
            stations = result.structured_content.get("stations", [])
            assert len(stations) > 0

            # Check first station (origin)
            origin = stations[0]
            assert origin["is_origin"] is True
            assert "station_code" in origin
            assert "station_name" in origin
            assert "departure_time" in origin

            # Check last station (destination)
            destination = stations[-1]
            assert destination["is_destination"] is True
            assert "arrival_time" in destination


@pytest.mark.asyncio
async def test_train_status_ui_generation():
    """Test UI generation and save HTML file for visual inspection."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_status")

    # Get available dates first
    dates_result = await tool.execute(trainNumber="12618")
    available_dates = dates_result.structured_content.get("available_dates", [])

    assert len(available_dates) > 0, "No available dates found"

    # Use the first available date (Today if available)
    valid_date = available_dates[0]["date"]

    # Get train status
    result = await tool.execute(
        trainNumber="12618",
        journeyDate=valid_date,
        _user_type="website",
    )

    assert result.is_error is False, f"Error: {result.response_text}"
    assert result.html is not None, "HTML should be generated"

    # Verify HTML contains key elements
    html = result.html
    assert "tst-card" in html
    assert "tst-header" in html
    assert "tst-train-name" in html
    assert "tst-dropdown" in html
    assert "tst-stations-list" in html

    # Check that stations are rendered
    stations = result.structured_content.get("stations", [])
    assert len(stations) > 0

    # Verify origin and destination codes are in the HTML
    origin_code = result.structured_content.get("origin_code", "")
    destination_code = result.structured_content.get("destination_code", "")
    assert origin_code in html
    assert destination_code in html

    # Check for live tracking info
    is_live = result.structured_content.get("is_live", False)
    distance_percentage = result.structured_content.get("distance_percentage", "")

    # Save HTML file for visual inspection
    with open("train_status_ui_test.html", "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Train Status UI Test - {result.structured_content.get('train_number', '')} {result.structured_content.get('train_name', '')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            margin: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 20px;
        }}
        .meta {{
            background: #fff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
            font-size: 13px;
        }}
        .meta p {{
            margin: 5px 0;
            color: #666;
        }}
        .live-badge {{
            display: inline-block;
            background: #4caf50;
            color: #fff;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-left: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Train Status UI Test {'<span class="live-badge">LIVE</span>' if is_live else ''}</h1>
        <div class="meta">
            <p><strong>Train:</strong> {result.structured_content.get('train_number', '')} - {result.structured_content.get('train_name', '')}</p>
            <p><strong>Route:</strong> {origin_code} → {destination_code}</p>
            <p><strong>Date:</strong> {result.structured_content.get('formatted_date', '')}</p>
            <p><strong>Live:</strong> {is_live}</p>
            {'<p><strong>Progress:</strong> ' + distance_percentage + '</p>' if distance_percentage else ''}
            <p><strong>Stations:</strong> {len(stations)}</p>
        </div>
        {html}
    </div>
</body>
</html>""")

    print(f"\n{'='*60}")
    print("Train Status UI Test Results")
    print(f"{'='*60}")
    print(f"Train: {result.structured_content.get('train_number', '')} - {result.structured_content.get('train_name', '')}")
    print(f"Route: {origin_code} -> {destination_code}")
    print(f"Date: {result.structured_content.get('formatted_date', '')}")
    print(f"Live: {is_live}")
    if distance_percentage:
        print(f"Progress: {distance_percentage}")
    print(f"Stations: {len(stations)}")
    print(f"HTML Size: {len(html)} characters")
    print(f"\nHTML saved to: train_status_ui_test.html")
    print(f"{'='*60}")


@pytest.mark.asyncio
async def test_train_status_dates_ui_generation():
    """Test available dates UI generation."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_status")

    # Call without date to get available dates UI
    result = await tool.execute(trainNumber="12618", _user_type="website")

    assert result.is_error is False
    assert result.html is not None
    assert "train-dates-widget" in result.html

    # Check that dates are rendered
    available_dates = result.structured_content.get("available_dates", [])
    for date_info in available_dates:
        assert date_info["formatted_date"] in result.html


@pytest.mark.asyncio
async def test_train_status_different_trains():
    """Test train status for different train numbers."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_status")

    train_numbers = ["12301", "12302", "12618"]  # Rajdhani trains

    for train_no in train_numbers:
        result = await tool.execute(trainNumber=train_no)

        # Should either return dates or an error for non-existent train
        assert result.structured_content is not None
        if not result.is_error:
            assert "available_dates" in result.structured_content
