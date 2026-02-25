"""Flight Search API Logic.

This module handles all flight search operations including:
- Searching flights via EaseMyTrip API
- Processing flight results
- Processing individual flight segments
"""
from .flight_schema import FlightSearchInput,WhatsappFlightFinalResponse,WhatsappFlightFormat
from datetime import datetime
from typing import Any, Dict, List, Optional,Set
from urllib.parse import quote, urlencode
from emt_client.clients.flight_client import FlightApiClient
from emt_client.utils import (
    gen_trace_id,
    fetch_first_city_code_country,
    generate_short_link,
)
from emt_client.config import FLIGHT_BASE_URL, FLIGHT_DEEPLINK
from enum import Enum
import re

class CabinClassEnum(int, Enum):
    ECONOMY = 0
    FIRST = 1
    BUSINESS = 2
    PREMIUM_ECONOMY = 4


def resolve_cabin_enum(user_cabin: Optional[str]) -> CabinClassEnum:
    if not user_cabin:
        return CabinClassEnum.ECONOMY  # default

    text = user_cabin.lower()

    if any(k in text for k in ["business", "biz", "buss"]):
        return CabinClassEnum.BUSINESS

    if any(k in text for k in ["first", "first class"]):
        return CabinClassEnum.FIRST

    if any(k in text for k in ["premium", "premium economy", "prem"]):
        return CabinClassEnum.PREMIUM_ECONOMY

    if any(k in text for k in ["economy", "eco", "coach"]):
        return CabinClassEnum.ECONOMY

    # safe fallback
    return CabinClassEnum.ECONOMY


def get_cabin_display_name(cabin_enum: CabinClassEnum) -> str:
    """Convert CabinClassEnum to readable display text."""
    cabin_map = {
        CabinClassEnum.ECONOMY: "Economy",
        CabinClassEnum.FIRST: "First Class",
        CabinClassEnum.BUSINESS: "Business",
        CabinClassEnum.PREMIUM_ECONOMY: "Premium Economy",
    }
    return cabin_map.get(cabin_enum, "Economy")


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


def _duration_to_minutes(value: Any) -> Optional[int]:
    """Parse duration strings like '09h 50m', '4h05m', '09:50' into minutes."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)

    text = str(value).strip().lower()
    if not text:
        return None

    # Pattern with hours and minutes
    match = re.search(r"(?:(\d+)\s*h)?\s*(\d+)\s*m", text)
    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2))
        return hours * 60 + minutes

    # Pattern like 4h05m (no space)
    match = re.search(r"(\d+)h(\d+)", text)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        return hours * 60 + minutes

    # Pattern HH:MM
    if ":" in text:
        parts = text.split(":")
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            hours = int(parts[0])
            minutes = int(parts[1][:2])
            return hours * 60 + minutes

    # Fallback digits: treat as HHMM if length>2 else hours
    digits = "".join(ch for ch in text if ch.isdigit())
    if digits:
        if len(digits) > 2:
            hours = int(digits[:-2])
            minutes = int(digits[-2:])
            return hours * 60 + minutes
        return int(digits) * 60

    return None

def _coerce_refundable_flag(value: Any) -> Optional[bool]:
    """
    Normalize refundable flags that may arrive as bool, 1/0, or strings like
    'True', 'False', 'Refundable', 'NonRefundable'.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        if value == 1:
            return True
        if value == 0:
            return False

    text = str(value).strip().lower()
    if not text:
        return None

    if text in {"1", "true", "t", "yes", "y", "refundable"}:
        return True
    if text in {"0", "false", "f", "no", "n", "nonrefundable", "non-refundable", "non refundable", "non-refund", "nonrefundable"}:
        return False
    return None


def _effective_total_fare(raw_tf: Any, ttdis: Any, icps: Any) -> float:
    """
    Calculate the payable fare using ICPS + TTDIS rule:
    - If ICPS is truthy and TTDIS is a valid positive number less than TF, use TTDIS.
    - Otherwise, use TF.
    """
    def _to_float(val) -> Optional[float]:
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    tf = _to_float(raw_tf) or 0.0
    discount = _to_float(ttdis)

    icps_flag = str(icps).strip().lower() in {"1", "true", "t", "yes", "y"} if icps is not None else False
    if icps_flag and discount is not None and discount > 0 and discount < tf:
        return discount
    return tf


def _sum_leg_durations(legs: List[Dict[str, Any]]) -> Optional[int]:
    total = 0
    found = False
    for leg in legs or []:
        minutes = _duration_to_minutes(leg.get("duration"))
        if minutes is not None:
            total += minutes
            found = True
    return total if found else None


