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
        """
        Execute hotel search with provided parameters.
        
        Args:
            city_name (str): City or area name (e.g., "Pune", "Viman Nagar, Pune")
            check_in_date (str): Check-in date in YYYY-MM-DD format
            check_out_date (str): Check-out date in YYYY-MM-DD format
            num_rooms (int, optional): Number of rooms. Default: 1
            num_adults (int, optional): Number of adults. Default: 2
            num_children (int, optional): Number of children. Default: 0
            page_no (int, optional): Page number for pagination. Default: 1
            hotel_count (int, optional): Max hotels per page. Default: 30
            min_price (int, optional): Minimum price filter in INR
            max_price (int, optional): Maximum price filter in INR. Default: 10000000
            sort_type (str, optional): Sort criteria. Default: "Popular|DESC"
            rating (List[str], optional): Star ratings filter (e.g., ["3", "4", "5"])
            amenities (List[str], optional): Amenities filter (e.g., ["Free WiFi", "Pool"])
            _limit (int, optional): Limit number of hotels returned (internal use)
            _html (bool, optional): Render HTML carousel (internal use)
        
        Returns:
            Dict containing:
                - text (str): Human-readable summary of results
                - structured_content (dict): Search results with hotel list and metadata
                - html (str): Rendered HTML carousel (if _html=True)
                - is_error (bool): Whether an error occurred
        
        Example:
            >>> tool = HotelSearchTool()
            >>> result = await tool.execute(
            ...     city_name="Pune",
            ...     check_in_date="2024-12-25",
            ...     check_out_date="2024-12-27",
            ...     num_rooms=1,
            ...     num_adults=2,
            ...     rating=["4", "5"],
            ...     amenities=["Free WiFi", "Pool"]
            ... )
            >>> print(result["text"])
            Found 150 hotels!
        """
        session_id = kwargs.pop("_session_id", None)
        limit = kwargs.pop("_limit", None)
        user_type = kwargs.pop("_user_type", "website")
        render_html = user_type.lower() == "website"
        is_whatsapp = user_type.lower() == "whatsapp"
        
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
       
        if limit is not None and "hotels" in results:
                results["hotels"] = results["hotels"][:limit]
        try:
            if results["hotels"]:
                results["hotels"] = generate_short_link(
                    results["hotels"],
                    product_type="hotel"
                )
        except Exception as e:
            # DO NOT FAIL hotel search because of short-link issues
            results["hotels"] = results["hotels"]

            
           
          
            
        hotels = results.get("hotels", [])
        hotel_count = len(hotels)

        whatsapp_response = None
        if is_whatsapp and not results.get("error"):
            whatsapp_response = self.service.build_whatsapp_hotel_response(
                results=results,
                search_input=search_input
            )
            
            # Create human-readable message
        if results.get("error"):
            text = f"No hotels found. {results.get('message', '')}"
        else:
            text = f"Found {hotel_count} hotels in {search_input.city_name}!"

        # --------------------------------------------------
        # Final unified response
        # --------------------------------------------------
        return ToolResponseFormat(
            response_text=text,
            structured_content=results if not is_whatsapp else {},
            html=render_hotel_results(results)
            if render_html and not results.get("error")
            else None,
             whatsapp_response=(
                whatsapp_response.model_dump()
                if whatsapp_response
                else None
            ),
            is_error=results.get("error") is not None,
        )


def create_hotel_search_tool() -> HotelSearchTool:
    return HotelSearchTool()
