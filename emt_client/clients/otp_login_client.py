"""OTP Login API Client for EMT - Two-step OTP authentication flow"""
import json
import base64
from typing import Dict, Any
import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from .client import EMTClient

# Three encryption contexts (AES-128-CBC, PKCS7 padding, key == IV)
FIELD_KEY = b"EMTmVUvDhT9aWsVG"
FIELD_IV = b"EMTmVUvDhT9aWsVG"

PAYLOAD_KEY = b"MT$1VU8DHQ8aWLVH"
PAYLOAD_IV = b"MT$1VU8DHQ8aWLVH"

RESPONSE_KEY = b"TMTOO1vDhT9aWsV1"
RESPONSE_IV = b"TMTOO1vDhT9aWsV1"

SEND_OTP_URL = "https://loginuser.easemytrip.com/api/Login/VerifyUserLogin"
AUTHENTICATE_OTP_URL = "https://loginuser.easemytrip.com/api/Login/AuthenticateLoginUser"


def encrypt_field(plain_text: str) -> str:
    """Encrypt a single field value (UID, UTY, IP, TKN, Pass, useridentity header)."""
    cipher = AES.new(FIELD_KEY, AES.MODE_CBC, FIELD_IV)
    encrypted = cipher.encrypt(pad(plain_text.encode("utf-8"), AES.block_size))
    return base64.b64encode(encrypted).decode("utf-8")


def encrypt_payload(json_string: str) -> str:
    """Encrypt the entire JSON payload string before sending."""
    cipher = AES.new(PAYLOAD_KEY, AES.MODE_CBC, PAYLOAD_IV)
    encrypted = cipher.encrypt(pad(json_string.encode("utf-8"), AES.block_size))
    return base64.b64encode(encrypted).decode("utf-8")


def decrypt_response(encrypted_value: str) -> str:
    """Decrypt server response body."""
    encrypted_value = encrypted_value.strip().strip('"')
    encrypted_bytes = base64.b64decode(encrypted_value)
    cipher = AES.new(RESPONSE_KEY, AES.MODE_CBC, RESPONSE_IV)
    decrypted = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
    return decrypted.decode("utf-8")


def detect_uty(identifier: str) -> str:
    """Auto-detect user type: 'Email' if contains @, else 'Mobile'."""
    if "@" in identifier:
        return "Email"
    return "Mobile"


class OtpLoginApiClient(EMTClient):
    """Client for OTP-based login flow (2 APIs, 3 encryption contexts)."""

    def __init__(self, token_provider=None):
        super().__init__(token_provider)

    async def send_otp(self, phone_or_email: str, ip: str) -> Dict[str, Any]:
        """
        API 1: Send OTP to user's phone/email.
        POST /api/Login/VerifyUserLogin
        """
        uty_word = detect_uty(phone_or_email)

        identity_raw = f"{phone_or_email}|{ip}|{uty_word}"
        useridentity = encrypt_field(identity_raw)

        headers = {
            "Content-Type": "application/json",
            "useridentity": useridentity,
        }

        payload = {
            "UID": encrypt_field(phone_or_email),
            "CC": "+91",
            "ATY": "Resend",
            "UTY": encrypt_field(uty_word),
            "IP": encrypt_field(ip),
            "VerifyToken": "",
        }

        payload_json = json.dumps(payload)
        encrypted_payload = encrypt_payload(payload_json)
        request_body = {"request": encrypted_payload}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(SEND_OTP_URL, json=request_body, headers=headers)

        if response.status_code != 200:
            return {"success": False, "error": f"HTTP_{response.status_code}"}

        try:
            decrypted_text = decrypt_response(response.text)
            data = json.loads(decrypted_text)
        except Exception as e:
            return {"success": False, "error": f"DECRYPT_OR_PARSE_FAILED: {e}"}

        return {
            "success": True,
            "status_code": response.status_code,
            "json": data,
        }

    async def authenticate_otp(
        self, phone_or_email: str, otp: str, token_from_api1: str, ip: str
    ) -> Dict[str, Any]:
        """
        API 2: Verify OTP and authenticate user.
        POST /api/Login/AuthenticateLoginUser
        """
        uty_word = detect_uty(phone_or_email)

        identity_raw = f"{phone_or_email}|{ip}|{uty_word}"
        useridentity = encrypt_field(identity_raw)

        headers = {
            "Content-Type": "application/json",
            "useridentity": useridentity,
        }

        payload = {
            "UID": encrypt_field(phone_or_email),
            "CC": "+91",
            "TKN": encrypt_field(token_from_api1),
            "ATY": "Login",
            "UTY": encrypt_field(uty_word),
            "Pass": encrypt_field(otp),
            "PTY": "O",
            "UA": "",
            "RefCd": "",
            "RefLnk": "",
            "IP": encrypt_field(ip),
            "VerifyToken": "",
            "Token": "",
        }

        payload_json = json.dumps(payload)
        encrypted_payload = encrypt_payload(payload_json)
        request_body = {"request": encrypted_payload}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(AUTHENTICATE_OTP_URL, json=request_body, headers=headers)

        if response.status_code != 200:
            return {"success": False, "error": f"HTTP_{response.status_code}"}

        try:
            decrypted_text = decrypt_response(response.text)
            data = json.loads(decrypted_text)
        except Exception as e:
            return {"success": False, "error": f"DECRYPT_OR_PARSE_FAILED: {e}"}

        return {
            "success": True,
            "status_code": response.status_code,
            "json": data,
        }
