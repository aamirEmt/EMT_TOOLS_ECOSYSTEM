"""Login API Client for EMT"""
import json
import base64
from typing import Dict, Any
import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from .client import EMTClient

KEY = b"EMTOO1BOTT9aWsV1"
IV = b"EMTOO1BOTT9aWsV1"

LOGIN_URL = "https://loginuser.easemytrip.com/api/Login/GoogleLogin"


def EncryptStringAES_BOT(plain_text: str) -> str:
    """Exact function from crypto_bot.py"""
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    encrypted = cipher.encrypt(pad(plain_text.encode("utf-8"), AES.block_size))
    return base64.b64encode(encrypted).decode("utf-8")


def DecryptStringAES_BOT(encrypted_value: str) -> str:
    # 🔑 EMT wraps ciphertext in quotes sometimes
    encrypted_value = encrypted_value.strip().strip('"')

    encrypted_bytes = base64.b64decode(encrypted_value)
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    decrypted = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
    return decrypted.decode("utf-8")


class LoginApiClient(EMTClient):
    
    def __init__(self, token_provider=None):
        super().__init__(token_provider)
    
    async def login_user(self, phone_number: str, ip_address: str) -> Dict[str, Any]:
        plain_value = f"{phone_number}|{ip_address}"
        id_token = EncryptStringAES_BOT(plain_value)

        payload = {
            "Id_Token": id_token,
            "loginType": "BOT",
            "userid": "EMTBOT",
            "password": "EMTBOT78XBWCcGdvzBhTY4yL3LqXJtzWKHwuNpA1wl"
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                LOGIN_URL,
                json=payload,
                headers=headers
            )

        raw_text = response.text
        decrypted_json = None
        error = None

        if response.status_code == 200:
            try:
                decrypted_text = DecryptStringAES_BOT(raw_text)
                decrypted_json = json.loads(decrypted_text)
            except Exception as e:
                error = f"DECRYPT_OR_PARSE_FAILED: {e}"
        else:
            error = f"HTTP_{response.status_code}"

        return {
            "success": decrypted_json is not None,
            "status_code": response.status_code,
            "raw_text": raw_text,
            "decrypted_text": decrypted_text if decrypted_json else None,
            "json": decrypted_json,
            "error": error,
        }
