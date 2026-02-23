"""
Hotel Search Tool
Wrapper for hotel search functionality in the Tool Factory
"""
from typing import Dict, Any, Optional
from pydantic import ValidationError
from ..base import BaseTool, ToolMetadata
from emt_client.utils import generate_short_link
from .hotel_schema import HotelSearchInput
from .hotel_search_service import HotelSearchService
from .hotel_renderer import render_hotel_results
from tools_factory.base_schema import ToolResponseFormat


class HotelSearchTool(BaseTool):
    """
    Tool for searching hotels on EaseMyTrip.
    
    This tool allows searching for hotels in a city with specified
    check-in/check-out dates, room configuration, and optional filters
    like price range, star ratings, and amenities.
    """
    
    def __init__(self):
        super().__init__()
        self.service = HotelSearchService()
    
    def get_metadata(self) -> ToolMetadata:
        """
        Return tool metadata for discovery and documentation.
        
        Returns:
            ToolMetadata with tool information including:
                - name: Unique identifier for the tool
                - description: What the tool does
                - category: Grouping category (e.g., "travel")
                - tags: Searchable keywords
                - input_schema: JSON schema dict for input validation
        """
        return ToolMetadata(
            name="search_hotels",
            description=(
                "Search for hotels in a specific city with check-in and check-out dates. "
                "Supports filtering by price range, star ratings, amenities, and sorting options. "
                "Returns a list of available hotels with pricing, ratings, and booking links."
            ),
            input_schema=HotelSearchInput.model_json_schema(),
            category="travel",
            tags=["hotel", "search", "booking", "travel", "accommodation"]
        )
    
    async def execute(self, **kwargs) -> ToolResponseFormat:
        session_id = kwargs.pop("_session_id", None)
        limit = kwargs.pop("_limit", 15) 
        user_type = kwargs.pop("_user_type", "website")
        render_html = user_type.lower() == "website"
        is_whatsapp = user_type.lower() == "whatsapp"
        
        if limit is None:
            limit = 15
        
        try:
            search_input = HotelSearchInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid hotel search input",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                html=None,
                whatsapp_response=None,
                is_error=True,
            )
            
        # Execute search through service layer
        try:
            results: Dict[str, Any] = await self.service.search(search_input)
        except Exception as exc:
            return ToolResponseFormat(
                response_text="Hotel search failed",
                structured_content={
                    "error": "SEARCH_ERROR",
                    "message": str(exc),
                },
                html=None,
                whatsapp_response=None,
                is_error=True,
            )
        
        has_error = bool(results.get("error"))
        
        # Store original total count BEFORE pagination
        all_hotels = results.get("hotels", [])
        total_hotel_count = len(all_hotels)

        # DEBUG: Print counts
        # print(f"DEBUG: Total hotels from API: {total_hotel_count}")
        # print(f"DEBUG: Page requested: {search_input.page}")
        # print(f"DEBUG: Limit: {limit}")
        
        # Pagination logic
        page = search_input.page
        offset = (page - 1) * limit
        end = offset + limit
        paginated_hotels = all_hotels[offset:end] if not has_error else []

        # DEBUG: Print pagination result
        # print(f"DEBUG: Offset: {offset}, End: {end}")
        # print(f"DEBUG: Paginated hotels count: {len(paginated_hotels)}")
        
        # Create limited_results as a COPY with paginated hotels
        limited_results = results.copy()
        limited_results["hotels"] = paginated_hotels
        limited_results["pagination"] = {
            "current_page": page,
            "per_page": limit,
            "total_results": total_hotel_count,
            "total_pages": (total_hotel_count + limit - 1) // limit if limit > 0 else 1,
            "has_next_page": end < total_hotel_count,
            "has_previous_page": page > 1,
            "showing_from": offset + 1 if paginated_hotels else 0,
            "showing_to": min(end, total_hotel_count),
        }
        
        hotel_count = len(paginated_hotels)

        # Generate short links for paginated hotels
        try:
            if paginated_hotels:
                limited_results["hotels"] = generate_short_link(
                    paginated_hotels,
                    product_type="hotel"
                )
        except Exception as e:
            # DO NOT FAIL hotel search because of short-link issues
            pass

        # Build WhatsApp response if needed
        whatsapp_response = None
        if is_whatsapp and not has_error:
            whatsapp_response = self.service.build_whatsapp_hotel_response(
                results=limited_results,
                search_input=search_input
            )
            
        # Create human-readable message
        if has_error:
            text = f"No hotels found. {results.get('message', '')}"
        elif hotel_count == 0:
            text = f"No more hotels available in {search_input.city_name}. All {total_hotel_count} hotels have been shown."
        else:
            pagination = limited_results.get("pagination", {})
            has_more = pagination.get("has_next_page", False)
            if page > 1:
                if has_more:
                    text = f"Here are {hotel_count} more hotels in {search_input.city_name} (page {page}). More available."
                else:
                    text = f"Here are the last {hotel_count} hotels in {search_input.city_name} (page {page}). This completes all {total_hotel_count} hotels."
            else:
                if has_more:
                    text = f"Here are {hotel_count} hotels in {search_input.city_name}. Say 'show more' for additional options."
                else:
                    text = f"Here are all {hotel_count} hotels available in {search_input.city_name}."

        # Render HTML for website
        html_output = None
        if render_html and not has_error and total_hotel_count > 0:
            render_data = results.copy()
            render_data["hotels"] = limited_results["hotels"]  # Use short-linked hotels
            render_data["viewAll"] = results.get("viewAll", "")  # Explicitly preserve viewAll
            
            html_output = render_hotel_results(
                render_data,
                total_hotel_count=total_hotel_count,
            )

        # Final unified response
        return ToolResponseFormat(
            response_text=text,
            structured_content=limited_results if not is_whatsapp else {},
            html=html_output,
            whatsapp_response=(
                whatsapp_response.model_dump()
                if whatsapp_response
                else None
            ),
            is_error=has_error,
        )


def create_hotel_search_tool() -> HotelSearchTool:
    return HotelSearchTool()
