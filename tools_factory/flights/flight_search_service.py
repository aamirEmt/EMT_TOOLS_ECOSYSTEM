"""Flight Search API Logic.

This module handles all flight search operations including:
- Searching flights via EaseMyTrip API
- Processing flight results
- Processing individual flight segments
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote
from emt_client.clients.flight_client import FlightApiClient
from emt_client.utils import gen_trace_id
from emt_client.config import FLIGHT_BASE_URL, FLIGHT_DEEPLINK


def _normalize_cabin(cabin: str) -> str:
    """Convert cabin codes into a readable label."""
    if not cabin:
        return ""
    cabin_code_map = {
        "E": "Economy",
        "Y": "Economy",
        "W": "Premium Economy",
        "S": "Premium Economy",
        "C": "Business",
        "J": "Business",
        "F": "First",
        "P": "First",
    }
    upper_value = cabin.strip().upper()
    if upper_value in cabin_code_map:
        return cabin_code_map[upper_value]
    return cabin.title()


def _parse_date_to_iso(raw_date: str, fallback: Optional[str] = None) -> str:
    """Parse various EMT date formats into YYYY-MM-DD."""
    if not raw_date:
        return fallback or ""

    for fmt in ("%Y-%m-%d", "%a-%d%b%Y", "%d-%b-%Y", "%d%b%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw_date.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return fallback or raw_date


def _clean_time(raw_time: str) -> str:
    """Remove separators from time values (e.g., 06:00 -> 0600)."""
    if not raw_time:
        return ""
    return "".join(ch for ch in str(raw_time) if ch.isdigit())


def _build_segment_strings(
    legs: List[Dict[str, Any]],
    default_departure: Optional[str],
) -> List[str]:
    """Build SegmentN strings for each flight leg."""
    segments: List[str] = []

    for idx, leg in enumerate(legs, start=1):
        dep_date = _parse_date_to_iso(leg.get("departure_date", ""), default_departure)
        arr_date = _parse_date_to_iso(
            leg.get("arrival_date", ""), dep_date or default_departure
        )

        dep_time = _clean_time(leg.get("departure_time", ""))
        arr_time = _clean_time(leg.get("arrival_time", ""))

        booking_code = (
            leg.get("booking_code")
            or leg.get("fare_class")
            or leg.get("cabin")
            or ""
        )
        cabin_label = _normalize_cabin(
            leg.get("cabin") or leg.get("cabin_class") or ""
        )

        segment_parts = [
            f"Origin={leg.get('origin', '')}",
            f"BookingCode={booking_code}",
            f"Destination={leg.get('destination', '')}",
            f"FlightNumber={leg.get('flight_number', '')}",
            f"Carrier={leg.get('airline_code', '')}",
        ]

        departure_base = dep_date or default_departure
        if departure_base:
            departure_value = f"{departure_base}T{dep_time}" if dep_time else departure_base
            segment_parts.append(f"DepartureDate={departure_value}")

        segment_parts.append(f"id={idx}")

        if cabin_label:
            segment_parts.append(f"Cabin={cabin_label}")

        if arr_date:
            arrival_value = f"{arr_date}T{arr_time}" if arr_time else arr_date
            segment_parts.append(f"ArrivalDate={arrival_value}")

        segments.append(",".join(filter(None, segment_parts)))

    return segments


def build_deep_link(
    *,
    flight: Dict[str, Any],
    passengers: Dict[str, int],
    trip_type: str,
    default_departure: Optional[str] = None,
) -> Dict[str, str]:
    """Create the EMT flight deep-link using flight legs and fare data."""
    legs: List[Dict[str, Any]] = flight.get("legs") or []
    if not legs:
        return {"deepLink": FLIGHT_DEEPLINK}

    first_leg = legs[0]
    last_leg = legs[-1]

    cabin_label = _normalize_cabin(first_leg.get("cabin", ""))
    booking_code = first_leg.get("booking_code") or first_leg.get("fare_class", "")
    flight_number = first_leg.get("flight_number", "")

    primary_departure = _parse_date_to_iso(
        first_leg.get("departure_date", ""),
        default_departure,
    )

    fare_options = flight.get("fare_options") or []
    cheapest_fare = fare_options[0] if fare_options else {}
    fare_value_raw = cheapest_fare.get("total_fare") or cheapest_fare.get("base_fare")
    try:
        fare_value = float(fare_value_raw) if fare_value_raw is not None else None
    except (TypeError, ValueError):
        fare_value = None

    params: List[tuple[str, str]] = [
        ("Adult", str(passengers.get("adults", 1))),
        ("Child", str(passengers.get("children", 0))),
        ("Infant", str(passengers.get("infants", 0))),
        ("ReferralId", "UserID"),
        ("UserLanguage", "en"),
        ("DisplayedPriceCurrency", "INR"),
        ("UserCurrency", "INR"),
        ("DisplayedPrice", f"{fare_value:.2f}" if fare_value is not None else ""),
        ("PointOfSaleCountry", "IN"),
        ("TripType", trip_type),
        ("Origin1", first_leg.get("origin", "")),
        ("Destination1", last_leg.get("destination", "")),
        ("DepartureDate1", primary_departure),
    ]

    if cabin_label:
        params.append(("Cabin1", cabin_label))
    if booking_code:
        params.append(("BookingCode1", booking_code))
    if flight_number:
        params.append(("FlightNumber1", flight_number))

    params.append(("cc", ""))

    slice_value = ",".join(str(i) for i in range(1, len(legs) + 1))
    if slice_value:
        params.append(("Slice1", slice_value))

    segment_strings = _build_segment_strings(legs, primary_departure)

    query_parts: List[str] = [
        f"{key}={quote(str(value), safe='')}" for key, value in params if value is not None
    ]
    for idx, segment in enumerate(segment_strings, start=1):
        if not segment:
            continue
        query_parts.append(
            f"Segment{idx}={quote(segment, safe='=,:-T')}"
        )

    deep_link = (
        f"{FLIGHT_DEEPLINK}?{'&'.join(query_parts)}" if query_parts else FLIGHT_DEEPLINK
    )

    return {"deepLink": deep_link}

async def search_flights(
    origin: str,
    destination: str,
    outbound_date: str,
    return_date: Optional[str],
    adults: int,
    children: int,
    infants: int,
) -> dict:
    """Call EaseMyTrip flight search API.

    Args:
        origin: Origin airport code (e.g., 'DEL')
        destination: Destination airport code (e.g., 'BOM')
        outbound_date: Outbound flight date in YYYY-MM-DD format
        return_date: Return flight date (optional for one-way)
        adults: Number of adult passengers
        children: Number of child passengers
        infants: Number of infant passengers

    Returns:
        Dict containing flight search results with outbound and return flights
    """
    #token = get_easemytrip_token()
    trace_id = gen_trace_id()

    is_roundtrip = return_date is not None
    search_context = {
        "origin": origin,
        "destination": destination,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "adults": adults,
        "children": children,
        "infants": infants,
    }

    payload = {
        "org": origin.upper(),
        "dept": destination.upper(),
        "adt": str(adults),
        "chd": str(children),
        "inf": str(infants),
        "queryname": trace_id,
        "deptDT": outbound_date,
        "arrDT": return_date if is_roundtrip else None,
        "userid": "",
        "IsDoubelSeat": False,
        "isDomestic": "true",
        "isOneway": not is_roundtrip,
        "airline": "undefined",
        "VIP_CODE": "",
        "VIP_UNIQUE": "",
        "Cabin": 0,
        "currCode": "INR",
        "appType": 1,
        "isSingleView": False,
        "ResType": 2,
        "IsNBA": True,
        "CouponCode": "",
        "IsArmedForce": False,
        "AgentCode": "",
        "IsWLAPP": False,
        "IsFareFamily": False,
        "serviceid": "EMTSERVICE",
        "serviceDepatment": "",
        "IpAddress": "",
        "LoginKey": "",
        "UUID": "",
        "TKN": "",
        "requesttime": "2025-03-25T09:22:38.407Z",
        "tokenResponsetime": "2025-03-25T09:22:38.406Z"
    }

    # 
    # async with httpx.AsyncClient(timeout=60) as client:
    #     res = await client.post(url, json=payload)
    #     res.raise_for_status()
    #     data = res.json()
    url = f"{FLIGHT_BASE_URL}/AirAvail_Lights/AirBus_New"
    api = FlightApiClient()
    data = await api.search(url, payload)

    # Check if response is error string
    if isinstance(data, str):
        return {
            "error": "INVALID_SEARCH",
            "message": data,
            "outbound_flights": [],
            "return_flights": [],
            "is_roundtrip": is_roundtrip,
            "origin": origin.upper(),
            "destination": destination.upper(),
        }

    # Process results
    processed_data = process_flight_results(data, is_roundtrip, search_context)
    processed_data["origin"] = origin.upper()
    processed_data["destination"] = destination.upper()
    return processed_data


def process_flight_results(
    search_response: dict,
    is_roundtrip: bool,
    search_context: Optional[Dict[str, Any]] = None,
) -> dict:
    """Process raw flight search response.

    Args:
        search_response: Raw API response from EaseMyTrip
        is_roundtrip: Whether this is a roundtrip search
        search_context: Original search parameters for deep-link building

    Returns:
        Dict containing processed outbound and return flights
    """
    outbound_flights = []
    return_flights = []

    airlines_map = search_response.get("C", {})
    flight_details_dict = search_response.get("dctFltDtl", {})
    journeys = search_response.get("j", [])

    if not journeys or not isinstance(journeys, list):
        return {
            "outbound_flights": [],
            "return_flights": [],
            "is_roundtrip": is_roundtrip
        }

    for journey_index, journey in enumerate(journeys):
        if journey_index > 0 and not is_roundtrip:
            continue

        segments = journey.get("s", [])
        if not isinstance(segments, list):
            continue

        for segment in segments:
            processed_flight = process_segment(
                segment,
                flight_details_dict,
                airlines_map,
                journey_index,
                search_context,
            )

            if processed_flight:
                if journey_index == 0:
                    outbound_flights.append(processed_flight)
                elif journey_index == 1 and is_roundtrip:
                    return_flights.append(processed_flight)

    return {
        "outbound_flights": outbound_flights[:10],
        "return_flights": return_flights[:10],
        "is_roundtrip": is_roundtrip
    }


def process_segment(
    segment: dict,
    flight_details_dict: dict,
    airlines_map: dict,
    journey_index: int,
    search_context: Optional[Dict[str, Any]] = None,
) -> Optional[dict]:
    """Process a single flight segment.

    Args:
        segment: Raw segment data from API response
        flight_details_dict: Dictionary mapping flight IDs to details
        airlines_map: Dictionary mapping airline codes to names
        journey_index: Index of the journey (0 for outbound, 1 for return)
        search_context: Original search parameters for deep-link building

    Returns:
        Processed flight dict or None if segment is invalid
    """
    segment_id = segment.get("id")
    segment_key = segment.get("SK")

    bonds = segment.get("b", [])
    if not isinstance(bonds, list) or len(bonds) == 0:
        return None

    bond = bonds[0]

    journey_time = bond.get("JyTm", "")
    is_refundable = bond.get("RF") == "1"
    stops = bond.get("stp", "0")
    flight_ids = bond.get("FL", [])

    # Process flight legs
    legs = []
    origin = None
    destination = None

    for flight_id in flight_ids:
        flight_detail = flight_details_dict.get(str(flight_id), {})
        if not flight_detail or not isinstance(flight_detail, dict):
            continue

        airline_code = flight_detail.get("AC", "")
        airline_name = airlines_map.get(airline_code, airline_code)

        leg = {
            "airline_code": airline_code,
            "airline_name": airline_name,
            "flight_number": flight_detail.get("FN", ""),
            "origin": flight_detail.get("OG", ""),
            "destination": flight_detail.get("DT", ""),
            "departure_date": flight_detail.get("DDT", ""),
            "departure_time": flight_detail.get("DTM", ""),
            "arrival_date": flight_detail.get("ADT", ""),
            "arrival_time": flight_detail.get("ATM", ""),
            "cabin": flight_detail.get("CB", ""),
            "fare_class": flight_detail.get("FCLS", ""),
            "booking_code": flight_detail.get("FCLS", ""),
            "duration": flight_detail.get("DUR", ""),
            "baggage": f"{flight_detail.get('BW', '')} {flight_detail.get('BU', '')}".strip()
        }
        legs.append(leg)

        if origin is None:
            origin = leg["origin"]
        destination = leg["destination"]

    if not legs:
        return None

    # Process fare options
    fare_options = []
    fares = segment.get("lstFr", [])

    if fares and isinstance(fares, list):
        for fare in fares:
            if not isinstance(fare, dict):
                continue

            fare_option = {
                "fare_id": fare.get("SID", ""),
                "fare_name": fare.get("FN", ""),
                "base_fare": fare.get("BF", 0),
                "total_fare": fare.get("TF", 0),
                "total_tax": fare.get("TTXMP", 0),
                "discount": fare.get("DA", 0)
            }
            fare_options.append(fare_option)

    # Create flight object
    flight = {
        "segment_id": segment_id,
        "segment_key": segment_key,
        "origin": origin,
        "destination": destination,
        "journey_time": journey_time,
        "is_refundable": is_refundable,
        "total_stops": int(stops),
        "direction": "outbound" if journey_index == 0 else "return",
        "legs": legs,
        "fare_options": fare_options

    }

    passengers = {
        "adults": search_context.get("adults", 1) if search_context else 1,
        "children": search_context.get("children", 0) if search_context else 0,
        "infants": search_context.get("infants", 0) if search_context else 0,
    }
    default_departure = None
    if search_context:
        default_departure = (
            search_context.get("return_date")
            if flight["direction"] == "return"
            else search_context.get("outbound_date")
        )
    trip_type = "RoundTrip" if search_context and search_context.get("return_date") else "OneWay"

    flight["deepLink"] = build_deep_link(
        flight=flight,
        passengers=passengers,
        trip_type=trip_type,
        default_departure=default_departure,
    )["deepLink"]

    return flight