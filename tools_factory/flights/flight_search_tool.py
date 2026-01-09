from typing import Dict, Any
from tools_factory.base import BaseTool, ToolMetadata
from pydantic import ValidationError
from emt_client.utils import generate_short_link
from .flight_scehma import FlightSearchInput
from .flight_search_service import search_flights


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
        try:
            payload = FlightSearchInput.model_validate(kwargs)
        except ValidationError as exc:
            return {
                "text": "Invalid flight search input",
                "structured_content": {
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                "is_error": True,
            }

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
        outbound_count = 0
        return_count = 0
        international_combos_count = 0

        is_roundtrip = flight_results.get("is_roundtrip")
        is_international = flight_results.get("is_international")

        international_combos = flight_results.get("international_combos") or []

        if is_international and international_combos:
            international_combos_count = len(international_combos)
            flight_results["international_combos"] = generate_short_link(
                international_combos,
                product_type="flight"
            )
            flight_results["outbound_flights"] = []
            flight_results["return_flights"] = []

        else:
            outbound_flights = flight_results.get("outbound_flights") or []
            outbound_count = len(outbound_flights)
            flight_results["outbound_flights"] = generate_short_link(
                outbound_flights, product_type="flight"
            )

            if is_roundtrip:
                return_flights = flight_results.get("return_flights") or []
                return_count = len(return_flights)
                flight_results["return_flights"] = generate_short_link(
                    return_flights, product_type="flight"
                )


    
        return_count = len(flight_results.get("return_flights", []))

        if flight_results.get("error"):
            text = f"No flights found. {flight_results.get('message', '')}"
        elif flight_results.get("is_roundtrip") and not flight_results.get("is_international"):
            text = f"Found {outbound_count} outbound and {return_count} return flights!"
        elif international_combos:
             text = f"Found {international_combos_count} flights!"
        else:
            text = f"Found {outbound_count} flights!"

        return {
            "text": text,
            "structured_content": flight_results,
            "is_error": flight_results.get("error") is not None,
        }
