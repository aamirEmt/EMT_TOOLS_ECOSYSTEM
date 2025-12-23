"""
Hotel API Client
Handles hotel-specific API operations with token injection
"""
from .client import EMTClient
from ..auth.hotel_auth import HotelTokenProvider
from ..config import VID, DEFAULT_AUTH
from ..utils import gen_trace_id


class HotelApiClient:
    """Client for EaseMyTrip Hotel API operations"""
    
    def __init__(self):
        self.token_provider = HotelTokenProvider()
        self.client = EMTClient(self._inject_hotel_tokens)
    
    async def _inject_hotel_tokens(self) -> dict:
        """
        Inject hotel authentication tokens into request payload.
        
        Returns:
            Dict containing 'token', 'emtToken', 'auth', 'vid', 'traceid'
        """
        tokens = await self.token_provider.get_tokens()
        
        return {
            "token": tokens.get("token", ""),
            "emtToken": tokens.get("emtToken", ""),
            "auth": DEFAULT_AUTH,
            "vid": VID,
            "traceid": gen_trace_id()
        }
    
    async def search(self, url: str, payload: dict) -> dict:
        """
        Execute hotel search API request.
        
        Args:
            url: API endpoint URL
            payload: Request payload (tokens will be auto-injected)
        
        Returns:
            API response dictionary
        
        Example:
            >>> client = HotelApiClient()
            >>> response = await client.search(
            ...     "https://hotelservice.easemytrip.com/api/HotelService/HotelListIdWiseNew",
            ...     {
            ...         "CheckInDate": "2024-12-25",
            ...         "CheckOut": "2024-12-27",
            ...         "CityCode": "PUNE,INDIA",
            ...         # ... other params
            ...     }
            ... )
        """
        return await self.client.post(url, payload)
    
    async def get_hotel_details(self, url: str, payload: dict) -> dict:
        """
        Fetch detailed information for a specific hotel.
        
        Args:
            url: Hotel details API endpoint
            payload: Request payload with hotel identifiers
        
        Returns:
            Hotel details response
        """
        return await self.client.post(url, payload)