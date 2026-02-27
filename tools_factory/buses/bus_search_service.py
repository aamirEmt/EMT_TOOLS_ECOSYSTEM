import base64
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
import re
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

from emt_client.clients.bus_client import BusApiClient

from emt_client.config import (
    BUS_SEARCH_URL,
    BUS_SEAT_BIND_URL as SEAT_BIND_URL,
    BUS_DEEPLINK_BASE,
    BUS_AUTOSUGGEST_URL,
    BUS_AUTOSUGGEST_KEY,
    BUS_ENCRYPTED_HEADER,
    BUS_DECRYPTION_KEY,
    BUS_CONFIRM_SEATS_URL,
    BUS_PAYMENT_URL,
)

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


def encrypt_v1(plain_text: str) -> str:

    AES, pad, unpad = _get_cipher()
    
    key = BUS_DECRYPTION_KEY.encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, iv=key)
    padded_data = pad(plain_text.encode("utf-8"), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted_bytes).decode("utf-8")


def decrypt_v1(cipher_text: str) -> str:

    AES, pad, unpad = _get_cipher()
    
    key = BUS_DECRYPTION_KEY.encode("utf-8")
    encrypted_bytes = base64.b64decode(cipher_text)
    cipher = AES.new(key, AES.MODE_CBC, iv=key)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    return unpad(decrypted_bytes, AES.block_size).decode("utf-8")

async def get_city_suggestions(
    city_prefix: str,
    country_code: str = "IN",
) -> List[Dict[str, Any]]:

    json_string = {
        "userName": "",
        "password": "",
        "Prefix": city_prefix,
        "country_code": country_code,
    }
    
    encrypted_request = encrypt_v1(json.dumps(json_string))
    
    api_payload = {
        "request": encrypted_request,
        "isIOS": False,
        "ip": "49.249.40.58",
        "encryptedHeader": BUS_ENCRYPTED_HEADER,
    }
    
    try:
        client = BusApiClient()
        encrypted_response = await client.get_city_suggestions(api_payload)
        
        decrypted_response = decrypt_v1(encrypted_response)
        data = json.loads(decrypted_response)
        
        return data.get("list", [])
                
    except Exception as e:
        print(f"Error fetching city suggestions: {e}")
        return []


async def get_city_id(city_name: str, country_code: str = "IN") -> Optional[str]:

    suggestions = await get_city_suggestions(city_name, country_code)
    
    if not suggestions:
        return None
    
    city_name_lower = city_name.lower().strip()
    for suggestion in suggestions:
        if suggestion.get("name", "").lower().strip() == city_name_lower:
            return suggestion.get("id")
    
    return suggestions[0].get("id") if suggestions else None


async def get_city_info(city_name: str, country_code: str = "IN") -> Optional[Dict[str, Any]]:

    suggestions = await get_city_suggestions(city_name, country_code)
    
    if not suggestions:
        return None
    
    city_name_lower = city_name.lower().strip()
    for suggestion in suggestions:
        if suggestion.get("name", "").lower().strip() == city_name_lower:
            return suggestion
    
    return suggestions[0] if suggestions else None


async def resolve_city_names_to_ids(
    source_city: str,
    destination_city: str,
    country_code: str = "IN",
) -> Dict[str, Any]:

    result = {
        "source_id": None,
        "source_name": None,
        "destination_id": None,
        "destination_name": None,
        "error": None,
    }
    
    if source_city.isdigit():
        result["source_id"] = source_city
        result["source_name"] = source_city  
    else:
        source_info = await get_city_info(source_city, country_code)
        if source_info:
            result["source_id"] = source_info.get("id")
            result["source_name"] = source_info.get("name")
        else:
            result["error"] = f"Could not find city: {source_city}"
            return result
    
    if destination_city.isdigit():
        result["destination_id"] = destination_city
        result["destination_name"] = destination_city  
    else:
        dest_info = await get_city_info(destination_city, country_code)
        if dest_info:
            result["destination_id"] = dest_info.get("id")
            result["destination_name"] = dest_info.get("name")
        else:
            result["error"] = f"Could not find city: {destination_city}"
            return result
    
    return result


