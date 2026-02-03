import uuid
import time
import json
from datetime import datetime
from typing import Tuple, List, Dict, Optional, Any
from emt_client.clients.flight_client import FlightApiClient
from .config import AUTOSUGGEST_URL
import httpx
import requests

def gen_trace_id(prefix="trace"):
    return f"{prefix}{int(time.time()*1000)}{str(uuid.uuid4())[:6]}"

def today_str():
    return datetime.utcnow().strftime("%Y-%m-%d")




async def fetch_autosuggest(client: "FlightApiClient", search_term: str) -> List[Dict]:
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

async def fetch_first_code_and_country(client: "FlightApiClient", search_term: str) -> Tuple[str, str]:
    suggestions = await fetch_autosuggest(client, search_term)
    return extract_first_code_and_country(suggestions)

def extract_first_city_code_country(suggestions: List[Dict]) -> Tuple[str, str, str]:
    if not suggestions:
        raise ValueError("Empty suggestions list.")
    first = suggestions[0] or {}
    city_field = first.get("City") or first.get("CityName") or first.get("Name") or ""
    country = (first.get("Country") or "").strip()

    city_field = str(city_field).strip()
    if "(" in city_field and ")" in city_field:
        name_part, code_part = city_field.split("(", 1)
        city_name = name_part.strip() or city_field
        city_code = code_part.split(")", 1)[0].strip() or city_field
    else:
        city_name = city_field
        city_code = city_field

    return city_code, country, city_name

async def fetch_first_city_code_country(
    client: FlightApiClient, search_term: str
) -> Tuple[str, str, str]:
    suggestions = await fetch_autosuggest(client, search_term)
    return extract_first_city_code_country(suggestions)


SOLR_AUTOSUGGEST_URL = "https://solr.easemytrip.com/v1/api/auto/GetHotelAutoSuggest_SolrUItest"

async def resolve_city_name(raw_city: str) -> str:
    """
    Normalize city name using Solr AutoSuggest API.
    
    Args:
        raw_city: User-provided city name
    
    Returns:
        Normalized city name (e.g., "PUNE,INDIA")
    
    Examples:
        "Pune" → "PUNE,INDIA"
        "Viman Nagar" → "VIMAN NAGAR, PUNE,INDIA"
        "Mumbai Airport" → "MUMBAI AIRPORT AREA,INDIA"
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                SOLR_AUTOSUGGEST_URL,
                json={"request": raw_city},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            normalized = data[0].get("name")
            if normalized:
                return normalized
        
        # Fallback: return original input
        return raw_city
    
    except Exception as e:
        print(f"[CityResolver] Error: {e}. Using raw input: {raw_city}")
        return raw_city
    
def generate_hotel_search_key(
    city_code: str,
    check_in: str,
    check_out: str,
    num_rooms: int,
    num_adults: int,
    num_children: int = 0,
    engine: str = "15",
    currency: str = "INR",
    provider: str = "EASEMYTRIP",
    country: str = "IN"
) -> str:
    """
    Generate search key for hotel API request.
    
    Format: ENGINE~CURRENCY~CITY~CHECKIN~CHECKOUT~ROOMS~ADULTS_CHILDREN~~PROVIDER~NA~NA~NA~COUNTRY
    
    Example Output:
        "15~INR~PUNE,INDIA~2024-12-25~2024-12-27~1~2_0~~~EASEMYTRIP~NA~NA~NA~IN"
    """
    child_config = f"{num_adults}_{num_children}" if num_children > 0 else f"{num_adults}_"
    
    search_key = (
        f"{engine}~{currency}~{city_code}~{check_in}~{check_out}~"
        f"{num_rooms}~{child_config}~~{provider}~NA~NA~NA~{country}"
    )
    
    return search_key


DEEPLINK_API_URL = "https://deeplinkapi.easemytrip.com/api/fire/GetShortLinkRawV1"


def generate_short_link(
    results: List[Dict[str, Any]],
    product_type: str,
) -> List[Dict[str, Any]]:
    """
    Create shortened EMT deeplinks for a list of results using the public shortener API.

    - If the API fails for any item, the original link is kept.
    - Processing continues for remaining items.
    """

    headers = {"Content-Type": "application/json"}

    for item in results:
        original_link = item.get("deepLink") or item.get("originalDeepLink")
        if not original_link:
            continue

        payload = {
            "Link": original_link,
            "UserId": "",
            "Mobile": "",
            "Email": "",
            "PageType": "2",
            "ProductType": product_type,
            "PlatformId": "6",
            "Authentication": {
                "UserName": "EMT",
                "Password": "123123",
            },
        }

        try:
            response = requests.post(
                DEEPLINK_API_URL,
                headers=headers,
                json=payload,      # ✅ use json instead of data=json.dumps
                timeout=10,
            )

            response.raise_for_status()
            data = response.json()

            short_link = data.get("ShortLink")

            # Only replace if a valid short link exists
            if short_link:
                item["deepLink"] = short_link
            else:
                item["deepLink"] = original_link

        except (requests.RequestException, ValueError) as e:
            # ❗ Any API / network / JSON error → keep original link
            item["deepLink"] = original_link
            # Optional: log the error
            # logger.warning("Short link failed for %s: %s", original_link, str(e))

    return results

# ============================================================================
# BUS UTILITIES
# ============================================================================


def build_bus_search_payload(
    source_id: str,
    destination_id: str,
    date: str,
    key: str,
    is_vrl: str = "False",
    is_volvo: str = "False",
    is_android_ios_hit: bool = False,
    agent_code: str = "",
    country_code: str = "IN",
    version: str = "1",
) -> Dict[str, Any]:
    """
    Build payload for Bus Search API.
    
    POST http://busapi.easemytrip.com/v1/api/detail/List/
    
    Args:
        source_id: Source city ID (e.g., "733" for Delhi)
        destination_id: Destination city ID (e.g., "757" for Manali)
        date: Journey date in dd-MM-yyyy format
        key: API key
        is_vrl: VRL filter ("True"/"False")
        is_volvo: Volvo filter ("True"/"False")
        is_android_ios_hit: Android/iOS flag
        agent_code: Agent code (optional)
        country_code: Country code (default "IN")
        version: API version (default "1")
        
    Returns:
        Dict payload for Bus Search API
    """
    return {
        "sourceId": source_id,
        "destinationId": destination_id,
        "date": date,
        "key": key,
        "version": version,
        "isVrl": is_vrl,
        "isVolvo": is_volvo,
        "IsAndroidIos_Hit": is_android_ios_hit,
        "agentCode": agent_code,
        "CountryCode": country_code,
    }


def build_bus_deeplink(
    source_id: str,
    destination_id: str,
    journey_date: str,
    bus_id: str,
) -> str:
    """
    Build EaseMyTrip bus booking deeplink.
    
    Args:
        source_id: Source city ID
        destination_id: Destination city ID
        journey_date: Journey date in dd-MM-yyyy format
        bus_id: Bus ID from search results
        
    Returns:
        Booking deeplink URL
    """
    return (
        f"https://www.easemytrip.com/bus/booking/"
        f"?src={source_id}&dest={destination_id}&date={journey_date}&busId={bus_id}"
    )