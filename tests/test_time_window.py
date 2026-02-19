"""Integration test to verify departure/arrival time-window filtering."""

import re
from datetime import datetime, timedelta

import pytest

from tools_factory.factory import get_tool_factory

pytestmark = pytest.mark.integration


def _to_minutes(raw_time: str) -> int:
    """Convert time strings like '0715' or '07:15' to minutes since midnight."""
    digits = re.sub(r"\D", "", str(raw_time or ""))
    if len(digits) < 3:
        return -1
    if len(digits) == 3:
        hour = int(digits[0])
        minute = int(digits[1:])
    else:
        hour = int(digits[:2])
        minute = int(digits[2:4])
    return hour * 60 + minute


@pytest.mark.asyncio
async def test_flight_search_time_window_filters():
    """Ensure flights returned respect the specified departure/arrival windows."""
    today = datetime.now()
    outbound = (today + timedelta(days=30)).strftime("%Y-%m-%d")

    payload = {
        "origin": "DEL",
        "destination": "BOM",
        "outbound_date": outbound,
        "adults": 1,
        "children": 0,
        "infants": 0,
        "departureTimeWindow": "06:00-23:00",
        "arrivalTimeWindow": "08:00-23:59",
    }

    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")

    result = await tool.execute(**payload)

    assert result.structured_content is not None
    data = result.structured_content
    flights = data.get("outbound_flights", [])
    # print(flights)
    # If flights exist, every flight should satisfy the windows.
    for flight in flights:
        legs = flight.get("legs") or []
        if not legs:
            continue
        dep_minutes = _to_minutes(legs[0].get("departure_time"))
        arr_minutes = _to_minutes(legs[-1].get("arrival_time"))
        assert 6 * 60 <= dep_minutes <= 23 * 60, "Departure outside window"
        assert 8 * 60 <= arr_minutes <= (23 * 60 + 59), "Arrival outside window"

    # At minimum, the API should respond without errors even if no flights match.
    assert "error" not in data
