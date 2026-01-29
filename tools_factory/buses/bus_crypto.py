"""
Bus City Autosuggest Encryption/Decryption Utility.

This module provides AES encryption/decryption for the EaseMyTrip bus city autosuggest API.
Used to convert city names to city IDs automatically.
"""

import base64
import json
from typing import Dict, Any, List, Optional
import aiohttp

# AES Key for encryption/decryption (from EaseMyTrip)
DEC_KEY = "TMTOO1vDhT9aWsV1"

# Autosuggest API endpoint
AUTOSUGGEST_URL = "https://autosuggest.easemytrip.com/api/auto/bus"
AUTOSUGGEST_KEY = "jNUYK0Yj5ibO6ZVIkfTiFA=="
ENCRYPTED_HEADER = "7ZTtohPgMEKTZQZk4/Cn1mpXnyNZDJIRcrdCFo5ahIk="


def _get_cipher():
    """Get AES cipher for encryption/decryption."""
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


def encrypt_v1(plain_text: str) -> str:
    """
    Encrypt plaintext using AES CBC mode.
    
    Args:
        plain_text: The plaintext string to encrypt
        
    Returns:
        Base64 encoded encrypted string
    """
    AES, pad, unpad = _get_cipher()
    
    key = DEC_KEY.encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, iv=key)
    padded_data = pad(plain_text.encode("utf-8"), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted_bytes).decode("utf-8")


def decrypt_v1(cipher_text: str) -> str:
    """
    Decrypt ciphertext using AES CBC mode.
    
    Args:
        cipher_text: Base64 encoded encrypted string
        
    Returns:
        Decrypted plaintext string
    """
    AES, pad, unpad = _get_cipher()
    
    key = DEC_KEY.encode("utf-8")
    encrypted_bytes = base64.b64decode(cipher_text)
    cipher = AES.new(key, AES.MODE_CBC, iv=key)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    return unpad(decrypted_bytes, AES.block_size).decode("utf-8")


async def get_city_suggestions(
    city_prefix: str,
    country_code: str = "IN",
) -> List[Dict[str, Any]]:
    """
    Get city suggestions from the autosuggest API.
    
    Args:
        city_prefix: City name prefix to search (e.g., "Delhi", "Mana")
        country_code: Country code (default: "IN" for India)
        
    Returns:
        List of city suggestions with id, name, state, etc.
    """
    # Build the request payload
    json_string = {
        "userName": "",
        "password": "",
        "Prefix": city_prefix,
        "country_code": country_code,
    }
    
    # Encrypt the request
    encrypted_request = encrypt_v1(json.dumps(json_string))
    
    # Build the final API payload
    api_payload = {
        "request": encrypted_request,
        "isIOS": False,
        "ip": "49.249.40.58",
        "encryptedHeader": ENCRYPTED_HEADER,
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{AUTOSUGGEST_URL}?useby=popularu&key={AUTOSUGGEST_KEY}",
                json=api_payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 200:
                    return []
                
                encrypted_response = await response.text()
                
                # Decrypt the response
                decrypted_response = decrypt_v1(encrypted_response)
                data = json.loads(decrypted_response)
                
                return data.get("list", [])
                
    except Exception as e:
        print(f"Error fetching city suggestions: {e}")
        return []


async def get_city_id(city_name: str, country_code: str = "IN") -> Optional[str]:
    """
    Get city ID for a given city name.
    
    Args:
        city_name: Full or partial city name
        country_code: Country code (default: "IN")
        
    Returns:
        City ID string or None if not found
    """
    suggestions = await get_city_suggestions(city_name, country_code)
    
    if not suggestions:
        return None
    
    # Try to find exact match first (case-insensitive)
    city_name_lower = city_name.lower().strip()
    for suggestion in suggestions:
        if suggestion.get("name", "").lower().strip() == city_name_lower:
            return suggestion.get("id")
    
    # Return first match if no exact match
    return suggestions[0].get("id") if suggestions else None


async def get_city_info(city_name: str, country_code: str = "IN") -> Optional[Dict[str, Any]]:
    """
    Get full city info for a given city name.
    
    Args:
        city_name: Full or partial city name
        country_code: Country code (default: "IN")
        
    Returns:
        City info dict with id, name, state, etc. or None if not found
    """
    suggestions = await get_city_suggestions(city_name, country_code)
    
    if not suggestions:
        return None
    
    # Try to find exact match first (case-insensitive)
    city_name_lower = city_name.lower().strip()
    for suggestion in suggestions:
        if suggestion.get("name", "").lower().strip() == city_name_lower:
            return suggestion
    
    # Return first match if no exact match
    return suggestions[0] if suggestions else None


async def resolve_city_names_to_ids(
    source_city: str,
    destination_city: str,
    country_code: str = "IN",
) -> Dict[str, Any]:
    """
    Resolve source and destination city names to their IDs.
    
    Args:
        source_city: Source city name or ID
        destination_city: Destination city name or ID
        country_code: Country code (default: "IN")
        
    Returns:
        Dict with source_id, source_name, destination_id, destination_name
    """
    result = {
        "source_id": None,
        "source_name": None,
        "destination_id": None,
        "destination_name": None,
        "error": None,
    }
    
    # Check if source is already an ID (numeric string)
    if source_city.isdigit():
        result["source_id"] = source_city
        result["source_name"] = source_city  # Will be updated from API response
    else:
        source_info = await get_city_info(source_city, country_code)
        if source_info:
            result["source_id"] = source_info.get("id")
            result["source_name"] = source_info.get("name")
        else:
            result["error"] = f"Could not find city: {source_city}"
            return result
    
    # Check if destination is already an ID (numeric string)
    if destination_city.isdigit():
        result["destination_id"] = destination_city
        result["destination_name"] = destination_city  # Will be updated from API response
    else:
        dest_info = await get_city_info(destination_city, country_code)
        if dest_info:
            result["destination_id"] = dest_info.get("id")
            result["destination_name"] = dest_info.get("name")
        else:
            result["error"] = f"Could not find city: {destination_city}"
            return result
    
    return result


# Synchronous wrapper for testing
def get_city_id_sync(city_name: str, country_code: str = "IN") -> Optional[str]:
    """Synchronous wrapper for get_city_id."""
    import asyncio
    return asyncio.run(get_city_id(city_name, country_code))


def get_city_suggestions_sync(city_prefix: str, country_code: str = "IN") -> List[Dict[str, Any]]:
    """Synchronous wrapper for get_city_suggestions."""
    import asyncio
    return asyncio.run(get_city_suggestions(city_prefix, country_code))