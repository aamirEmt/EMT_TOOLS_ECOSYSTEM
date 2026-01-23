"""Tool to fetch fare calendar data for one-way flights."""

from pydantic import ValidationError

from tools_factory.base import BaseTool, ToolMetadata
from tools_factory.base_schema import ToolResponseFormat

from .fare_calendar_schema import FareCalendarInput
from .fare_calendar_service import FareCalendarService


class FareCalendarTool(BaseTool):
    """Fetch fare calendar data from EaseMyTrip."""

    def __init__(self):
        super().__init__()
        self.service = FareCalendarService()

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="fare_calendar",
            description="Get fare calendar data for one-way flights.",
            input_schema=FareCalendarInput.model_json_schema(),
            category="travel",
            tags=["flight", "fare", "calendar"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        try:
            search_input = FareCalendarInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid fare calendar input",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        try:
            data = await self.service.fetch(search_input)
        except Exception as exc:
            return ToolResponseFormat(
                response_text="Failed to fetch fare calendar",
                structured_content={
                    "error": "API_ERROR",
                    "message": str(exc),
                },
                is_error=True,
            )

        return ToolResponseFormat(
            response_text=(
                f"Fetched fare calendar for "
                f"{search_input.departure_code}->{search_input.arrival_code} "
                f"on {search_input.date}."
            ),
            # API sometimes returns a bare list; wrap so it conforms to dict type
            structured_content={"results": data} if isinstance(data, list) else data,
            is_error=False,
        )