def get_city_id_sync(city_name: str, country_code: str = "IN") -> Optional[str]:
    import asyncio
    return asyncio.run(get_city_id(city_name, country_code))


def get_city_suggestions_sync(city_prefix: str, country_code: str = "IN") -> List[Dict[str, Any]]:
    import asyncio
    return asyncio.run(get_city_suggestions(city_prefix, country_code))


def _generate_session_id() -> str:
    return uuid.uuid4().hex


def _generate_visitor_id() -> str:
    return uuid.uuid4().hex



def _normalize_rating(rating_value: Any) -> Optional[str]:

    if rating_value is None or rating_value == "" or rating_value == 0:
        return None
    
    try:
        rating_float = float(rating_value)
        
        if rating_float > 5:
            rating_float = rating_float / 10
        
        if rating_float < 0 or rating_float > 5:
            return None
        
        if rating_float == 0:
            return None
        
        if rating_float == int(rating_float):
            return str(int(rating_float))
        return f"{rating_float:.1f}"
        
    except (ValueError, TypeError):
        return None

def _clean_point_name(name: str) -> str:

    if not name:
        return ""
    cleaned = re.sub(r'^\d{10}\s+', '', name.strip())
    return cleaned


def _parse_time_to_minutes(time_str: str) -> Optional[int]:

    if not time_str:
        return None
    try:
        time_str = str(time_str).strip()
        if ":" in time_str:
            parts = time_str.split(":")
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            return hours * 60 + minutes
        digits = ''.join(filter(str.isdigit, time_str))
        if len(digits) >= 3:
            hours = int(digits[:-2])
            minutes = int(digits[-2:])
            return hours * 60 + minutes
        return None
    except (ValueError, TypeError):
        return None


def _build_bus_listing_url(
    source_id: str,
    destination_id: str,
    journey_date: str,
    source_name: str = "",
    destination_name: str = "",
) -> str:

    org_name = source_name or source_id
    des_name = destination_name or destination_id
    
    return (
        f"{BUS_DEEPLINK_BASE}"
        f"?org={org_name}&des={des_name}&date={journey_date}"
        f"&searchid={source_id}_{destination_id}&CCode=IN&AppCode=Emt"
    )


def _extract_amenities(lst_amenities: List[Dict[str, Any]]) -> List[str]:
    if not lst_amenities:
        return []
    return [amenity.get("name", "") for amenity in lst_amenities if amenity.get("name")]


def _process_boarding_points(bd_points: List[Dict[str, Any]]) -> List[BoardingPoint]:
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
    filter_ac: Optional[bool] = None,
    filter_seater: Optional[bool] = None,
    filter_sleeper: Optional[bool] = None,
    filter_departure_from: Optional[str] = None,
    filter_departure_to: Optional[str] = None,
) -> Optional[BusInfo]:

    is_volvo = bus.get("isVolvo", False)
    if filter_volvo is True and not is_volvo:
        return None

    bus_is_ac = bus.get("AC", False)
    bus_is_non_ac = bus.get("nonAC", False)
    if filter_ac is True and not bus_is_ac:
        return None
    if filter_ac is False and not bus_is_non_ac:
        return None

    bus_is_seater = bus.get("seater", False)
    if filter_seater is True and not bus_is_seater:
        return None

    bus_is_sleeper = bus.get("sleeper", False)
    if filter_sleeper is True and not bus_is_sleeper:
        return None
    
    bus_departure_time = bus.get("departureTime", "") or bus.get("DepartureTime", "")
    bus_departure_minutes = _parse_time_to_minutes(bus_departure_time)
    
    if bus_departure_minutes is not None:
        from_minutes = _parse_time_to_minutes(filter_departure_from) if filter_departure_from else None
        to_minutes = _parse_time_to_minutes(filter_departure_to) if filter_departure_to else None
        
        if from_minutes is not None and to_minutes is not None:
            if from_minutes > to_minutes:
                if not (bus_departure_minutes >= from_minutes or bus_departure_minutes < to_minutes):
                    return None
            else:
                if bus_departure_minutes < from_minutes or bus_departure_minutes >= to_minutes:
                    return None
        elif from_minutes is not None:
            if bus_departure_minutes < from_minutes:
                return None
        elif to_minutes is not None:
            if bus_departure_minutes >= to_minutes:
                return None

    bus_id = str(bus.get("id", ""))
    
    book_now = _build_bus_listing_url(
        source_id=source_id,
        destination_id=destination_id,
        journey_date=journey_date,
        source_name=source_name,
        destination_name=destination_name,
    )

    boarding_points = _process_boarding_points(bus.get("bdPoints", []))
    dropping_points = _process_dropping_points(bus.get("dpPoints", []))
    
    amenities = _extract_amenities(bus.get("lstamenities", []))
    
    cancellation_policy = _process_cancellation_policy(bus.get("cancelPolicyList", []))

    fares = bus.get("fares", [])
    if not fares:
        price = bus.get("price", "0")
        fares = [str(price)] if price else ["0"]
    
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
    filter_ac: Optional[bool] = None,
    filter_seater: Optional[bool] = None,
    filter_sleeper: Optional[bool] = None,
    filter_departure_from: Optional[str] = None,
    filter_departure_to: Optional[str] = None,
) -> Dict[str, Any]:

    buses = []
    
    response_data = search_response.get("Response", search_response)
    available_trips = response_data.get("AvailableTrips", [])
    
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
            filter_ac,
            filter_seater,
            filter_sleeper,
            filter_departure_from,
            filter_departure_to,
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


