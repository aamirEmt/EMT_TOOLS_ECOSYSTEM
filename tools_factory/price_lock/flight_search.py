"""Flight Search API Logic.

This module handles all flight search operations including:
- Searching flights via EaseMyTrip API
- Processing flight results
- Processing individual flight segments
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx

from app.flight_token import get_easemytrip_token
from app.utils import gen_trace_id, fetch_first_code_and_country
from app.config import FLIGHT_BASE_URL, FLIGHT_DEEPLINK


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


def _build_leg_from_detail(detail: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Map dctFltDtl entry to a leg structure."""
    if not detail or not isinstance(detail, dict):
        return None

    airline_code = detail.get("AC", "") or detail.get("airline_code", "")
    airline_name = detail.get("ALN") or detail.get("AN") or detail.get("airline_name") or airline_code

    return {
        "airline_code": airline_code,
        "airline_name": airline_name,
        "flight_number": detail.get("FN", "") or detail.get("flight_number", ""),
        "origin": detail.get("OG", "") or detail.get("origin", ""),
        "destination": detail.get("DT", "") or detail.get("destination", ""),
        "departure_date": detail.get("DDT", "") or detail.get("departure_date", ""),
        "departure_time": detail.get("DTM", "") or detail.get("departure_time", ""),
        "arrival_date": detail.get("ADT", "") or detail.get("arrival_date", ""),
        "arrival_time": detail.get("ATM", "") or detail.get("arrival_time", ""),
        "cabin": detail.get("CB", "") or detail.get("cabin", ""),
        "fare_class": detail.get("FCLS", "") or detail.get("fare_class", ""),
        "booking_code": detail.get("FCLS", "") or detail.get("booking_code", "") or detail.get("fare_class", ""),
        "duration": detail.get("DUR", "") or detail.get("duration", ""),
        "baggage": f"{detail.get('BW', '')} {detail.get('BU', '')}".strip(),
    }


def _derive_combo_fare(segment: Dict[str, Any]) -> float:
    """Extract fare from combo segment."""
    if not segment or not isinstance(segment, dict):
        return 0.0
    fares = segment.get("lstFr") or []
    if fares and isinstance(fares, list):
        primary = fares[0] if fares else {}
        try:
            total = float(primary.get("TF") or primary.get("total_fare") or primary.get("total") or 0)
            if total:
                return total
        except (TypeError, ValueError):
            pass
        try:
            base = float(primary.get("BF") or primary.get("base_fare") or 0)
            return base or 0.0
        except (TypeError, ValueError):
            return 0.0
    return 0.0


def _build_fare_options_from_combo(segment: Dict[str, Any], per_leg_fare: float) -> List[Dict[str, Any]]:
    fares = segment.get("lstFr") or []
    primary = fares[0] if fares and isinstance(fares, list) else {}
    base_fare = per_leg_fare or primary.get("BF") or primary.get("base_fare") or 0
    total_fare = per_leg_fare or primary.get("TF") or primary.get("total_fare") or primary.get("total") or base_fare
    try:
        base_fare = float(base_fare)
    except (TypeError, ValueError):
        base_fare = 0.0
    try:
        total_fare = float(total_fare)
    except (TypeError, ValueError):
        total_fare = base_fare

    return [
        {
            "fare_id": primary.get("SID", "") if primary else "",
            "fare_name": primary.get("FN", "") if primary else "",
            "base_fare": base_fare,
            "total_fare": total_fare or base_fare,
            "total_tax": primary.get("TTXMP", 0) if primary else 0,
            "discount": primary.get("DA", 0) if primary else 0,
        }
    ]


def _get_flight_details_for_refs(refs, flight_details_dict):
    """
    Returns list of flight detail objects, one per leg.
    """
    if isinstance(refs, list):
        details = []
        for ref in refs:
            detail = (
                flight_details_dict.get(str(ref))
                or flight_details_dict.get(ref)
            )
            if detail:
                details.append(detail)
        return details

    # single-leg journey
    detail = (
        flight_details_dict.get(str(refs))
        or flight_details_dict.get(refs)
    )
    return [detail] if detail else []

