"""
Quick script to test train status UI with real API data.
Tests train status check with HTML rendering (date picker + status timeline).
"""

import pytest
import json
from datetime import datetime, timedelta
from tools_factory.trains.Train_StatusCheck.train_status_tool import TrainStatusTool


@pytest.mark.asyncio
async def test_status_no_date_shows_date_picker():
    """Test: No date provided → should render date picker UI with clickable dates."""
    tool = TrainStatusTool()

    result = await tool.execute(
        trainNumber="12302",
        _user_type="website"
    )

    assert not result.is_error, f"Should not error. Got: {result.response_text}"
    assert result.html is not None, "Should have HTML output"

    html = result.html

    # Date picker structure
    assert 'class="train-dates-widget"' in html, "Should have date picker widget"
    assert 'data-train-number="12302"' in html, "Widget should have train number data attr"
    assert "Select a date to check status" in html, "Should have subtitle"

    # Clickable dates
    assert "tdt-date-item" in html, "Should have date items"
    assert "data-date=" in html, "Date items should have data-date attribute"
    assert "cursor: pointer" in html, "Date items should be clickable"

    # Script block for API calls
    assert "<script>" in html, "Should have script block"
    assert "fetchTrainStatus" in html, "Should have fetchTrainStatus function"
    assert "AUTOSUGGEST_URL" in html, "Should have autosuggest URL"
    assert "LIVE_STATUS_URL" in html, "Should have live status URL"
    assert "buildStatusHtml" in html, "Should have buildStatusHtml function"

    # Available dates in structured content
    data = result.structured_content
    assert data is not None
    dates = data.get("available_dates", [])
    assert len(dates) > 0, "Should have available dates"

    print(f"\n[PASS] Date Picker UI Test")
    print(f"   Train: 12302")
    print(f"   Available dates: {len(dates)}")
    for d in dates[:5]:
        display = d.get("display_day", "")
        label = f" ({display})" if display else ""
        print(f"     {d['formatted_date']} - {d['day_name']}{label}")
    print(f"   HTML length: {len(html)} chars")
    print(f"   Has script block: True")
    print(f"   Has clickable dates: True")

    if html:
        with open("train_status_date_picker.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"   HTML saved: train_status_date_picker.html")


@pytest.mark.asyncio
async def test_status_with_date_shows_timeline():
    """Test: Date provided → should render full status timeline UI."""
    tool = TrainStatusTool()

    # First get available dates
    dates_result = await tool.execute(
        trainNumber="12302",
        _user_type="website"
    )

    data = dates_result.structured_content
    dates = data.get("available_dates", [])
    assert len(dates) > 0, "Need at least one available date"

    # Use the first available date
    test_date = dates[0]["date"]

    result = await tool.execute(
        trainNumber="12302",
        journeyDate=test_date,
        _user_type="website"
    )

    assert not result.is_error, f"Should not error. Got: {result.response_text}"
    assert result.html is not None, "Should have HTML output"

    html = result.html

    # Status card structure
    assert 'class="train-status"' in html, "Should have status card"
    assert 'class="status-card"' in html, "Should have status card wrapper"
    assert 'class="status-header"' in html, "Should have header"

    # Train info
    assert "12302" in html, "Should show train number"
    assert 'class="status-train-name"' in html, "Should have train name"
    assert 'class="status-train-no"' in html, "Should have train number badge"

    # Running days
    assert 'class="day-chip' in html, "Should have running day chips"

    # Timing row
    assert 'class="status-time"' in html, "Should have departure/arrival times"
    assert 'class="status-stn-code"' in html, "Should have station codes"

    # Timeline
    assert 'class="status-timeline"' in html, "Should have timeline section"
    assert 'class="timeline-dot' in html, "Should have timeline dots"
    assert 'class="timeline-line' in html, "Should have timeline lines"
    assert 'class="stop-station-name"' in html, "Should have station names"

    # Show All button
    assert 'class="show-more-btn"' in html, "Should have Show All button"
    assert "Show All" in html, "Button should say Show All"

    # Footer
    assert 'class="status-footer"' in html, "Should have footer"
    assert "stations" in html, "Footer should mention station count"

    # Structured content
    status_data = result.structured_content
    stations = status_data.get("stations", [])
    is_live = status_data.get("is_live", False)

    print(f"\n[PASS] Status Timeline UI Test")
    print(f"   Train: {status_data.get('train_number')} - {status_data.get('train_name')}")
    print(f"   Date: {test_date}")
    print(f"   Mode: {'Live' if is_live else 'Schedule only'}")
    print(f"   Stations: {len(stations)}")
    print(f"   Origin: {status_data.get('origin_station')} ({status_data.get('origin_code')})")
    print(f"   Destination: {status_data.get('destination_station')} ({status_data.get('destination_code')})")
    print(f"   Departure: {status_data.get('departure_time')}")
    print(f"   Arrival: {status_data.get('arrival_time')}")
    print(f"   Duration: {status_data.get('journey_duration')}")
    print(f"   HTML length: {len(html)} chars")

    if html:
        with open("train_status_timeline.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"   HTML saved: train_status_timeline.html")


@pytest.mark.asyncio
async def test_status_not_started_banner():
    """Test: Future date or schedule-only → should show 'Train has not started yet' banner."""
    tool = TrainStatusTool()

    # Get available dates
    dates_result = await tool.execute(
        trainNumber="12302",
        _user_type="website"
    )

    data = dates_result.structured_content
    dates = data.get("available_dates", [])
    assert len(dates) > 0, "Need at least one available date"

    # Try to find a future date (not today/yesterday)
    future_date = None
    for d in dates:
        if d.get("display_day") not in ("Today", "Yesterday"):
            future_date = d["date"]
            break

    if not future_date:
        future_date = dates[-1]["date"]

    result = await tool.execute(
        trainNumber="12302",
        journeyDate=future_date,
        _user_type="website"
    )

    assert not result.is_error, f"Should not error. Got: {result.response_text}"
    assert result.html is not None, "Should have HTML output"

    html = result.html
    status_data = result.structured_content
    is_live = status_data.get("is_live", False)
    current_idx = status_data.get("current_station_index")

    # Check banner logic
    if not is_live or current_idx is None:
        assert "not-started-banner" in html, "Should show not-started banner for non-live/no-departed train"
        assert "Train has not started yet" in html, "Banner should say 'Train has not started yet'"
        print(f"\n[PASS] Not Started Banner Test")
        print(f"   Date: {future_date}")
        print(f"   is_live: {is_live}, current_station_index: {current_idx}")
        print(f"   Banner shown: Yes")
    else:
        assert "not-started-banner" not in html, "Should NOT show banner when train has started"
        print(f"\n[PASS] Not Started Banner Test (train already running)")
        print(f"   Date: {future_date}")
        print(f"   is_live: {is_live}, current_station_index: {current_idx}")
        print(f"   Banner shown: No (train has started)")

    if html:
        with open("train_status_not_started.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"   HTML saved: train_status_not_started.html")


@pytest.mark.asyncio
async def test_status_timeline_icons():
    """Test: Timeline dots have correct icons (tick for passed, train for current)."""
    tool = TrainStatusTool()

    # Get available dates and pick today if available
    dates_result = await tool.execute(
        trainNumber="12302",
        _user_type="website"
    )

    data = dates_result.structured_content
    dates = data.get("available_dates", [])
    assert len(dates) > 0

    test_date = dates[0]["date"]

    result = await tool.execute(
        trainNumber="12302",
        journeyDate=test_date,
        _user_type="website"
    )

    assert not result.is_error
    assert result.html is not None

    html = result.html
    status_data = result.structured_content
    is_live = status_data.get("is_live", False)

    # Check icon URLs are present
    tick_url = "https://railways.easemytrip.com/Content/Train/img/tick.svg"
    train_url = "https://railways.easemytrip.com/Content/Train/img/train.svg"

    has_tick = tick_url in html
    has_train = train_url in html

    print(f"\n[PASS] Timeline Icons Test")
    print(f"   Date: {test_date}")
    print(f"   Mode: {'Live' if is_live else 'Schedule'}")
    print(f"   Has tick icon (passed stations): {has_tick}")
    print(f"   Has train icon (current/progress): {has_train}")

    # Origin always gets tick icon
    if 'timeline-dot origin' in html:
        print(f"   Origin dot present: Yes")

    # Destination dot
    if 'timeline-dot destination' in html:
        print(f"   Destination dot present: Yes")

    if is_live:
        # Live mode should have progress bar with train icon
        assert has_train, "Live mode should have train icon in progress bar"
        print(f"   Live progress bar: Yes")

    if html:
        with open("train_status_icons.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"   HTML saved: train_status_icons.html")


@pytest.mark.asyncio
async def test_status_whatsapp_response():
    """Test: WhatsApp user type → no HTML, has whatsapp_response."""
    tool = TrainStatusTool()

    # Get available dates first
    dates_result = await tool.execute(
        trainNumber="12618",
        _user_type="website"
    )

    data = dates_result.structured_content
    dates = data.get("available_dates", [])
    assert len(dates) > 0

    test_date = dates[0]["date"]

    result = await tool.execute(
        trainNumber="12618",
        journeyDate=test_date,
        _user_type="whatsapp"
    )

    assert not result.is_error, f"Should not error. Got: {result.response_text}"

    # WhatsApp should NOT have HTML
    assert result.html is None, "WhatsApp should not have HTML output"

    # Should have whatsapp_response
    assert result.whatsapp_response is not None, "WhatsApp should have whatsapp_response"

    wa = result.whatsapp_response
    wa_json = wa.get("whatsapp_json", {})

    assert wa_json.get("type") == "train_status", "Type should be train_status"
    assert wa_json.get("train_number"), "Should have train number"
    assert wa_json.get("train_name"), "Should have train name"
    assert wa_json.get("stations"), "Should have stations list"

    print(f"\n[PASS] WhatsApp Response Test")
    print(f"   Train: {wa_json.get('train_number')} - {wa_json.get('train_name')}")
    print(f"   Date: {test_date}")
    print(f"   Stations in response: {len(wa_json.get('stations', []))}")
    print(f"   Response text: {wa.get('response_text', '')[:80]}...")

    with open("train_status_whatsapp.json", "w", encoding="utf-8") as f:
        json.dump(wa, f, indent=2, ensure_ascii=False)
    print(f"   Response saved: train_status_whatsapp.json")


@pytest.mark.asyncio
async def test_status_invalid_train():
    """Test: Invalid train number → should return error."""
    tool = TrainStatusTool()

    result = await tool.execute(
        trainNumber="99999",
        _user_type="website"
    )

    assert result.is_error, "Invalid train should return error"
    assert "99999" in result.response_text, "Error should mention train number"

    print(f"\n[PASS] Invalid Train Test")
    print(f"   Train: 99999")
    print(f"   Error: {result.response_text}")


@pytest.mark.asyncio
async def test_status_invalid_date():
    """Test: Invalid date → should return error with available dates."""
    tool = TrainStatusTool()

    result = await tool.execute(
        trainNumber="12302",
        journeyDate="01-01-2020",
        _user_type="website"
    )

    assert result.is_error, "Past invalid date should return error"
    assert "not trackable" in result.response_text.lower() or "available dates" in result.response_text.lower(), \
        f"Error should mention available dates. Got: {result.response_text}"

    print(f"\n[PASS] Invalid Date Test")
    print(f"   Train: 12302, Date: 01-01-2020")
    print(f"   Error: {result.response_text}")


@pytest.mark.asyncio
async def test_status_date_picker_js_has_all_functions():
    """Test: Date picker JS includes all required functions for client-side rendering."""
    tool = TrainStatusTool()

    result = await tool.execute(
        trainNumber="12302",
        _user_type="website"
    )

    assert not result.is_error
    assert result.html is not None

    html = result.html

    # All JS functions
    required_functions = [
        "parseRunningDays",
        "calcDuration",
        "formatDate",
        "processLiveStations",
        "processScheduleStations",
        "buildStationHtml",
        "buildStatusHtml",
        "fetchTrainStatus",
    ]

    for fn in required_functions:
        assert fn in html, f"Missing JS function: {fn}"

    # API URLs
    assert "autosuggest.easemytrip.com" in html, "Should have autosuggest URL"
    assert "TrainLiveStatus" in html, "Should have live status URL"

    # Event listener
    assert "addEventListener" in html, "Should attach click event listeners"
    assert "tdt-date-item" in html, "Should target date items"

    # Not started banner CSS in JS
    assert "not-started-banner" in html, "JS CSS should include not-started-banner"

    print(f"\n[PASS] Date Picker JS Functions Test")
    print(f"   All {len(required_functions)} functions present")
    for fn in required_functions:
        print(f"     {fn}: OK")
    print(f"   API URLs: OK")
    print(f"   Event listeners: OK")
    print(f"   Not-started banner CSS in JS: OK")


if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("TRAIN STATUS UI TESTS")
    print("=" * 70)

    async def run_all_tests():
        print("\n1. Testing date picker (no date)...")
        await test_status_no_date_shows_date_picker()

        print("\n2. Testing status timeline (with date)...")
        await test_status_with_date_shows_timeline()

        print("\n3. Testing not-started banner...")
        await test_status_not_started_banner()

        print("\n4. Testing timeline icons...")
        await test_status_timeline_icons()

        print("\n5. Testing WhatsApp response...")
        await test_status_whatsapp_response()

        print("\n6. Testing invalid train...")
        await test_status_invalid_train()

        print("\n7. Testing invalid date...")
        await test_status_invalid_date()

        print("\n8. Testing date picker JS functions...")
        await test_status_date_picker_js_has_all_functions()

        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETED!")
        print("=" * 70)

    asyncio.run(run_all_tests())
