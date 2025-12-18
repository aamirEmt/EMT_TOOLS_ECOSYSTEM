# app/utils.py
import uuid
import time
from datetime import datetime
from typing import Tuple, List, Dict
from emt_client.clients.flight_client import FlightApiClient
from .config import AUTOSUGGEST_URL

def gen_trace_id(prefix="trace"):
    return f"{prefix}{int(time.time()*1000)}{str(uuid.uuid4())[:6]}"

def today_str():
    return datetime.utcnow().strftime("%Y-%m-%d")




async def fetch_autosuggest(client: FlightApiClient, search_term: str) -> List[Dict]:
    if not search_term:
        raise ValueError("Search term must be provided.")
    payload = {"Prefix": search_term, "Search": search_term}
    data = await client.search(AUTOSUGGEST_URL, payload)  # your actual URL
    if not isinstance(data, list):
        raise ValueError(f"Unexpected response type: {type(data)}")
    return data

def extract_first_code_and_country(suggestions: List[Dict]) -> Tuple[str, str]:
    if not suggestions:
        raise ValueError("Empty suggestions list.")
    first = suggestions[0]
    city_field = first.get("City", "") or ""
    code = city_field.split("(")[1].split(")")[0] if "(" in city_field else city_field.strip()
    country = first.get("Country", "") or ""
    return code, country

async def fetch_first_code_and_country(client: FlightApiClient, search_term: str) -> Tuple[str, str]:
    suggestions = await fetch_autosuggest(client, search_term)
    return extract_first_code_and_country(suggestions)