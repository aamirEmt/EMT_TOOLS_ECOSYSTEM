"""
Bus Authentication Provider
Similar to flight_auth.py but for bus API
"""
from typing import Dict
from .base import TokenProvider


class BusTokenProvider(TokenProvider):
    """
    Bus API doesn't require token authentication like flights.
    It uses a static API key passed in the payload.
    This class provides a consistent interface.
    """
    
    def __init__(self):
        pass
    
    async def get_tokens(self) -> Dict[str, str]:
        """
        Bus API uses static key in payload, not header tokens.
        Returns empty dict as tokens are handled in config.
        """
        return {}