# emt_client/config.py
"""
Configuration module for EMT Client
Supports configuration injection from parent projects
"""
from os import getenv
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# ============================================================================
# 🆕 NEW: Configuration Injection Support
# ============================================================================
# Global configuration storage
_injected_config: Optional[Dict[str, Any]] = None

def inject_config(config: Dict[str, Any]):
    """
    🆕 NEW: Inject configuration from parent project
    
    This allows parent projects to pass configuration without needing .env files
    
    Args:
        config: Configuration dictionary with keys like:
            - FLIGHT_TOKEN_URL
            - FLIGHT_BASE_URL
            - FLIGHT_ATK_TOKEN
            - FLIGHT_DEEPLINK
            - etc.
    
    Example:
        from app.config import FLIGHT_TOKEN_URL, FLIGHT_BASE_URL
        from emt_client.config import inject_config
        
        inject_config({
            'FLIGHT_TOKEN_URL': FLIGHT_TOKEN_URL,
            'FLIGHT_BASE_URL': FLIGHT_BASE_URL,
            'FLIGHT_ATK_TOKEN': FLIGHT_ATK_TOKEN,
        })
    """
    global _injected_config
    _injected_config = config

def _get_config_value(key: str, env_key: str, default: Any = None, required: bool = False) -> Any:
    """
    🆕 NEW: Get configuration value with priority: injected > env > default
    
    Args:
        key: Key in injected config dictionary
        env_key: Environment variable name
        default: Default value if not found
        required: If True, raises error when not found
        
    Returns:
        Configuration value
    """
    # Priority 1: Check injected config
    if _injected_config is not None and key in _injected_config:
        return _injected_config[key]
    
    # Priority 2: Check environment variables (only if no injection)
    if _injected_config is None:
        load_dotenv()
        env_value = getenv(env_key)
        if env_value is not None:
            return env_value
    
    # Priority 3: Use default
    if default is not None:
        return default
    
    # If required and still not found, raise error
    if required:
        raise ValueError(
            f"Required configuration '{key}' not found. "
            f"Either inject it via inject_config() or set environment variable '{env_key}'"
        )
    
    return None

def has_injected_config() -> bool:
    """🆕 NEW: Check if configuration has been injected"""
    return _injected_config is not None

def reset_config():
    """🆕 NEW: Reset injected configuration (useful for testing)"""
    global _injected_config
    _injected_config = None

# ============================================================================
# ✅ MODIFIED: Flight Configuration (now supports injection)
# ============================================================================

# 🔄 CHANGED: Now uses _get_config_value for injection support
FLIGHT_TOKEN_URL = _get_config_value(
    'FLIGHT_TOKEN_URL',
    'FLIGHT_TOKEN_URL',
    default='https://gi.easemytrip.com/etm/api/etoken/jypppm'
)

FLIGHT_BASE_URL = _get_config_value(
    'FLIGHT_BASE_URL',
    'FLIGHT_BASE_URL',
    default='https://flightservice-node.easemytrip.com'
)

FLIGHT_ATK_TOKEN = _get_config_value(
    'FLIGHT_ATK_TOKEN',
    'FLIGHT_ATK_TOKEN',
    required=True  # This will error if not provided via injection or env
)

CHATBOT_API_BASE_URL = _get_config_value(
    'CHATBOT_API_BASE_URL',
    'CHATBOT_API_BASE_URL',
    default='https://staging-aiml-chatbotapi.easemytrip.com'
)

MYBOOKINGS_BASE_URL = _get_config_value(
    'MYBOOKINGS_BASE_URL',
    'MYBOOKINGS_BASE_URL',
    default='https://mybookings.easemytrip.com'
)

FLIGHT_DEEPLINK = _get_config_value(
    'FLIGHT_DEEPLINK',
    'FLIGHT_DEEPLINK',
    default='https://flight.easemytrip.com/RemoteSearchHandlers/index'
)

FLIGHT_AMENITIES_URL = f"{FLIGHT_BASE_URL}/FlightStatus/FlightAmentiesByListing"

# ============================================================================
# ✅ STAYS THE SAME: All your existing configurations
# ============================================================================

# Load environment variables (only used if config not injected)
if _injected_config is None:
    load_dotenv()
# 🏨 HOTEL SERVICE BASE URL
BASE_URL = "https://hotelservice.easemytrip.com/api"
HOTEL_DEEPLINK = "https://www.easemytrip.com/hotel-new/details?"

