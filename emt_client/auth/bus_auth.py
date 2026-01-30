import base64
import json
from typing import Dict, Any
from emt_client.config import BUS_DECRYPTION_KEY


def _get_cipher():
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad, unpad
        return AES, pad, unpad
    except ImportError:
        try:
            from Cryptodome.Cipher import AES
            from Cryptodome.Util.Padding import pad, unpad
            return AES, pad, unpad
        except ImportError:
            raise ImportError(
                "pycryptodome is required. Install with: pip install pycryptodome"
            )


def encrypt_bus_request(plain_text: str) -> str:
    AES, pad, unpad = _get_cipher()
    
    key = BUS_DECRYPTION_KEY.encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, iv=key)
    padded_data = pad(plain_text.encode("utf-8"), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted_bytes).decode("utf-8")


def decrypt_bus_response(cipher_text: str) -> str:
    AES, pad, unpad = _get_cipher()
    
    key = BUS_DECRYPTION_KEY.encode("utf-8")
    encrypted_bytes = base64.b64decode(cipher_text)
    cipher = AES.new(key, AES.MODE_CBC, iv=key)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    return unpad(decrypted_bytes, AES.block_size).decode("utf-8")