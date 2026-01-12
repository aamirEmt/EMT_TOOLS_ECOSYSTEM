# app/config.py
"""
Centralized configuration for EaseMyTrip MCP Server
All API endpoints, authentication, and settings in one place
"""
from os import getenv
from typing import Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# 🏨 HOTEL SERVICE BASE URL
# ============================================================================
BASE_URL = "https://hotelservice.easemytrip.com/api"
HOTEL_DEEPLINK="https://www.easemytrip.com/hotel-new/details?"
# ============================================================================
# 🏨 HOTEL API ENDPOINTS
# ============================================================================
LOGIN_URL = f"{BASE_URL}/HotelService/UserLogin"
HOTEL_SEARCH_URL = f"{BASE_URL}/HotelService/HotelListIdWiseNew"
HOTEL_SEARCH_WITH_FILTER_URL = f"{BASE_URL}/HotelService/HotelSearch"
# HOTEL_DESCRIPTION_URL = f"{BASE_URL}/HotelInfo/GetHotelDescriptionV1"
# PRODUCT_DETAILS_URL = f"{BASE_URL}/HotelInfo/GetProductDetails"
# CREATE_TRANSACTION_URL = f"{BASE_URL}/HotelInfo/HotelTraveller"

# Payment/Checkout URL
PAYMENT_CHECKOUT_BASE_URL = "https://safepay.easemytrip.com/new/checkout"

# Legacy URL mappings (for backward compatibility)
HOTEL_LIST_URL = HOTEL_SEARCH_URL
USER_LOGIN_URL = LOGIN_URL
# CREATE_BOOKING_URL = CREATE_TRANSACTION_URL

# ============================================================================
# 🛫 FLIGHT SERVICE (For Future Expansion)
# ============================================================================
FLIGHT_TOKEN_URL = "https://gi.easemytrip.com/etm/api/etoken/jypppm"
FLIGHT_BASE_URL = "https://flightservice-web.easemytrip.com/EmtAppService"
FLIGHT_AMENITIES_URL = f"{FLIGHT_BASE_URL}/FlightStatus/FlightAmentiesByListing"
FLIGHT_ATK_TOKEN = getenv("FLIGHT_ATK_TOKEN")
FLIGHT_DEEPLINK="https://flight.easemytrip.com/RemoteSearchHandlers/index"
AUTOSUGGEST_URL = "https://www.easemytrip.com/api/Flight/GetAutoSuggestNew"


# ============================================================================
# 🔐 AUTHENTICATION CONFIGURATION
# ============================================================================

def get_agent_auth() -> Dict[str, str]:
    """
    Get agent authentication credentials from environment variables

    Returns:
        dict: Agent authentication credentials

    Raises:
        ValueError: If required environment variables are not set
    """
    agent_code = getenv("AGENT_CODE")
    agent_user = getenv("AGENT_USER")
    agent_pwd = getenv("AGENT_PWD")

    if not all([agent_code, agent_user, agent_pwd]):
        raise ValueError(
            "Missing required environment variables: AGENT_CODE, AGENT_USER, AGENT_PWD"
        )

    return {
        "AgentCode": agent_code,
        "UserName": agent_user,
        "Password": agent_pwd,
        "loginInfo": ""
    }

# Default agent auth (can be overridden by environment variables)
AGENT_AUTH = get_agent_auth()

# For backward compatibility
DEFAULT_AUTH = AGENT_AUTH

# ============================================================================
# 🆔 VENDOR & SESSION CONFIGURATION
# ============================================================================
VID = getenv("VID")
if not VID:
    raise ValueError("Missing required environment variable: VID")
DEFAULT_VID = VID

# ============================================================================
# ⚙️ API CONFIGURATION
# ============================================================================

# HTTP Request Settings
_api_timeout = getenv("API_TIMEOUT")
if not _api_timeout:
    raise ValueError("Missing required environment variable: API_TIMEOUT")
DEFAULT_TIMEOUT = float(_api_timeout)

_max_retries = getenv("MAX_RETRIES")
if not _max_retries:
    raise ValueError("Missing required environment variable: MAX_RETRIES")
MAX_RETRIES = int(_max_retries)

# Token Management
_token_validity = getenv("TOKEN_VALIDITY_MINUTES")
if not _token_validity:
    raise ValueError("Missing required environment variable: TOKEN_VALIDITY_MINUTES")
TOKEN_VALIDITY_MINUTES = int(_token_validity)