# 🏨 HOTEL API ENDPOINTS
LOGIN_URL = f"{BASE_URL}/HotelService/UserLogin"
HOTEL_SEARCH_URL = f"{BASE_URL}/HotelService/HotelListIdWiseNew"
HOTEL_SEARCH_WITH_FILTER_URL = f"{BASE_URL}/HotelService/HotelSearch"

# 🚂 TRAIN SERVICE BASE URL
TRAIN_BASE_URL = "https://railways.easemytrip.com"
TRAIN_API_URL = f"{TRAIN_BASE_URL}/Train/_TrainBtwnStationList"
TRAIN_LIST_INFO_URL = f"{TRAIN_BASE_URL}/TrainListInfo"
TRAIN_BOOKING_URL = f"{TRAIN_BASE_URL}/TrainInfo"
PNR_STATUS_URL = f"{TRAIN_BASE_URL}/Train/PnrchkStatus"
TRAIN_ROUTE_API_URL = f"{TRAIN_BASE_URL}/Train/TrainScheduleEnquiry"
TRAIN_NAME_API_URL = "https://autosuggest.easemytrip.com/api/auto/train_name?useby=popularu&key=jNUYK0Yj5ibO6ZVIkfTiFA=="

# 🔐 PNR ENCRYPTION CONFIGURATION
# AES-128 CBC encryption constants for PNR number encryption
PNR_ENCRYPTION_KEY = b"8080808080808080"  # 16 bytes
PNR_ENCRYPTION_IV = b"8080808080808080"  # 16 bytes

# 🔍 AUTOSUGGEST SERVICE URLS
SOLR_BASE_URL = "https://solr.easemytrip.com"
SOLR_AUTOSUGGEST_URL = f"{SOLR_BASE_URL}/v1/api/auto/GetHotelAutoSuggest_SolrUI"
TRAIN_AUTOSUGGEST_URL = f"{SOLR_BASE_URL}/api/auto/GetTrainAutoSuggest"

# 🔗 DEEPLINK SERVICE URL
DEEPLINK_API_URL = "https://deeplinkapi.easemytrip.com/api/fire/GetShortLinkRawV1"

# Payment/Checkout URL
PAYMENT_CHECKOUT_BASE_URL = "https://safepay.easemytrip.com/new/checkout"

# Legacy URL mappings (for backward compatibility)
HOTEL_LIST_URL = HOTEL_SEARCH_URL
USER_LOGIN_URL = LOGIN_URL

# ============================================================================
# 🔐 AUTHENTICATION CONFIGURATION - STAYS THE SAME
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
DEFAULT_AUTH = AGENT_AUTH

# ============================================================================
# 🆔 VENDOR & SESSION CONFIGURATION - STAYS THE SAME
# ============================================================================
VID = getenv("VID")
if not VID:
    raise ValueError("Missing required environment variable: VID")
DEFAULT_VID = VID

# ============================================================================
# ⚙️ API CONFIGURATION - STAYS THE SAME
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
# 🌍 SEARCH KEY CONFIGURATION - STAYS THE SAME
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
# 📊 LOGGING CONFIGURATION - STAYS THE SAME
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
# 🔧 DEVELOPMENT / DEBUG SETTINGS - STAYS THE SAME
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
# 📝 API HEADERS CONFIGURATION - STAYS THE SAME
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
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "EaseMyTrip-MCP-Server/1.0"
    }

    if trace_id:
        headers["traceid"] = trace_id

    return headers

# ============================================================================
# 🏷️ CONSTANTS - STAYS THE SAME
# ============================================================================

# Engine IDs
ENGINE_DEFAULT = "15"
ENGINE_BOOKING_JINI = "10"

AUTOSUGGEST_HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
}
AUTOSUGGEST_URL = "https://www.easemytrip.com/api/Flight/GetAutoSuggestNew"
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
# 🌐 ENVIRONMENT-SPECIFIC OVERRIDES - STAYS THE SAME
# ============================================================================

# Allow environment variables to override any URL
LOGIN_URL = getenv("LOGIN_URL", LOGIN_URL)
HOTEL_SEARCH_URL = getenv("HOTEL_SEARCH_URL", HOTEL_SEARCH_URL)

# ============================================================================
# 🚌 BUS API CONFIGURATION
# ============================================================================

# Bus Search API endpoint
BUS_SEARCH_URL = _get_config_value(
    'BUS_SEARCH_URL',
    'BUS_SEARCH_URL',
    default='https://busservice.easemytrip.com/v1/api/Home/GetSearchResult/'
)

