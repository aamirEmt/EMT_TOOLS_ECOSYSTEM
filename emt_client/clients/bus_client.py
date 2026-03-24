import aiohttp
from typing import Dict, Any, List
from ..config import (
    BUS_SEARCH_URL,
    BUS_SEAT_BIND_URL,
    BUS_AUTOSUGGEST_URL,
    BUS_AUTOSUGGEST_KEY,
    BUS_ENCRYPTED_HEADER,
    BUS_SECRET_KEY,
    BUS_SOURCE_AUTOSUGGEST_URL,
    BUS_DEST_AUTOSUGGEST_URL,
)


class BusApiClient:
    
    def __init__(self):
        self.search_url = BUS_SEARCH_URL
        self.seat_bind_url = BUS_SEAT_BIND_URL
        self.autosuggest_url = BUS_AUTOSUGGEST_URL
        self.autosuggest_key = BUS_AUTOSUGGEST_KEY
        self.encrypted_header = BUS_ENCRYPTED_HEADER
        self.secret_key = BUS_SECRET_KEY
        self.source_autosuggest_url = BUS_SOURCE_AUTOSUGGEST_URL
        self.dest_autosuggest_url = BUS_DEST_AUTOSUGGEST_URL

    async def search(self, payload: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.search_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-client-secret-key": self.secret_key,
                },
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                if response.status != 200:
                    return {"error": f"API returned status {response.status}"}
                return await response.json(content_type=None)

    async def get_seat_layout(self, payload: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.seat_bind_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-client-secret-key": self.secret_key,
                },
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 200:
                    return {"error": f"API returned status {response.status}"}
                return await response.json(content_type=None)

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
            
    async def get_source_city_suggestions(self, prefix: str = '') -> List[Dict]:
        url = self.source_autosuggest_url
        if prefix:
            url = f"{url}?prefix={prefix}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={"Accept": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status != 200:
                    return []
                return await response.json(content_type=None)

    async def get_dest_city_suggestions(self, source_id: str, prefix: str = '') -> List[Dict]:
        url = f"{self.dest_autosuggest_url}?sourceId={source_id}"
        if prefix:
            url = f"{url}&prefix={prefix}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={"Accept": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status != 200:
                    return []
                return await response.json(content_type=None)

    async def confirm_seats(self, payload: Dict[str, Any]) -> Dict[str, Any]:

        from emt_client.config import BUS_CONFIRM_SEATS_URL
        
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "x-requested-with": "XMLHttpRequest",
            "access-control-allow-origin": "true",
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
                        return await response.json(content_type=None)
                    else:
                        return {
                            "error": f"HTTP {response.status}: {await response.text()}"
                        }
        except Exception as e:
            return {"error": str(e)}