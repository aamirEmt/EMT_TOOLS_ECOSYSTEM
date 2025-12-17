from .client import EMTClient
from ..auth.flight_auth import FlightTokenProvider

class FlightApiClient:
    def __init__(self):
        self.token_provider = FlightTokenProvider()
        self.client = EMTClient(self._inject_itk)

    async def _inject_itk(self):
        itk = await self.token_provider.get_itk()
        return {"TKN": itk}

    async def search(self, url: str, payload: dict) -> dict:
        return await self.client.post(url, payload)
