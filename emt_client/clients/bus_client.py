import aiohttp
from ..config import (
    BUS_SEARCH_URL,
    BUS_SEAT_BIND_URL,
    BUS_AUTOSUGGEST_URL,
    BUS_AUTOSUGGEST_KEY,
    BUS_ENCRYPTED_HEADER,
)


class BusApiClient:
    """Bus API client for EaseMyTrip bus service."""
    
    def __init__(self):
        self.search_url = BUS_SEARCH_URL
        self.seat_bind_url = BUS_SEAT_BIND_URL
        self.autosuggest_url = BUS_AUTOSUGGEST_URL
        self.autosuggest_key = BUS_AUTOSUGGEST_KEY
        self.encrypted_header = BUS_ENCRYPTED_HEADER

    async def search(self, payload: dict) -> dict:
        """Search buses between cities."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.search_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=120),
            ) as response:
                if response.status != 200:
                    return {"error": f"API returned status {response.status}"}
                return await response.json()

    async def get_seat_layout(self, payload: dict) -> dict:
        """Get seat layout for a specific bus."""
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
        """Get city suggestions from autosuggest API."""
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