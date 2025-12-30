"""Booking API Client for EMT - Using exact code from get_bookings.py"""
import httpx
from typing import Dict, Any

from .client import EMTClient

# Exact URL from get_bookings.py
BOOKINGS_URL = "https://emtservice-ln.easemytrip.com/api/Product/search-product"


class BookingApiClient(EMTClient):
    """Booking API Client using exact logic from get_bookings.py"""
    
    def __init__(self, token_provider=None):
        super().__init__(token_provider)
    
    async def fetch_bookings(
        self,
        auth: str,
        email: str,
        ip: str
    ) -> Dict[str, Any]:
        """Exact get_all_bookings logic from get_bookings.py"""
        
        # Exact payload from get_bookings.py
        payload = {
            "Auth": auth,
            "EmailId": email if isinstance(email, str) else email[0],
            "Password": "android",
            "ProcessType": 45,
            "Authentication": {
                "AgentCode": 1003,
                "UserName": "android",
                "Password": "android",
                "IPAddress": "49.249.40.58", 
            }
        }

        # Exact headers from get_bookings.py
        # Use EmailId from payload for auth, fallback to hardcoded if not present
        auth_email = payload.get("EmailId", "upmanyu.wadhwa@easemytrip.com")
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0",
            "auth": auth_email
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    BOOKINGS_URL,
                    json=payload,
                    headers=headers
                )
            data = response.json()
            
            # Debug output - matches get_bookings.py
            print("===== EMT BOOKINGS RAW RESPONSE =====")
            print(data)
            print("====================================")
        except Exception as e:
            return {
                "success": False,
                "error": "INVALID_RESPONSE",
                "raw": str(e)
            }

        return {
            "success": True,
            "data": data
        }
