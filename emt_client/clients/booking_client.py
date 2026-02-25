"""Booking API Client for EMT"""
import httpx
from typing import Dict, Any

from .client import EMTClient

BOOKINGS_URL = "https://emtservice-ln.easemytrip.com/api/Product/search-product"


class BookingApiClient(EMTClient):
    
    def __init__(self, token_provider=None):
        super().__init__(token_provider)
    
    async def fetch_bookings(
        self,
        action2_token: str,
        uid: str,
        ip: str,
        process_type: int = 45
    ) -> Dict[str, Any]:
        
        payload = {
            "Auth": action2_token,
            "EmailId": uid,
            "Password": "android",
            "ProcessType": process_type,
            "Authentication": {
                "AgentCode": 1003,
                "UserName": "android",
                "Password": "android",
                "IPAddress": ip, 
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0",
            "auth": uid
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    BOOKINGS_URL,
                    json=payload,
                    headers=headers
                )
            data = response.json()
            
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
