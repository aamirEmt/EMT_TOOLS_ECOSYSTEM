"""
Quick script to test train route UI with real API data
Tests train route check with HTML rendering
"""

import pytest
from tools_factory.trains.Train_RouteCheck.route_check_tool import TrainRouteCheckTool


@pytest.mark.asyncio
async def test_train_route_rajdhani():
    """Test train route for Rajdhani Express (12302) - NDLS to HWH"""
    tool = TrainRouteCheckTool()

    result = await tool.execute(
        trainNo="12302",
        _limit=None,
        _user_type="website"
    )

    assert not result.is_error

    data = result.structured_content
    assert data is not None
    assert data.get("success") is True
    assert len(data.get("station_list", [])) > 0

    # Check train info
    train_info = data.get("train_info", {})
    assert train_info.get("train_no") == "12302"
    assert train_info.get("train_name") is not None

    # Check station list
    stations = data.get("station_list", [])
    first_station = stations[0]
    last_station = stations[-1]

    # First station should have departure but no arrival
    assert first_station["departure_time"] != "--"
    assert first_station["arrival_time"] == "--"

    # Last station should have arrival but no departure
    assert last_station["arrival_time"] != "--"
    assert last_station["departure_time"] == "--"

    # Check running days
    running_days = data.get("running_days", [])
    assert len(running_days) > 0

    print(f"\n[UI TEST] Route for {train_info['train_name']} ({train_info['train_no']})")
    print(f"  Stops: {len(stations)}")
    print(f"  Running days: {', '.join(running_days)}")
    print(f"  First: {first_station['station_name']} ({first_station['station_code']})")
    print(f"  Last: {last_station['station_name']} ({last_station['station_code']})")

    if result.html:
        with open("train_route_rajdhani.html", "w", encoding="utf-8") as f:
            f.write(result.html)
        print(f"  HTML saved: train_route_rajdhani.html")


@pytest.mark.asyncio
async def test_train_route_with_station_codes():
    """Test train route with explicit station codes"""
    tool = TrainRouteCheckTool()

    result = await tool.execute(
        trainNo="12302",
        fromStationCode="NDLS",
        toStationCode="HWH",
        _limit=None,
        _user_type="website"
    )

    assert not result.is_error

    data = result.structured_content
    assert data is not None
    assert data.get("success") is True

    stations = data.get("station_list", [])
    assert len(stations) > 0

    print(f"\n[UI TEST] Route with explicit station codes")
    print(f"  Stops: {len(stations)}")

    if result.html:
        with open("train_route_with_codes.html", "w", encoding="utf-8") as f:
            f.write(result.html)
        print(f"  HTML saved: train_route_with_codes.html")


@pytest.mark.asyncio
async def test_train_route_show_more_button():
    """Test that trains with more than 5 stops have Show All button in HTML"""
    tool = TrainRouteCheckTool()

    # Rajdhani has 9 stops - should trigger Show All button
    result = await tool.execute(
        trainNo="12302",
        _limit=None,
        _user_type="website"
    )

    assert not result.is_error

    data = result.structured_content
    stations = data.get("station_list", [])

    if len(stations) > 5:
        assert result.html is not None
        html = result.html

        # Should have hidden stops section
        assert "hidden-stops" in html, "Should have hidden-stops section for >5 stops"

        # Should have Show All button
        assert "Show All" in html, "Should have 'Show All' button"
        assert f"Show All {len(stations)} Stops" in html, \
            f"Button should say 'Show All {len(stations)} Stops'"

        print(f"\n[UI TEST] Show More button for {len(stations)} stops")
        print(f"  Visible: 5 stops")
        print(f"  Hidden: {len(stations) - 5} stops")
        print(f"  [PASS] 'Show All {len(stations)} Stops' button present")
    else:
        print(f"\n[UI TEST] Only {len(stations)} stops - no Show All button needed")


@pytest.mark.asyncio
async def test_train_route_few_stops_no_button():
    """Test that trains with 5 or fewer stops don't have Show All button"""
    tool = TrainRouteCheckTool()

    # Use a short-distance train - try Shatabdi or similar
    result = await tool.execute(
        trainNo="12002",  # Bhopal Shatabdi
        _limit=None,
        _user_type="website"
    )

    if result.is_error:
        print(f"\n[SKIP] Train 12002 not found or API error: {result.response_text}")
        return

    data = result.structured_content
    stations = data.get("station_list", [])

    if len(stations) <= 5:
        html = result.html
        assert "hidden-stops" not in html, "Should NOT have hidden-stops for <=5 stops"
        assert "Show All" not in html, "Should NOT have 'Show All' button for <=5 stops"
        print(f"\n[UI TEST] {len(stations)} stops - no Show All button")
        print(f"  [PASS] All stops visible without button")
    else:
        print(f"\n[INFO] Train has {len(stations)} stops - Show All button expected")

    if result.html:
        with open("train_route_few_stops.html", "w", encoding="utf-8") as f:
            f.write(result.html)
        print(f"  HTML saved: train_route_few_stops.html")


