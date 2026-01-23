"""Service for fetching fare calendar data."""

from emt_client.clients.flight_client import FlightApiClient

from .fare_calendar_schema import FareCalendarInput

FARE_CALENDAR_URL = (
    "https://flightservice.easemytrip.com/EmtAppService/FareCalendar/FillCalendarDataByMonth"
)


class FareCalendarService:
    """Lightweight wrapper around the fare calendar API."""

    def __init__(self):
        self.client = FlightApiClient()

    async def fetch(self, search_input: FareCalendarInput) -> dict:
        """Call the fare calendar endpoint and return raw data."""
        cal_key = (
            f"{search_input.departure_code}_"
            f"{search_input.arrival_code}_"
            f"ddate__{search_input.date}_"
        )

        payload = {"CalKey_": cal_key, "month": "1"}
        return await self.client.search(FARE_CALENDAR_URL, payload)
