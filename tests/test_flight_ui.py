"""
Quick script to test flight UI with real API data
Tests all three modes: one-way, domestic round-trip, and international round-trip
"""

import pytest
from datetime import datetime, timedelta
from tools_factory.flights.flight_search_tool import FlightSearchTool


@pytest.mark.asyncio
async def test_oneway_flight():
    tool = FlightSearchTool()

    outbound = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    result = await tool.execute(
        origin="DEL",
        destination="LHR",
        outbound_date=outbound,
        adults=2,
        _limit=10,
        _html=True,
    )

    # ✅ Updated attribute access
    assert not result.is_error

    # Keep HTML saving logic
    if result.html:
        with open("flight_oneway_results.html", "w", encoding="utf-8") as f:
            f.write(result.html)


@pytest.mark.asyncio
async def test_domestic_roundtrip():
    tool = FlightSearchTool()

    today = datetime.now()
    outbound = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    return_date = (today + timedelta(days=37)).strftime("%Y-%m-%d")

    result = await tool.execute(
        origin="DEL",
        destination="BOM",
        outbound_date=outbound,
        return_date=return_date,
        adults=2,
        children=1,
        _limit=8,
        _html=True,
    )

    # ✅ Updated attribute access
    assert not result.is_error

    # Access structured_content as attribute
    data = result.structured_content
    assert len(data.get("outbound_flights", [])) > 0
    assert len(data.get("return_flights", [])) > 0

    if result.html:
        with open("flight_domestic_roundtrip_results.html", "w", encoding="utf-8") as f:
            f.write(result.html)


@pytest.mark.asyncio
async def test_international_roundtrip():
    tool = FlightSearchTool()

    today = datetime.now()
    outbound = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    return_date = (today + timedelta(days=37)).strftime("%Y-%m-%d")

    result = await tool.execute(
        origin="DEL",
        destination="LHR",
        outbound_date=outbound,
        return_date=return_date,
        adults=1,
        _limit=10,
        _html=True,
    )

    # ✅ Updated attribute access
    assert not result.is_error

    data = result.structured_content
    assert data.get("is_international") is True
    assert data.get("is_roundtrip") is True

    if result.html:
        with open("flight_international_roundtrip_results.html", "w", encoding="utf-8") as f:
            f.write(result.html)