def _flight_duration_minutes(flight: Dict[str, Any]) -> int:
    """Compute duration in minutes for sorting; inf if unknown."""
    if not flight:
        return float("inf")
    minutes = _duration_to_minutes(flight.get("journey_time"))
    if minutes is None:
        minutes = _sum_leg_durations(flight.get("legs", []))
    if minutes is None:
        return float("inf")
    return minutes


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


def _build_leg_from_detail(detail: Dict[str, Any], airlines_map: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
    """Map dctFltDtl entry to a leg structure."""
    if not detail or not isinstance(detail, dict):
        return None

    airline_code = detail.get("AC", "") or detail.get("airline_code", "")
    
    # Get airline name from airlines_map, extracting just the name part before the pipe
    airline_name = airline_code
    if airlines_map and airline_code in airlines_map:
        full_info = airlines_map.get(airline_code, "")
        # Format is "Airline Name|number|number", extract just the name
        airline_name = full_info.split("|")[0] if "|" in full_info else full_info
    elif not airlines_map:
        # Fallback to detail fields if airlines_map not provided
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
        total = _effective_total_fare(
            primary.get("TF") or primary.get("total_fare") or primary.get("total") or 0,
            segment.get("TTDIS"),
            segment.get("ICPS"),
        )
        if total:
            return total
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
    total_fare = _effective_total_fare(total_fare, segment.get("TTDIS"), segment.get("ICPS"))
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
    airlines_map: Optional[Dict[str, str]] = None,
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
        # print("Intl combos: journeys missing/empty.")
        return combos

    # Normalize journeys input
    if isinstance(journeys, dict):
        journeys_iterable = list(journeys.values())
    elif isinstance(journeys, list):
        journeys_iterable = journeys
    else:
        # print(f"Intl combos: unsupported journeys type: {type(journeys)}")
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

    # print(
    #     "Intl combos: starting processing",
    #     {
    #         "journey_count": len(journeys_iterable),
    #         "detail_keys": list(flight_details_dict.keys())[:5],
    #     },
    # )

    for journey_idx, journey in enumerate(journeys_iterable):
        segments = journey.get("s", [])
        if not isinstance(segments, list):
            continue

        for segment_idx, segment in enumerate(segments):
            total_segments += 1
            segment_refundable = _coerce_refundable_flag(segment.get("RF"))

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

            # outbound_leg = _build_leg_from_detail(outbound_detail, airlines_map)
            # inbound_leg = _build_leg_from_detail(inbound_detail, airlines_map)
            outbound_leg = [
                _build_leg_from_detail(d, airlines_map) for d in outbound_detail if d
            ]
            inbound_leg = [
                _build_leg_from_detail(d, airlines_map) for d in inbound_detail if d
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

            outbound_refundable = _coerce_refundable_flag(outbound_block.get("RF")) or segment_refundable
            inbound_refundable = _coerce_refundable_flag(inbound_block.get("RF")) or segment_refundable

            combos.append(
                {
                    "id": f"{journey_idx}-{segment_idx}-{outbound_ref}-{inbound_ref}",
                    "onward_flight": {
                        #"segment_id": f"ob-{outbound_ref}",
                        "segement_id": f"ob-{'-'.join(map(str, outbound_ref))}",
                        "origin": outbound_leg[0]["origin"],
                        "destination": outbound_leg[-1]["destination"],
                        "journey_time": outbound_block.get("JyTm", ""),
                        "is_refundable": outbound_refundable if outbound_refundable is not None else False,
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
                        "is_refundable": inbound_refundable if inbound_refundable is not None else False,
                        "total_stops": max(len(_extract_flight_ids(inbound_block)) - 1, 0),
                        "direction": "return",
                       # "legs": [inbound_leg],
                       "legs": inbound_leg if isinstance(inbound_leg, list) else [inbound_leg],
                        "fare_options": inbound_fare_options,
                    },
                    "combo_fare": combo_fare,
                }
            )

    # print(
    #     "Intl combos: completed",
    #     {
    #         "combo_count": len(combos),
    #         "total_segments": total_segments,
    #         "segments_with_blocks": segments_with_blocks,
    #         "segments_with_refs": segments_with_refs,
    #         "segments_with_details": segments_with_details,
    #     },
    # )

    return combos



def build_deep_link(
    is_international,
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
    if not is_international and trip_type=="RoundTrip":
        trip_type="OneWay"

    params: List[tuple[str, str]] = [
        ("Adult", str(passengers.get("adults", 1))),
        ("Child", str(passengers.get("children", 0))),
        ("Infant", str(passengers.get("infants", 0))),
        ("ReferralId", ""),
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

def build_roundtrip_combo_deep_link(
    *,
    onward_flight: Dict[str, Any],
    return_flight: Dict[str, Any],
    passengers: Dict[str, int],
    referral_id: str = "",
    language: str = "en",
    currency: str = "INR",
    pos_country: str = "IN",
) -> str:
    """
    Build EMT deep link for combo roundtrip (multi-leg onward + return)
    """

    onward_legs = onward_flight.get("legs") or []
    return_legs = return_flight.get("legs") or []

    if not onward_legs or not return_legs:
        return FLIGHT_DEEPLINK

    
    def _fare(f):
        fares = f.get("fare_options") or []
        try:
            return float(fares[0].get("total_fare") or fares[0].get("base_fare") or 0)
        except Exception:
            return 0.0

    total_price = _fare(onward_flight) + _fare(return_flight)

    # ---- basic params ----
    params = {
        "Adult": passengers.get("adults", 1),
        "Child": passengers.get("children", 0),
        "Infant": passengers.get("infants", 0),
        "ReferralId": referral_id,
        "UserLanguage": language,
        "DisplayedPriceCurrency": currency,
        "UserCurrency": currency,
        "DisplayedPrice": f"{total_price:.2f}",
        "PointOfSaleCountry": pos_country,
        "TripType": "RoundTrip",

        # onward
        "Origin1": onward_legs[0]["origin"],
        "Destination1": onward_legs[-1]["destination"],
        "DepartureDate1": _parse_date_to_iso(onward_legs[0]["departure_date"]),
        "Cabin1": _normalize_cabin(onward_legs[0].get("cabin")),
        "BookingCode1": onward_legs[0].get("booking_code") or onward_legs[0].get("fare_class", ""),
        "FlightNumber1": onward_legs[0].get("flight_number", ""),

        # return
        "Origin2": return_legs[0]["origin"],
        "Destination2": return_legs[-1]["destination"],
        "DepartureDate2": _parse_date_to_iso(return_legs[0]["departure_date"]),
        "Cabin2": _normalize_cabin(return_legs[0].get("cabin")),
        "BookingCode2": return_legs[0].get("booking_code") or return_legs[0].get("fare_class", ""),
        "FlightNumber2": return_legs[0].get("flight_number", ""),

        "cc": "",
    }

    # ---- slices ----
    slice1 = ",".join(str(i + 1) for i in range(len(onward_legs)))
    slice2 = ",".join(
        str(len(onward_legs) + i + 1) for i in range(len(return_legs))
    )

    params["Slice1"] = slice1
    params["Slice2"] = slice2

    # ---- segments ----
    all_legs = onward_legs + return_legs
    segment_strings = _build_segment_strings(
        all_legs,
        _parse_date_to_iso(onward_legs[0]["departure_date"])
    )

    query = "&".join(
        f"{k}={quote(str(v), safe='')}" for k, v in params.items()
    )

    segment_query = "&".join(
        f"Segment{i+1}={quote(seg, safe='=,:-T')}"
        for i, seg in enumerate(segment_strings)
        if seg
    )
    print(f"{FLIGHT_DEEPLINK}?{query}&{segment_query}")
    return f"{FLIGHT_DEEPLINK}?{query}&{segment_query}"


def _format_listing_date(raw_date: Optional[str]) -> str:
    if not raw_date:
        return ""

    raw_text = str(raw_date).strip()
    if not raw_text:
        return ""

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d-%b-%Y", "%d%b%Y"):
        try:
            return datetime.strptime(raw_text, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue

    return raw_text


def _build_view_all_link(search_context: Optional[Dict[str, Any]]) -> str:
    if not search_context:
        return ""

    def _format_location(code: str, name: str, country: str) -> str:
        parts = [code, name, country]
        return "-".join([p for p in parts if p])

    def _safe_int(value: Any, default: int) -> int:
        try:
            parsed = int(value)
            return parsed if parsed >= 0 else default
        except (TypeError, ValueError):
            return default

    origin_code = search_context.get("origin") or ""
    destination_code = search_context.get("destination") or ""
    origin_name = search_context.get("origin_name") or origin_code
    destination_name = search_context.get("destination_name") or destination_code
    origin_country = search_context.get("origin_country") or ""
    destination_country = search_context.get("destination_country") or ""

    outbound_date = _format_listing_date(search_context.get("outbound_date"))
    return_date = _format_listing_date(search_context.get("return_date"))

    if not origin_code or not destination_code or not outbound_date:
        return ""

    is_roundtrip = bool(return_date)
    is_domestic = not bool(search_context.get("is_international"))

    srch_parts = [
        _format_location(origin_code, origin_name, origin_country),
        _format_location(destination_code, destination_name, destination_country),
        outbound_date,
    ]

    srch_value = "|".join(srch_parts)
    if is_roundtrip:
        srch_value = f"{srch_value}-{return_date}"

    passengers = search_context.get("passengers") or {}
    adults = _safe_int(passengers.get("adults", 1), 1)
    children = _safe_int(passengers.get("children", 0), 0)
    infants = _safe_int(passengers.get("infants", 0), 0)

    fare_type=search_context.get("fare_type", 0)

    query_params = {
        "srch": srch_value,
        "px": f"{adults}-{children}-{infants}",
        "cbn": search_context.get("cabin", 0),
        "ar": "undefined",
        "isow": str(not is_roundtrip).lower(),
        "isdm": str(is_domestic).lower(),
        "lang": "en-us",
        "IsDoubleSeat": "false",
        "CCODE": "IN",
        "curr": "INR",
        "apptype": "B2C",
        "fn":fare_type
    }

    base_url = "https://www.easemytrip.com/flight-search/listing"
    raw_link = f"{base_url}?{urlencode(query_params, quote_via=quote)}"

    try:
        short_link = generate_short_link(
            [{"deepLink": raw_link}],
            product_type="flight",
        )[0].get("deepLink")
        return short_link or raw_link
    except Exception:
        return raw_link


async def search_flights(
    origin: str,
    destination: str,
    outbound_date: str,
    return_date: Optional[str],
    adults: int,
    children: int,
    infants: int,
    cabin: Optional[str] = None,
    stops: Optional[int] = None,
    fastest: Optional[bool] = None,
    refundable: Optional[bool] = None,
    fare_type: Optional[int] = 0,
    departure_time_window: Optional[str] = None,
    arrival_time_window: Optional[str] = None,
    airline_names: Optional[list[str]] = None,
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
        stops: Number of preferred stops (0 = nonstop, 1 = one stop, etc.)
        fastest: If true, sort results by shortest journey time
        refundable: If true, only refundable options; if false, only non-refundable
        fare_type: Fare type code (0=standard, 1=defence, 2=student, 3=senior, 4=doctor/nurse)
        departure_time_window: Time-of-day window for departure (e.g., '06:00-12:00')
        arrival_time_window: Time-of-day window for arrival (e.g., '18:00-23:00')
        airline_names: Optional list of airline names to filter results (case-insensitive)

    Returns:
        Dict containing flight search results with outbound and return flights
    """
    #token = get_easemytrip_token()
    trace_id = gen_trace_id()
    client = FlightApiClient()
    is_roundtrip = return_date is not None
    try:
        origin_code, origin_country, origin_name = await fetch_first_city_code_country(
            client, origin
        )
    except Exception:
        origin_code, origin_country, origin_name = origin, "", origin

    try:
        destination_code, destination_country, destination_name = await fetch_first_city_code_country(
            client, destination
        )
    except Exception:
        destination_code, destination_country, destination_name = destination, "", destination

    if origin_country and destination_country:
        is_international = not (
            origin_country.strip().lower() == "india"
            and destination_country.strip().lower() == "india"
        )
    # if origin_country and destination_country:
    #     is_international = not (
    #         origin_country.strip().lower() == destination_country.strip().lower()
    #     )
    else:
        is_international = False
    cabin_enum = resolve_cabin_enum(cabin)

    passengers = {
        "adults": adults,
        "children": children,
        "infants": infants,
    }
    try:
        fare_type_code = int(fare_type or 0)
    except (TypeError, ValueError):
        fare_type_code = 0

    is_fare_family = fare_type_code != 1
    is_armed_force = fare_type_code == 1

    search_context = {
        "origin": origin_code,
        "destination": destination_code,
        "origin_name": origin_name or origin,
        "destination_name": destination_name or destination,
        "origin_country": origin_country,
        "destination_country": destination_country,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "adults": adults,
        "children": children,
        "infants": infants,
        "passengers": passengers,
        "cabin": cabin_enum.value,
        "is_international": is_international,
        "stops": stops,
        "fare_type": fare_type,
        "fastest": fastest,
        "refundable": refundable,
        "departure_time_window": departure_time_window,
        "arrival_time_window": arrival_time_window,
        "airline_names": airline_names,
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
        "FareTypeUI": fare_type_code,
        "userid": "",
        "IsDoubelSeat": False,
        "isDomestic": not is_international,
        "isOneway": not is_roundtrip,
        "airline": "undefined",
        "VIP_CODE": "",
        "VIP_UNIQUE": "",
        "Cabin": cabin_enum.value,
        "currCode": "INR",
        "appType": 1,
        "isSingleView": False,
        "ResType": 0 if is_international else 2,
        "IsNBA": True,
        "CouponCode": "",
        "IsArmedForce": is_armed_force,
        "AgentCode": "",
        "IsWLAPP": False,
        "IsFareFamily": is_fare_family,
        "serviceid": "EMTSERVICE",
        "serviceDepatment": "",
        "IpAddress": "",
        "LoginKey": "",
        "UUID": "",
        "TKN": "",
        "requesttime": "2025-03-25T09:22:38.407Z",
        "tokenResponsetime": "2025-03-25T09:22:38.406Z"
    }

    
    url = f"{FLIGHT_BASE_URL}/AirAvail_Lights/AirBus_New"
   
    data = await client.search(url, payload)

    # Check if response is error string
    if isinstance(data, str):
        return {
            "error": "INVALID_SEARCH",
            "message": data,
            "outbound_flights": [],
            "return_flights": [],
            "is_roundtrip": is_roundtrip,
            "is_international": is_international,
            "international_combos": [],
            "origin": origin_code,
            "destination": destination_code,
            "viewAll": None,
        }

    # Process results
    processed_data = process_flight_results(data, is_roundtrip,is_international, search_context)
    processed_data["origin"] = origin_code
    processed_data["destination"] = destination_code
    processed_data["outbound_date"] = outbound_date
    processed_data["return_date"] = return_date
    processed_data["cabin"] = get_cabin_display_name(cabin_enum)
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
    def _coerce_stops(value: Any) -> Optional[int]:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _build_calendar_suggestions(calendar_data: Any) -> List[Dict[str, Any]]:
        """Pick top 3 alternate airports from lstCalendarFareData."""
        if not isinstance(calendar_data, list):
            return []

        def _to_float(val: Any) -> Optional[float]:
            try:
                return float(val)
            except (TypeError, ValueError):
                return None

        suggestions: List[Dict[str, Any]] = []
        for item in calendar_data:
            if not isinstance(item, dict):
                continue
            dest_code = item.get("Destination") or item.get("destination")
            if not dest_code:
                continue
            suggestions.append({
                "destination": str(dest_code),
                "destination_name": (item.get("destName") or item.get("destinationName") or item.get("dest_name")),
                "distance": _to_float(item.get("DistanceArr") or item.get("Distance")),
                "total_fare": _to_float(item.get("TotalFare")),
                "departure_date": _parse_date_to_iso(str(item.get("newDate") or item.get("DepDate") or "")) if (item.get("newDate") or item.get("DepDate")) else None,
            })

        suggestions.sort(
            key=lambda s: (
                s["distance"] if s["distance"] is not None else float("inf"),
                s["total_fare"] if s["total_fare"] is not None else float("inf"),
            )
        )

        return suggestions[:3]

    def _parse_single_time(value: Any) -> Optional[int]:
        """Parse 'HH:MM' or 'HHMM' (24h)."""
        if value is None:
            return None
        raw = str(value).strip()
        if not raw:
            return None

        raw = raw.replace(" ", "")
        if ":" in raw:
            parts = raw.split(":", 1)
            if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                return None
            hour = int(parts[0])
            minute = int(parts[1])
        else:
            digits = re.sub(r"\D", "", raw)
            if len(digits) not in (3, 4):
                return None
            hour = int(digits[:-2])
            minute = int(digits[-2:])

        if hour > 24 or minute > 59:
            return None
        if hour == 24 and minute > 0:
            return None

        return hour * 60 + minute

    def _parse_time_window(window_value: Optional[Any]) -> tuple[int, int, bool]:
        default_window = (0, 1440, False)
        if window_value is None:
            return default_window

        text = str(window_value).strip()
        if not text:
            return default_window

        if "-" not in text and "to" not in text:
            return default_window

        sep = "-" if "-" in text else "to"
        parts = [p.strip() for p in text.split(sep, 1)]
        if len(parts) != 2:
            return default_window

        start = _parse_single_time(parts[0])
        end = _parse_single_time(parts[1])

        if start is None or end is None:
            return default_window

        wrap = end < start
        return (start, end, wrap)

    def _time_to_minutes(raw_time: Any) -> Optional[int]:
        if raw_time is None:
            return None

        digits = re.sub(r"\D", "", str(raw_time))
        if not digits:
            return None

        if len(digits) == 3:
            hour = int(digits[0])
            minute = int(digits[1:])
        else:
            hour = int(digits[:2])
            minute = int(digits[2:4]) if len(digits) >= 4 else 0

        if hour > 24 or minute > 59:
            return None

        if hour == 24 and minute > 0:
            hour, minute = 23, 59

        return hour * 60 + minute

    def _is_within_window(raw_time: Any, window: tuple[int, int, bool]) -> bool:
        if not window:
            return True
        start, end, wrap = window
        if start == 0 and end == 1440 and not wrap:
            return True
        minutes = _time_to_minutes(raw_time)
        if minutes is None:
            return False
        if wrap:
            return minutes >= start or minutes <= end
        return start <= minutes <= end

    departure_window = _parse_time_window(search_context.get("departure_time_window") if search_context else None)
    arrival_window = _parse_time_window(search_context.get("arrival_time_window") if search_context else None)

    def _matches_time_filters(flight: Dict[str, Any]) -> bool:
        legs = flight.get("legs") or []
        if not legs:
            return True
        dep_time = legs[0].get("departure_time")
        arr_time = legs[-1].get("arrival_time")
        return _is_within_window(dep_time, departure_window) and _is_within_window(arr_time, arrival_window)

    def _matches_airline_filters(flight: Dict[str, Any]) -> bool:
        names = search_context.get("airline_names") if search_context else None
        if not names:
            return True
        legs = flight.get("legs") or []
        if not legs:
            return False
        airline = (legs[0].get("airline_name") or "").lower()
        code = (legs[0].get("airline_code") or "").lower()
        for name in names:
            n = str(name).lower()
            if n in airline or n in code:
                return True
        return False

    def _matches_refundable_filters(flight: Dict[str, Any]) -> bool:
        preference = search_context.get("refundable") if search_context else None
        if preference is None:
            return True
        flag = flight.get("is_refundable")
        if preference is True:
            return flag is True
        if preference is False:
            return flag is False
        return True

    stops_filter = _coerce_stops(search_context.get("stops")) if search_context else None
    fastest_flag = bool(search_context.get("fastest")) if search_context else False

    outbound_flights = []
    return_flights = []

    airlines_map = search_response.get("C", {})
    flight_details_dict = search_response.get("dctFltDtl", {})
    journeys = search_response.get("j", [])
    calendar_suggestions = _build_calendar_suggestions(search_response.get("lstCalendarFareData"))

    if not journeys or not isinstance(journeys, list):
        return {
            "outbound_flights": [],
            "return_flights": [],
            "is_roundtrip": is_roundtrip,
            "is_international": is_international,
            "international_combos": [],
            "viewAll": None,
            "calendar_suggestions": calendar_suggestions,
            "message": (search_response.get("err") or {}).get("desp") or "No flights available for the selected route/date.",
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
                is_international,
                is_roundtrip,
                search_context
                
            )

            if (
                processed_flight
                and _matches_time_filters(processed_flight)
                and _matches_airline_filters(processed_flight)
                and _matches_refundable_filters(processed_flight)
            ):
                if journey_index == 0:
                    outbound_flights.append(processed_flight)
                elif journey_index == 1 and is_roundtrip:
                    return_flights.append(processed_flight)

    if is_international and is_roundtrip:
        combos = _process_international_combos(journeys, flight_details_dict, airlines_map)

        if combos and search_context:
            passengers = {
                "adults": search_context.get("adults", 1),
                "children": search_context.get("children", 0),
                "infants": search_context.get("infants", 0),
                }

            for combo in combos:
                combo["deepLink"] = build_roundtrip_combo_deep_link(
                onward_flight=combo["onward_flight"],
                return_flight=combo["return_flight"],
                passengers=passengers,
                )
        if combos:
            combos = [
                combo for combo in combos
                if _matches_time_filters(combo.get("onward_flight", {}))
                # and _matches_time_filters(combo.get("return_flight", {}))
                and _matches_airline_filters(combo.get("onward_flight", {}))
                and _matches_airline_filters(combo.get("return_flight", {}))
                and _matches_refundable_filters(combo.get("onward_flight", {}))
                and _matches_refundable_filters(combo.get("return_flight", {}))
            ]
    else:
        combos=[]

    if stops_filter is not None:
        outbound_flights = [
            flight for flight in outbound_flights
            if _coerce_stops(flight.get("total_stops")) == stops_filter
        ]
        return_flights = [
            flight for flight in return_flights
            if _coerce_stops(flight.get("total_stops")) == stops_filter
        ]
        combos = [
            combo for combo in combos
            if _coerce_stops(combo.get("onward_flight", {}).get("total_stops")) == stops_filter
            and _coerce_stops(combo.get("return_flight", {}).get("total_stops")) == stops_filter
        ]

    if fastest_flag:
        outbound_flights = sorted(outbound_flights, key=_flight_duration_minutes)
        return_flights = sorted(return_flights, key=_flight_duration_minutes)
        combos = sorted(
            combos,
            key=lambda c: _flight_duration_minutes(c.get("onward_flight", {}))
            + _flight_duration_minutes(c.get("return_flight", {}))
        )

    view_all_link = _build_view_all_link(search_context)

    return {
        "outbound_flights": outbound_flights,
        "return_flights": return_flights,
        "is_roundtrip": is_roundtrip,
        "is_international": is_international,
        "international_combos": combos,
        "viewAll": view_all_link,
        "calendar_suggestions": calendar_suggestions,
        }

def process_segment(
    segment: dict,
    flight_details_dict: dict,
    airlines_map: dict,
    journey_index: int,
    is_international:bool,
    is_roundtrip,
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
    segment_refundable = _coerce_refundable_flag(segment.get("RF"))
    bonds=[]
    if is_international and  not is_roundtrip:
         bonds = segment.get("l_OB", [])
    else:
        bonds = segment.get("b", [])
    if not isinstance(bonds, list) or len(bonds) == 0:
        return None

    bond = bonds[0]

    journey_time = bond.get("JyTm", "")
    refundable_flag = _coerce_refundable_flag(bond.get("RF"))
    if refundable_flag is None:
        refundable_flag = segment_refundable
    is_refundable = refundable_flag if refundable_flag is not None else False
    if is_international and  not is_roundtrip:
        stops = bond.get("STP", "0")
        

        stops = re.split(r'[-+]', stops)[0].replace('|', '')

        if stops == "Non":
            stops=0
        
    else:
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
    if is_international and  not is_roundtrip:
        fare=segment.get("TF", [])
        effective_tf = _effective_total_fare(fare, segment.get("TTDIS"), segment.get("ICPS"))
        fare_option={ "base_fare":fare,
                    "total_fare": effective_tf,}
        fare_options.append(fare_option)
    else:
        fares = segment.get("lstFr", [])

        if fares and isinstance(fares, list):
            for fare in fares:
                if not isinstance(fare, dict):
                    continue

                effective_tf = _effective_total_fare(
                    fare.get("TF", 0),
                    segment.get("TTDIS"),
                    segment.get("ICPS"),
                )
                fare_option = {
                    "fare_id": fare.get("SID", ""),
                    "fare_name": fare.get("FN", ""),
                    "base_fare": fare.get("BF", 0),
                    "total_fare": effective_tf,
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
        is_international,
        flight=flight,
        passengers=passengers,
        trip_type=trip_type,
        default_departure=default_departure,
    )["deepLink"]

    return flight

def extract_segment_summary(segment: dict) -> dict:
    legs = segment.get("legs") or []

    if not legs:
        return {
            "airline": None,
            "flight_number": None,
            "departure_time": None,
             "departure_date": None,
            "arrival_date": None,
            "arrival_time": None,
            "duration": segment.get("journey_time"),
            "stops": segment.get("total_stops", 0),
        }
    stop_airports = [leg["destination"] for leg in legs[:-1]] if len(legs) > 1 else []
    first_leg = legs[0]
    last_leg = legs[-1]

    return {
        "airline": first_leg.get("airline_name"),
        "flight_number": " / ".join(
            f"{leg.get('airline_code')}{leg.get('flight_number')}"
            for leg in legs
            if leg.get("flight_number")
        ),
        "departure_date": first_leg.get("departure_date"),
        "arrival_date": last_leg.get("arrival_date"),
        "arrival_city": last_leg.get("destination"),
        "departure_city": first_leg.get("origin"),
        "departure_time": first_leg.get("departure_time"),
        "arrival_time": last_leg.get("arrival_time"),
        "duration": segment.get("journey_time"),
        "stops": segment.get("total_stops", 0),
        "stop_airports": stop_airports,
    }


# 🧹 IMPROVEMENT: extracted WhatsApp builder for clarity & testability
def build_whatsapp_flight_response(
    payload: FlightSearchInput,
    flight_results: dict,
) -> WhatsappFlightFinalResponse:

    options = []

    is_roundtrip = flight_results.get("is_roundtrip")
    is_international = flight_results.get("is_international")

    # ---------- ONEWAY ----------
    if not is_roundtrip:
        for idx, flight in enumerate(flight_results.get("outbound_flights", []), start=1):
            summary = extract_segment_summary(flight)
            fare = (flight.get("fare_options") or [{}])[0]

            options.append({
                "option_id": idx,
                "outbound_flight": {
                    "airline": summary["airline"],
                    "flight_number": summary["flight_number"],
                    "origin": payload.origin,
                    "destination": payload.destination,
                    "departure_time": summary["departure_time"],
                    "arrival_time": summary["arrival_time"],
                    "duration": summary["duration"],
                    "stops": summary["stops"],
                    "stop_airports": summary.get("stop_airports", []),
                    "date": payload.outbound_date,
                },
                "price": fare.get("total_fare"),
                "booking_url": flight.get("deepLink"),
            })

        trip_type = "oneway"

    # ---------- ROUNDTRIP DOMESTIC ----------
    elif is_roundtrip and not is_international:
        passengers = {
            "adults": payload.adults,
            "children": payload.children,
            "infants": payload.infants,
        }
        for idx, (out_f, ret_f) in enumerate(
            zip(
                flight_results.get("outbound_flights", []),
                flight_results.get("return_flights", []),
            ),
            start=1,
        ):
            out_summary = extract_segment_summary(out_f)
            ret_summary = extract_segment_summary(ret_f)

            out_fare = (out_f.get("fare_options") or [{}])[0]
            ret_fare = (ret_f.get("fare_options") or [{}])[0]
            combo_deep_link = build_roundtrip_combo_deep_link(
                onward_flight=out_f,
                return_flight=ret_f,
                passengers=passengers,
            )
            try:
                booking_url = generate_short_link(
                    [{"deepLink": combo_deep_link}],
                    product_type="flight",
                )[0].get("deepLink") or combo_deep_link
            except Exception:
                booking_url = combo_deep_link

            options.append({
                "option_id": idx,
                "outbound_flight": out_summary,
                "inbound_flight": ret_summary,
                "total_price": (out_fare.get("total_fare") or 0)
                               + (ret_fare.get("total_fare") or 0),
                "booking_url": booking_url,
            })

        trip_type = "roundtrip"

    # ---------- ROUNDTRIP INTERNATIONAL ----------
    else:
        for idx, combo in enumerate(flight_results.get("international_combos", []), start=1):
            options.append({
                "option_id": idx,
                "outbound_flight": extract_segment_summary(combo.get("onward_flight", {})),
                "inbound_flight": extract_segment_summary(combo.get("return_flight", {})),
                "total_price": combo.get("combo_fare"),
                "booking_url": combo.get("deepLink"),
            })

        trip_type = "roundtrip"

    whatsapp_json = WhatsappFlightFormat(
        options=options,
        trip_type=trip_type,
        journey_type="international" if is_international else "domestic",
        currency=flight_results.get("currency", "INR"),
        view_all_flights_url=flight_results.get("viewAll", ""),
    )

    return WhatsappFlightFinalResponse(
        response_text=f"Here are the best flights options from {payload.origin} to {payload.destination}",
        whatsapp_json=whatsapp_json,
    )

def normalize_time(time_str: Optional[str]) -> Optional[str]:
    """
    Converts:
    - '17:15' → '1715'
    - '1715'  → '1715'
    - '17.15' → '1715'
    """
    if not time_str:
        return None

    digits = re.sub(r"\D", "", time_str)

    if len(digits) >= 4:
        return digits[:4]

    return None
def build_datetime(date_str: Optional[str], time_str: Optional[str]) -> Optional[datetime]:
    if not date_str or not time_str:
        return None
    date_str =_parse_date_to_iso(date_str)
    time_str = normalize_time(time_str)
    try:
        hh = time_str[:2]
        mm = time_str[2:4]
        return datetime.fromisoformat(f"{date_str}T{hh}:{mm}:00")
    except Exception:
        return None


def is_valid_domestic_roundtrip(out_flight: dict, ret_flight: dict) -> bool:
    """
    STRICT RULE:
    Return flight must depart >= 4 hours after onward arrival
    """
    out_summary = extract_segment_summary(out_flight)
    ret_summary = extract_segment_summary(ret_flight)

    out_arrival = build_datetime(
        out_summary.get("arrival_date"),
        out_summary.get("arrival_time"),
    )
    ret_departure = build_datetime(
        ret_summary.get("departure_date"),
        ret_summary.get("departure_time"),
    )

    if not out_arrival or not ret_departure:
        return False

    diff_hours = (ret_departure - out_arrival).total_seconds() / 3600
    return diff_hours > 4
from typing import Dict, List, Tuple


def filter_domestic_roundtrip_flights(flight_results: Dict) -> Dict:
    """
    Reorders outbound & return flights so that
    valid roundtrip pairs appear FIRST and MATCHED.
    """

    if not flight_results.get("is_roundtrip"):
        return flight_results

    if flight_results.get("is_international"):
        return flight_results

    outbound_flights = flight_results.get("outbound_flights", [])
    return_flights = flight_results.get("return_flights", [])

    if not outbound_flights or not return_flights:
        flight_results["outbound_flights"] = []
        flight_results["return_flights"] = []
        return flight_results

    valid_pairs: List[Tuple[int, int]] = []

    # Step 1: collect valid PAIRS (preserve order)
    for o_idx, out_f in enumerate(outbound_flights):
        for r_idx, ret_f in enumerate(return_flights):
            if is_valid_domestic_roundtrip(out_f, ret_f):
                valid_pairs.append((o_idx, r_idx))

    if not valid_pairs:
        flight_results["outbound_flights"] = []
        flight_results["return_flights"] = []
        return flight_results

    # Step 2: build ordered unique lists based on PAIRS
    ordered_outbounds = []
    ordered_returns = []

    seen_out = set()
    seen_ret = set()

    for o_idx, r_idx in valid_pairs:
        if o_idx not in seen_out:
            ordered_outbounds.append(outbound_flights[o_idx])
            seen_out.add(o_idx)

        if r_idx not in seen_ret:
            ordered_returns.append(return_flights[r_idx])
            seen_ret.add(r_idx)

    flight_results["outbound_flights"] = ordered_outbounds
    flight_results["return_flights"] = ordered_returns

    return flight_results

