from tools_factory.base import BaseTool, ToolMetadata
from pydantic import ValidationError

from .train_schema import TrainSearchInput
from .train_search_service import search_trains, build_whatsapp_train_response
from .train_renderer import render_train_results
from tools_factory.base_schema import ToolResponseFormat


class TrainSearchTool(BaseTool):
    """Train search tool for EaseMyTrip Railways"""

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="search_trains",
            description="Search for trains on EaseMyTrip with origin station, destination station, and journey date",
            input_schema=TrainSearchInput.model_json_schema(),
            output_template="ui://widget/train-carousel.html",
            category="travel",
            tags=["train", "railway", "booking", "travel", "search"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        """Execute train search with provided parameters."""

        # Extract runtime flags
        limit = kwargs.pop("_limit", None)
        user_type = kwargs.pop("_user_type", "website")
        is_whatsapp = user_type.lower() == "whatsapp"

        try:
            payload = TrainSearchInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid train search input",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        # Search trains
        train_results = await search_trains(
            from_station=payload.from_station,
            to_station=payload.to_station,
            journey_date=payload.journey_date,
            travel_class=payload.travel_class,
            quota=payload.quota or "GN",
        )

        has_error = bool(train_results.get("error"))

        # Apply limit if specified
        if limit is not None and "trains" in train_results:
            train_results["trains"] = train_results["trains"][:limit]

        trains = train_results.get("trains", [])
        train_count = len(trains)

        # Build WhatsApp response if needed
        whatsapp_response = (
            build_whatsapp_train_response(payload, train_results)
            if is_whatsapp and not has_error
            else None
        )

        if has_error:
            text = f"No trains found. {train_results.get('message', '')}"
        else:
            text = f"Found {train_count} trains from {payload.from_station} to {payload.to_station}!"

        # Render HTML for website users only when trains are found
        html_content = None
        if not is_whatsapp and not has_error and train_count > 0:
            html_content = render_train_results(train_results)

        return ToolResponseFormat(
            response_text=text,
            structured_content=None if is_whatsapp else train_results,
            html=html_content,
            whatsapp_response=(
                whatsapp_response.model_dump()
                if whatsapp_response
                else None
            ),
            is_error=has_error,
        )
