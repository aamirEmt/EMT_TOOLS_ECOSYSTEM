import httpx
from typing import Dict
from ..config import FLIGHT_TOKEN_URL, FLIGHT_ATK_TOKEN
from .base import TokenProvider

import asyncio

class FlightTokenProvider(TokenProvider):
    def __init__(self):
        self._itk: str | None = None
        self._lock = asyncio.Lock()

    
    async def get_itk(self) -> str:
        return (await self.get_tokens())["ITK"]
    

    async def get_tokens(self) -> Dict[str, str]:
        if self._itk:
            return {"ITK": self._itk}

        async with self._lock:
            # double-check after acquiring lock
            if self._itk:
                return {"ITK": self._itk}

            headers = {
                "ATK": FLIGHT_ATK_TOKEN,
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=30) as client:
                res = await client.post(FLIGHT_TOKEN_URL, headers=headers, json={})
                res.raise_for_status()
                data = res.json()

            self._itk = data.get("ITK")
            if not self._itk:
                raise RuntimeError("Failed to retrieve ITK token")

            return {"ITK": self._itk}
