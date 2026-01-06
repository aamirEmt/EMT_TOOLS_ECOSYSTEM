from typing import Dict, Any
from tools_factory.base import BaseTool, ToolMetadata
from pydantic import ValidationError

from .flight_scehma import FlightSearchInput
from .flight_search_service import (
    search_flights,
    build_ui_flight_card,
)
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
        # --------------------------
        # Extract extra runtime flags
        # --------------------------
        limit = kwargs.pop("_limit", None)
        render_html = kwargs.pop("_html", False)

        # --------------------------
        # Validate LLM-facing args only
        # --------------------------
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

        # --------------------------
        # Perform the flight search
        # --------------------------
        flight_results = await search_flights(
            origin=payload.origin,
            destination=payload.destination,
            outbound_date=payload.outbound_date,
            return_date=payload.return_date,
            adults=payload.adults,
            children=payload.children,
            infants=payload.infants,
        )

        # --------------------------
        # Apply limit to results if requested
        # --------------------------
        if limit is not None:
            if "outbound_flights" in flight_results:
                flight_results["outbound_flights"] = flight_results["outbound_flights"][:limit]
            if "return_flights" in flight_results:
                flight_results["return_flights"] = flight_results["return_flights"][:limit]
            if "international_combos" in flight_results:
                flight_results["international_combos"] = flight_results["international_combos"][:limit]

        # --------------------------
        # Compose text summary
        # --------------------------
        outbound_count = len(flight_results.get("outbound_flights", []))
        return_count = len(flight_results.get("return_flights", []))

        if flight_results.get("error"):
            text = f"No flights found. {flight_results.get('message', '')}"
        elif flight_results.get("is_roundtrip"):
            text = f"Found {outbound_count} outbound and {return_count} return flights!"
        else:
            text = f"Found {outbound_count} flights!"

        # --------------------------
        # Prepare generic response
        # --------------------------
        response: Dict[str, Any] = {
            "text": text,
            "structured_content": flight_results,
            "html": None,  # placeholder for rendered HTML
            "is_error": flight_results.get("error") is not None,
        }

        # --------------------------
        # Build React-equivalent UI cards
        # --------------------------
        ui_cards = []

        for flight in flight_results.get("outbound_flights", []):
            card = build_ui_flight_card(flight)
            if card:
                ui_cards.append(card)


        # --------------------------
        # Render HTML carousel if requested
        # --------------------------
        if render_html and not flight_results.get("error"):
            response["html"] = render_flight_results(
                {"flights": ui_cards}
            )

        return response