# Bus SeatBind API endpoint
BUS_SEAT_BIND_URL = _get_config_value(
    'BUS_SEAT_BIND_URL',
    'BUS_SEAT_BIND_URL',
    default='https://bus.easemytrip.com/Home/SeatBind/'
)

# Bus Deeplink base URL
BUS_DEEPLINK_BASE = _get_config_value(
    'BUS_DEEPLINK_BASE',
    'BUS_DEEPLINK_BASE',
    default='https://bus.easemytrip.com/home/list'
)

# Bus Autosuggest API endpoint
BUS_AUTOSUGGEST_URL = _get_config_value(
    'BUS_AUTOSUGGEST_URL',
    'BUS_AUTOSUGGEST_URL',
    default='https://autosuggest.easemytrip.com/api/auto/bus'
)

# Bus Autosuggest API Key
BUS_AUTOSUGGEST_KEY = _get_config_value(
    'BUS_AUTOSUGGEST_KEY',
    'BUS_AUTOSUGGEST_KEY',
    default='jNUYK0Yj5ibO6ZVIkfTiFA=='
)

# Bus Autosuggest Encrypted Header
BUS_ENCRYPTED_HEADER = _get_config_value(
    'BUS_ENCRYPTED_HEADER',
    'BUS_ENCRYPTED_HEADER',
    default='7ZTtohPgMEKTZQZk4/Cn1mpXnyNZDJIRcrdCFo5ahIk='
)

# Bus Decryption Key (from .env)
BUS_DECRYPTION_KEY = _get_config_value(
    'BUS_DECRYPTION_KEY',
    'BUS_DECRYPTION_KEY',
    default='TMTOO1vDhT9aWsV1'
)

# ============================================================================
# 📦 EXPORT ALL CONFIGURATIONS
# ============================================================================

__all__ = [
    # 🆕 NEW: Injection functions
    "inject_config",
    "has_injected_config",
    "reset_config",

    # Base URLs
    "BASE_URL",
    "FLIGHT_BASE_URL",
    "FLIGHT_TOKEN_URL",
    "FLIGHT_DEEPLINK",
    "TRAIN_BASE_URL",

    # Hotel Endpoints
    "LOGIN_URL",
    "HOTEL_SEARCH_URL",
    "HOTEL_SEARCH_WITH_FILTER_URL",
    "PAYMENT_CHECKOUT_BASE_URL",
    "HOTEL_DEEPLINK",

    # Flight Endpoints
    "FLIGHT_AMENITIES_URL",
    "FLIGHT_ATK_TOKEN",

    # Bus Configuration
    "BUS_SEARCH_URL",
    "BUS_SEAT_BIND_URL",
    "BUS_DEEPLINK_BASE",
    "BUS_AUTOSUGGEST_URL",
    "BUS_AUTOSUGGEST_KEY",
    "BUS_ENCRYPTED_HEADER",
    "BUS_DECRYPTION_KEY",
    # Train Endpoints
    "TRAIN_API_URL",
    "TRAIN_LIST_INFO_URL",
    "TRAIN_BOOKING_URL",
    "PNR_STATUS_URL",
    "TRAIN_NAME_API_URL",
    "TRAIN_AUTOSUGGEST_URL",
    "TRAIN_ROUTE_API_URL",
    "PNR_ENCRYPTION_KEY",
    "PNR_ENCRYPTION_IV",

    # Autosuggest Services
    "SOLR_BASE_URL",
    "SOLR_AUTOSUGGEST_URL",

    # Deeplink Service
    "DEEPLINK_API_URL",

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


# Hotel API URLs
HOTEL_BASE_URL = os.getenv(
    "HOTEL_BASE_URL",
    "https://hotelservice.easemytrip.com/api"
)
HOTEL_LOGIN_URL = f"{HOTEL_BASE_URL}/HotelService/UserLogin"
HOTEL_SEARCH_URL = f"{HOTEL_BASE_URL}/HotelService/HotelListIdWiseNew"

# Authentication Credentials
DEFAULT_AUTH: Dict[str, str] = {
    "AgentCode": os.getenv("AGENT_CODE", ""),
    "UserName": os.getenv("AGENT_USER", ""),
    "Password": os.getenv("AGENT_PWD", ""),
}

# Vendor ID
VID: str = os.getenv("VID", "")

# Token Settings
TOKEN_VALIDITY_MINUTES: int = int(os.getenv("TOKEN_VALIDITY_MINUTES", "28"))
TOKEN_CACHE_ENABLED: bool = os.getenv("TOKEN_CACHE_ENABLED", "true").lower() == "true"

# Debug Settings
DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"