from tools_factory.base import BaseTool, ToolMetadata
from pydantic import ValidationError
from .bus_schema import BusSearchInput
from .bus_search_service import search_buses, build_whatsapp_bus_response
from tools_factory.base_schema import ToolResponseFormat
from .bus_renderer import render_bus_results
from .bus_schema import SeatBindInput
from .bus_search_service import get_seat_layout
from .bus_renderer import render_seat_layout

class BusSearchTool(BaseTool):

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="search_buses",
            description="Search for buses on EaseMyTrip with source city ID, destination city ID, and journey date",
            input_schema=BusSearchInput.model_json_schema(),
            output_template="ui://widget/bus-carousel.html",
            category="travel",
            tags=["bus", "transport", "booking", "travel", "search"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:

        limit = kwargs.pop("_limit", None)
        user_type = kwargs.pop("_user_type", "website")
        is_whatsapp = user_type.lower() == "whatsapp"

        try:
            payload = BusSearchInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid bus search input",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        bus_results = await search_buses(
            source_id=payload.source_id,
            destination_id=payload.destination_id,
            journey_date=payload.journey_date,
            is_volvo=payload.is_volvo,
        )

        has_error = bool(bus_results.get("error"))

        if limit is not None and "buses" in bus_results:
            bus_results["buses"] = bus_results["buses"][:limit]

        buses = bus_results.get("buses", [])
        bus_count = len(buses)

        whatsapp_response = (
            build_whatsapp_bus_response(payload, bus_results)
            if is_whatsapp and not has_error
            else None
        )

        html_output = None
        if not has_error and not is_whatsapp:
            html_output = render_bus_results(bus_results)

        if has_error:
            text = f"No buses found. {bus_results.get('message', '')}"
        else:
            text = f"Found {bus_count} buses from {payload.source_id} to {payload.destination_id}!"

        return ToolResponseFormat(
            response_text=text,
            structured_content=None if is_whatsapp else bus_results,
            html=html_output,
            whatsapp_response=(
                whatsapp_response.model_dump()
                if whatsapp_response
                else None
            ),
            is_error=has_error,
        )

class BusSeatLayoutTool(BaseTool):

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="get_bus_seat_layout",
            description="Get seat layout for a specific bus with boarding/dropping points",
            input_schema=SeatBindInput.model_json_schema(),
            output_template="ui://widget/bus-seat-layout.html",
            category="travel",
            tags=["bus", "seat", "layout", "booking"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:

        user_type = kwargs.pop("_user_type", "website")
        is_whatsapp = user_type.lower() == "whatsapp"

        try:
            payload = SeatBindInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid seat layout input",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        layout_response = await get_seat_layout(
            source_id=payload.source_id,
            destination_id=payload.destination_id,
            journey_date=payload.journey_date,
            bus_id=payload.bus_id,
            route_id=payload.route_id,
            engine_id=payload.engine_id,
            boarding_point_id=payload.boarding_point_id,
            dropping_point_id=payload.dropping_point_id,
        )

        has_error = not layout_response.get("success")

        html_output = None
        if not is_whatsapp:
            html_output = render_seat_layout(layout_response)

        if has_error:
            text = f"Failed to load seat layout: {layout_response.get('message', 'Unknown error')}"
        else:
            layout = layout_response.get("layout", {})
            text = f"Seat layout loaded: {layout.get('available_seats', 0)} seats available out of {layout.get('total_seats', 0)}"

        return ToolResponseFormat(
            response_text=text,
            structured_content=layout_response,
            html=html_output,
            is_error=has_error,
        )