"""
Hotel Authentication Provider
Handles JWT and EMT token retrieval for Hotel API requests
"""
import httpx
import asyncio
from typing import Dict
from datetime import datetime
import time

from .base import TokenProvider
from ..config import (
    HOTEL_LOGIN_URL,
    DEFAULT_AUTH,
    VID,
    TOKEN_VALIDITY_MINUTES,
    TOKEN_CACHE_ENABLED,
    DEBUG_MODE
)
from ..utils import gen_trace_id


class HotelTokenProvider(TokenProvider):
    """
    Token provider for Hotel API authentication.
    Manages JWT token and EMT session token with automatic refresh.
    """
    
    def __init__(self):
        self._token: str | None = None
        self._emt_token: str | None = None
        self._token_expiry: float = 0.0
        self._lock = asyncio.Lock()
    
    async def get_tokens(self) -> Dict[str, str]:
        """
        Retrieves valid tokens, refreshing if necessary.
        
        Returns:
            Dict containing 'token' (JWT) and 'emtToken' (EMT session token)
        """
        # If caching is disabled, always fetch new tokens
        if not TOKEN_CACHE_ENABLED:
            return await self._fetch_new_tokens()
        
        # Check if current tokens are still valid (with 2-minute buffer)
        if time.time() < (self._token_expiry - 120) and self._token:
            return {
                "token": self._token,
                "emtToken": self._emt_token or ""
            }
        
        # Acquire lock to prevent concurrent refresh attempts
        async with self._lock:
            # Double-check after acquiring lock
            if time.time() < (self._token_expiry - 120) and self._token:
                return {
                    "token": self._token,
                    "emtToken": self._emt_token or ""
                }
            
            return await self._fetch_new_tokens()
    
    async def _fetch_new_tokens(self) -> Dict[str, str]:
        """
        Calls the UserLogin API to fetch fresh tokens.
        
        Returns:
            Dict with 'token' and 'emtToken'
        
        Raises:
            RuntimeError: If token retrieval fails
        """
        payload = {
            "auth": DEFAULT_AUTH,
            "vid": VID,
            "traceid": gen_trace_id()
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(HOTEL_LOGIN_URL, headers=headers, json=payload)
                res.raise_for_status()
                
                # Handle 204 No Content - API might not require explicit login
                if res.status_code == 204 or not res.text:
                    if DEBUG_MODE:
                        print(f"[HotelAuth] API returned 204 No Content - using empty tokens")
                    
                    # Use empty tokens (API might work without explicit auth)
                    self._token = ""
                    self._emt_token = ""
                    self._token_expiry = time.time() + (TOKEN_VALIDITY_MINUTES * 60)
                    
                    return {
                        "token": self._token,
                        "emtToken": self._emt_token
                    }
                
                data = res.json()
            
            if data.get("status", "").lower() != "success":
                error_msg = data.get("message", "Unknown failure")
                raise RuntimeError(f"Hotel login failed: {error_msg}")
            
            # Extract tokens from response
            jwt_token = data.get("message") or data.get("token")
            emt_token = data.get("emtToken", "")
            
            if not jwt_token:
                raise RuntimeError("Failed to retrieve JWT token from login response")
            
            # Update cache
            self._token = jwt_token
            self._emt_token = emt_token
            self._token_expiry = time.time() + (TOKEN_VALIDITY_MINUTES * 60)
            
            if DEBUG_MODE:
                expiry_time = datetime.fromtimestamp(self._token_expiry)
                print(f"[HotelAuth] Tokens refreshed. Expiry: {expiry_time}")
            
            return {
                "token": self._token,
                "emtToken": self._emt_token
            }
        
        except httpx.HTTPError as e:
            raise RuntimeError(f"HTTP error during hotel login: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch hotel tokens: {str(e)}")
    
    async def get_token(self) -> str:
        """
        Convenience method to get just the JWT token.
        
        Returns:
            JWT token string
        """
        tokens = await self.get_tokens()
        return tokens["token"]
    
    async def get_emt_token(self) -> str:
        """
        Convenience method to get just the EMT token.
        
        Returns:
            EMT token string
        """
        tokens = await self.get_tokens()
        return tokens["emtToken"]
    
    def invalidate_tokens(self) -> None:
        """Clear cached tokens and force refresh on next request"""
        self._token = None
        self._emt_token = None
        self._token_expiry = 0.0