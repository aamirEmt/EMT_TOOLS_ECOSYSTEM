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

        # --------------------------------------------------
        # Runtime flags (internal)
        # --------------------------------------------------
        # limit = kwargs.pop("_limit", None)
        # render_html = kwargs.pop("_html", False)
        # is_coming_from_whatsapp = kwargs.pop("_is_coming_from_whatsapp", False)

        # --------------------------
        # Extract runtime flags (with backward compatibility)
        # --------------------------
        limit = kwargs.pop("_limit", None)
        user_type = kwargs.pop("_user_type", "website")
        render_html = user_type.lower() == "website"
        is_whatsapp = user_type.lower() == "whatsapp"


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
            fare_type=payload.fare_type,
            departure_time_window=payload.departure_time_window,
            arrival_time_window=payload.arrival_time_window,
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
           flight_results= filter_domestic_roundtrip_flights(flight_results)

        # --------------------------------------------------
        if limit is not None:
            for key in ("outbound_flights", "return_flights", "international_combos"):
                if key in flight_results:
                    flight_results[key] = flight_results[key][:limit]


        outbound_flights = flight_results.get("outbound_flights") or []
        return_flights = flight_results.get("return_flights") or []
        international_combos = flight_results.get("international_combos") or []

        outbound_count = len(outbound_flights)
        return_count = len(return_flights)
        combo_count = len(international_combos)

        

        if is_international and international_combos:
            flight_results["international_combos"] = generate_short_link(
                international_combos,
                product_type="flight",
            )
            flight_results["outbound_flights"] = []
            flight_results["return_flights"] = []
        else:
            flight_results["outbound_flights"] = generate_short_link(
                outbound_flights,
                product_type="flight",
            )

            if is_roundtrip:
                flight_results["return_flights"] = generate_short_link(
                    return_flights,
                    product_type="flight",
                )

       
        whatsapp_response = (
            build_whatsapp_flight_response(payload, flight_results)
            if is_whatsapp and not has_error
            else None
        )

        if has_error:
            text = f"No flights found. {flight_results.get('message', '')}"
        elif is_international and is_roundtrip:
            text = f"Found {combo_count} international round-trip combinations!"
        elif is_roundtrip:
            text = f"Found {outbound_count} outbound and {return_count} return flights!"
        else:
            text = f"Found {outbound_count} flights!"

        # Check if any flights were found
        has_flights = (
            (is_international and is_roundtrip and combo_count > 0) or
            (not is_international and is_roundtrip and outbound_count > 0 and return_count > 0) or
            (not is_roundtrip and outbound_count > 0)
        )

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
