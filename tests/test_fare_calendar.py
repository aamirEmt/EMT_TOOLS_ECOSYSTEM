import pytest
from datetime import datetime, timedelta

from tools_factory.factory import get_tool_factory

# Mark as integration since this hits the real API
pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_fare_calendar_real_api_prints_result():
    """Basic smoke test that fetches fare calendar data and prints the raw response."""
    factory = get_tool_factory()
    tool = factory.get_tool("fare_calendar")

    travel_date = (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")
    payload = {
        "date": travel_date,
        "departure_code": "DEL",
        "arrival_code": "PNQ",
    }

    result = await tool.execute(**payload)
    print("Fare calendar response:", result.structured_content)

    assert result is not None
    assert result.is_error is False
    assert result.structured_content is not None