_token_cache = getenv("TOKEN_CACHE_ENABLED")
if not _token_cache:
    raise ValueError("Missing required environment variable: TOKEN_CACHE_ENABLED")
TOKEN_CACHE_ENABLED = _token_cache.lower() == "true"

# Search Defaults
_default_hotel_count = getenv("DEFAULT_HOTEL_COUNT")
if not _default_hotel_count:
    raise ValueError("Missing required environment variable: DEFAULT_HOTEL_COUNT")
DEFAULT_HOTEL_COUNT = int(_default_hotel_count)

_default_page_no = getenv("DEFAULT_PAGE_NO")
if not _default_page_no:
    raise ValueError("Missing required environment variable: DEFAULT_PAGE_NO")
DEFAULT_PAGE_NO = int(_default_page_no)

DEFAULT_CURRENCY = getenv("DEFAULT_CURRENCY")
if not DEFAULT_CURRENCY:
    raise ValueError("Missing required environment variable: DEFAULT_CURRENCY")

DEFAULT_COUNTRY_CODE = getenv("DEFAULT_COUNTRY_CODE")
if not DEFAULT_COUNTRY_CODE:
    raise ValueError("Missing required environment variable: DEFAULT_COUNTRY_CODE")

# Price Filters
_default_min_price = getenv("DEFAULT_MIN_PRICE")
if not _default_min_price:
    raise ValueError("Missing required environment variable: DEFAULT_MIN_PRICE")
DEFAULT_MIN_PRICE = int(_default_min_price)

_default_max_price = getenv("DEFAULT_MAX_PRICE")
if not _default_max_price:
    raise ValueError("Missing required environment variable: DEFAULT_MAX_PRICE")
DEFAULT_MAX_PRICE = int(_default_max_price)

# Sorting Options
SORT_OPTIONS = {
    "popular_desc": "Popular|DESC",
    "price_asc": "Price|ASC",
    "price_desc": "Price|DESC",
    "rating_desc": "Rating|DESC"
}
DEFAULT_SORT = SORT_OPTIONS["popular_desc"]

# ============================================================================
# 🌍 SEARCH KEY CONFIGURATION
# ============================================================================

def generate_search_key(
    city_code: str,
    check_in: str,
    check_out: str,
    num_rooms: int,
    num_adults: int,
    engine: str = "15",
    currency: str = "INR",
    provider: str = "EASEMYTRIP",
    country: str = "IN"
) -> str:
    """
    Generate SearchKey for hotel API requests

    Format: ENGINE~CURRENCY~CITY~CHECKIN~CHECKOUT~ROOMS~ADULTS_~~~PROVIDER~NA~NA~NA~COUNTRY

    Args:
        city_code: City code (e.g., "NEWDELHI,INDIA")
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        num_rooms: Number of rooms
        num_adults: Number of adults
        engine: Engine ID (default: "15")
        currency: Currency code (default: "INR")
        provider: Provider name (default: "EASEMYTRIP")
        country: Country code (default: "IN")

    Returns:
        str: Formatted SearchKey
    """
    # Normalize city code (uppercase, remove spaces)
    city_normalized = city_code.upper().replace(" ", "")

    return (
        f"{engine}~{currency}~{city_normalized}~{check_in}~{check_out}~"
        f"{num_rooms}~{num_adults}_~~~{provider}~NA~NA~NA~{country}"
    )

# ============================================================================
# 📊 LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL = getenv("LOG_LEVEL")
if not LOG_LEVEL:
    raise ValueError("Missing required environment variable: LOG_LEVEL")

_log_api_requests = getenv("LOG_API_REQUESTS")
if not _log_api_requests:
    raise ValueError("Missing required environment variable: LOG_API_REQUESTS")
LOG_API_REQUESTS = _log_api_requests.lower() == "true"

_log_api_responses = getenv("LOG_API_RESPONSES")
if not _log_api_responses:
    raise ValueError("Missing required environment variable: LOG_API_RESPONSES")
LOG_API_RESPONSES = _log_api_responses.lower() == "true"

# ============================================================================
# 🔧 DEVELOPMENT / DEBUG SETTINGS
# ============================================================================
_debug_mode = getenv("DEBUG_MODE")
if not _debug_mode:
    raise ValueError("Missing required environment variable: DEBUG_MODE")
DEBUG_MODE = _debug_mode.lower() == "true"

_mock_api_calls = getenv("MOCK_API_CALLS")
if not _mock_api_calls:
    raise ValueError("Missing required environment variable: MOCK_API_CALLS")
MOCK_API_CALLS = _mock_api_calls.lower() == "true"

