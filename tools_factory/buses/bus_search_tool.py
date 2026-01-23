"""Bus Search Tool for EaseMyTrip.

This module provides the bus search tool that integrates with
the EaseMyTrip Bus API for searching buses between cities.

"""

from tools_factory.base import BaseTool, ToolMetadata
from pydantic import ValidationError
from .bus_schema import BusSearchInput
from .bus_search_service import search_buses, build_whatsapp_bus_response
from tools_factory.base_schema import ToolResponseFormat


class BusSearchTool(BaseTool):
    """Bus search tool for EaseMyTrip Bus Service."""

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
        """Execute bus search with provided parameters.
        
        Args (from ):
            sourceId: Source city ID (e.g., "733" for Delhi)
            destinationId: Destination city ID (e.g., "757" for Manali)
            journeyDate: Journey date in YYYY-MM-DD format (converted to dd-MM-yyyy for API)
            isVolvo: Optional filter for Volvo buses only
            _limit: Optional limit for number of results
            _user_type: User type ("website" or "whatsapp")
            
        Returns:
            ToolResponseFormat with bus search results
        """
        # Extract runtime flags
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

        # Search buses using  API endpoint
        bus_results = await search_buses(
            source_id=payload.source_id,
            destination_id=payload.destination_id,
            journey_date=payload.journey_date,
            is_volvo=payload.is_volvo,
        )

        has_error = bool(bus_results.get("error"))

        # Apply limit if specified
        if limit is not None and "buses" in bus_results:
            bus_results["buses"] = bus_results["buses"][:limit]

        buses = bus_results.get("buses", [])
        bus_count = len(buses)

        # Build WhatsApp response if needed
        whatsapp_response = (
            build_whatsapp_bus_response(payload, bus_results)
            if is_whatsapp and not has_error
            else None
        )

        if has_error:
            text = f"No buses found. {bus_results.get('message', '')}"
        else:
            text = f"Found {bus_count} buses from {payload.source_id} to {payload.destination_id}!"

        return ToolResponseFormat(
            response_text=text,
            structured_content=None if is_whatsapp else bus_results,
            html=None,
            whatsapp_response=(
                whatsapp_response.model_dump()
                if whatsapp_response
                else None
            ),
            is_error=has_error,
        )