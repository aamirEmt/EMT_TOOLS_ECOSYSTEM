"""OTP Login Tool - Single tool with send_otp and verify_otp actions"""
import logging

from ..base import BaseTool, ToolMetadata
from .otp_login_service import OtpLoginService
from .otp_login_schema import OtpLoginInput
from tools_factory.base_schema import ToolResponseFormat
from emt_client.auth.session_manager import SessionManager

logger = logging.getLogger(__name__)


class OtpLoginTool(BaseTool):

    def __init__(self, session_manager: SessionManager = None):
        super().__init__()
        self.session_manager = session_manager

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="otp_login",
            description=(
                "Login a user via OTP. Has two actions: "
                "'send_otp' sends an OTP to the user's phone/email, "
                "'verify_otp' verifies the OTP received by the user. "
                "Call send_otp first, then ask the user for the OTP, then call verify_otp."
            ),
            input_schema=OtpLoginInput.model_json_schema(),
            output_template=None,
            category="authentication",
            tags=["login", "auth", "otp"]
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        try:
            # Accept session_id from either _session_id or session_id
            session_id = kwargs.pop("_session_id", None) or kwargs.pop("session_id", None)
            action = kwargs.pop("action", None)

            if not action or action not in ("send_otp", "verify_otp"):
                return ToolResponseFormat(
                    response_text="action is required and must be 'send_otp' or 'verify_otp'.",
                    is_error=True
                )

            if action == "send_otp":
                return await self._handle_send_otp(session_id, **kwargs)
            else:
                return await self._handle_verify_otp(session_id, **kwargs)

        except Exception as e:
            logger.error("Error executing otp_login tool", exc_info=True)
            return ToolResponseFormat(
                response_text=f"OTP login failed: {str(e)}",
                is_error=True
            )

    async def _handle_send_otp(self, session_id, **kwargs) -> ToolResponseFormat:
        phone_or_email = kwargs.get("phone_or_email")

        if not phone_or_email:
            return ToolResponseFormat(
                response_text="phone_or_email is required for send_otp action.",
                is_error=True
            )

        # Get or create session
        if self.session_manager:
            session_id, token_provider = self.session_manager.get_or_create_session(session_id)
            service = OtpLoginService(token_provider)
        else:
            service = OtpLoginService()
            session_id = None

        result = await service.send_otp(phone_or_email=phone_or_email)

        if not result.get("success"):
            return ToolResponseFormat(
                response_text=f"Failed to send OTP: {result.get('message', 'Unknown error')}",
                structured_content=result,
                is_error=True
            )

        return ToolResponseFormat(
            response_text=(
                f"OTP sent successfully to {phone_or_email}. "
                f"Please ask the user for the OTP they received, "
                f"then call this tool again with action='verify_otp' and the otp_code."
            ),
            structured_content={
                "session_id": session_id,
                "phone_or_email": phone_or_email,
                "message": result.get("message"),
            }
        )

    async def _handle_verify_otp(self, session_id, **kwargs) -> ToolResponseFormat:
        otp_code = kwargs.get("otp_code")

        if not otp_code:
            return ToolResponseFormat(
                response_text="otp_code is required for verify_otp action.",
                is_error=True
            )

        if not session_id:
            return ToolResponseFormat(
                response_text="session_id is required. Please call send_otp first.",
                is_error=True
            )

        if self.session_manager:
            token_provider = self.session_manager.get_session(session_id)
            if not token_provider:
                return ToolResponseFormat(
                    response_text="Invalid or expired session. Please call send_otp again.",
                    is_error=True
                )
            service = OtpLoginService(token_provider)
        else:
            return ToolResponseFormat(
                response_text="Session manager not available.",
                is_error=True
            )

        result = await service.verify_otp(otp_code=otp_code)

        if not result.get("success"):
            return ToolResponseFormat(
                response_text=f"OTP verification failed: {result.get('message', 'Unknown error')}",
                structured_content=result,
                is_error=True
            )

        user = result.get("user", {})
        return ToolResponseFormat(
            response_text=(
                "Login successful. Continue handling the user's original request.\n\n"
                f"Name: {user.get('name', 'N/A')}\n"
                f"Email: {user.get('email', 'N/A')}\n"
                f"Phone: {user.get('phone', 'N/A')}"
            ),
            structured_content={
                "session_id": session_id,
                "user": user,
                "session": result.get("session"),
                "result": result,
            }
        )
