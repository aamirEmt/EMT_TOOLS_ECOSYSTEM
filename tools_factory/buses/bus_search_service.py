import base64
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

try:
    from .bus_schema import (
        BusSearchInput,
        BusInfo,
        BoardingPoint,
        DroppingPoint,
        CancellationPolicy,
        WhatsappBusFormat,
        WhatsappBusFinalResponse,
    )
except ImportError:
    from bus_schema import (
        BusSearchInput,
        BusInfo,
        BoardingPoint,
        DroppingPoint,
        CancellationPolicy,
        WhatsappBusFormat,
        WhatsappBusFinalResponse,
    )

from emt_client.config import (
    BUS_SEARCH_URL,
    BUS_SEAT_BIND_URL as SEAT_BIND_URL,
    BUS_DEEPLINK_BASE,
    BUS_AUTOSUGGEST_URL,
    BUS_AUTOSUGGEST_KEY,
    BUS_ENCRYPTED_HEADER,
    BUS_DECRYPTION_KEY,
)
from emt_client.clients.bus_client import BusApiClient


# ============================================================================
# ENCRYPTION/DECRYPTION FUNCTIONS 
# ============================================================================

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
    
    key = BUS_DECRYPTION_KEY.encode("utf-8")
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
    
    key = BUS_DECRYPTION_KEY.encode("utf-8")
    encrypted_bytes = base64.b64decode(cipher_text)
    cipher = AES.new(key, AES.MODE_CBC, iv=key)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    return unpad(decrypted_bytes, AES.block_size).decode("utf-8")


# ============================================================================
# CITY AUTOSUGGEST FUNCTIONS 
# ============================================================================

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
        "encryptedHeader": BUS_ENCRYPTED_HEADER,
    }
    
    try:
        client = BusApiClient()
        encrypted_response = await client.get_city_suggestions(api_payload)
        
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


# Synchronous wrappers for testing
def get_city_id_sync(city_name: str, country_code: str = "IN") -> Optional[str]:
    """Synchronous wrapper for get_city_id."""
    import asyncio
    return asyncio.run(get_city_id(city_name, country_code))


def get_city_suggestions_sync(city_prefix: str, country_code: str = "IN") -> List[Dict[str, Any]]:
    """Synchronous wrapper for get_city_suggestions."""
    import asyncio
    return asyncio.run(get_city_suggestions(city_prefix, country_code))

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _generate_session_id() -> str:
    """Generate a unique session ID (Sid) for API calls."""
    return uuid.uuid4().hex


def _generate_visitor_id() -> str:
    """Generate a unique visitor ID (Vid) for API calls."""
    return uuid.uuid4().hex



def _normalize_rating(rating_value: Any) -> Optional[str]:
    """
    Normalize rating from API (0-50 scale) to display format (0-5 scale).
    
    Handles:
    - "45" -> "4.5"
    - 45 -> "4.5"
    - "4.5" -> "4.5"
    - 0 or None -> None (don't display)
    
    Args:
        rating_value: Raw rating from API
        
    Returns:
        Normalized rating string or None
    """
    if rating_value is None or rating_value == "" or rating_value == 0:
        return None
    
    try:
        rating_float = float(rating_value)
        
        # If rating > 5, assume it's on 0-50 scale and normalize
        if rating_float > 5:
            rating_float = rating_float / 10
        
        # Validate range
        if rating_float < 0 or rating_float > 5:
            return None
        
        # Don't show 0 ratings
        if rating_float == 0:
            return None
        
        # Format: whole number or one decimal
        if rating_float == int(rating_float):
            return str(int(rating_float))
        return f"{rating_float:.1f}"
        
    except (ValueError, TypeError):
        return None

# def _convert_date_to_api_format(date_str: str) -> str:
#     """
#     Convert date from YYYY-MM-DD to dd-MM-yyyy format for API.
    
#     Args:
#         date_str: Date in YYYY-MM-DD format
        
#     Returns:
#         Date in dd-MM-yyyy format
#     """
#     try:
#         dt = datetime.strptime(date_str, "%Y-%m-%d")
#         return dt.strftime("%d-%m-%Y")
#     except ValueError:
#         return date_str


