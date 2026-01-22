import uuid
import time
import json
import asyncio
import random
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
TRAIN_AUTOSUGGEST_URL = "https://solr.easemytrip.com/api/auto/GetTrainAutoSuggest"

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


async def fetch_train_station_suggestions(
    search_term: str,
    max_retries: int = 5,
    base_delay: float = 0.2,
) -> List[Dict]:
    """
    Fetch train station suggestions from EaseMyTrip Solr API with retry and exponential backoff.

    Args:
        search_term: User-provided station/city name (e.g., "Jammu", "Delhi")
        max_retries: Maximum number of retry attempts (default: 5)
        base_delay: Initial delay in seconds before first retry (default: 0.2s / 200ms)

    Returns:
        List of station suggestions with Code, Name, State

    Example Response:
        [{"Code": "JAT", "Name": "Jammu Tawi", "State": "Jammu & Kashmir"}, ...]

    Retry Strategy:
        - Exponential backoff: delay doubles each attempt (200ms, 400ms, 800ms, 1.6s, 3.2s)
        - Jitter: random variance (0-50%) to prevent thundering herd
        - Retries on: HTTP 5xx errors, connection errors, timeouts
    """
    if not search_term:
        raise ValueError("Search term must be provided.")

    url = f"{TRAIN_AUTOSUGGEST_URL}/{search_term}"
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            if not isinstance(data, list):
                raise ValueError(f"Unexpected response type: {type(data)}")

            return data

        except httpx.HTTPStatusError as e:
            last_exception = e
            # Only retry on 5xx server errors
            if e.response.status_code >= 500 and attempt < max_retries:
                delay = _calculate_backoff_delay(attempt, base_delay)
                print(f"[TrainAutosuggest] HTTP {e.response.status_code}, retrying in {delay:.0f}ms (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
                continue
            raise ValueError(f"Train autosuggest failed: {e}")

        except (httpx.ConnectError, httpx.TimeoutException) as e:
            last_exception = e
            # Retry on connection/timeout errors
            if attempt < max_retries:
                delay = _calculate_backoff_delay(attempt, base_delay)
                print(f"[TrainAutosuggest] {type(e).__name__}, retrying in {delay:.0f}ms (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
                continue
            raise ValueError(f"Train autosuggest failed: {e}")

        except Exception as e:
            # Don't retry on other errors (e.g., JSON parse errors)
            raise ValueError(f"Train autosuggest failed: {e}")

    # Should not reach here, but just in case
    raise ValueError(f"Train autosuggest failed after {max_retries} retries: {last_exception}")


def _calculate_backoff_delay(attempt: int, base_delay: float) -> float:
    """
    Calculate delay with exponential backoff and jitter.

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds

    Returns:
        Delay in seconds with jitter applied

    Formula: base_delay * (2 ^ attempt) * (1 + random(0, 0.5))
    Example with base_delay=0.2 (200ms):
        attempt 0: 0.2s * 1 * jitter = ~200-300ms
        attempt 1: 0.2s * 2 * jitter = ~400-600ms
        attempt 2: 0.2s * 4 * jitter = ~800-1200ms
        attempt 3: 0.2s * 8 * jitter = ~1600-2400ms
        attempt 4: 0.2s * 16 * jitter = ~3200-4800ms
    """
    exponential_delay = base_delay * (2 ** attempt)
    jitter = 1 + random.uniform(0, 0.5)  # Add 0-50% random jitter
    return exponential_delay * jitter


async def resolve_train_station(search_term: str) -> str:
    """
    Resolve user input to formatted train station string.

    Args:
        search_term: User-provided station/city name (e.g., "Jammu", "Delhi")

    Returns:
        Formatted station string: "Station Name (CODE)"

    Examples:
        "Jammu" → "Jammu Tawi (JAT)"
        "Delhi" → "Delhi All Stations (NDLS)"
        "Mumbai" → "Mumbai Central (MMCT)"
    """
    try:
        suggestions = await fetch_train_station_suggestions(search_term)

        if not suggestions:
            # Fallback: return original input
            return search_term

        first = suggestions[0]
        code = first.get("Code", "")
        name = first.get("Name", "") or first.get("Show", "")

        if code and name:
            return f"{name} ({code})"
        elif code:
            return f"{search_term} ({code})"
        else:
            return search_term

    except Exception as e:
        print(f"[TrainStationResolver] Error: {e}. Using raw input: {search_term}")
        return search_term


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