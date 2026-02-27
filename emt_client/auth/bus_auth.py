from .base import TokenProvider


class BusTokenProvider(TokenProvider):
    
    async def get_tokens(self):
        """Bus API doesn't need tokens, return empty dict."""
        return {}