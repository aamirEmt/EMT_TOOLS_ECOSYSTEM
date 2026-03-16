import aiohttp
from typing import Dict, Any
from ..config import (
    BUS_SEARCH_URL,
    BUS_SEAT_BIND_URL,
    BUS_AUTOSUGGEST_URL,
    BUS_AUTOSUGGEST_KEY,
    BUS_ENCRYPTED_HEADER,
)


class BusApiClient:
    
    def __init__(self):
        self.search_url = BUS_SEARCH_URL
        self.seat_bind_url = BUS_SEAT_BIND_URL
        self.autosuggest_url = BUS_AUTOSUGGEST_URL
        self.autosuggest_key = BUS_AUTOSUGGEST_KEY
        self.encrypted_header = BUS_ENCRYPTED_HEADER

    async def search(self, payload: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.search_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"[BUS_SEARCH] HTTP {response.status}: {error_text[:500]}")
                    return {"error": f"API returned status {response.status}"}
                data = await response.json(content_type=None)
                # Debug: log top-level keys and Response sub-keys
                resp_obj = data.get("Response", {}) if isinstance(data, dict) else {}
                print(f"[BUS_SEARCH] Top-level keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                print(f"[BUS_SEARCH] Response keys: {list(resp_obj.keys()) if isinstance(resp_obj, dict) else resp_obj}")
                trips = resp_obj.get("AvailableTrips") if isinstance(resp_obj, dict) else None
                print(f"[BUS_SEARCH] AvailableTrips count: {len(trips) if trips else 0}")
                return data

    async def get_seat_layout(self, payload: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.seat_bind_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 200:
                    return {"error": f"API returned status {response.status}"}
                return await response.json()

    async def get_city_suggestions(self, encrypted_payload: dict) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.autosuggest_url}?useby=popularu&key={self.autosuggest_key}",
                json=encrypted_payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 200:
                    raise Exception(f"Autosuggest API returned status {response.status}")
                return await response.text()
            
    async def confirm_seats(self, payload: Dict[str, Any]) -> Dict[str, Any]:

        from emt_client.config import BUS_CONFIRM_SEATS_URL
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    BUS_CONFIRM_SEATS_URL,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {
                            "error": f"HTTP {response.status}: {await response.text()}"
                        }
        except Exception as e:
            return {"error": str(e)}