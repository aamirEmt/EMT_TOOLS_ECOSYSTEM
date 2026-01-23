"""Integration tests for WhatsApp flight response formatting."""

from datetime import datetime, timedelta

import pytest

from tools_factory.factory import get_tool_factory
from tools_factory.base_schema import ToolResponseFormat

pytestmark = pytest.mark.integration


@pytest.fixture
def dummy_flight_roundtrip():
    """Dummy payload for round-trip flight search."""
    today = datetime.now()
    outbound = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    return_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")

    return {
        "origin": "DEL",
        "destination": "PNQ",
        "outbound_date": outbound,
        "return_date": return_date,
        "adults": 1,
        "children": 0,
        "infants": 0,
    }


@pytest.mark.asyncio
async def test_whatsapp_flight_roundtrip_booking_url_real_api(dummy_flight_roundtrip):
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")
    payload = {**dummy_flight_roundtrip, "_user_type": "whatsapp"}

    result: ToolResponseFormat = await tool.execute(**payload)

    assert result.whatsapp_response is not None
    whatsapp_json = result.whatsapp_response.get("whatsapp_json") or {}
    options = whatsapp_json.get("options") or []
    assert options, "Expected at least one WhatsApp option"

    for idx, option in enumerate(options, start=1):
        booking_url = option.get("booking_url")
        print(f"Booking URL {idx}:", booking_url)
        assert isinstance(booking_url, str) and booking_url.startswith("http")
        if "RemoteSearchHandlers/index" in booking_url:
            assert "TripType=RoundTrip" in booking_url
