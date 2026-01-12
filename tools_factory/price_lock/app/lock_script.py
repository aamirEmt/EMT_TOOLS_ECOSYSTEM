"""
Quick CLI to search flights, select one, reprice to fetch segKey, and lock the fare.

Flow:
1) Login (uses login/login.py) to fetch CookC (LoginKey).
2) Fetch flight token (ITK) and search flights (AirBus_New).
3) Let the user pick a flight and fare; reprice (AirReprice_L) to get segKey.
4) Call GenrateTransactionWithReprice with that segKey and LoginKey.

Note: This is a slimmed-down version of the flow in main.py focused on the lock use-case.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Paths and sys.path setup
# --------------------------------------------------------------------------- #
ROOT_DIR = Path(__file__).resolve().parent.parent  # DEV/
EMT_SERVER_DIR = ROOT_DIR / "EaseMyTrip_OPENAI_APP" / "emt_mcp_server"
LOGIN_DIR = ROOT_DIR / "login"

# Ensure dependent modules can be imported
for path in [EMT_SERVER_DIR, LOGIN_DIR]:
    sys.path.insert(0, str(path))

# Load environment variables needed by app.config
ENV_PATHS = [
    EMT_SERVER_DIR / ".env",
    ROOT_DIR / "test" / ".env",  # fallback if user mirrors test config
]
for env_path in ENV_PATHS:
    if env_path.exists():
        load_dotenv(env_path)
        break

# These imports rely on env already being loaded
try:
    from app.config import FLIGHT_BASE_URL  # type: ignore
    from app.flight_token import get_easemytrip_token  # type: ignore
    from app.utils import fetch_first_code_and_country, gen_trace_id  # type: ignore
    import flight_search as flight_search_module  # type: ignore
except Exception as exc:  # noqa: BLE001
    raise RuntimeError(
        f"Failed to import EMT modules. Ensure .env exists under {EMT_SERVER_DIR} "
        f"and dependencies are installed. Details: {exc}"
    ) from exc

# login package
from login.login_script import emt_login  # type: ignore
from login.crypto_bot import DecryptStringAES_BOT # type: ignore

# JS for ConvertSegFinal
try:
    from py_mini_racer import py_mini_racer  # type: ignore
except ImportError as exc:  # noqa: BLE001
    raise RuntimeError(
        "py_mini_racer is required. Install with `pip install py-mini-racer`."
    ) from exc


REPRICE_ENDPOINT = f"{FLIGHT_BASE_URL}/AirAvail_Lights/AirReprice_L"
SEARCH_ENDPOINT = f"{FLIGHT_BASE_URL}/AirAvail_Lights/AirBus_New"
LOCK_ENDPOINT = f"{FLIGHT_BASE_URL}/Book/GenrateTransactionWithReprice"


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def prompt(text: str, default: Optional[str] = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{text}{suffix}: ").strip()
    return value or (default or "")


def login_and_get_key(phone: str, ip_address: str = "") -> str:
    """Call login.emt_login and extract CookC as LoginKey."""
    login_response = emt_login(phone_number=phone, ip_address=ip_address)
    json_body = login_response.get("json") or {}
    decrypted_server_payload = DecryptStringAES_BOT(json_body)
    if decrypted_server_payload:
        obj = json.loads(decrypted_server_payload)
        key = obj.get("CookC")
        if key:
            return key
    raise RuntimeError("LoginKey (CookC) not found in login response.")


def fetch_itk_token() -> str:
    token = get_easemytrip_token()
    if not token:
        raise RuntimeError("Could not fetch ITK flight token.")
    return token


def normalize_airports(origin: str, destination: str) -> Tuple[str, str, bool]:
    """Return (origin_code, destination_code, is_international)."""
    o_code, o_country = fetch_first_code_and_country(origin)
    d_code, d_country = fetch_first_code_and_country(destination)
    is_international = not ((o_country == "India") and (d_country == "India"))
    return o_code, d_code, is_international


def build_search_payload(
    token: str,
    origin: str,
    destination: str,
    outbound_date: str,
    return_date: Optional[str],
    adults: int,
    children: int,
    infants: int,
    is_international: bool,
) -> Dict[str, Any]:
    now_iso = datetime.utcnow().isoformat() + "Z"
    return {
        "org": origin,
        "dept": destination,
        "adt": str(adults),
        "chd": str(children),
        "inf": str(infants),
        "queryname": gen_trace_id(),
        "deptDT": outbound_date,
        "arrDT": return_date if return_date else None,
        "userid": "",
        "IsDoubelSeat": False,
        "isDomestic": f"{not is_international}",
        "isOneway": return_date is None,
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
        "requesttime": now_iso,
        "tokenResponsetime": now_iso,
    }


def call_search(payload: Dict[str, Any]) -> Dict[str, Any]:
    res = requests.post(SEARCH_ENDPOINT, json=payload, timeout=60)
    res.raise_for_status()
    data = res.json()
    if isinstance(data, str):
        raise RuntimeError(f"Search failed: {data}")
    return data


def build_raw_segment_map(search_response: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    mapping: Dict[str, Dict[str, Any]] = {}
    for journey_index, journey in enumerate(search_response.get("j", [])):
        for segment in journey.get("s", []):
            seg_key = segment.get("SK")
            if seg_key:
                mapping[seg_key] = {
                    "segment": segment,
                    "journey_index": journey_index,
                }
    return mapping


def process_flights_for_display(
    search_response: Dict[str, Any],
    is_roundtrip: bool,
    is_international: bool,
    search_context: Dict[str, Any],
) -> List[Dict[str, Any]]:
    processed = flight_search_module.process_flight_results(
        search_response, is_roundtrip, is_international, search_context
    )
    flights = processed.get("outbound_flights", [])
    # Keep raw search response reference for later repricing
    for flight in flights:
        flight["searchResponse"] = search_response
    return flights


def display_flights(flights: List[Dict[str, Any]]) -> None:
    print("\nAvailable flights (top 10):")
    for idx, flight in enumerate(flights[:10], start=1):
        legs = flight.get("legs", [])
        first_leg = legs[0] if legs else {}
        last_leg = legs[-1] if legs else {}
        fare_options = flight.get("fare_options", [])
        lowest_fare = fare_options[0].get("total_fare") if fare_options else "N/A"
        print(
            f"{idx}) {first_leg.get('airline_code', '')} "
            f"{first_leg.get('flight_number', '')} "
            f"{first_leg.get('origin', '')}->{last_leg.get('destination', '')} "
            f"{first_leg.get('departure_time', '')}-{last_leg.get('arrival_time', '')} "
            f"Stops:{flight.get('total_stops', '')} Fare:{lowest_fare}"
        )


def select_flight(flights: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not flights:
        raise RuntimeError("No flights found for selection.")
    display_flights(flights)
    while True:
        choice = prompt("Pick flight number", "1")
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= min(len(flights), 10):
                return flights[idx - 1]
        print("Invalid choice, try again.")


def select_fare(flight: Dict[str, Any]) -> int:
    fare_options = flight.get("fare_options", [])
    if not fare_options:
        raise RuntimeError("No fare options available for selected flight.")
    print("\nFare options:")
    for idx, fare in enumerate(fare_options, start=1):
        print(
            f"{idx}) {fare.get('fare_name', 'Fare')} - Total: {fare.get('total_fare')} "
            f"Base: {fare.get('base_fare')}"
        )
    while True:
        choice = prompt("Pick fare number", "1")
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(fare_options):
                return idx - 1  # 0-based index for ConvertSegFinal
        print("Invalid fare choice, try again.")


def build_new_segment_js(
    raw_segment: Dict[str, Any],
    search_response: Dict[str, Any],
    origin: str,
    destination: str,
    adults: int,
    children: int,
    infants: int,
    is_roundtrip: bool,
    fare_index: int,
) -> Dict[str, Any]:
    js_path = Path(__file__).parent / "repricing_script.js"
    js_code = js_path.read_text(encoding="utf-8")
    ctx = py_mini_racer.MiniRacer()
    ctx.eval(js_code)
    return ctx.call(
        "ConvertSegFinal",
        raw_segment,
        search_response,
        origin,
        destination,
        "",
        "",
        adults,
        children,
        infants,
        "",
        is_roundtrip,
        fare_index,
    )


def call_reprice(
    new_segment: Dict[str, Any],
    search_response: Dict[str, Any],
    journey_index: int,
    login_key: str,
    adults: int,
    children: int,
    infants: int,
) -> Dict[str, Any]:
    air_reprice_payload = {
        "Res": {
            "jrneys": [{"segs": [new_segment]}],
            "TraceID": gen_trace_id(),
            "lstSearchReq": [search_response.get("SQ", [{}])[journey_index]]
            if search_response.get("SQ")
            else [],
            "adt": adults,
            "chd": children,
            "inf": infants,
            "displayFareAmt": 0,
            "DisplayFareKey": "",
        },
        "RepriceStep": 1,
        "IsHD": "true",
        "LoginKey": login_key,
        "userid": "",
        "SegKey": "",
        "IPAddress": "",
        "adt": adults,
        "chd": children,
        "inf": infants,
        "AgentCode": "",
        "IsWLAPP": "false",
        "brandFareKey": "",
        "cVID": "",
        "cID": "",
        "UUID": "",
    }
    res = requests.post(REPRICE_ENDPOINT, json=air_reprice_payload, timeout=60)
    res.raise_for_status()
    return res.json()


def call_lock(
    seg_key: str,
    login_key: str,
    lock_amount: float,
    payload_template: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    base_payload = payload_template or {}
    payload = {
        "IsLock": True,
        "LockAmount": lock_amount,
        "LockPeriod": "8Hours",
        "SegKey": seg_key,
        "LoginKey": login_key,
        "TransRefId": "",
        "IpAddress": "",
        "IsWLAPP": False,
        "cVID": "",
        "cID": "",
        "Travs": {
            "AdtTrv": [{"EmlAdd": "", "LName": "", "fName": "", "Title": ""}],
            "ChdTrv": [],
            "InfTrv": [],
        },
    }
    payload.update(base_payload)
    res = requests.post(LOCK_ENDPOINT, json=payload, timeout=60)
    res.raise_for_status()
    return res.json()


# --------------------------------------------------------------------------- #
# Main flow
# --------------------------------------------------------------------------- #
def main() -> None:
    print("=== EaseMyTrip Flight Lock Helper ===")

    # Login
    phone = prompt("Enter phone number for login", "7838958509")
    login_key = login_and_get_key(phone)
    print(f"LoginKey fetched: {login_key[:6]}... (truncated)")

    # Search inputs
    origin_raw = prompt("Origin airport code", "DEL")
    destination_raw = prompt("Destination airport code", "BOM")
    outbound_date = prompt("Outbound date (YYYY-MM-DD)", "2026-01-10")
    return_date = ""  # keeping one-way for lock flow
    adults = int(prompt("Adults", "1") or "1")
    children = int(prompt("Children", "0") or "0")
    infants = int(prompt("Infants", "0") or "0")

    origin, destination, is_international = normalize_airports(origin_raw, destination_raw)
    is_roundtrip = bool(return_date)

    # Flight token and search
    itk_token = fetch_itk_token()
    search_payload = build_search_payload(
        token=itk_token,
        origin=origin,
        destination=destination,
        outbound_date=outbound_date,
        return_date=return_date or None,
        adults=adults,
        children=children,
        infants=infants,
        is_international=is_international,
    )
    search_response = call_search(search_payload)
    raw_segment_map = build_raw_segment_map(search_response)

    search_context = {
        "origin": origin,
        "destination": destination,
        "outbound_date": outbound_date,
        "return_date": return_date or None,
        "adults": adults,
        "children": children,
        "infants": infants,
    }
    flights = process_flights_for_display(
        search_response, is_roundtrip, is_international, search_context
    )
    selected_flight = select_flight(flights)
    fare_index = select_fare(selected_flight)

    seg_key = selected_flight.get("segment_key")
    if not seg_key:
        raise RuntimeError("Segment key not found on selected flight.")
    if seg_key not in raw_segment_map:
        raise RuntimeError("Raw segment data missing for selected flight.")

    raw_seg_info = raw_segment_map[seg_key]
    new_segment = build_new_segment_js(
        raw_segment=raw_seg_info["segment"],
        search_response=search_response,
        origin=selected_flight.get("origin", origin),
        destination=selected_flight.get("destination", destination),
        adults=adults,
        children=children,
        infants=infants,
        is_roundtrip=is_roundtrip,
        fare_index=fare_index,
    )

    segment_object=json.loads(new_segment)

    reprice_response = call_reprice(
        segment_object,
        search_response,
        raw_seg_info["journey_index"],
        login_key,
        adults,
        children,
        infants,
    )

    seg_key_repriced = (
        reprice_response.get("jrneys", [{}])[0]
        .get("segs", [{}])[0]
        .get("segKey")
    )
    if not seg_key_repriced:
        raise RuntimeError("Reprice response missing segKey.")
    fare_info = (
        reprice_response.get("jrneys", [{}])[0].get("segs", [{}])[0].get("Fare", {})
    )
    total_fare = fare_info.get("TtlFrWthMkp") or fare_info.get("TtlFr") or 0

    lock_payload_resp = call_lock(
        seg_key=seg_key_repriced,
        login_key=login_key,
        lock_amount=total_fare or 0,
    )

    price_lock_id = lock_payload_resp.get("PriceLockID") or lock_payload_resp.get("PriceLockId")
    if not price_lock_id:
        raise RuntimeError("PriceLockID not found in lock response.")

    checkout_url = f"https://safepay.easemytrip.com/new/checkout?orderid={price_lock_id}"
    print(f"\nCheckout URL: {checkout_url}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}")
