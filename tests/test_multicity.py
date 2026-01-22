import pytest
from datetime import datetime, timedelta
from tools_factory.factory import get_tool_factory

# Mark as integration since this hits the real API
pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_multicity_oneway_real_api():
    """Multi-city one-way search should return outbound options from the real API."""
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")

    outbound = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    payload = {
        "origin": "DEL",
        "destination": "BLR",
        "outbound_date": outbound,
        "adults": 1,
        "children": 0,
        "infants": 0,
        "is_multicity": True,
        # Single leg to keep this a one-way multi-city request
        "multiCitySegments": [
            {"org": "DEL", "dept": "BLR", "deptDT": "2026-01-25"},
            {"org": "BLR", "dept": "BOM", "deptDT": "2026-01-27"},
            {"org": "BOM", "dept": "LHR", "deptDT": "2026-01-29"},
        ],
    }

    result = await tool.execute(**payload)
    data = result.structured_content
    print(data)

    assert data is not None
    assert data.get("is_multicity") is True
    assert data.get("is_roundtrip") is False

    outbound_flights = data.get("outbound_flights", [])
    assert outbound_flights, "Multi-city one-way should return outbound flights"

    final_destination = payload["multiCitySegments"][-1]["dept"]
    for flight in outbound_flights:
        legs = flight.get("legs", [])
        if not legs:
            continue
        if legs and isinstance(legs[0], list):
            grouped_count = len(legs)
            flat_legs = [leg for group in legs if isinstance(group, list) for leg in group]
        else:
            grouped_count = len(legs)
            flat_legs = legs
        # Combined multi-city option should end at the final segment's destination
        assert flight.get("destination") == final_destination
        assert flat_legs[-1].get("destination") == final_destination
        assert flight.get("total_stops") == max(len(flat_legs) - 1, 0)
        # There should be one group per multi-city segment
        assert grouped_count == len(payload["multiCitySegments"])
        break
