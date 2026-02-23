"""Login Token Provider for EMT API """
from typing import Optional
from .base import TokenProvider


class LoginTokenProvider(TokenProvider):
    """Token provider for login operations"""
    
    def __init__(self):
        super().__init__()
        self._logged_in: bool = False
        self._auth: Optional[str] = None
        self._action2_token: Optional[str] = None
        self._cookc: Optional[str] = None
        self._cookm: Optional[str] = None
        self._email: Optional[str] = None
        self._phone: Optional[str] = None
        self._uid: Optional[str] = None
        self._name: Optional[str] = None
        self._ip: str = "49.249.40.58"
        # OTP intermediate state (between send_otp and verify_otp)
        self._otp_token: Optional[str] = None
        self._otp_phone_or_email: Optional[str] = None
    
    async def get_tokens(self) -> dict:
        """Return tokens required for the service"""
        if self._auth:
            return {"AUTH": self._auth}
        return {}
    
    async def get_token(self) -> Optional[str]:
        return self._auth
    
    def set_auth_token(
        self,
        auth_token: str,
        email: str,
        phone: str,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        action2_token: Optional[str] = None,
        cookc: Optional[str] = None,
        cookm: Optional[str] = None
    ) -> None:
        self._logged_in = True
        self._auth = auth_token
        self._action2_token = action2_token
        self._cookc = cookc
        self._cookm = cookm
        self._email = email
        self._phone = phone
        self._uid = uid
        self._name = name
        self._ip = "49.249.40.58"
    
    def get_session(self) -> dict:
        return {
            "logged_in": self._logged_in,
            "auth": self._auth,
            "action2_token": self._action2_token,
            "cookc": self._cookc,
            "cookm": self._cookm,
            "email": self._email,
            "phone": self._phone,
            "uid": self._uid,
            "name": self._name,
            "ip": self._ip
        }
    
    def get_user_info(self) -> dict:
        return {
            "email": self._email,
            "phone": self._phone,
            "uid": self._uid,
            "name": self._name,
            "ip": self._ip,
            "has_token": self._auth is not None
        }
    
    def clear_session(self) -> None:
        self._logged_in = False
        self._auth = None
        self._action2_token = None
        self._cookc = None
        self._cookm = None
        self._email = None
        self._phone = None
        self._uid = None
        self._name = None
        self._ip = "49.249.40.58"
        self._otp_token = None
        self._otp_phone_or_email = None
    
    def is_authenticated(self) -> bool:
        return self._logged_in and self._auth is not None
    
    def get_auth(self) -> Optional[str]:
        """Get auth token"""
        return self._auth
    
    def get_email(self) -> Optional[str]:
        """Get user email"""
        return self._email
    
    def get_phone(self) -> Optional[str]:
        """Get user phone"""
        return self._phone
    
    def get_ip(self) -> str:
        """Get stored IP (always returns hardcoded IP)"""
        return self._ip
    
    def get_action2_token(self) -> Optional[str]:
        """Get Action2Token for booking API calls"""
        return self._action2_token
    
    def get_cookc(self) -> Optional[str]:
        """Get CookC token"""
        return self._cookc
    
    def get_uid(self) -> Optional[str]:
        """Get UID (phone or email used for login)"""
        return self._uid

    def get_cookm(self) -> Optional[str]:
        """Get CookM token"""
        return self._cookm

    def set_otp_pending(self, otp_token: str, phone_or_email: str) -> None:
        """Store intermediate OTP token from API 1 (between send and verify)."""
        self._otp_token = otp_token
        self._otp_phone_or_email = phone_or_email

    def get_otp_token(self) -> Optional[str]:
        """Get stored OTP token from API 1."""
        return self._otp_token

    def get_otp_phone_or_email(self) -> Optional[str]:
        """Get phone/email used for OTP send."""
        return self._otp_phone_or_email

    def clear_otp_pending(self) -> None:
        """Clear intermediate OTP state after verification completes."""
        self._otp_token = None
        self._otp_phone_or_email = None