async def search_buses(
    source_id: Optional[str] = None,
    destination_id: Optional[str] = None,
    journey_date: str = "",
    is_volvo: Optional[bool] = None,
    is_ac: Optional[bool] = None,
    is_seater: Optional[bool] = None,
    is_sleeper: Optional[bool] = None,
    source_name: Optional[str] = None,
    destination_name: Optional[str] = None,
    departure_time_from: Optional[str] = None,
    departure_time_to: Optional[str] = None,
) -> Dict[str, Any]:

    resolved_source_id = source_id
    resolved_dest_id = destination_id
    resolved_source_name = source_name or ""
    resolved_dest_name = destination_name or ""
    
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
    
    if not resolved_source_id or not resolved_dest_id:
        return {
            "error": "MISSING_PARAMS",
            "message": "Source and destination city IDs or names are required",
            "buses": [],
            "total_count": 0,
            "is_bus_available": False,
        }
    
    api_date = journey_date

    sid = _generate_session_id()
    vid = _generate_visitor_id()
    
    payload = {
        "SourceCityId": resolved_source_id,
        "DestinationCityId": resolved_dest_id,
        "SourceCityName": resolved_source_name,
        "DestinatinCityName": resolved_dest_name,  
        "JournyDate": api_date,  
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
    
    processed_data = process_bus_results(
        data,
        resolved_source_id,
        resolved_dest_id,
        journey_date,
        resolved_source_name,
        resolved_dest_name,
        is_volvo,
        is_ac,
        is_seater,
        is_sleeper,
        departure_time_from,
        departure_time_to,
    )
    
    processed_data["source_id"] = resolved_source_id
    processed_data["destination_id"] = resolved_dest_id
    processed_data["source_name"] = resolved_source_name
    processed_data["destination_name"] = resolved_dest_name
    processed_data["journey_date"] = journey_date
    processed_data["filter_volvo"] = is_volvo
    processed_data["session_id"] = sid
    processed_data["visitor_id"] = vid
    
    processed_data["view_all_link"] = _build_bus_listing_url(
        source_id=resolved_source_id,
        destination_id=resolved_dest_id,
        journey_date=journey_date,
        source_name=resolved_source_name,
        destination_name=resolved_dest_name,
    )
    
    return processed_data

def extract_bus_summary(bus: Dict[str, Any]) -> Dict[str, Any]:
    actual_price = None
    
    try:
        price_val = bus.get("price")
        if price_val is not None and price_val != "" and price_val != "0":
            actual_price = float(price_val)
    except (ValueError, TypeError):
        pass
    
    if actual_price is None:
        fares = bus.get("fares", [])
        for fare in fares:
            try:
                fare_val = float(fare)
                if actual_price is None or fare_val < actual_price:
                    actual_price = fare_val
            except (ValueError, TypeError):
                continue
    
    if actual_price is None:
        actual_price = 0

    boarding_points = bus.get("boarding_points", [])
    dropping_points = bus.get("dropping_points", [])
    
    all_boarding_names = []
    for bp in boarding_points:
        bp_name = bp.get("bd_long_name", "") or bp.get("bd_point", "")
        if bp_name:
            all_boarding_names.append(_clean_point_name(bp_name))
    boarding_point_str = ", ".join(all_boarding_names) if all_boarding_names else ""
    
    all_dropping_names = []
    for dp in dropping_points:
        dp_name = dp.get("dp_name", "")
        if dp_name:
            all_dropping_names.append(_clean_point_name(dp_name))
    dropping_point_str = ", ".join(all_dropping_names) if all_dropping_names else ""

    return {
        "bus_id": bus.get("bus_id"),
        "operator_name": bus.get("operator_name"),
        "bus_type": bus.get("bus_type"),
        "departure_time": bus.get("departure_time"),
        "arrival_time": bus.get("arrival_time"),
        "duration": bus.get("duration"),
        "available_seats": bus.get("available_seats"),
        "cheapest_fare": actual_price,
        "is_ac": bus.get("is_ac"),
        "is_non_ac": bus.get("is_non_ac"),
        "is_seater": bus.get("is_seater"),
        "is_sleeper": bus.get("is_sleeper"),
        "is_volvo": bus.get("is_volvo"),
        "rating": bus.get("rating"),
        "live_tracking": bus.get("live_tracking_available"),
        "is_cancellable": bus.get("is_cancellable"),
        "boarding_point_str": boarding_point_str,
        "dropping_point_str": dropping_point_str,
        "amenities_count": len(bus.get("amenities", [])),
        "book_now": bus.get("book_now"),
    }


def build_whatsapp_bus_response(
    payload: BusSearchInput,
    bus_results: Dict[str, Any],
) -> WhatsappBusFinalResponse:
    
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
            "is_non_ac": summary["is_non_ac"],
            "is_seater": summary["is_seater"],
            "is_sleeper": summary["is_sleeper"],
            "is_volvo": summary["is_volvo"],
            "rating": summary["rating"],
            "boarding_point": summary["boarding_point_str"],
            "dropping_point": summary["dropping_point_str"],
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


def _process_seat(seat: Dict[str, Any], deck_name: str) -> Optional[Dict[str, Any]]:
    
    if not seat:
        return None
    
    seat_type = seat.get("seatType", "") or seat.get("SeatType", "")
    is_available = seat.get("available", False)
    
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
    
    if not api_response:
        return {
            "success": False,
            "message": "Empty API response",
            "layout": None,
            "raw_response": api_response,
        }
    
    seats = api_response.get("Seats", []) or api_response.get("seats", [])
    
    if not seats:
        return {
            "success": False,
            "message": "No seat layout available for this bus",
            "layout": None,
            "raw_response": api_response,
        }
    
    lower_seats = [s for s in seats if s.get("lowerShow", True)]
    upper_seats = [s for s in seats if s.get("upperShow", False)]
    
    lower_deck = _process_deck(lower_seats, "Lower") if lower_seats else None
    upper_deck = _process_deck(upper_seats, "Upper") if upper_seats else None
    
    if not lower_deck and not upper_deck and seats:
        lower_deck = _process_deck(seats, "Lower")
    
    all_seats = []
    if lower_deck and lower_deck.get("seats"):
        all_seats.extend(lower_deck["seats"])
    if upper_deck and upper_deck.get("seats"):
        all_seats.extend(upper_deck["seats"])
    
    total_seats = len(all_seats)
    available_seats = sum(1 for s in all_seats if s.get("is_available"))
    booked_seats = sum(1 for s in all_seats if s.get("is_booked"))
    
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
    
    api_date = journey_date
    
    sid = session_id or _generate_session_id()
    vid = visitor_id or _generate_visitor_id()
    
    search_req = f"{source_id}|{destination_id}|{source_name}|{destination_name}|{api_date}"
    
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

async def confirm_seats(
    available_trip_id: str,
    engine_id: int,
    route_id: str,
    operator_id: str,
    source: str,
    destination: str,
    bus_operator: str,
    bus_type: str,
    departure_time: str,
    arrival_time: str,
    seats: List[Dict[str, Any]],
    boarding_id: str,
    boarding_point: Dict[str, Any],
    drop_id: str,
    dropping_point: Dict[str, Any],
    session_id: str = "",
    sid: str = "",
    vid: str = "",
    trace_id: str = "",
    total_fare: float = 0,
    discount: float = 0,
    coupon_code: str = "",
    cancel_policy_list: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    
    if not sid:
        sid = _generate_session_id()
    if not vid:
        vid = _generate_visitor_id()
    if not trace_id:
        trace_id = str(uuid.uuid4())
    
    payload = {
        "seats": seats,
        "sessionId": session_id,
        "totalFare": total_fare,
        "boardingId": boarding_id,
        "boardingName": boarding_point.get("bdLongName", "") or boarding_point.get("bdPoint", ""),
        "boardingPoint": boarding_point,
        "dropId": drop_id,
        "DropingPoint": dropping_point,
        "availableTripId": available_trip_id,
        "source": source,
        "destination": destination,
        "busOperator": bus_operator,
        "busType": bus_type,
        "routeId": route_id,
        "engineId": engine_id,
        "operator_id": operator_id,
        "DepTime": departure_time,
        "arrivalDate": arrival_time,
        "departureDate": None,
        "Discount": discount,
        "CashBack": 0,
        "serviceFee": 0,
        "STF": 0,
        "TDS": 0,
        "cpnCode": coupon_code,
        "agentCode": "",
        "agentType": "",
        "agentMarkUp": 0,
        "agentACBalance": 0,
        "Sid": sid,
        "Vid": vid,
        "TraceId": trace_id,
        "cancelPolicyList": cancel_policy_list or [],
    }
    
    try:
        client = BusApiClient()
        data = await client.confirm_seats(payload)
        
        if "error" in data:
            return {
                "success": False,
                "message": data.get("error", "Unknown error"),
                "payment_url": None,
            }
        
        payment_url = f"{BUS_PAYMENT_URL}?userid=Emt"
        
        return {
            "success": True,
            "message": "Seats confirmed successfully",
            "payment_url": payment_url,
            "confirmation_data": data,
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"API Error: {str(e)}",
            "payment_url": None,
        }


def build_seat_bind_payload(
    bus_data: Dict[str, Any],
    source_id: str,
    destination_id: str,
    source_name: str,
    destination_name: str,
    journey_date: str,
    session_id: str = "",
    visitor_id: str = "",
) -> Dict[str, Any]:

    bus_id = bus_data.get("bus_id", "")
    route_id = bus_data.get("route_id", "")
    engine_id = bus_data.get("engine_id", 0)
    operator_id = bus_data.get("operator_id", "")
    operator_name = bus_data.get("operator_name", "")
    bus_type = bus_data.get("bus_type", "")
    departure_time = bus_data.get("departure_time", "")
    arrival_time = bus_data.get("arrival_time", "")
    duration = bus_data.get("duration", "")
    is_seater = bus_data.get("is_seater", True)
    is_sleeper = bus_data.get("is_sleeper", True)
    trace_id = bus_data.get("trace_id", "") or str(uuid.uuid4())
    
    sid = session_id or _generate_session_id()
    vid = visitor_id or _generate_visitor_id()
    
    search_req = f"{source_id}|{destination_id}|{source_name}|{destination_name}|{journey_date}"
    
    return {
        "id": bus_id,
        "engineId": engine_id,
        "routeid": route_id,
        "JourneyDate": journey_date,
        "OperatorId": operator_id,
        "Sid": sid,
        "Vid": vid,
        "TraceID": trace_id,
        "agentType": "NAN",
        "bpId": "",
        "dpId": "",
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