def _build_bus_listing_url(
    source_id: str,
    destination_id: str,
    journey_date: str,
    source_name: str = "",
    destination_name: str = "",
) -> str:
    """
    Build the EaseMyTrip bus listing URL for View All link.
    
    Args:
        source_id: Source city ID
        destination_id: Destination city ID
        journey_date: Journey date in dd-MM-yyyy format
        source_name: Source city name
        destination_name: Destination city name
        
    Returns:
        Full URL to bus listing page
    """
    org_name = source_name or source_id
    des_name = destination_name or destination_id
    
    return (
        f"{BUS_DEEPLINK_BASE}"
        f"?org={org_name}&des={des_name}&date={journey_date}"
        f"&searchid={source_id}_{destination_id}&CCode=IN&AppCode=Emt"
    )


def _extract_amenities(lst_amenities: List[Dict[str, Any]]) -> List[str]:
    """Extract amenity names from API response."""
    if not lst_amenities:
        return []
    return [amenity.get("name", "") for amenity in lst_amenities if amenity.get("name")]


def _process_boarding_points(bd_points: List[Dict[str, Any]]) -> List[BoardingPoint]:
    """Process boarding points from API response."""
    if not bd_points:
        return []
    
    processed = []
    for bp in bd_points:
        try:
            processed.append(BoardingPoint(
                bdid=bp.get("bdid", ""),
                bdLongName=bp.get("bdLongName", "") or bp.get("bdPoint", ""),
                bdlocation=bp.get("bdlocation"),
                bdPoint=bp.get("bdPoint"),
                landmark=bp.get("landmark"),
                time=bp.get("time"),
                contactNumber=bp.get("contactNumber"),
                latitude=bp.get("latitude"),
                longitude=bp.get("longitude"),
                bordingDate=bp.get("bordingDate"),
            ))
        except Exception:
            continue
    return processed


def _process_dropping_points(dp_points: List[Dict[str, Any]]) -> List[DroppingPoint]:
    """Process dropping points from API response."""
    if not dp_points:
        return []
    
    processed = []
    for dp in dp_points:
        try:
            processed.append(DroppingPoint(
                dpId=dp.get("dpId", "") or dp.get("dpid", ""),
                dpName=dp.get("dpName", "") or dp.get("dpPoint", ""),
                locatoin=dp.get("locatoin") or dp.get("location"),
                dpTime=dp.get("dpTime") or dp.get("time"),
                contactNumber=dp.get("contactNumber"),
                landmark=dp.get("landmark"),
                latitude=dp.get("latitude"),
                longitude=dp.get("longitude"),
            ))
        except Exception:
            continue
    return processed


def _process_cancellation_policy(cancel_policy_list: List[Dict[str, Any]]) -> List[CancellationPolicy]:
    """Process cancellation policy from API response."""
    if not cancel_policy_list:
        return []
    
    processed = []
    for policy in cancel_policy_list:
        try:
            processed.append(CancellationPolicy(
                timeFrom=policy.get("timeFrom", 0),
                timeTo=policy.get("timeTo", 0),
                percentageCharge=policy.get("percentageCharge", 0.0),
                flatCharge=policy.get("flatCharge", 0),
                isFlat=policy.get("isFlat", False),
            ))
        except Exception:
            continue
    return processed


