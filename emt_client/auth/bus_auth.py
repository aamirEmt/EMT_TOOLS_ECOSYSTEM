from .base import TokenProvider


class BusTokenProvider(TokenProvider):
    """Bus API token provider - Bus API doesn't require token injection like flights."""
    
    async def get_tokens(self):
        """Bus API doesn't need tokens, return empty dict."""
        return {}