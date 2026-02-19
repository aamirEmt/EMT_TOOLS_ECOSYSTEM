from typing import Dict, Any
from tools_factory.base import BaseTool, ToolMetadata
from pydantic import ValidationError

from emt_client.utils import generate_short_link
from .flight_schema import FlightSearchInput,WhatsappFlightFinalResponse,WhatsappFlightFormat
from .flight_search_service import search_flights,build_whatsapp_flight_response,filter_domestic_roundtrip_flights
from .flight_renderer import render_flight_results
from tools_factory.base_schema import ToolResponseFormat 


def extract_segment_summary(segment: dict) -> dict:
    """
    Extract normalized flight data from a real EMT flight segment.
    Works for single-leg and multi-leg journeys.
    """
    legs = segment.get("legs") or []

    if not legs:
        return {
            "airline": None,
            "flight_number": None,
            "departure_time": None,
            "arrival_time": None,
            "duration": segment.get("journey_time"),
            "stops": segment.get("total_stops", 0),
        }

    first_leg = legs[0]
    last_leg = legs[-1]

    return {
        "airline": first_leg.get("airline_name"),
        "flight_number": " / ".join(
            f"{leg.get('airline_code')}{leg.get('flight_number')}"
            for leg in legs
            if leg.get("flight_number")
        ),
        "departure_time": first_leg.get("departure_time"),
        "arrival_time": last_leg.get("arrival_time"),
        "duration": segment.get("journey_time"),
        "stops": segment.get("total_stops", 0),
    }


