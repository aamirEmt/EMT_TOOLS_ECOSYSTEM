"""Login Tool """
from typing import Dict, Any
import logging

from ..base import BaseTool, ToolMetadata
from .login_service import LoginService
from .login_schema import LoginInput
from tools_factory.base_schema import ToolResponseFormat

logger = logging.getLogger(__name__)


class LoginTool(BaseTool):
    
    def __init__(self):
        super().__init__()
        self.service = LoginService()
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="login_user",
            description="Login a user with phone number or email.",
            input_schema=LoginInput.model_json_schema(),
            output_template=None,
            category="authentication",
            tags=["login", "auth"]
        )
    
    async def execute(self, **kwargs) -> ToolResponseFormat:
        try:
            phone_number = kwargs.get("phone_number")
            # ip_address = kwargs.get("ip_address", "49.249.40.58")  # Use default if not provided
            
            # Validate required parameters - only phone_number is mandatory
            if not phone_number:
                return ToolResponseFormat(
                    response_text="phone_number (or email) is required to login.",
                    is_error=True
                )
            
            logger.info(f"Executing login for: {phone_number}")
            
            result = await self.service.authenticate_user(
                phone_or_email=phone_number,
                # ip_address=ip_address  # Commented out - not needed
            )
            
            # Handle failure
            if not result.get("success"):
                error_message = result.get("message", "Login failed")
                return ToolResponseFormat(
                    response_text=f"❌ {error_message}",
                    structured_content=result,
                    is_error=True
                )
            
            user = result.get("user", {})
            name = user.get("name", "N/A")
            email = user.get("email", "N/A")
            phone = user.get("phone", "N/A")
            session = result.get("session")
            
            response_text = (
                "Login successful. Continue handling the user's original request\n\n"
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Phone: {phone}"
            )
            
            return ToolResponseFormat(
                response_text=response_text,
                structured_content={
                    "user": user,
                    "session": session,
                    "result": result
                }
            )

        except Exception as e:
            logger.error("Error executing login tool", exc_info=True)
            return ToolResponseFormat(
                response_text=f"❌ Login failed: {str(e)}",
                is_error=True
            )

