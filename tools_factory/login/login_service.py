"""Login Service - Business logic matching main.py exactly"""
from typing import Dict, Any
import logging

from emt_client.clients.login_client import LoginApiClient
from emt_client.auth.login_auth import LoginTokenProvider
from .login_schema import LoginInput

logger = logging.getLogger(__name__)


class LoginService:
    """Login service matching main.py _call_tool_request login logic"""
    
    def __init__(self):
        self.token_provider = LoginTokenProvider()
        self.client = LoginApiClient(token_provider=self.token_provider)
    
    async def authenticate_user(self, phone_number: str, ip_address: str) -> Dict[str, Any]:
        """Authenticate user - exactly matches main.py login flow"""
        try:
            login_input = LoginInput(
                phone_number=phone_number,
                ip_address=ip_address
            )
            
            logger.info(f"Attempting login for phone: {login_input.phone_number}")
            
            # Call login API - matches main.py emt_login()
            result = await self.client.login_user(
                phone_number=login_input.phone_number,
                ip_address=login_input.ip_address
            )
            
            raw_text = result.get("raw_text")
            json_data = result.get("json")
            
            print("\nEMT LOGIN RAW RESPONSE:\n", raw_text)
            print("\nEMT LOGIN PARSED JSON:\n", json_data)
            
            # Check if response is valid JSON - matches main.py check
            if not isinstance(json_data, dict):
                return {
                    "success": False,
                    "error": "EMT response was not valid JSON",
                    "message": "Login failed: EMT response was not valid JSON"
                }
            
            # Extract auth token - matches main.py token extraction
            auth_token = (
                json_data.get("Auth") or
                json_data.get("AuthenticationToken") or
                json_data.get("auth")
            )
            
            print("Auth token length:", len(auth_token) if auth_token else 0)
            print("Auth token preview:", auth_token[:50] if auth_token else None, "...", auth_token[-50:] if auth_token else None)
            
            # Extract user info - matches main.py extraction
            email_list = json_data.get("EmailList") or []
            name = json_data.get("Name")
            uid = json_data.get("UID") or phone_number
            
            # Check for auth token - matches main.py validation
            if not auth_token:
                return {
                    "success": False,
                    "error": "Authentication token missing",
                    "message": "Login failed: Authentication token missing"
                }
            
            # Clear and update session - matches main.py SESSION.clear() and SESSION.update()
            self.token_provider.clear_session()
            self.token_provider.set_auth_token(
                auth_token=auth_token,
                email=email_list[0] if email_list else None,
                phone=phone_number,
                uid=uid,
                name=name
            )
            
            logger.info(f"Login successful for user: {email_list[0] if email_list else 'N/A'}")
            
            # Return response matching main.py format
            return {
                "success": True,
                "message": "Login successful",
                "user": {
                    "name": name or "N/A",
                    "email": email_list[0] if email_list else "N/A",
                    "phone": phone_number,
                    "uid": uid
                },
                "session": self.token_provider.get_session()
            }
        
        except Exception as e:
            logger.error(f"Error during login: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "An unexpected error occurred"
            }
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        return self.token_provider.get_session()
    
    def logout(self) -> Dict[str, Any]:
        """Logout user and clear session - matches SESSION.clear()"""
        self.token_provider.clear_session()
        logger.info("User logged out successfully")
        
        return {
            "success": True,
            "message": "Logged out successfully",
            "authenticated": False
        }
    
    def is_authenticated(self) -> bool:
        return self.token_provider.is_authenticated()