def _process_international_combos(
    journeys: List[Dict[str, Any]],
    flight_details_dict: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Build pre-combined international outbound + return flight combos.
    """

    combos: List[Dict[str, Any]] = []

    total_segments = 0
    segments_with_blocks = 0
    segments_with_refs = 0
    segments_with_details = 0

    if not journeys:
        print("Intl combos: journeys missing/empty.")
        return combos

    # Normalize journeys input
    if isinstance(journeys, dict):
        journeys_iterable = list(journeys.values())
    elif isinstance(journeys, list):
        journeys_iterable = journeys
    else:
        print(f"Intl combos: unsupported journeys type: {type(journeys)}")
        return combos

    def _get_combo_list(segment: Dict[str, Any], target: str) -> Any:
        """
        Fetch l_OB / l_IB arrays, tolerant to casing and underscores.
        """
        direct = segment.get(target)
        if direct is not None:
            return direct

        normalized = target.replace("_", "").lower()
        for key, val in segment.items():
            if key and str(key).replace("_", "").lower() == normalized:
                return val
        return None

    def _first_block(items: Any) -> Dict[str, Any]:
        """
        Return first meaningful block containing flight data.
        """
        if not items:
            return {}

        if isinstance(items, dict):
            return items

        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and item.get("FL"):
                    return item
            return items[0] if items else {}

        return {}

    def _first_flight_id(block: Any) -> Any:
        """
        Extract first flight ID from block.
        """
        if not block:
            return None

        if isinstance(block, dict):
            fl = block.get("FL") or block.get("fl") or block.get("flights")
            if isinstance(fl, list) and fl:
                return fl
            if isinstance(fl, (str, int)):
                return fl

        return None

    def _extract_flight_ids(block: Dict[str, Any]) -> List[Any]:
        """
        Extract all flight IDs for stop calculation.
        """
        if not isinstance(block, dict):
            return []

        fl = block.get("FL") or block.get("fl") or block.get("flights")

        if isinstance(fl, list):
            return fl
        if isinstance(fl, (str, int)):
            return [fl]

        return []

    print(
        "Intl combos: starting processing",
        {
            "journey_count": len(journeys_iterable),
            "detail_keys": list(flight_details_dict.keys())[:5],
        },
    )

    for journey_idx, journey in enumerate(journeys_iterable):
        segments = journey.get("s", [])
        if not isinstance(segments, list):
            continue

        for segment_idx, segment in enumerate(segments):
            total_segments += 1

            lob_items = _get_combo_list(segment, "l_OB") or []
            lib_items = _get_combo_list(segment, "l_IB") or []

            if not lob_items or not lib_items:
                continue

            segments_with_blocks += 1

            outbound_block = _first_block(lob_items)
            inbound_block = _first_block(lib_items)

            # pick only the first referenced flight from each block (first pair)
            outbound_ref = _first_flight_id(outbound_block) 
            inbound_ref = _first_flight_id(inbound_block) 

           

            if outbound_ref is None or inbound_ref is None:
                continue
            

            segments_with_refs += 1
            
            outbound_detail = _get_flight_details_for_refs(outbound_ref, flight_details_dict)
            inbound_detail = _get_flight_details_for_refs(inbound_ref, flight_details_dict)
            # outbound_detail = (
            #     flight_details_dict.get(str(outbound_ref)) #TODO: MAY BE UNCOMMENT LATER COMMENTING FOR TESTING
            #     or flight_details_dict.get(outbound_ref)
            # )
            # inbound_detail = (
            #     flight_details_dict.get(str(inbound_ref))
            #     or flight_details_dict.get(inbound_ref) #TODO: MAY BE UNCOMMENT LATER COMMENTING FOR TESTING
            # )

            # outbound_leg = _build_leg_from_detail(outbound_detail)
            # inbound_leg = _build_leg_from_detail(inbound_detail)
            outbound_leg = [
                _build_leg_from_detail(d) for d in outbound_detail if d
            ]
            inbound_leg = [
                _build_leg_from_detail(d) for d in inbound_detail if d
            ]

            if not outbound_leg or not inbound_leg:
                continue

            segments_with_details += 1

            # derive fares: prefer segment-level combo fare; fall back to per-leg cheapest fares
            combo_fare = None
            # possible places where combo fare may live on segment
            for fk in ("TF", "comboFare", "combo_fare", "totalFare", "total_fare", "total"):
                if segment.get(fk) is not None:
                    try:
                        combo_fare = float(segment.get(fk))
                        break
                    except (TypeError, ValueError):
                        combo_fare = None

            # build fare options for outbound/inbound from combo
            combo_fare = combo_fare or _derive_combo_fare(segment)

            per_leg_fare = combo_fare / 2 if combo_fare else 0.0
            outbound_fare_options = _build_fare_options_from_combo(segment, per_leg_fare)
            inbound_fare_options = _build_fare_options_from_combo(segment, per_leg_fare)

            # final fallback: sum cheapest available fares from the two sides
            if not combo_fare:
                cheapest_out = outbound_fare_options[0]["total_fare"] if outbound_fare_options else 0.0
                cheapest_in = inbound_fare_options[0]["total_fare"] if inbound_fare_options else 0.0
                try:
                    combo_fare = float(cheapest_out) + float(cheapest_in)
                except (TypeError, ValueError):
                    combo_fare = 0.0

            combos.append(
                {
                    "id": f"{journey_idx}-{segment_idx}-{outbound_ref}-{inbound_ref}",
                    "onward_flight": {
                        #"segment_id": f"ob-{outbound_ref}",
                        "segement_id": f"ob-{'-'.join(map(str, outbound_ref))}",
                        "origin": outbound_leg[0]["origin"],
                        "destination": outbound_leg[-1]["destination"],
                        "journey_time": outbound_block.get("JyTm", ""),
                        "is_refundable": outbound_block.get("RF") == "Refundable",
                        "total_stops": max(len(_extract_flight_ids(outbound_block)) - 1, 0),
                        "direction": "outbound",
                        "legs": outbound_leg if isinstance(outbound_leg, list) else [outbound_leg],
                        "fare_options": outbound_fare_options,
                    },
                    "return_flight": {
                        #"segment_id": f"ib-{inbound_ref}",
                        "segement_id": f"ob-{'-'.join(map(str, inbound_ref))}",
                        "origin": inbound_leg[0]["origin"],
                        "destination": inbound_leg[-1]["destination"],
                        "journey_time": inbound_block.get("JyTm", ""),
                        "is_refundable": inbound_block.get("RF") == "Refundable",
                        "total_stops": max(len(_extract_flight_ids(inbound_block)) - 1, 0),
                        "direction": "return",
                       # "legs": [inbound_leg],
                       "legs": inbound_leg if isinstance(inbound_leg, list) else [inbound_leg],
                        "fare_options": inbound_fare_options,
                    },
                    "combo_fare": combo_fare,
                }
            )

    print(
        "Intl combos: completed",
        {
            "combo_count": len(combos),
            "total_segments": total_segments,
            "segments_with_blocks": segments_with_blocks,
            "segments_with_refs": segments_with_refs,
            "segments_with_details": segments_with_details,
        },
    )

    return combos



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
    token = get_easemytrip_token()
    trace_id = gen_trace_id()

    is_roundtrip = return_date is not None
    origin_code, origin_country=fetch_first_code_and_country(origin)
    destination_code, destination_country=fetch_first_code_and_country(destination)

    is_international=not((origin_country=="India") and (destination_country=="India"))

    search_context = {
        "origin": origin_code,
        "destination": destination_code,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "adults": adults,
        "children": children,
        "infants": infants,
    }

    payload = {
        "org": origin_code,
        "dept": destination_code,
        "adt": str(adults),
        "chd": str(children),
        "inf": str(infants),
        "queryname": trace_id,
        "deptDT": outbound_date,
        "arrDT": return_date if is_roundtrip else None,
        "userid": "",
        "IsDoubelSeat": False,
        "isDomestic": f"{not is_international}",
        "isOneway": not is_roundtrip,
        "airline": "undefined",
        "VIP_CODE": "",
        "VIP_UNIQUE": "",
        "Cabin": 0,
        "currCode": "INR",
        "appType": 1,
        "isSingleView": False,
        "ResType": 0 if is_international else 2,
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
        "TKN": token,
        "requesttime": "2025-03-25T09:22:38.407Z",
        "tokenResponsetime": "2025-03-25T09:22:38.406Z"
    }

    url = f"{FLIGHT_BASE_URL}/AirAvail_Lights/AirBus_New"
    async with httpx.AsyncClient(timeout=60) as client:
        res = await client.post(url, json=payload)
        res.raise_for_status()
        data = res.json()

    # Check if response is error string
    if isinstance(data, str):
        return {
            "error": "INVALID_SEARCH",
            "message": data,
            "outbound_flights": [],
            "return_flights": [],
            "is_roundtrip": is_roundtrip,
            "origin": origin_code,
            "destination": destination_code,
        }

    # Process results
    processed_data = process_flight_results(data, is_roundtrip,is_international, search_context)
    processed_data["origin"] = origin_code
    processed_data["destination"] = destination_code
    return processed_data


def process_flight_results(
    search_response: dict,
    is_roundtrip: bool,
    is_international:bool,
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
        "is_roundtrip": is_roundtrip,
        "is_international":is_international,
        "international_combos": _process_international_combos(journeys, flight_details_dict),
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
