from .client import EMTClient


class BusApiClient:
    """Bus API client for EaseMyTrip bus service."""

    def __init__(self):
        # Bus API doesn't require token injection like flights
        self.client = EMTClient(token_provider=None)

    async def search(self, url: str, payload: dict) -> dict:
        return await self.client.post(url, payload)