class FlightSearchTool(BaseTool):
    """Flight search tool for EaseMyTrip"""

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="search_flights",
            description=(
                "Purpose:\n"
                "- Search for flights on EaseMyTrip with comprehensive filtering options including origin, destination, dates, passengers, cabin class, stops, time windows, and special fare types.\n"
                "Parameters (Fields):\n"
                "- origin (string, required): Origin airport IATA code. Examples: 'DEL' for Delhi, 'BOM' for Mumbai, 'BLR' for Bangalore.\n"
                "- destination (string, required): Destination airport IATA code. Examples: 'BOM' for Mumbai, 'DEL' for Delhi, 'MAA' for Chennai.\n"
                "- outboundDate (string, required): Outbound flight date in YYYY-MM-DD format. Example: '2024-12-25'.\n"
                "- returnDate (string | null, optional): Return flight date in YYYY-MM-DD format for round-trip. Set null/omit for one-way. Example: '2024-12-30'.\n"
                "- adults (integer, default: 1): Number of adults (12+). Range 1-9.\n"
                "- children (integer, default: 0): Number of children (2-11). Range 0-8.\n"
                "- infants (integer, default: 0): Number of infants (<2). Range 0-8; cannot exceed adults.\n"
                "- cabin (string | null, optional): Cabin class 'economy', 'premium economy', 'business', 'first'.\n"
                "- stops (integer | null, optional): Max stops: 0=non-stop, 1=max 1 stop, 2=max 2 stops. Omit for no preference.\n"
                "- fastest (boolean | null, optional): true if user asks for fastest/shortest/quickest flights.\n"
                "- refundable (boolean | null, optional): true to show only refundable options, false for non-refundable only; omit for all.\n"
                "- departureTimeWindow (string, default '00:00-24:00'): Preferred departure range 'HH:MM-HH:MM'; accepts natural terms like morning/afternoon/evening/night/early morning or loose ranges like '6am-11am'.\n"
                "- arrivalTimeWindow (string, default '00:00-24:00'): Preferred arrival range 'HH:MM-HH:MM'; accepts natural terms like morning/afternoon/evening/night/early morning or loose ranges like '5pm-9:30pm'.\n"
                "- fareType (integer, default: 0): Special fare category. 0=Standard, 1=Defence/Armed Forces, 2=Student, 3=Senior Citizen (60+), 4=Doctor/Nurse."
            ),
            input_schema=FlightSearchInput.model_json_schema(),
            output_template="ui://widget/flight-carousel.html",
            category="travel",
            tags=["flight", "booking", "travel", "search"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        """
        Execute flight search with provided parameters.
        """

        # --------------------------
        # Extract runtime flags
        # --------------------------
        session_id = kwargs.pop("_session_id", None)
        limit = kwargs.pop("_limit", 15)
        user_type = kwargs.pop("_user_type", "website")
        render_html = user_type.lower() == "website"
        is_whatsapp = user_type.lower() == "whatsapp"

        if limit is None:
            limit = 15

        try:
            payload = FlightSearchInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid flight search input",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        # --------------------------------------------------
        # Search flights
        # --------------------------------------------------
        flight_results = await search_flights(
            origin=payload.origin,
            destination=payload.destination,
            outbound_date=payload.outbound_date,
            return_date=payload.return_date,
            adults=payload.adults,
            children=payload.children,
            infants=payload.infants,
            cabin=payload.cabin,
            stops=payload.stops,
            fastest=payload.fastest,
            refundable=payload.refundable,
            fare_type=payload.fare_type,
            departure_time_window=payload.departure_time_window,
            arrival_time_window=payload.arrival_time_window,
            airline_names=payload.airline_names,
        )
        has_error = bool(flight_results.get("error")) 
        
        # --------------------------------------------------
        # Passenger context (required for deeplinks)
        # --------------------------------------------------
        flight_results["passengers"] = {
            "adults": payload.adults,
            "children": payload.children,
            "infants": payload.infants,
        }
        flight_results["fastest"] = payload.fastest
        is_roundtrip = flight_results.get("is_roundtrip")
        is_international = flight_results.get("is_international")
        
        if is_whatsapp and not is_international:
           flight_results = filter_domestic_roundtrip_flights(flight_results)

        # --------------------------------------------------
        # Store TOTAL counts BEFORE pagination
        # --------------------------------------------------
        all_outbound = flight_results.get("outbound_flights") or []
        all_return = flight_results.get("return_flights") or []
        all_combos = flight_results.get("international_combos") or []
        
        total_outbound_count = len(all_outbound)
        total_return_count = len(all_return)
        total_combo_count = len(all_combos)

        # DEBUG
        # print(f"DEBUG: Total outbound flights: {total_outbound_count}")
        # print(f"DEBUG: Total return flights: {total_return_count}")
        # print(f"DEBUG: Total international combos: {total_combo_count}")
        # print(f"DEBUG: Page requested: {payload.page}")
        # print(f"DEBUG: Limit: {limit}")

        # --------------------------------------------------
        # Pagination logic
        # --------------------------------------------------
        page = payload.page
        offset = (page - 1) * limit
        end = offset + limit

        # print(f"DEBUG: Offset: {offset}, End: {end}")

        # Paginate each list
        paginated_outbound = all_outbound[offset:end] if not has_error else []
        paginated_return = all_return[offset:end] if not has_error else []
        paginated_combos = all_combos[offset:end] if not has_error else []

        # print(f"DEBUG: Paginated outbound count: {len(paginated_outbound)}")
        # print(f"DEBUG: Paginated return count: {len(paginated_return)}")
        # print(f"DEBUG: Paginated combos count: {len(paginated_combos)}")

        # --------------------------------------------------
        # Generate short links for PAGINATED flights
        # --------------------------------------------------
        if is_international and paginated_combos:
            paginated_combos = generate_short_link(
                paginated_combos,
                product_type="flight",
            )
            paginated_outbound = []
            paginated_return = []
        else:
            paginated_outbound = generate_short_link(
                paginated_outbound,
                product_type="flight",
            ) if paginated_outbound else []

            if is_roundtrip and paginated_return:
                paginated_return = generate_short_link(
                    paginated_return,
                    product_type="flight",
                )

        # --------------------------------------------------
        # Update flight_results with paginated data
        # --------------------------------------------------
        flight_results["outbound_flights"] = paginated_outbound
        flight_results["return_flights"] = paginated_return
        flight_results["international_combos"] = paginated_combos

        # Add pagination info
        if is_international and is_roundtrip:
            total_count = total_combo_count
            paginated_count = len(paginated_combos)
        elif is_roundtrip:
            total_count = min(total_outbound_count, total_return_count)
            paginated_count = min(len(paginated_outbound), len(paginated_return))
        else:
            total_count = total_outbound_count
            paginated_count = len(paginated_outbound)

        flight_results["pagination"] = {
            "current_page": page,
            "per_page": limit,
            "total_results": total_count,
            "total_pages": (total_count + limit - 1) // limit if limit > 0 else 1,
            "has_next_page": end < total_count,
            "has_previous_page": page > 1,
            "showing_from": offset + 1 if paginated_count > 0 else 0,
            "showing_to": min(end, total_count),
        }

        # --------------------------------------------------
        # WhatsApp response
        # --------------------------------------------------
        whatsapp_response = (
            build_whatsapp_flight_response(payload, flight_results)
            if is_whatsapp and not has_error
            else None
        )

        # --------------------------------------------------
        # Response text
        # --------------------------------------------------
        if has_error:
            text = f"No flights found. {flight_results.get('message', '')}"
        elif paginated_count == 0:
            text = f"No more flights available. All {total_count} flights have been shown."
        else:
            has_more = flight_results["pagination"]["has_next_page"]
            if is_international and is_roundtrip:
                if page > 1:
                    if has_more:
                        text = f"Here are {paginated_count} more international round-trip combinations (page {page}). More available."
                    else:
                        text = f"Here are the last {paginated_count} international round-trip combinations (page {page})."
                else:
                    if has_more:
                        text = f"Found {paginated_count} international round-trip combinations. Say 'show more' for additional options."
                    else:
                        text = f"Found all {paginated_count} international round-trip combinations."
            elif is_roundtrip:
                if page > 1:
                    if has_more:
                        text = f"Here are {len(paginated_outbound)} more outbound and {len(paginated_return)} return flights (page {page}). More available."
                    else:
                        text = f"Here are the last {len(paginated_outbound)} outbound and {len(paginated_return)} return flights (page {page})."
                else:
                    if has_more:
                        text = f"Found {len(paginated_outbound)} outbound and {len(paginated_return)} return flights. Say 'show more' for additional options."
                    else:
                        text = f"Found {len(paginated_outbound)} outbound and {len(paginated_return)} return flights."
            else:
                if page > 1:
                    if has_more:
                        text = f"Here are {paginated_count} more flights (page {page}). More available."
                    else:
                        text = f"Here are the last {paginated_count} flights (page {page})."
                else:
                    if has_more:
                        text = f"Found {paginated_count} flights. Say 'show more' for additional options."
                    else:
                        text = f"Found all {paginated_count} flights."

        # --------------------------------------------------
        # Check if any flights to render
        # --------------------------------------------------
        has_flights = paginated_count > 0

        return ToolResponseFormat(
            response_text=text,
            structured_content=None if is_whatsapp else flight_results,
            html=render_flight_results(flight_results)
            if render_html and not has_error and has_flights
            else None,
            whatsapp_response=(
                whatsapp_response.model_dump()
                if whatsapp_response
                else None
            ),
            is_error=has_error,
        )
