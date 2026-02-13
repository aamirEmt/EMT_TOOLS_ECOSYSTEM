"""Train Route Check Tool - Check route/schedule for Indian Railways trains."""

from pydantic import ValidationError

from tools_factory.base import BaseTool, ToolMetadata
from tools_factory.base_schema import ToolResponseFormat

from .route_check_schema import RouteCheckInput
from .route_check_service import TrainRouteCheckService, build_whatsapp_route_response
from .route_check_renderer import render_route_check


class TrainRouteCheckTool(BaseTool):
    """Tool for checking train route/schedule."""

    def __init__(self):
        super().__init__()
        self.service = TrainRouteCheckService()

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="check_train_route",
            description="Check the route/schedule of a train. Shows all stops with arrival/departure times, halt duration, and distance. Only train number is required.",
            input_schema=RouteCheckInput.model_json_schema(),
            output_template="ui://widget/train-route.html",
            category="travel",
            tags=["train", "railway", "route", "schedule", "stops"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        """Execute route check."""

        # Extract runtime flags
        user_type = kwargs.pop("_user_type", "website")
        is_whatsapp = user_type.lower() == "whatsapp"
        _ = kwargs.pop("_limit", None)

        # Validate input
        try:
            payload = RouteCheckInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid route check input",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        # Check route
        result = await self.service.check_route(
            train_no=payload.train_no,
            from_station_code=payload.from_station_code,
            to_station_code=payload.to_station_code,
        )

        if not result.get("success"):
            return ToolResponseFormat(
                response_text=result.get("error", "Could not check route"),
                structured_content=result,
                is_error=True,
            )

        train_info = result.get("train_info", {})
        station_list = result.get("station_list", [])
        running_days = result.get("running_days", [])

        # Build response text
        response_text = self._build_response_text(train_info, station_list, running_days)

        # Build WhatsApp response if needed
        whatsapp_response = None
        if is_whatsapp:
            whatsapp_response = build_whatsapp_route_response(
                train_info=train_info,
                station_list=station_list,
                running_days=running_days,
            )

        # Render HTML for website users
        html_content = None
        if not is_whatsapp:
            html_content = render_route_check(
                train_info=train_info,
                station_list=station_list,
                running_days=running_days,
            )

        return ToolResponseFormat(
            response_text=response_text,
            structured_content=None if is_whatsapp else result,
            html=html_content,
            whatsapp_response=whatsapp_response,
            is_error=False,
        )

    def _build_response_text(self, train_info: dict, station_list: list, running_days: list) -> str:
        """Build human-readable response text."""
        train_name = train_info.get("train_name", "Unknown Train")
        train_no = train_info.get("train_no", "")
        total_stops = len(station_list)

        if not station_list:
            return f"No route information found for {train_name} ({train_no})."

        first = station_list[0]
        last = station_list[-1]
        distance = last.get("distance", "")

        days_str = ", ".join(running_days) if running_days else "N/A"

        return (
            f"Route for {train_name} ({train_no}): "
            f"{first['station_name']} to {last['station_name']}, "
            f"{total_stops} stops, {distance} km. "
            f"Runs on: {days_str}"
        )
