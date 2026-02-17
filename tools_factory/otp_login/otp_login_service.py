"""OTP Login Service - Two-step OTP authentication business logic"""
from typing import Dict, Any
import logging

from emt_client.clients.otp_login_client import OtpLoginApiClient
from emt_client.auth.login_auth import LoginTokenProvider

logger = logging.getLogger(__name__)


class OtpLoginService:

    def __init__(self, token_provider: LoginTokenProvider = None):
        self.token_provider = token_provider or LoginTokenProvider()
        self.client = OtpLoginApiClient(token_provider=self.token_provider)

    async def send_otp(self, phone_or_email: str) -> Dict[str, Any]:
        """
        Step 1: Send OTP to user's phone/email.
        Stores intermediate Token in LoginTokenProvider for step 2.
        """
        try:
            ip = self.token_provider.get_ip()

            logger.info(f"Sending OTP to: {phone_or_email}")
            result = await self.client.send_otp(phone_or_email, ip)

            if not result.get("success"):
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "message": f"Failed to send OTP: {result.get('error', 'Unknown error')}",
                }

            json_data = result.get("json", {})
            token = json_data.get("Token")
            message = json_data.get("Message", "")

            if not token:
                return {
                    "success": False,
                    "error": "NO_TOKEN_IN_RESPONSE",
                    "message": message or "OTP send failed: no token received",
                }

            # Store intermediate state in session for step 2
            self.token_provider.set_otp_pending(
                otp_token=token,
                phone_or_email=phone_or_email,
            )

            logger.info(f"OTP sent successfully to: {phone_or_email}")
            return {
                "success": True,
                "message": message or "OTP sent successfully",
                "phone_or_email": phone_or_email,
            }

        except Exception as e:
            logger.error(f"Error sending OTP: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "An unexpected error occurred while sending OTP",
            }

    async def verify_otp(self, otp_code: str) -> Dict[str, Any]:
        """
        Step 2: Verify OTP and authenticate user.
        Retrieves stored Token + phone_or_email from LoginTokenProvider.
        On success, stores full auth credentials.
        """
        try:
            otp_token = self.token_provider.get_otp_token()
            phone_or_email = self.token_provider.get_otp_phone_or_email()

            if not otp_token or not phone_or_email:
                return {
                    "success": False,
                    "error": "NO_PENDING_OTP",
                    "message": "No pending OTP found. Please send OTP first.",
                }

            ip = self.token_provider.get_ip()

            logger.info(f"Verifying OTP for: {phone_or_email}")
            result = await self.client.authenticate_otp(
                phone_or_email=phone_or_email,
                otp=otp_code,
                token_from_api1=otp_token,
                ip=ip,
            )

            if not result.get("success"):
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "message": f"OTP verification failed: {result.get('error', 'Unknown error')}",
                }

            json_data = result.get("json", {})

            auth_token = json_data.get("Auth")
            action2_token = json_data.get("A2T")
            cookc = json_data.get("CookC")
            cookm = json_data.get("CookM")
            name = json_data.get("Name")
            uid = json_data.get("UID") or phone_or_email
            customer_id = json_data.get("CustomerId")
            message = json_data.get("Message", "")

            if not auth_token:
                return {
                    "success": False,
                    "error": "AUTH_TOKEN_MISSING",
                    "message": message or "OTP verification failed: auth token missing",
                }

            # Clear OTP pending state and set full auth credentials
            self.token_provider.clear_otp_pending()
            self.token_provider.set_auth_token(
                auth_token=auth_token,
                email=phone_or_email if "@" in phone_or_email else None,
                phone=phone_or_email if "@" not in phone_or_email else None,
                uid=uid,
                name=name,
                action2_token=action2_token,
                cookc=cookc,
                cookm=cookm,
            )

            logger.info(f"OTP login successful for: {phone_or_email}")
            return {
                "success": True,
                "message": message or "Login successful",
                "user": {
                    "name": name or "N/A",
                    "email": phone_or_email if "@" in phone_or_email else "N/A",
                    "phone": phone_or_email if "@" not in phone_or_email else "N/A",
                    "uid": uid,
                    "customer_id": customer_id,
                },
                "session": self.token_provider.get_session(),
            }

        except Exception as e:
            logger.error(f"Error verifying OTP: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "An unexpected error occurred during OTP verification",
            }
