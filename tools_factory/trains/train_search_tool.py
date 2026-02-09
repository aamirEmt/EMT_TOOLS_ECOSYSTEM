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
        limit = kwargs.pop("_limit", 15)  # Default limit: 15 trains per page
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
            quota= "GN",
        )

        has_error = bool(train_results.get("error"))

        # Store original total count BEFORE pagination
        total_trains = len(train_results.get("trains", []))

        # Apply pagination
        if not has_error and "trains" in train_results:
            page = payload.page  # Get page from validated payload
            offset = (page - 1) * limit
            end = offset + limit
            train_results["trains"] = train_results["trains"][offset:end]

            # Add pagination metadata
            train_results["pagination"] = {
                "current_page": page,
                "per_page": limit,
                "total_results": total_trains,
                "total_pages": (total_trains + limit - 1) // limit if limit > 0 else 0,
                "has_next_page": end < total_trains,
                "has_previous_page": page > 1,
                "showing_from": offset + 1 if train_results["trains"] else 0,
                "showing_to": min(end, total_trains)
            }

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
            pagination = train_results.get("pagination", {})
            if pagination:
                total = pagination.get("total_results", train_count)
                current_page = pagination.get("current_page", 1)
                showing_from = pagination.get("showing_from", 1)
                showing_to = pagination.get("showing_to", train_count)
                text = f"Showing trains {showing_from}-{showing_to} of {total} from {payload.from_station} to {payload.to_station} (Page {current_page})"
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