def _process_single_bus(
    bus: Dict[str, Any],
    source_id: str,
    destination_id: str,
    journey_date: str,
    source_name: str = "",
    destination_name: str = "",
    filter_volvo: Optional[bool] = None,
) -> Optional[BusInfo]:
    """
    Process a single bus from API response.
    
    Handles the new API response format from GetSearchResult.
    """
    is_volvo = bus.get("isVolvo", False)
    if filter_volvo is True and not is_volvo:
        return None

    bus_id = str(bus.get("id", ""))
    
    # Build deeplink to listing page
    book_now = _build_bus_listing_url(
        source_id=source_id,
        destination_id=destination_id,
        journey_date=journey_date,
        source_name=source_name,
        destination_name=destination_name,
    )

    # Process boarding/dropping points
    boarding_points = _process_boarding_points(bus.get("bdPoints", []))
    dropping_points = _process_dropping_points(bus.get("dpPoints", []))
    
    # Process amenities
    amenities = _extract_amenities(bus.get("lstamenities", []))
    
    # Process cancellation policy
    cancellation_policy = _process_cancellation_policy(bus.get("cancelPolicyList", []))

    # Get fares
    fares = bus.get("fares", [])
    if not fares:
        price = bus.get("price", "0")
        fares = [str(price)] if price else ["0"]
    
    # Normalize rating (fix for "45" appearing in UI)
    raw_rating = bus.get("rt") or bus.get("rating")
    normalized_rating = _normalize_rating(raw_rating)

    return BusInfo(
        bus_id=bus_id,
        operator_name=bus.get("Travels", "") or bus.get("travels", ""),
        operator_id=str(bus.get("operatorid", "") or bus.get("OperatorId", "")),
        bus_type=bus.get("busType", "") or bus.get("bustype", ""),
        departure_time=bus.get("departureTime", "") or bus.get("DepartureTime", ""),
        arrival_time=bus.get("ArrivalTime", "") or bus.get("arrivalTime", ""),
        duration=bus.get("duration", "") or bus.get("Duration", ""),
        available_seats=str(bus.get("AvailableSeats", "0") or bus.get("availableSeats", "0")),
        price=str(bus.get("price", "0")),
        fares=fares,
        is_ac=bus.get("AC", False) or bus.get("ac", False),
        is_non_ac=bus.get("nonAC", False) or bus.get("NonAC", False),
        is_volvo=is_volvo,
        is_seater=bus.get("seater", False) or bus.get("Seater", False),
        is_sleeper=bus.get("sleeper", False) or bus.get("Sleeper", False),
        is_semi_sleeper=bus.get("isSemiSleeper", False),
        rating=normalized_rating,
        live_tracking_available=bus.get("liveTrackingAvailable", False),
        is_cancellable=bus.get("isCancellable", False),
        m_ticket_enabled=str(bus.get("mTicketEnabled", "")),
        departure_date=bus.get("departureDate", "") or bus.get("DepartureDate", ""),
        arrival_date=bus.get("arrivalDate", "") or bus.get("ArrivalDate", ""),
        route_id=str(bus.get("routeId", "") or bus.get("routeid", "")),
        engine_id=bus.get("engineId", 0) or bus.get("EngineId", 0),
        trace_id=bus.get("TraceID") or bus.get("traceId"),
        boarding_points=boarding_points,
        dropping_points=dropping_points,
        amenities=amenities,
        cancellation_policy=cancellation_policy,
        book_now=book_now,
    )


