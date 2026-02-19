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
                "MANDATORY: Use this tool for ANY query about buses including seater buses, sleeper buses, AC buses, bus tickets, bus travel. "
                "TRIGGER WORDS: bus, buses, seater, sleeper, AC bus, non-AC bus, Volvo, bus ticket, bus booking, morning bus, evening bus, night bus. "
                "Search for buses on EaseMyTrip. Use city NAMES like 'Delhi', 'Mumbai', 'Ranchi', 'Manali' - NOT city IDs. "
                "The system automatically resolves city names to IDs. "
                "Required: source_name (source city), destination_name (destination city), journey_date (dd-mm-yyyy format). "
                "FILTER PARAMETERS - Use these when user requests specific bus types: "
                "- isAC: true for AC buses, false for Non-AC buses "
                "- isSleeper: true for sleeper/semi-sleeper buses (beds/berths) "
                "- isSeater: true for seater buses (regular sitting seats, NOT sleeper) "
                "- isVolvo: true for Volvo buses only "
                "DEPARTURE TIME FILTERS (use 24-hour HH:MM format): "
                "- departureTimeFrom: buses departing AFTER this time (e.g., '06:00' for after 6 AM) "
                "- departureTimeTo: buses departing BEFORE this time (e.g., '18:00' for before 6 PM) "
                "DEPARTURE TIME KEYWORD MATCHING: "
                "- 'early morning', 'before 6 AM', 'night bus' -> departureTimeTo='06:00' "
                "- 'morning bus', '6 AM to 12 PM' -> departureTimeFrom='06:00' AND departureTimeTo='12:00' "
                "- 'afternoon bus', '12 PM to 6 PM' -> departureTimeFrom='12:00' AND departureTimeTo='18:00' "
                "- 'evening bus', 'after 6 PM', 'night departure' -> departureTimeFrom='18:00' "
                "- 'after 10 AM' -> departureTimeFrom='10:00' "
                "- 'before 11 PM' -> departureTimeTo='23:00' "
                "- 'between 8 AM and 2 PM' -> departureTimeFrom='08:00' AND departureTimeTo='14:00' "
                "KEYWORD MATCHING (existing): "
                "- 'seater bus', 'seater', 'sitting bus', 'chair bus', 'regular seat' -> set isSeater=true "
                "- 'sleeper bus', 'sleeper', 'sleeping bus', 'semi-sleeper', 'berth', 'bed bus' -> set isSleeper=true "
                "- 'AC bus', 'air conditioned' -> set isAC=true "
                "- 'Non-AC bus', 'non ac', 'without AC' -> set isAC=false "
                "COMBINATIONS: "
                "- 'AC seater' -> isAC=true AND isSeater=true "
                "- 'Non-AC sleeper' -> isAC=false AND isSleeper=true "
                "- 'morning AC bus' -> isAC=true AND departureTimeFrom='06:00' AND departureTimeTo='12:00' "
                "- 'evening sleeper' -> isSleeper=true AND departureTimeFrom='18:00' "
                "ALWAYS make a fresh API call with filters - never filter from cached results. "
                "ALWAYS call this tool for any bus-related query. Never show menu options for bus searches."
            ),
            input_schema=BusSearchInput.model_json_schema(),
            output_template="ui://widget/bus-carousel.html",
            category="travel",
            tags=["bus", "transport", "booking", "travel", "search"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        session_id = kwargs.pop("_session_id", None)
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

        print(f"DEBUG: Bus search filters - is_ac={payload.is_ac}, is_seater={payload.is_seater}, is_sleeper={payload.is_sleeper}, is_volvo={payload.is_volvo}, departure_from={payload.departure_time_from}, departure_to={payload.departure_time_to}")

        bus_results = await search_buses(
            source_id=payload.source_id,
            destination_id=payload.destination_id,
            journey_date=payload.journey_date,
            is_volvo=payload.is_volvo,
            is_ac=payload.is_ac,
            is_seater=payload.is_seater,
            is_sleeper=payload.is_sleeper,
            source_name=payload.source_name,
            destination_name=payload.destination_name,
            departure_time_from=payload.departure_time_from,
            departure_time_to=payload.departure_time_to,
        )

        has_error = bool(bus_results.get("error"))

        # Store original total count BEFORE pagination
        total_bus_count = len(bus_results.get("buses", []))

        # Get all buses for rendering (DO NOT MODIFY bus_results["buses"])
        all_buses = bus_results.get("buses", [])
        
        # Create paginated version for structured_content ONLY
        page = payload.page
        offset = (page - 1) * limit
        end = offset + limit
        paginated_buses = all_buses[offset:end] if not has_error else []
        
        # Create limited_bus_results as a COPY with paginated buses
        limited_bus_results = bus_results.copy()
        limited_bus_results["buses"] = paginated_buses
        limited_bus_results["pagination"] = {
            "current_page": page,
            "per_page": limit,
            "total_results": total_bus_count,
            "total_pages": (total_bus_count + limit - 1) // limit if limit > 0 else 1,
            "has_next_page": end < total_bus_count,
            "has_previous_page": page > 1,
            "showing_from": offset + 1 if paginated_buses else 0,
            "showing_to": min(end, total_bus_count),
        }
        
        bus_count = len(paginated_buses)

        # Build WhatsApp response if needed
        whatsapp_response = None
        if is_whatsapp and not has_error:
            whatsapp_response = build_whatsapp_bus_response(payload, limited_bus_results)

        # # Render HTML for website
        # # Pass FULL bus_results (not limited) so View All card shows correct total
        # html_output = None
        # if not has_error and not is_whatsapp and total_bus_count > 0:
        #     html_output = render_bus_results_with_limit(
        #         bus_results,
        #         display_limit=display_limit,
        #         show_view_all=True,
        #     )

        # Render HTML for website
        # Create render data with paginated buses but preserve total count for header/View All
        html_output = None
        if not has_error and not is_whatsapp and total_bus_count > 0:
            # Build render data: paginated buses + original metadata for header
            render_data = bus_results.copy()
            render_data["buses"] = paginated_buses  # Only buses for this page
            
            html_output = render_bus_results_with_limit(
                render_data,
                display_limit=len(paginated_buses),  # Show all paginated buses (no further slicing)
                show_view_all=True,
                total_bus_count=total_bus_count,  # Pass original total for header & View All card
            )

        # Build response text
        source_display = bus_results.get("source_name") or payload.source_id or payload.source_name
        dest_display = bus_results.get("destination_name") or payload.destination_id or payload.destination_name


        if has_error:
            text = f"No buses found. {bus_results.get('message', '')}"
        else:
            pagination = limited_bus_results.get("pagination", {})
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