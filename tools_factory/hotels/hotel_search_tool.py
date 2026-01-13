"""
Hotel Search Tool
Wrapper for hotel search functionality in the Tool Factory
"""
from typing import Dict, Any
from pydantic import ValidationError
from ..base import BaseTool, ToolMetadata
from emt_client.utils import generate_short_link
from .hotel_schema import HotelSearchInput
from .hotel_search_service import HotelSearchService
from .hotel_renderer import render_hotel_results


class HotelSearchTool(BaseTool):
    """
    Tool for searching hotels on EaseMyTrip.
    """

    def __init__(self):
        super().__init__()
        self.service = HotelSearchService()

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="search_hotels",
            description=(
                "Search for hotels in a specific city with check-in and check-out dates. "
                "Supports filtering by price range, star ratings, amenities, and sorting options."
            ),
            input_schema=HotelSearchInput.model_json_schema(),
            category="travel",
            tags=["hotel", "search", "booking", "travel"],
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        # --------------------------
        # Extract runtime flags
        # --------------------------
        limit = kwargs.pop("_limit", None)
        render_html = kwargs.pop("_html", False)
        is_coming_from_whatsapp = kwargs.pop("is_coming_from_whatsapp", False)

        try:
            # Validate input
            search_input = HotelSearchInput(**kwargs)

            # Execute hotel search
            results = await self.service.search(search_input)
            hotels = results.get("hotels") or []

            # Generate short links (best-effort)
            try:
                if hotels:
                    results["hotels"] = generate_short_link(
                        hotels,
                        product_type="hotel"
                    )
            except Exception:
                results["hotels"] = hotels

            # --------------------------
            # Apply limit
            # --------------------------
            if limit is not None and "hotels" in results:
                results["hotels"] = results["hotels"][:limit]

            hotels = results.get("hotels", [])
            hotel_count = len(hotels)

            # =========================================================
            # WHATSAPP RESPONSE MODE
            # =========================================================
            if is_coming_from_whatsapp:
                whatsapp_hotels = []

                for hotel in hotels[:3]:
                    whatsapp_hotels.append({
                        "hotel_name": hotel.get("name"),
                        "location": hotel.get("location"),
                        "rating": hotel.get("rating"),
                        "price": str(
                            hotel.get("price", {}).get("amount", "")
                        ),
                        "price_unit": "per night",
                        "image_url": hotel.get("hotelImage"),
                        "amenities": hotel.get("highlights") or "Not specified",
                        "booking_url": hotel.get("deepLink"),
                    })

                whatsapp_resp = {
                    "type": "hotel_collection",
                    "hotels": whatsapp_hotels,
                    "view_all_hotels_url": results.get("viewAll", ""),
                }

            # =========================================================
            # NORMAL RESPONSE MODE
            # =========================================================
            if results.get("error"):
                text = f"No hotels found. {results.get('message', '')}"
            else:
                text = f"Found {hotel_count} hotels in {search_input.city_name}!"

            response: Dict[str, Any] = {
                "text": text,
                "structured_content": results,
                "html": None,
                "whatsapp_response": whatsapp_resp if is_coming_from_whatsapp else None,
                "is_error": results.get("error") is not None,
            }

            # Render HTML if requested
            if render_html and not results.get("error"):
                response["html"] = render_hotel_results(results)

            return response

        except ValidationError as exc:
            return {
                "text": "Invalid hotel search input",
                "structured_content": {
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                "html": None,
                "is_error": True,
            }

        except Exception as e:
            return {
                "text": f"Hotel search failed: {str(e)}",
                "structured_content": {
                    "error": "SEARCH_ERROR",
                    "message": str(e),
                },
                "html": None,
                "is_error": True,
            }


def create_hotel_search_tool() -> HotelSearchTool:
    return HotelSearchTool()
