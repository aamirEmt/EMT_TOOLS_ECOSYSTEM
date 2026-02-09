from tools_factory.base import BaseTool, ToolMetadata
from pydantic import ValidationError
# from .bus_schema import BusSearchInput, SeatBindInput
# from .bus_search_service import search_buses, build_whatsapp_bus_response, get_seat_layout
# from tools_factory.base_schema import ToolResponseFormat
# from .bus_renderer import render_bus_results, render_bus_results_with_limit, render_seat_layout
from .bus_schema import BusSearchInput
from .bus_search_service import search_buses, build_whatsapp_bus_response
from tools_factory.base_schema import ToolResponseFormat
from .bus_renderer import render_bus_results_with_limit


class BusSearchTool(BaseTool):
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="search_buses",
            description=(
                "Search for buses on EaseMyTrip. "
                "Use city NAMES like 'Delhi', 'Mumbai', 'Ranchi', 'Manali' - NOT city IDs. "
                "The system automatically resolves city names to IDs. "
                "Required: source_name (source city), destination_name (destination city), journey_date (YYYY-MM-DD format)."
            ),
            input_schema=BusSearchInput.model_json_schema(),
            output_template="ui://widget/bus-carousel.html",
            category="travel",
            tags=["bus", "transport", "booking", "travel", "search"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        limit = kwargs.pop("_limit", 15)  # Default limit: 15 buses per page
        user_type = kwargs.pop("_user_type", "website")
        display_limit = kwargs.pop("_display_limit", 15)
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

        if not payload.source_id and not payload.source_name:
            return ToolResponseFormat(
                response_text="Please provide either source_id or source_name",
                structured_content={
                    "error": "MISSING_PARAMS",
                    "message": "Source city ID or name is required",
                },
                is_error=True,
            )
        
        if not payload.destination_id and not payload.destination_name:
            return ToolResponseFormat(
                response_text="Please provide either destination_id or destination_name",
                structured_content={
                    "error": "MISSING_PARAMS",
                    "message": "Destination city ID or name is required",
                },
                is_error=True,
            )

        # bus_results = await search_buses(
        #     source_id=payload.source_id,
        #     destination_id=payload.destination_id,
        #     journey_date=payload.journey_date,
        #     is_volvo=payload.is_volvo,
        #     source_name=payload.source_name,
        #     destination_name=payload.destination_name,
        # )

        # has_error = bool(bus_results.get("error"))

        # # Apply limit if specified
        # if limit is not None and "buses" in bus_results:
        #     bus_results["buses"] = bus_results["buses"][:limit]

        # buses = bus_results.get("buses", [])
        # bus_count = len(buses)

        bus_results = await search_buses(
            source_id=payload.source_id,
            destination_id=payload.destination_id,
            journey_date=payload.journey_date,
            is_volvo=payload.is_volvo,
            source_name=payload.source_name,
            destination_name=payload.destination_name,
        )

        has_error = bool(bus_results.get("error"))

        # Store original total count BEFORE pagination
        total_bus_count = len(bus_results.get("buses", []))

        # Apply pagination
        if not has_error and "buses" in bus_results:
            page = payload.page  # Get page from validated payload
            offset = (page - 1) * limit
            end = offset + limit
            bus_results["buses"] = bus_results["buses"][offset:end]

            # Add pagination metadata
            bus_results["pagination"] = {
                "current_page": page,
                "per_page": limit,
                "total_results": total_bus_count,
                "total_pages": (total_bus_count + limit - 1) // limit if limit > 0 else 0,
                "has_next_page": end < total_bus_count,
                "has_previous_page": page > 1,
                "showing_from": offset + 1 if bus_results["buses"] else 0,
                "showing_to": min(end, total_bus_count)
            }

        buses = bus_results.get("buses", [])
        bus_count = len(buses)

        # Create limited version for structured_content (same as paginated now)
        limited_bus_results = bus_results

        # Build WhatsApp response if needed
        whatsapp_response = None
        if is_whatsapp and not has_error:
            whatsapp_response = build_whatsapp_bus_response(payload, limited_bus_results)

        # # Render HTML for website
        # html_output = None
        # if not has_error and not is_whatsapp and bus_count > 0:
        #     # Use render_bus_results_with_limit for View All card support
        #     html_output = render_bus_results_with_limit(
        #         bus_results,
        #         display_limit=display_limit,
        #         show_view_all=True,
        #     )

        # Render HTML for website
        # Pass FULL bus_results (not limited) so View All card shows correct total
        html_output = None
        if not has_error and not is_whatsapp and total_bus_count > 0:
            html_output = render_bus_results_with_limit(
                bus_results,  # Full results, not limited
                display_limit=display_limit,
                show_view_all=True,
            )

        # Build response text
        source_display = bus_results.get("source_name") or payload.source_id or payload.source_name
        dest_display = bus_results.get("destination_name") or payload.destination_id or payload.destination_name

        # if has_error:
        #     text = f"No buses found. {bus_results.get('message', '')}"
        # else:
        #     text = f"Found {bus_count} buses from {source_display} to {dest_display}!"

        # return ToolResponseFormat(
        #     response_text=text,
        #     structured_content=None if is_whatsapp else bus_results,
        
        if has_error:
            text = f"No buses found. {bus_results.get('message', '')}"
        else:
            pagination = bus_results.get("pagination", {})
            if pagination:
                total = pagination.get("total_results", bus_count)
                current_page = pagination.get("current_page", 1)
                showing_from = pagination.get("showing_from", 1)
                showing_to = pagination.get("showing_to", bus_count)
                text = f"Showing buses {showing_from}-{showing_to} of {total} from {source_display} to {dest_display} (Page {current_page})"
            else:
                text = f"Found {total_bus_count} buses from {source_display} to {dest_display}!"

        return ToolResponseFormat(
            response_text=text,
            structured_content=None if is_whatsapp else limited_bus_results,
            html=html_output,
            whatsapp_response=(
                whatsapp_response.model_dump()
                if whatsapp_response
                else None
            ),
            is_error=has_error,
        )


# class BusSeatLayoutTool(BaseTool):

#     def get_metadata(self) -> ToolMetadata:
#         return ToolMetadata(
#             name="get_bus_seat_layout",
#             description="Get seat layout for a specific bus with boarding/dropping points. Shows available and booked seats.",
#             input_schema=SeatBindInput.model_json_schema(),
#             output_template="ui://widget/bus-seat-layout.html",
#             category="travel",
#             tags=["bus", "seat", "layout", "booking"],
#         )

#     async def execute(self, **kwargs) -> ToolResponseFormat:
#         user_type = kwargs.pop("_user_type", "website")
#         is_whatsapp = user_type.lower() == "whatsapp"

#         # Validate input
#         try:
#             payload = SeatBindInput.model_validate(kwargs)
#         except ValidationError as exc:
#             return ToolResponseFormat(
#                 response_text="Invalid seat layout input",
#                 structured_content={
#                     "error": "VALIDATION_ERROR",
#                     "details": exc.errors(),
#                 },
#                 is_error=True,
#             )

#         # Get seat layout from API
#         layout_response = await get_seat_layout(
#             source_id=payload.source_id,
#             destination_id=payload.destination_id,
#             journey_date=payload.journey_date,
#             bus_id=payload.bus_id,
#             route_id=payload.route_id,
#             engine_id=payload.engine_id,
#             boarding_point_id=payload.boarding_point_id,
#             dropping_point_id=payload.dropping_point_id,
#             source_name=payload.source_name or "",
#             destination_name=payload.destination_name or "",
#             operator_id=payload.operator_id or "",
#             operator_name=payload.operator_name or "",
#             bus_type=payload.bus_type or "",
#             departure_time=payload.departure_time or "",
#             arrival_time=payload.arrival_time or "",
#             duration=payload.duration or "",
#             trace_id=payload.trace_id or "",
#             is_seater=payload.is_seater if payload.is_seater is not None else True,
#             is_sleeper=payload.is_sleeper if payload.is_sleeper is not None else True,
#         )

#         has_error = not layout_response.get("success")

#         # Render HTML for website
#         html_output = None
#         if not is_whatsapp:
#             html_output = render_seat_layout(layout_response)

#         # Build response text
#         if has_error:
#             text = f"Failed to load seat layout: {layout_response.get('message', 'Unknown error')}"
#         else:
#             layout = layout_response.get("layout", {})
#             text = f"Seat layout loaded: {layout.get('available_seats', 0)} seats available out of {layout.get('total_seats', 0)}"

#         return ToolResponseFormat(
#             response_text=text,
#             structured_content=layout_response,
#             html=html_output,
#             is_error=has_error,
#         )