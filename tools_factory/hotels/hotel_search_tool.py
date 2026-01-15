"""
Hotel Search Tool
Wrapper for hotel search functionality in the Tool Factory
"""
from typing import Dict, Any
from pydantic import ValidationError
from ..base import BaseTool, ToolMetadata
from emt_client.utils import generate_short_link
from .hotel_schema import HotelSearchInput, HotelResponseFormat, WhatsappHotelFinalResponse, WhatsappHotelFormat
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

    async def execute(self, **kwargs) -> HotelResponseFormat:
        # --------------------------
        # Extract runtime flags
        # --------------------------
        
        # limit = kwargs.pop("_limit", None)
        # render_html = kwargs.pop("_html", False)
        # is_coming_from_whatsapp = kwargs.pop("is_coming_from_whatsapp", False)

        # --------------------------
        # Extract runtime flags (with backward compatibility)
        # --------------------------
        limit = kwargs.pop("_limit", None)

        # Handle legacy flags
        if "_user_type" not in kwargs:
            if kwargs.pop("is_coming_from_whatsapp", False):
                kwargs["_user_type"] = "whatsapp"
            elif kwargs.pop("_html", False):
                kwargs["_user_type"] = "web"

        # Unified user type handling
        user_type = kwargs.pop("_user_type", "web")
        render_html = user_type.lower() != "whatsapp"
        is_coming_from_whatsapp = user_type.lower() == "whatsapp"


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

                for idx, hotel in enumerate(hotels[:3], start=1):
                    whatsapp_hotels.append({
                        "option_id": idx,
                        "hotel_name": hotel.get("name"),
                        "location": hotel.get("location"),
                        "rating": hotel.get("rating"),
                        "price": hotel.get("price", {}).get("amount", ""),
                        "price_unit": "per night",
                        "image_url": hotel.get("hotelImage"),
                        "amenities": hotel.get("highlights") or "Not specified",
                        "booking_url": hotel.get("deepLink"),
                    })

                whatsapp_json: WhatsappHotelFormat = WhatsappHotelFormat(
                    type="hotel_collection",
                    options=whatsapp_hotels,
                    check_in_date=search_input.check_in_date,
                    check_out_date=search_input.check_out_date,
                    currency=results.get("currency", "INR"),
                    view_all_hotels_url=results.get("viewAll", ""),
                )

                whatsapp_response: WhatsappHotelFinalResponse = WhatsappHotelFinalResponse(
                    response_text=f"Here are the best hotel options in {search_input.city_name}",
                    whatsapp_json=whatsapp_json
                )

            # =========================================================
            # NORMAL RESPONSE MODE
            # =========================================================
            if results.get("error"):
                text = f"No hotels found. {results.get('message', '')}"
            else:
                text = f"Found {hotel_count} hotels in {search_input.city_name}!"

            response: HotelResponseFormat = HotelResponseFormat(
                response_text=text,
                structured_content=results if not is_coming_from_whatsapp else {},
                html=render_hotel_results(results) if render_html and not results.get("error") else None,
                whatsapp_response=whatsapp_response if is_coming_from_whatsapp and not results.get("error") else None,
                is_error=results.get("error") is not None,
            )

            return response

        except ValidationError as exc:
            return HotelResponseFormat(
                response_text="Invalid hotel search input",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                html=None,
                whatsapp_response=None,
                is_error=True,
            )

        except Exception as e:
            return HotelResponseFormat(
                response_text=f"Hotel search failed: {str(e)}",
                structured_content={
                    "error": "SEARCH_ERROR",
                    "message": str(e),
                },
                html=None,
                whatsapp_response=None,
                is_error=True,
            )


def create_hotel_search_tool() -> HotelSearchTool:
    return HotelSearchTool()