def process_bus_results(
    search_response: Dict[str, Any],
    source_id: str,
    destination_id: str,
    journey_date: str,
    source_name: str = "",
    destination_name: str = "",
    filter_volvo: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Process bus search results from the new API.
    
    The new API returns data in Response.AvailableTrips structure.
    """
    buses = []
    
    # Handle new API response structure
    response_data = search_response.get("Response", search_response)
    available_trips = response_data.get("AvailableTrips", [])
    
    # If no trips in Response, try root level
    if not available_trips:
        available_trips = search_response.get("AvailableTrips", [])
    
    if not available_trips:
        return {
            "buses": [],
            "total_count": 0,
            "total_trips": response_data.get("TotalTrips", 0),
            "ac_count": response_data.get("AcCount", 0),
            "non_ac_count": response_data.get("NonAcCount", 0),
            "is_bus_available": False,
        }

    for bus in available_trips:
        processed_bus = _process_single_bus(
            bus,
            source_id,
            destination_id,
            journey_date,
            source_name,
            destination_name,
            filter_volvo,
        )
        if processed_bus:
            buses.append(processed_bus.model_dump())

    return {
        "buses": buses,
        "total_count": len(buses),
        "total_trips": response_data.get("TotalTrips", 0),
        "ac_count": response_data.get("AcCount", 0),
        "non_ac_count": response_data.get("NonAcCount", 0),
        "max_price": response_data.get("MaxPrice"),
        "min_price": response_data.get("MinPrice"),
        "is_bus_available": len(buses) > 0,
    }


# ============================================================================
# MAIN SEARCH FUNCTION
# ============================================================================

async def search_buses(
    source_id: Optional[str] = None,
    destination_id: Optional[str] = None,
    journey_date: str = "",
    is_volvo: Optional[bool] = None,
    source_name: Optional[str] = None,
    destination_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Search for buses using the new EaseMyTrip API.
    
    Supports both city IDs and city names (auto-resolved via autosuggest).
    
    Args:
        source_id: Source city ID (e.g., "733")
        destination_id: Destination city ID (e.g., "757")
        journey_date: Journey date in YYYY-MM-DD format
        is_volvo: Filter for Volvo buses only
        source_name: Source city name (e.g., "Delhi") - will be resolved to ID
        destination_name: Destination city name (e.g., "Manali") - will be resolved to ID
        
    Returns:
        Dict with buses, counts, and metadata
    """
    
    # Resolve city names to IDs if needed
    resolved_source_id = source_id
    resolved_dest_id = destination_id
    resolved_source_name = source_name or ""
    resolved_dest_name = destination_name or ""
    
    # If source_name provided but no source_id, resolve it
    if source_name and not source_id:
        source_info = await get_city_info(source_name)
        if source_info:
            resolved_source_id = source_info.get("id")
            resolved_source_name = source_info.get("name", source_name)
        else:
            return {
                "error": "CITY_NOT_FOUND",
                "message": f"Could not find source city: {source_name}",
                "buses": [],
                "total_count": 0,
                "is_bus_available": False,
            }
    
    # If destination_name provided but no destination_id, resolve it
    if destination_name and not destination_id:
        dest_info = await get_city_info(destination_name)
        if dest_info:
            resolved_dest_id = dest_info.get("id")
            resolved_dest_name = dest_info.get("name", destination_name)
        else:
            return {
                "error": "CITY_NOT_FOUND",
                "message": f"Could not find destination city: {destination_name}",
                "buses": [],
                "total_count": 0,
                "is_bus_available": False,
            }
    
    # Validate we have both IDs
    if not resolved_source_id or not resolved_dest_id:
        return {
            "error": "MISSING_PARAMS",
            "message": "Source and destination city IDs or names are required",
            "buses": [],
            "total_count": 0,
            "is_bus_available": False,
        }
    
    # Convert date to API format (dd-MM-yyyy)
    # api_date = journey_date
    api_date = journey_date

    # Generate session IDs
    sid = _generate_session_id()
    vid = _generate_visitor_id()
    
    # Build payload for new API
    payload = {
        "SourceCityId": resolved_source_id,
        "DestinationCityId": resolved_dest_id,
        "SourceCityName": resolved_source_name,
        "DestinatinCityName": resolved_dest_name,  # Note: API has typo
        "JournyDate": api_date,  # Note: API has typo "JournyDate"
        "Vid": vid,
        "Sid": sid,
        "agentCode": "NAN",
        "agentType": "NAN",
        "CurrencyDomain": "IN",
        "snapApp": "Emt",
        "TravelPolicy": [],
        "isInventory": 0,
    }
    
    try:
        client = BusApiClient()
        data = await client.search(payload)
        
        if "error" in data:
            return {
                "error": "API_ERROR",
                "message": data.get("error", "Unknown error"),
                "buses": [],
                "total_count": 0,
                "is_bus_available": False,
            }
                
    except Exception as e:
        return {
            "error": "API_ERROR",
            "message": str(e),
            "buses": [],
            "total_count": 0,
            "is_bus_available": False,
        }
    
    # Process results
    processed_data = process_bus_results(
        data,
        resolved_source_id,
        resolved_dest_id,
        journey_date,
        resolved_source_name,
        resolved_dest_name,
        is_volvo,
    )
    
    # Add metadata
    processed_data["source_id"] = resolved_source_id
    processed_data["destination_id"] = resolved_dest_id
    processed_data["source_name"] = resolved_source_name
    processed_data["destination_name"] = resolved_dest_name
    processed_data["journey_date"] = journey_date
    processed_data["filter_volvo"] = is_volvo
    processed_data["session_id"] = sid
    processed_data["visitor_id"] = vid
    
    # Build View All link
    processed_data["view_all_link"] = _build_bus_listing_url(
        source_id=resolved_source_id,
        destination_id=resolved_dest_id,
        journey_date=journey_date,
        source_name=resolved_source_name,
        destination_name=resolved_dest_name,
    )
    
    return processed_data


# ============================================================================
# WHATSAPP RESPONSE BUILDER
# ============================================================================

def extract_bus_summary(bus: Dict[str, Any]) -> Dict[str, Any]:
    """Extract summary information from a bus for WhatsApp response."""
    
    fares = bus.get("fares", [])
    
    cheapest_fare = None
    for fare in fares:
        try:
            fare_val = float(fare)
            if cheapest_fare is None or fare_val < cheapest_fare:
                cheapest_fare = fare_val
        except (ValueError, TypeError):
            continue

    if cheapest_fare is None:
        try:
            cheapest_fare = float(bus.get("price", 0))
        except (ValueError, TypeError):
            cheapest_fare = 0

    boarding_points = bus.get("boarding_points", [])
    dropping_points = bus.get("dropping_points", [])
    
    first_boarding = ""
    if boarding_points:
        first_boarding = boarding_points[0].get("bd_long_name", "") or boarding_points[0].get("bd_point", "")
    
    first_dropping = ""
    if dropping_points:
        first_dropping = dropping_points[0].get("dp_name", "")

    return {
        "bus_id": bus.get("bus_id"),
        "operator_name": bus.get("operator_name"),
        "bus_type": bus.get("bus_type"),
        "departure_time": bus.get("departure_time"),
        "arrival_time": bus.get("arrival_time"),
        "duration": bus.get("duration"),
        "available_seats": bus.get("available_seats"),
        "cheapest_fare": cheapest_fare,
        "is_ac": bus.get("is_ac"),
        "is_volvo": bus.get("is_volvo"),
        "rating": bus.get("rating"),
        "live_tracking": bus.get("live_tracking_available"),
        "is_cancellable": bus.get("is_cancellable"),
        "first_boarding_point": first_boarding,
        "first_dropping_point": first_dropping,
        "amenities_count": len(bus.get("amenities", [])),
        "book_now": bus.get("book_now"),
    }


def build_whatsapp_bus_response(
    payload: BusSearchInput,
    bus_results: Dict[str, Any],
) -> WhatsappBusFinalResponse:
    """Build WhatsApp response format for bus search results."""
    
    options = []

    for idx, bus in enumerate(bus_results.get("buses", []), start=1):
        summary = extract_bus_summary(bus)

        options.append({
            "option_id": idx,
            "bus_id": summary["bus_id"],
            "operator_name": summary["operator_name"],
            "bus_type": summary["bus_type"],
            "departure_time": summary["departure_time"],
            "arrival_time": summary["arrival_time"],
            "duration": summary["duration"],
            "date": payload.journey_date,
            "available_seats": summary["available_seats"],
            "fare": summary["cheapest_fare"],
            "is_ac": summary["is_ac"],
            "is_volvo": summary["is_volvo"],
            "rating": summary["rating"],
            "boarding_point": summary["first_boarding_point"],
            "dropping_point": summary["first_dropping_point"],
            "amenities_count": summary["amenities_count"],
            "book_now": summary["book_now"],
        })

    source_display = bus_results.get("source_name") or payload.source_id or payload.source_name
    dest_display = bus_results.get("destination_name") or payload.destination_id or payload.destination_name

    whatsapp_json = WhatsappBusFormat(
        options=options,
        currency="INR",
        view_all_buses_url=bus_results.get("view_all_link", ""),
    )

    return WhatsappBusFinalResponse(
        response_text=f"Found {len(options)} buses from {source_display} to {dest_display}",
        whatsapp_json=whatsapp_json,
    )


# ============================================================================
# SEAT LAYOUT FUNCTIONS
# ============================================================================

def _process_seat(seat: Dict[str, Any], deck_name: str) -> Optional[Dict[str, Any]]:
    """Process a single seat from the new SeatBind API response."""
    
    if not seat:
        return None
    
    # Determine availability from seatType or available field
    seat_type = seat.get("seatType", "") or seat.get("SeatType", "")
    is_available = seat.get("available", False)
    
    # Check seat status from seatType
    seat_type_lower = str(seat_type).lower()
    is_booked = "unavailable" in seat_type_lower or "booked" in seat_type_lower
    is_ladies = "ladies" in seat_type_lower or "female" in seat_type_lower
    is_blocked = "blocked" in seat_type_lower
    
    if not is_booked:
        is_available = seat.get("available", True)
    
    seat_number = str(seat.get("name", "") or seat.get("id", "") or seat.get("seatNumber", ""))
    seat_name = seat_number
    
    fare = str(seat.get("fare", "0") or seat.get("baseFare", "0"))
    
    row = int(seat.get("rowNo", 0) or seat.get("row", 0))
    column = int(seat.get("columnNo", 0) or seat.get("column", 0))
    
    # Determine if sleeper
    seat_style = seat.get("seatStyle", "") or seat.get("SeatStyle", "")
    is_sleeper = seat.get("isSleeper", False) or seat_style.upper() in ["SL", "SLEEPER"]
    
    return {
        "seat_number": seat_number,
        "seat_name": seat_name,
        "seat_type": seat_style or "ST",
        "seat_status": seat_type,
        "is_available": is_available and not is_booked,
        "is_ladies": is_ladies,
        "fare": fare,
        "row": row,
        "column": column,
        "deck": deck_name,
        "width": int(seat.get("width", 1)),
        "length": int(seat.get("length", 1)),
        "is_booked": is_booked,
        "is_blocked": is_blocked,
        "gender": seat.get("gender"),
        "encrypted_seat": seat.get("EncriSeat"),
    }


def _process_deck(deck_data: Any, deck_name: str) -> Optional[Dict[str, Any]]:
    """Process deck data from API response."""
    
    if not deck_data:
        return None
    
    if isinstance(deck_data, dict):
        deck_data = deck_data.get("seats") or deck_data.get("Seats") or []
    
    if not isinstance(deck_data, list) or not deck_data:
        return None
    
    seats = []
    max_row = 0
    max_col = 0
    
    for seat in deck_data:
        if not isinstance(seat, dict):
            continue
        processed = _process_seat(seat, deck_name)
        if processed:
            seats.append(processed)
            max_row = max(max_row, processed["row"])
            max_col = max(max_col, processed["column"])
    
    if not seats:
        return None
    
    return {
        "deck_name": deck_name,
        "rows": max_row + 1,
        "columns": max_col + 1,
        "seats": seats,
    }


def process_seat_layout_response(
    api_response: Dict[str, Any],
    bus_id: str,
    boarding_point: str,
    dropping_point: str,
    operator_name: str = "",
    bus_type: str = "",
) -> Dict[str, Any]:
    """
    Process seat layout from the new SeatBind API response.
    
    The new API returns seats in a flat "Seats" array with lowerShow/upperShow flags.
    """
    
    if not api_response:
        return {
            "success": False,
            "message": "Empty API response",
            "layout": None,
            "raw_response": api_response,
        }
    
    # Get seats from response
    seats = api_response.get("Seats", []) or api_response.get("seats", [])
    
    if not seats:
        return {
            "success": False,
            "message": "No seat layout available for this bus",
            "layout": None,
            "raw_response": api_response,
        }
    
    # Separate lower and upper deck seats
    lower_seats = [s for s in seats if s.get("lowerShow", True)]
    upper_seats = [s for s in seats if s.get("upperShow", False)]
    
    lower_deck = _process_deck(lower_seats, "Lower") if lower_seats else None
    upper_deck = _process_deck(upper_seats, "Upper") if upper_seats else None
    
    # If no deck separation, treat all as lower
    if not lower_deck and not upper_deck and seats:
        lower_deck = _process_deck(seats, "Lower")
    
    # Calculate stats
    all_seats = []
    if lower_deck and lower_deck.get("seats"):
        all_seats.extend(lower_deck["seats"])
    if upper_deck and upper_deck.get("seats"):
        all_seats.extend(upper_deck["seats"])
    
    total_seats = len(all_seats)
    available_seats = sum(1 for s in all_seats if s.get("is_available"))
    booked_seats = sum(1 for s in all_seats if s.get("is_booked"))
    
    # Get operator/bus info from response
    travel_name = (
        api_response.get("TravelName") or
        api_response.get("travel") or
        operator_name
    )
    bus_type_resp = (
        api_response.get("_bustype") or
        api_response.get("bustype") or
        bus_type
    )
    
    layout_info = {
        "bus_id": bus_id,
        "bus_type": bus_type_resp,
        "operator_name": travel_name,
        "total_seats": total_seats,
        "available_seats": available_seats,
        "booked_seats": booked_seats,
        "lower_deck": lower_deck,
        "upper_deck": upper_deck,
        "boarding_point": boarding_point,
        "dropping_point": dropping_point,
        "boarding_time": api_response.get("deptTime", ""),
        "dropping_time": api_response.get("arrTime", ""),
        "fare_details": [],
    }
    
    success = total_seats > 0
    
    if success:
        message = f"Found {available_seats} available seats out of {total_seats}"
    else:
        message = "Seat layout not available for this bus"
    
    return {
        "success": success,
        "message": message,
        "layout": layout_info,
        "raw_response": api_response,
    }


async def get_seat_layout(
    source_id: str,
    destination_id: str,
    journey_date: str,
    bus_id: str,
    route_id: str,
    engine_id: int,
    boarding_point_id: str,
    dropping_point_id: str,
    source_name: str = "",
    destination_name: str = "",
    operator_id: str = "",
    operator_name: str = "",
    bus_type: str = "",
    departure_time: str = "",
    arrival_time: str = "",
    duration: str = "",
    trace_id: str = "",
    is_seater: bool = True,
    is_sleeper: bool = True,
    session_id: str = "",
    visitor_id: str = "",
) -> Dict[str, Any]:
    """
    Get seat layout from the new SeatBind API.
    
    Uses the new endpoint: https://bus.easemytrip.com/Home/SeatBind/
    """
    
    # Convert date to API format
    api_date = journey_date
    
    # Generate session IDs if not provided
    sid = session_id or _generate_session_id()
    vid = visitor_id or _generate_visitor_id()
    
    # Build search request string
    search_req = f"{source_id}|{destination_id}|{source_name}|{destination_name}|{api_date}"
    
    # Build payload for new SeatBind API
    payload = {
        "id": bus_id,
        "engineId": engine_id,
        "routeid": route_id,
        "JourneyDate": api_date,
        "OperatorId": operator_id,
        "Sid": sid,
        "Vid": vid,
        "TraceID": trace_id or str(uuid.uuid4()),
        "agentType": "NAN",
        "bpId": boarding_point_id,
        "dpId": dropping_point_id,
        "bustype": bus_type,
        "travel": operator_name,
        "DepartureTime": departure_time,
        "ArrivalTime": arrival_time,
        "duration": duration,
        "seater": is_seater,
        "sleeper": is_sleeper,
        "sessionId": None,
        "Idproof": 0,
        "SeatPrice": 0,
        "isBpdp": False,
        "stStatus": False,
        "countryCode": None,
        "searchReq": search_req,
    }
    
    try:
        client = BusApiClient()
        data = await client.get_seat_layout(payload)
        
        if "error" in data:
            return {
                "success": False,
                "message": data.get("error", "Unknown error"),
                "layout": None,
                "raw_response": None,
            }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"API Error: {str(e)}",
            "layout": None,
            "raw_response": None,
        }
    
    return process_seat_layout_response(
        data,
        bus_id,
        boarding_point_id,
        dropping_point_id,
        operator_name,
        bus_type,
    )