"""Login Tool """
from typing import Dict, Any
import logging

from ..base import BaseTool, ToolMetadata
from .login_service import LoginService
from .login_schema import LoginInput
from tools_factory.base_schema import ToolResponseFormat
from emt_client.auth.session_manager import SessionManager

logger = logging.getLogger(__name__)


class LoginTool(BaseTool):

    def __init__(self, session_manager: SessionManager = None):
        """
        Initialize LoginTool.

        Args:
            session_manager: SessionManager for multi-user session isolation.
                           If not provided, creates a standalone service (legacy mode).
        """
        super().__init__()
        self.session_manager = session_manager
        # Legacy mode: create a single service if no session_manager provided
        self._legacy_service = LoginService() if not session_manager else None
    
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
            # Extract runtime flags (internal)
            session_id = kwargs.pop("_session_id", None)

            phone_number = kwargs.get("phone_number")

            # Validate required parameters - only phone_number is mandatory
            if not phone_number:
                return ToolResponseFormat(
                    response_text="phone_number (or email) is required to login.",
                    is_error=True
                )

            logger.info(f"Executing login for: {phone_number}")

            # Get or create session-specific service
            if self.session_manager:
                # Multi-user mode: use session-specific provider
                session_id, token_provider = self.session_manager.get_or_create_session(session_id)
                service = LoginService(token_provider)
            else:
                # Legacy mode: use single shared service
                service = self._legacy_service
                session_id = None  # No session tracking in legacy mode

            result = await service.authenticate_user(
                phone_or_email=phone_number,
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
                    "session_id": session_id,  # Return session_id for caller to track
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