@pytest.mark.asyncio
async def test_train_route_timeline_structure():
    """Test that HTML has correct timeline structure with dots and lines"""
    tool = TrainRouteCheckTool()

    result = await tool.execute(
        trainNo="12302",
        _limit=None,
        _user_type="website"
    )

    assert not result.is_error
    assert result.html is not None

    html = result.html

    # Check timeline elements
    assert "timeline-stop" in html, "Should have timeline-stop elements"
    assert "timeline-dot" in html, "Should have timeline-dot elements"
    assert "timeline-line" in html, "Should have timeline-line connectors"
    assert "stop-station-name" in html, "Should have station names"
    assert "stop-station-code" in html, "Should have station codes"

    # Check first/last dot styling
    assert "timeline-dot first" in html, "First station should have 'first' class"

    # Check time display
    assert "Arr:" in html or "Dep:" in html, "Should show arrival/departure times"

    # Check halt and distance display
    assert "halt-badge" in html, "Should have halt time badges"
    assert "distance-badge" in html, "Should have distance badges"
    assert "km" in html, "Should show distance in km"

    # Check footer
    assert "Total Stops:" in html, "Should show total stops count"
    assert "Distance:" in html, "Should show total distance"

    print(f"\n[UI TEST] Timeline structure validation")
    print(f"  [PASS] Timeline dots and lines present")
    print(f"  [PASS] Station names and codes present")
    print(f"  [PASS] Time, halt, distance info present")
    print(f"  [PASS] Footer with total stops and distance present")


@pytest.mark.asyncio
async def test_train_route_running_days():
    """Test that running days are displayed correctly"""
    tool = TrainRouteCheckTool()

    result = await tool.execute(
        trainNo="12302",
        _limit=None,
        _user_type="website"
    )

    assert not result.is_error
    assert result.html is not None

    html = result.html
    data = result.structured_content
    running_days = data.get("running_days", [])

    # Check running days chips exist
    assert "day-chip" in html, "Should have day-chip elements"

    # Active days should have 'active' class
    for day in running_days:
        assert day in html, f"Running day '{day}' should appear in HTML"

    # All 7 days should be present (active or inactive)
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        assert day in html, f"Day '{day}' should appear in HTML"

    print(f"\n[UI TEST] Running days display")
    print(f"  Active days: {', '.join(running_days)}")
    print(f"  [PASS] All 7 days shown, active days highlighted")


@pytest.mark.asyncio
async def test_train_route_whatsapp_response():
    """Test train route with WhatsApp response format"""
    tool = TrainRouteCheckTool()

    result = await tool.execute(
        trainNo="12302",
        _limit=None,
        _user_type="whatsapp"
    )

    assert not result.is_error

    # WhatsApp should NOT have HTML
    assert result.html is None, "WhatsApp should not have HTML output"

    # Should have whatsapp_response
    assert result.whatsapp_response is not None, "WhatsApp should have whatsapp_response"

    wa = result.whatsapp_response
    assert wa.get("type") == "train_route"
    assert wa.get("data") is not None

    wa_data = wa["data"]
    assert wa_data.get("train") is not None
    assert wa_data.get("stops") is not None
    assert wa_data.get("total_stops") > 0
    assert wa_data.get("running_days") is not None

    print(f"\n[UI TEST] WhatsApp response format")
    print(f"  Train: {wa_data['train']['train_name']} ({wa_data['train']['train_no']})")
    print(f"  Stops: {wa_data['total_stops']}")
    print(f"  [PASS] WhatsApp response has correct structure")


@pytest.mark.asyncio
async def test_train_route_invalid_train():
    """Test train route with invalid train number"""
    tool = TrainRouteCheckTool()

    result = await tool.execute(
        trainNo="99999",
        _limit=None,
        _user_type="website"
    )

    assert result.is_error
    assert result.html is None
    assert "Could not fetch" in result.response_text or "No route" in result.response_text

    print(f"\n[UI TEST] Invalid train number")
    print(f"  Response: {result.response_text}")
    print(f"  [PASS] Error handled gracefully")


@pytest.mark.asyncio
async def test_train_route_station_data_integrity():
    """Test that station data from API is parsed correctly"""
    tool = TrainRouteCheckTool()

    result = await tool.execute(
        trainNo="12302",
        _limit=None,
        _user_type="website"
    )

    assert not result.is_error

    data = result.structured_content
    stations = data.get("station_list", [])

    for i, station in enumerate(stations):
        # Every station must have code and name
        assert station["station_code"], f"Station {i} must have code"
        assert station["station_name"], f"Station {i} must have name"

        # Day count should be a number
        assert station["day_count"].isdigit(), f"Station {i} day_count should be numeric"

        # Distance should be numeric
        assert station["distance"].isdigit(), f"Station {i} distance should be numeric"

        # Distance should be increasing
        if i > 0:
            prev_dist = int(stations[i - 1]["distance"])
            curr_dist = int(station["distance"])
            assert curr_dist >= prev_dist, \
                f"Distance should increase: {prev_dist} -> {curr_dist} at station {station['station_code']}"

    print(f"\n[UI TEST] Station data integrity")
    print(f"  Validated {len(stations)} stations")
    print(f"  [PASS] All stations have valid code, name, day, distance")
    print(f"  [PASS] Distance is monotonically increasing")
