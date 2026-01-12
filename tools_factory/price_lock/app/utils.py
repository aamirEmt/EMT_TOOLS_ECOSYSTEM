# app/utils.py
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests

from app.config import AUTOSUGGEST_URL

def gen_trace_id(prefix="trace"):
    return f"{prefix}{int(time.time()*1000)}{str(uuid.uuid4())[:6]}"

def today_str():
    return datetime.utcnow().strftime("%Y-%m-%d")


# Basic browser-like headers help avoid being rejected by the auto-suggest endpoint.
AUTOSUGGEST_HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
}


def fetch_autosuggest(search_term: str, *, headers: Optional[Dict[str, str]] = None, timeout: float = 15.0) -> List[Dict]:
    """
    Call the EaseMyTrip auto-suggest API and return the raw suggestions list.
    """
    if not search_term:
        raise ValueError("Search term must be provided.")

    merged_headers = {**AUTOSUGGEST_HEADERS, **(headers or {})}
    payload = {"Prefix": search_term, "Search": search_term}

    response = requests.post(
        AUTOSUGGEST_URL,
        json=payload,
        headers=merged_headers,
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()

    if isinstance(data, str):
        raise ValueError(f"Unexpected string response from API: {data}")
    if not isinstance(data, list):
        raise ValueError(f"Unexpected response type: {type(data)}")

    return data


def extract_first_code_and_country(suggestions: List[Dict]) -> Tuple[str, str]:
    """
    Parse the first suggestion and pull out the airport code + country.
    """
    if not suggestions:
        raise ValueError("Empty suggestions list.")

    first = suggestions[0]
    city_field = first.get("City", "") or ""

    code = ""
    if "(" in city_field and ")" in city_field:
        # e.g., "Jaipur(JAI)" -> "JAI"
        code = city_field.split("(", 1)[1].split(")", 1)[0]
    else:
        code = city_field.strip()

    country = first.get("Country", "") or ""
    return code, country


def fetch_first_code_and_country(search_term: str, *, headers: Optional[Dict[str, str]] = None, timeout: float = 15.0) -> Tuple[str, str]:
    """
    Convenience wrapper: call API then parse first entry.
    """
    suggestions = fetch_autosuggest(search_term, headers=headers, timeout=timeout)
    return extract_first_code_and_country(suggestions)
