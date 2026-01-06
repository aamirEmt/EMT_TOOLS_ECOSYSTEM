import uuid
import time
from datetime import datetime
from typing import Tuple, List, Dict,Optional, TYPE_CHECKING
from .config import AUTOSUGGEST_URL
import httpx

if TYPE_CHECKING:
    from emt_client.clients.flight_client import FlightApiClient

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