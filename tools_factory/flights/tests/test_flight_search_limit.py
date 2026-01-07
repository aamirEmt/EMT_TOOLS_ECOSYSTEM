import pytest

from tools_factory.flights.flight_renderer import render_flight_results
from tools_factory.flights.flight_search_tool import FlightSearchTool


def test_limit_applies_to_structured_and_html(real_flight_data):
    structured = real_flight_data["structured_content"]

    # simulate limit already applied
    structured["outbound_flights"] = structured["outbound_flights"][:5]

    html = render_flight_results(structured)

    assert len(structured["outbound_flights"]) == 5
    assert html.count('<div class="flight-card">') == 5


@pytest.mark.asyncio
async def test_tool_limit_flag(monkeypatch, real_flight_data):
    async def mock_search_flights(**kwargs):
        return real_flight_data["structured_content"]

    monkeypatch.setattr(
        "tools_factory.flights.flight_search_tool.search_flights",
        mock_search_flights
    )

    tool = FlightSearchTool()

    response = await tool.execute(
        origin="DEL",
        destination="BOM",
        outbound_date="2025-02-01",
        adults=1,
        _html=True,
        _limit=3,
    )

    assert response["html"] is not None
    assert response["html"].count('<div class="flight-card">') == 3
