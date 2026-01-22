from .client import EMTClient


class TrainApiClient:
    """Train API client for EaseMyTrip railways service."""

    def __init__(self):
        # Train API doesn't require token injection like flights
        self.client = EMTClient(token_provider=None)

    async def search(self, url: str, payload: dict) -> dict:
        """Search trains between stations."""
        return await self.client.post(url, payload)
