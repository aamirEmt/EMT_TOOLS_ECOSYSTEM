"""Login Service"""
from typing import Dict, Any
import logging

from emt_client.clients.login_client import LoginApiClient
from emt_client.auth.login_auth import LoginTokenProvider
from .login_schema import LoginInput

logger = logging.getLogger(__name__)


class LoginService:
    
    def __init__(self):
        self.token_provider = LoginTokenProvider()
        self.client = LoginApiClient(token_provider=self.token_provider)
    
    async def authenticate_user(self, phone_or_email: str, ip_address: str) -> Dict[str, Any]:
        """Authenticate user with phone number or email
        
        Args:
            phone_or_email: Phone number or email address for authentication
            ip_address: User's IP address
            
        Returns:
            Dict containing authentication result and user info
        """
        try:
            login_input = LoginInput(
                phone_number=phone_or_email,
                ip_address=ip_address
            )
            
            logger.info(f"Attempting login for: {login_input.phone_number}")
            
            # Call login API - matches main.py emt_login()
            result = await self.client.login_user(
                phone_number=login_input.phone_number,
                ip_address=login_input.ip_address
            )
            
            raw_text = result.get("raw_text")
            json_data = result.get("json")
            
            print("\nEMT LOGIN RAW RESPONSE:\n", raw_text)
            print("\nEMT LOGIN PARSED JSON:\n", json_data)
            
            # Check if response is valid JSON 
            if not isinstance(json_data, dict):
                return {
                    "success": False,
                    "error": "EMT response was not valid JSON",
                    "message": "Login failed: EMT response was not valid JSON"
                }
            
            # Extract auth token 
            auth_token = (
                json_data.get("Auth") or
                json_data.get("AuthenticationToken") or
                json_data.get("auth")
            )
            
            # Extract Action2Token for booking API calls
            action2_token = json_data.get("Action2Token")
            
            # Extract CookC token
            cookc = json_data.get("CookC")
            
            print("Auth token length:", len(auth_token) if auth_token else 0)
            print("Auth token preview:", auth_token[:50] if auth_token else None, "...", auth_token[-50:] if auth_token else None)
            print("Action2Token length:", len(action2_token) if action2_token else 0)
            print("CookC length:", len(cookc) if cookc else 0)
            
            # Extract user info 
            email_list = json_data.get("EmailList") or []
            name = json_data.get("Name")
            uid = json_data.get("UID") or phone_or_email
            
            # Check for auth token 
            if not auth_token:
                return {
                    "success": False,
                    "error": "Authentication token missing",
                    "message": "Login failed: Authentication token missing"
                }
            
            # Check for Action2Token
            if not action2_token:
                logger.warning("Action2Token not found in response")
            
            # Clear and update session 
            self.token_provider.clear_session()
            self.token_provider.set_auth_token(
                auth_token=auth_token,
                email=email_list[0] if email_list else None,
                phone=phone_or_email,
                uid=uid,
                name=name,
                action2_token=action2_token,
                cookc=cookc
            )
            
            logger.info(f"Login successful for user: {email_list[0] if email_list else 'N/A'}")
            
            return {
                "success": True,
                "message": "Login successful",
                "user": {
                    "name": name or "N/A",
                    "email": email_list[0] if email_list else "N/A",
                    "phone": phone_or_email,
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
        """Logout user and clear session """
        self.token_provider.clear_session()
        logger.info("User logged out successfully")
        
        return {
            "success": True,
            "message": "Logged out successfully",
            "authenticated": False
        }
    
    def is_authenticated(self) -> bool:
        return self.token_provider.is_authenticated()
