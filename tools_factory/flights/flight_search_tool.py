from typing import Dict, Any
from tools_factory.base import BaseTool, ToolMetadata
from pydantic import ValidationError

from emt_client.utils import generate_short_link
from .flight_scehma import FlightSearchInput
from .flight_search_service import search_flights
from .flight_renderer import render_flight_results


class FlightSearchTool(BaseTool):
    """Flight search tool for EaseMyTrip"""

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="search_flights",
            description="Search for flights on EaseMyTrip with origin, destination, dates, and passengers",
            input_schema=FlightSearchInput.model_json_schema(),
            output_template="ui://widget/flight-carousel.html",
            category="travel",
            tags=["flight", "booking", "travel", "search"],
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute flight search with provided parameters.
        """

        # Runtime flags (internal)
        limit = kwargs.pop("_limit", None)
        render_html = kwargs.pop("_html", False)
        

        try:
            payload = FlightSearchInput.model_validate(kwargs)
        except ValidationError as exc:
            return {
                "text": "Invalid flight search input",
                "structured_content": {
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                "html": None,
                "is_error": True,
            }

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
        )

        # --------------------------------------------------
        # ✅ Passenger context (required for deeplinks)
        # --------------------------------------------------
        flight_results["passengers"] = {
            "adults": payload.adults,
            "children": payload.children,
            "infants": payload.infants,
        }

        # --------------------------------------------------
        # Apply limit (if requested)
        # --------------------------------------------------
        if limit is not None:
            if "outbound_flights" in flight_results:
                flight_results["outbound_flights"] = flight_results["outbound_flights"][:limit]
            if "return_flights" in flight_results:
                flight_results["return_flights"] = flight_results["return_flights"][:limit]
            if "international_combos" in flight_results:
                flight_results["international_combos"] = flight_results["international_combos"][:limit]

        # --------------------------------------------------
        # Normalize & short-link results
        # --------------------------------------------------
        outbound_count = 0
        return_count = 0
        combo_count = 0

        is_roundtrip = flight_results.get("is_roundtrip")
        is_international = flight_results.get("is_international")

        international_combos = flight_results.get("international_combos") or []

        if is_international and international_combos:
            combo_count = len(international_combos)
            flight_results["international_combos"] = generate_short_link(
                international_combos,
                product_type="flight",
            )
            flight_results["outbound_flights"] = []
            flight_results["return_flights"] = []

        else:
            outbound_flights = flight_results.get("outbound_flights") or []
            outbound_count = len(outbound_flights)
            flight_results["outbound_flights"] = generate_short_link(
                outbound_flights,
                product_type="flight",
            )

            if is_roundtrip:
                return_flights = flight_results.get("return_flights") or []
                return_count = len(return_flights)
                flight_results["return_flights"] = generate_short_link(
                    return_flights,
                    product_type="flight",
                )

        # --------------------------------------------------
        # Human-readable text
        # --------------------------------------------------
        if flight_results.get("error"):
            text = f"No flights found. {flight_results.get('message', '')}"
        elif is_international and is_roundtrip:
            text = f"Found {combo_count} international round-trip combinations!"
        elif is_roundtrip:
            text = f"Found {outbound_count} outbound and {return_count} return flights!"
        else:
            text = f"Found {outbound_count} flights!"

        # --------------------------------------------------
        # Response
        # --------------------------------------------------
        response: Dict[str, Any] = {
            "text": text,
            "structured_content": flight_results,
            "html": None,
            "is_error": flight_results.get("error") is not None,
        }

        # --------------------------------------------------
        # Render HTML (if requested)
        # --------------------------------------------------
        if render_html and not flight_results.get("error"):
            response["html"] = render_flight_results(flight_results)

        return response