# ============================================================================
# 📝 API HEADERS CONFIGURATION
# ============================================================================

def get_default_headers(trace_id: str = None) -> Dict[str, str]:
    """
    Get default HTTP headers for API requests

    Args:
        trace_id: Optional trace ID for request tracking

    Returns:
        dict: Default headers
    """
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json, text/plain, */*",
        # Keep encoding to gzip/deflate only; httpx isn't built with brotli by default,
        # and the API returns br-compressed bodies otherwise, which breaks JSON decoding.
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "EaseMyTrip-MCP-Server/1.0"
    }

    if trace_id:
        headers["traceid"] = trace_id

    return headers

# ============================================================================
# 🏷️ CONSTANTS
# ============================================================================

# Engine IDs
ENGINE_DEFAULT = "15"
ENGINE_BOOKING_JINI = "10"

# Room Configuration
MAX_ROOMS = 9
MAX_ADULTS_PER_ROOM = 6
MAX_CHILDREN_PER_ROOM = 4

# Star Ratings
STAR_RATINGS = ["1", "2", "3", "4", "5"]

# Meal Types
MEAL_TYPES = [
    "Breakfast included",
    "Breakfast not included",
    "Breakfast included (Non-Refundable)",
    "Breakfast not included (Non-Refundable)"
]

# Hotel Property Types
PROPERTY_TYPES = [
    "Hotel",
    "Resort",
    "Apartment",
    "Villa",
    "Guesthouse"
]

# Booking Policies
BOOKING_POLICIES = {
    "REFUNDABLE": "Refundable booking",
    "NON_REFUNDABLE": "Non-refundable booking",
    "FREE_CANCELLATION": "Free cancellation"
}

# ============================================================================
# 🌐 ENVIRONMENT-SPECIFIC OVERRIDES
# ============================================================================

# Allow environment variables to override any URL
LOGIN_URL = getenv("LOGIN_URL", LOGIN_URL)
HOTEL_SEARCH_URL = getenv("HOTEL_SEARCH_URL", HOTEL_SEARCH_URL)
# HOTEL_DESCRIPTION_URL = getenv("HOTEL_DESCRIPTION_URL", HOTEL_DESCRIPTION_URL)
# PRODUCT_DETAILS_URL = getenv("PRODUCT_DETAILS_URL", PRODUCT_DETAILS_URL)

# ============================================================================
# 📦 EXPORT ALL CONFIGURATIONS
# ============================================================================

__all__ = [
    # Base URLs
    "BASE_URL",
    "FLIGHT_BASE_URL",

    # Hotel Endpoints
    "LOGIN_URL",
    "HOTEL_SEARCH_URL",
    "HOTEL_SEARCH_WITH_FILTER_URL",
    "HOTEL_DESCRIPTION_URL",
    "PRODUCT_DETAILS_URL",
    "CREATE_TRANSACTION_URL",
    "PAYMENT_CHECKOUT_BASE_URL",

    # Flight Endpoints
    "FLIGHT_AMENITIES_URL",
    "AUTOSUGGEST_URL",

    # Authentication
    "AGENT_AUTH",
    "DEFAULT_AUTH",
    "get_agent_auth",

    # Vendor/Session
    "VID",
    "DEFAULT_VID",

    # API Configuration
    "DEFAULT_TIMEOUT",
    "MAX_RETRIES",
    "TOKEN_VALIDITY_MINUTES",
    "TOKEN_CACHE_ENABLED",

    # Search Defaults
    "DEFAULT_HOTEL_COUNT",
    "DEFAULT_PAGE_NO",
    "DEFAULT_CURRENCY",
    "DEFAULT_COUNTRY_CODE",
    "DEFAULT_MIN_PRICE",
    "DEFAULT_MAX_PRICE",
    "DEFAULT_SORT",
    "SORT_OPTIONS",

    # Utilities
    "generate_search_key",
    "get_default_headers",

    # Constants
    "ENGINE_DEFAULT",
    "ENGINE_BOOKING_JINI",
    "MAX_ROOMS",
    "MAX_ADULTS_PER_ROOM",
    "MAX_CHILDREN_PER_ROOM",
    "STAR_RATINGS",
    "MEAL_TYPES",
    "PROPERTY_TYPES",
    "BOOKING_POLICIES",

    # Logging
    "LOG_LEVEL",
    "LOG_API_REQUESTS",
    "LOG_API_RESPONSES",

    # Debug
    "DEBUG_MODE",
    "MOCK_API_CALLS"
]
