"""Login Tool """
from typing import Dict, Any
import logging

from ..base import BaseTool, ToolMetadata
from .login_service import LoginService

logger = logging.getLogger(__name__)


class LoginTool(BaseTool):
    
    def __init__(self):
        super().__init__()
        self.service = LoginService()
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="login_user",
            description="Login a user with phone number or email and IP address.",
            input_schema={
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "User phone number or email address"
                    },
                    "ip_address": {
                        "type": "string",
                        "description": "User IP address"
                    },
                },
                "required": ["phone_number", "ip_address"],
                "additionalProperties": False,
            },
            output_template=None,
            category="authentication",
            tags=["login", "auth"]
        )
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            phone_number = kwargs.get("phone_number")
            ip_address = kwargs.get("ip_address")
            
            # Validate required parameters - matches main.py check
            if not phone_number or not ip_address:
                return {
                    "success": False,
                    "error": "phone_number (or email) and ip_address are required",
                    "text_content": "phone_number (or email) and ip_address are required",
                    "isError": True
                }
            
            logger.info(f"Executing login for: {phone_number}")
            
            result = await self.service.authenticate_user(
                phone_or_email=phone_number,
                ip_address=ip_address
            )
            
            # Handle failure
            if not result.get("success"):
                error_message = result.get("message", "Unknown error")
                return {
                    "success": False,
                    "error": error_message,
                    "text_content": error_message,
                    "isError": True
                }
            
            user = result.get("user", {})
            name = user.get("name", "N/A")
            email = user.get("email", "N/A")
            phone = user.get("phone", "N/A")
            
            text_content = (
                "Login successful\n\n"
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Phone: {phone}"
            )
            
            return {
                "success": True,
                "message": result.get("message"),
                "user": user,
                "session": result.get("session"),
                "text_content": text_content,
                "structured_content": result,
                "isError": False
            }
        
        except Exception as e:
            logger.error(f"Error executing login tool: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "text_content": f"Login failed: {str(e)}",
                "isError": True
            }
