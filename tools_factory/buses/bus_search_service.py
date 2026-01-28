"""Bus Search API Logic.

This module handles all bus search operations including:
- Searching buses via EaseMyTrip Bus API
- Processing bus results
- Extracting boarding/dropping points, amenities, cancellation policies

"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from emt_client.clients.bus_client import BusApiClient
from .bus_schema import (
    BusSearchInput,
    BusInfo,
    BoardingPoint,
    DroppingPoint,
    CancellationPolicy,
    WhatsappBusFormat,
    WhatsappBusFinalResponse,
)

# Bus API endpoint from docA
BUS_API_URL = "http://busapi.easemytrip.com/v1/api/detail/List/"

# API Key from docA
BUS_API_KEY = "dsasa4gfdg4543gfdg6ghgf45325gfd"

# City ID to Name mapping (common cities)
CITY_ID_TO_NAME = {
    "733": "Delhi",
    "757": "Manali",
    "1": "Mumbai",
    "2": "Bangalore",
    "3": "Chennai",
    "4": "Kolkata",
    "5": "Hyderabad",
    "6": "Pune",
    "7": "Ahmedabad",
    "8": "Jaipur",
    "9": "Lucknow",
    "10": "Chandigarh",
}


def _get_city_name(city_id: str) -> str:
    """Get city name from city ID. Returns ID if not found."""
    return CITY_ID_TO_NAME.get(city_id, city_id)


def _convert_date_to_api_format(date_str: str) -> str:
    """Convert YYYY-MM-DD to dd-MM-yyyy format for Bus API.
    
    As per docA: SearchDate should be in date format 'dd-MM-yyyy'
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d-%m-%Y")
    except ValueError:
        return date_str


def _build_bus_listing_url(
    source_id: str,
    destination_id: str,
    journey_date: str,
    source_name: str = None,
    destination_name: str = None,
) -> str:
    """Build EaseMyTrip bus listing page URL.
    
    Real website URL format:
    https://bus.easemytrip.com/home/list?org=Delhi&des=Manali&date=03-02-2026&searchid=733_757&CCode=IN&AppCode=Emt
    
    Args:
        source_id: Source city ID (e.g., "733")
        destination_id: Destination city ID (e.g., "757")
        journey_date: Journey date in YYYY-MM-DD format
        source_name: Optional source city name
        destination_name: Optional destination city name
    
    Returns:
        Bus listing URL
    """
    # Convert date from YYYY-MM-DD to dd-MM-yyyy for URL
    date_formatted = _convert_date_to_api_format(journey_date)
    
    # Get city names
    org_name = source_name or _get_city_name(source_id)
    des_name = destination_name or _get_city_name(destination_id)
    
    return (
        f"https://bus.easemytrip.com/home/list"
        f"?org={org_name}&des={des_name}&date={date_formatted}"
        f"&searchid={source_id}_{destination_id}&CCode=IN&AppCode=Emt"
    )


def _build_bus_deeplink(
    source_id: str,
    destination_id: str,
    journey_date: str,
    bus_id: str,
    source_name: str = None,
    destination_name: str = None,
) -> str:
    """Build EaseMyTrip bus booking deeplink.
    
    Uses the actual website URL format for the bus listing page.
    The specific bus can be selected from the listing.
    
    Args:
        source_id: Source city ID (e.g., "733")
        destination_id: Destination city ID (e.g., "757")
        journey_date: Journey date in YYYY-MM-DD format
        bus_id: Bus ID from API response ("id" field in AvailableTrips)
        source_name: Optional source city name
        destination_name: Optional destination city name
    
    Returns:
        Booking URL for the bus
    """
    # Use the listing URL - user can select the specific bus from there
    return _build_bus_listing_url(
        source_id=source_id,
        destination_id=destination_id,
        journey_date=journey_date,
        source_name=source_name,
        destination_name=destination_name,
    )


def _extract_amenities(lst_amenities: List[Dict[str, Any]]) -> List[str]:
    """Extract amenity names from lstamenities array in API response (docA).
    
    docA example:
    "lstamenities": [
        {"name": "USB Charging Point", "id": 25},
        {"name": "Water Bottle", "id": 1},
        {"name": "AC", "id": 24}
    ]
    """
    if not lst_amenities:
        return []
    return [amenity.get("name", "") for amenity in lst_amenities if amenity.get("name")]


def _process_boarding_points(bd_points: List[Dict[str, Any]]) -> List[BoardingPoint]:
    """Process bdPoints array from API response (docA).
    
    docA example:
    "bdPoints": [
        {
            "bdPoint": "Kashmere Gate...",
            "bdLongName": "Kashmere Gate",
            "bdid": "303",
            "bdlocation": "Kashmere Gate,Platform no.59,60",
            "landmark": "Kashmere Gate",
            "time": "23:14",
            "contactNumber": "09667676919",
            "latitude": null,
            "longitude": null
        }
    ]
    """
    if not bd_points:
        return []
    
    processed = []
    for bp in bd_points:
        try:
            processed.append(BoardingPoint(
                bdid=bp.get("bdid", ""),
                bdLongName=bp.get("bdLongName", ""),
                bdlocation=bp.get("bdlocation"),
                landmark=bp.get("landmark"),
                time=bp.get("time"),
                contactNumber=bp.get("contactNumber"),
                latitude=bp.get("latitude"),
                longitude=bp.get("longitude"),
            ))
        except Exception:
            continue
    return processed


def _process_dropping_points(dp_points: List[Dict[str, Any]]) -> List[DroppingPoint]:
    """Process dpPoints array from API response (docA).
    
    docA example:
    "dpPoints": [
        {
            "dpId": "139",
            "dpName": "Patlikuhal Bypass near fishfarm",
            "locatoin": "Patlikuhal Bypass...",  # Note: typo in API
            "dpTime": "10:18",
            "contactNumber": null,
            "landmark": null,
            "latitude": null,
            "longitude": null
        }
    ]
    """
    if not dp_points:
        return []
    
    processed = []
    for dp in dp_points:
        try:
            processed.append(DroppingPoint(
                dpId=dp.get("dpId", ""),
                dpName=dp.get("dpName", ""),
                locatoin=dp.get("locatoin"),  # Note: API has typo "locatoin"
                dpTime=dp.get("dpTime"),
                contactNumber=dp.get("contactNumber"),
                landmark=dp.get("landmark"),
                latitude=dp.get("latitude"),
                longitude=dp.get("longitude"),
            ))
        except Exception:
            continue
    return processed


def _process_cancellation_policy(cancel_policy_list: List[Dict[str, Any]]) -> List[CancellationPolicy]:
    """Process cancelPolicyList array from API response (docA).
    
    docA example:
    "cancelPolicyList": [
        {
            "timeFrom": 0,
            "timeTo": 6,
            "percentageCharge": 100.0,
            "flatCharge": 0,
            "isFlat": false
        },
        {
            "timeFrom": 6,
            "timeTo": 12,
            "percentageCharge": 80.0,
            "flatCharge": 0,
            "isFlat": false
        }
    ]
    """
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
    source_name: str = None,
    destination_name: str = None,
    filter_volvo: Optional[bool] = None,
) -> Optional[BusInfo]:
    """Process a single bus entry from AvailableTrips array in API response (docA).
    
    docA AvailableTrips fields:
    - id, Travels, busType, departureTime, ArrivalTime, duration
    - AvailableSeats, price, fares, AC, nonAC, isVolvo
    - seater, sleeper, isSemiSleeper, rt, liveTrackingAvailable
    - isCancellable, mTicketEnabled, departureDate, arrivalDate
    - routeId, operatorid, engineId
    - bdPoints, dpPoints, lstamenities, cancelPolicyList
    """
    # Apply Volvo filter if specified (from docA request: "isVolvo")
    is_volvo = bus.get("isVolvo", False)
    if filter_volvo is True and not is_volvo:
        return None

    # Get bus ID (from docA: "id" field)
    bus_id = str(bus.get("id", ""))
    
    # Build booking deeplink using real website URL format
    book_now = _build_bus_deeplink(
        source_id=source_id,
        destination_id=destination_id,
        journey_date=journey_date,
        bus_id=bus_id,
        source_name=source_name,
        destination_name=destination_name,
    )

    # Process nested arrays from docA
    boarding_points = _process_boarding_points(bus.get("bdPoints", []))
    dropping_points = _process_dropping_points(bus.get("dpPoints", []))
    amenities = _extract_amenities(bus.get("lstamenities", []))
    cancellation_policy = _process_cancellation_policy(bus.get("cancelPolicyList", []))

    # Extract fares array (from docA: "fares": ["559", "549"])
    fares = bus.get("fares", [])
    if not fares:
        price = bus.get("price", "0")
        fares = [str(price)] if price else ["0"]

    return BusInfo(
        bus_id=bus_id,
        operator_name=bus.get("Travels", ""),
        bus_type=bus.get("busType", ""),
        departure_time=bus.get("departureTime", ""),
        arrival_time=bus.get("ArrivalTime", ""),
        duration=bus.get("duration", ""),
        available_seats=str(bus.get("AvailableSeats", "0")),
        price=str(bus.get("price", "0")),
        fares=fares,
        is_ac=bus.get("AC", False),
        is_non_ac=bus.get("nonAC", False),
        is_volvo=is_volvo,
        is_seater=bus.get("seater", False),
        is_sleeper=bus.get("sleeper", False),
        is_semi_sleeper=bus.get("isSemiSleeper", False),
        rating=bus.get("rt"),
        live_tracking_available=bus.get("liveTrackingAvailable", False),
        is_cancellable=bus.get("isCancellable", False),
        m_ticket_enabled=str(bus.get("mTicketEnabled", "")),
        departure_date=bus.get("departureDate", ""),
        arrival_date=bus.get("arrivalDate", ""),
        route_id=str(bus.get("routeId", "")),
        operator_id=str(bus.get("operatorid", "")),
        engine_id=bus.get("engineId", 0),
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
    source_name: str = None,
    destination_name: str = None,
    filter_volvo: Optional[bool] = None,
) -> Dict[str, Any]:
    """Process raw bus search response from API (docA).

    Args:
        search_response: Raw API response from EaseMyTrip Bus API
        source_id: Source city ID
        destination_id: Destination city ID
        journey_date: Journey date in YYYY-MM-DD format
        source_name: Optional source city name
        destination_name: Optional destination city name
        filter_volvo: Optional Volvo filter

    Returns:
        Dict containing processed bus list and metadata
        
    docA response fields used:
    - AvailableTrips: Array of bus objects
    - TotalTrips: Total number of trips
    - AcCount: Count of AC buses
    - NonAcCount: Count of Non-AC buses
    - MaxPrice, MinPrice: Price range
    - isBusAvailable: Boolean availability flag
    """
    buses = []
    
    # Get available trips from response (docA: "AvailableTrips" array)
    available_trips = search_response.get("AvailableTrips", [])
    
    if not available_trips:
        return {
            "buses": [],
            "total_count": 0,
            "total_trips": search_response.get("TotalTrips", 0),
            "ac_count": search_response.get("AcCount", 0),
            "non_ac_count": search_response.get("NonAcCount", 0),
            "is_bus_available": search_response.get("isBusAvailable", False),
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
        "total_trips": search_response.get("TotalTrips", 0),
        "ac_count": search_response.get("AcCount", 0),
        "non_ac_count": search_response.get("NonAcCount", 0),
        "max_price": search_response.get("MaxPrice"),
        "min_price": search_response.get("MinPrice"),
        "is_bus_available": search_response.get("isBusAvailable", False),
    }


async def search_buses(
    source_id: str,
    destination_id: str,
    journey_date: str,
    is_volvo: Optional[bool] = None,
    source_name: str = None,
    destination_name: str = None,
) -> Dict[str, Any]:
    """Call EaseMyTrip bus search API.

    Args:
        source_id: Source city ID (e.g., "733" for Delhi) - from docA
        destination_id: Destination city ID (e.g., "757" for Manali) - from docA
        journey_date: Journey date in YYYY-MM-DD format
        is_volvo: Optional filter for Volvo buses (docA: "isVolvo")
        source_name: Optional source city name for URL building
        destination_name: Optional destination city name for URL building

    Returns:
        Dict containing processed bus search results
        
    API Endpoint (from docA):
        POST http://busapi.easemytrip.com/v1/api/detail/List/
        
    Request payload (from docA):
        {
            "sourceId": "733",
            "destinationId": "757",
            "date": "08-11-2025",
            "key": "...",
            "version": "1",
            "isVrl": "False",
            "isVolvo": "False",
            "IsAndroidIos_Hit": false,
            "agentCode": "",
            "CountryCode": "IN"
        }
    """
    client = BusApiClient()

    # Convert date format for API (YYYY-MM-DD -> dd-MM-yyyy as per docA)
    api_date = _convert_date_to_api_format(journey_date)

    # Build payload exactly as per docA
    payload = {
        "sourceId": source_id,
        "destinationId": destination_id,
        "date": api_date,
        "key": BUS_API_KEY,
        "version": "1",
        "isVrl": "False",
        "isVolvo": "True" if is_volvo else "False",
        "IsAndroidIos_Hit": False,
        "agentCode": "",
        "CountryCode": "IN",
    }

    try:
        data = await client.search(BUS_API_URL, payload)
    except Exception as e:
        return {
            "error": "API_ERROR",
            "message": str(e),
            "buses": [],
            "total_count": 0,
            "is_bus_available": False,
        }

    # Check if response is error string
    if isinstance(data, str):
        return {
            "error": "INVALID_SEARCH",
            "message": data,
            "buses": [],
            "total_count": 0,
            "is_bus_available": False,
        }

    # Check if buses are available (docA: "isBusAvailable" field)
    if not data.get("isBusAvailable", False):
        return {
            "error": "NO_BUSES",
            "message": "No buses available for this route and date",
            "buses": [],
            "total_count": 0,
            "is_bus_available": False,
        }

    # Get city names for URL building
    src_name = source_name or _get_city_name(source_id)
    dest_name = destination_name or _get_city_name(destination_id)

    # Process results
    processed_data = process_bus_results(
        data,
        source_id,
        destination_id,
        journey_date,
        src_name,
        dest_name,
        is_volvo,
    )
    
    # Add search context to response
    processed_data["source_id"] = source_id
    processed_data["destination_id"] = destination_id
    processed_data["source_name"] = src_name
    processed_data["destination_name"] = dest_name
    processed_data["journey_date"] = journey_date
    processed_data["filter_volvo"] = is_volvo
    
    # Add view_all_link for the carousel
    processed_data["view_all_link"] = _build_bus_listing_url(
        source_id=source_id,
        destination_id=destination_id,
        journey_date=journey_date,
        source_name=src_name,
        destination_name=dest_name,
    )

    return processed_data


def extract_bus_summary(bus: Dict[str, Any]) -> Dict[str, Any]:
    """Extract summary info from processed bus data.
    
    Args:
        bus: Processed bus dict from process_bus_results
        
    Returns:
        Summary dict with key bus information
    """
    fares = bus.get("fares", [])
    
    # Find cheapest fare from fares array
    cheapest_fare = None
    for fare in fares:
        try:
            fare_val = float(fare)
            if cheapest_fare is None or fare_val < cheapest_fare:
                cheapest_fare = fare_val
        except (ValueError, TypeError):
            continue

    # Fallback to price field if no fares
    if cheapest_fare is None:
        try:
            cheapest_fare = float(bus.get("price", 0))
        except (ValueError, TypeError):
            cheapest_fare = 0

    # Get first boarding and dropping point names
    boarding_points = bus.get("boarding_points", [])
    dropping_points = bus.get("dropping_points", [])
    
    first_boarding = ""
    if boarding_points:
        first_boarding = boarding_points[0].get("bd_long_name", "")
    
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
    """Build WhatsApp-formatted response for bus search results.
    
    Args:
        payload: Original search input
        bus_results: Processed bus search results
        
    Returns:
        WhatsappBusFinalResponse with formatted data
    """
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

    whatsapp_json = WhatsappBusFormat(
        options=options,
        currency="INR",
        view_all_buses_url=bus_results.get("view_all_link", ""),
    )

    return WhatsappBusFinalResponse(
        response_text=f"Found {len(options)} buses from {payload.source_id} to {payload.destination_id}",
        whatsapp_json=whatsapp_json,
    )


# =====================================================================
# SEAT LAYOUT / SEAT BIND SERVICE (docA: POST /v1/api/detail/SeatBind/)
# =====================================================================

# Seat Bind API endpoint from docA
SEAT_BIND_API_URL = "http://busapi.easemytrip.com/v1/api/detail/SeatBind/"


def _process_seat(seat: Dict[str, Any], deck_name: str) -> Optional[Dict[str, Any]]:
    """Process a single seat from the API response.
    
    docA seat fields may include:
    - seatNumber, seatName, seatType, seatStatus
    - fare, row, column, deck, width, length
    - isLadies, isBooked, isAvailable
    """
    if not seat:
        return None
    
    # Get seat status - check multiple possible field names
    seat_status = (
        seat.get("seatStatus") or 
        seat.get("SeatStatus") or 
        seat.get("status") or 
        seat.get("Status") or 
        "Unknown"
    )
    seat_status_lower = str(seat_status).lower()
    
    # Determine availability from various possible indicators
    is_available = (
        seat_status_lower in ["available", "empty", "free", "1", "true"] or
        seat.get("isAvailable", False) or
        seat.get("IsAvailable", False) or
        seat.get("available", False)
    )
    
    is_booked = (
        seat_status_lower in ["booked", "reserved", "sold", "0", "false"] or
        seat.get("isBooked", False) or
        seat.get("IsBooked", False) or
        seat.get("booked", False)
    )
    
    is_ladies = (
        seat.get("isLadies", False) or
        seat.get("IsLadies", False) or
        seat.get("ladies", False) or
        "ladies" in seat_status_lower or
        "female" in seat_status_lower
    )
    
    is_blocked = (
        seat_status_lower in ["blocked", "unavailable", "disabled"] or
        seat.get("isBlocked", False) or
        seat.get("IsBlocked", False)
    )
    
    # Get seat number from various possible field names
    seat_number = str(
        seat.get("seatNumber") or 
        seat.get("SeatNumber") or 
        seat.get("SeatNo") or 
        seat.get("seatNo") or 
        seat.get("number") or
        seat.get("name") or
        ""
    )
    
    # Get seat name
    seat_name = str(
        seat.get("seatName") or 
        seat.get("SeatName") or 
        seat.get("name") or
        seat_number
    )
    
    # Get seat type
    seat_type = (
        seat.get("seatType") or 
        seat.get("SeatType") or 
        seat.get("type") or
        "ST"
    )
    
    # Get fare
    fare = str(
        seat.get("fare") or 
        seat.get("Fare") or 
        seat.get("SeatFare") or 
        seat.get("seatFare") or 
        seat.get("price") or
        "0"
    )
    
    # Get position
    row = int(seat.get("row") or seat.get("Row") or seat.get("rowNo") or 0)
    column = int(seat.get("column") or seat.get("Column") or seat.get("colNo") or 0)
    
    return {
        "seat_number": seat_number,
        "seat_name": seat_name,
        "seat_type": seat_type,
        "seat_status": seat_status,
        "is_available": is_available,
        "is_ladies": is_ladies,
        "fare": fare,
        "row": row,
        "column": column,
        "deck": deck_name,
        "width": int(seat.get("width") or seat.get("Width") or 1),
        "length": int(seat.get("length") or seat.get("Length") or 1),
        "is_booked": is_booked,
        "is_blocked": is_blocked,
    }


def _process_deck(deck_data: Any, deck_name: str) -> Optional[Dict[str, Any]]:
    """Process a deck (lower/upper) from the API response."""
    if not deck_data:
        return None
    
    # Handle if deck_data is a dict with seats inside
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
) -> Dict[str, Any]:
    """Process raw seat layout API response.
    
    docA response structure may include:
    - seatLayout or SeatLayout
    - lowerDeck, upperDeck
    - seats array with seat details
    - fareDetails
    """
    if not api_response:
        return {
            "success": False,
            "message": "Empty API response",
            "layout": None,
            "raw_response": api_response,
        }
    
    # Try to find seat layout data from various possible locations in response
    seat_layout = None
    possible_keys = [
        "seatLayout", "SeatLayout", "Result", "result", 
        "data", "Data", "response", "Response",
        "seatDetails", "SeatDetails", "layout", "Layout"
    ]
    
    for key in possible_keys:
        if key in api_response and api_response[key]:
            seat_layout = api_response[key]
            break
    
    # If no nested structure found, use the response itself
    if not seat_layout:
        seat_layout = api_response
    
    # Extract lower deck - try multiple possible keys
    lower_deck_data = None
    lower_keys = ["lowerDeck", "LowerDeck", "lower", "Lower", "lowerSeats", "LowerSeats"]
    for key in lower_keys:
        if key in seat_layout and seat_layout[key]:
            lower_deck_data = seat_layout[key]
            break
    
    lower_deck = _process_deck(lower_deck_data, "Lower")
    
    # Extract upper deck - try multiple possible keys
    upper_deck_data = None
    upper_keys = ["upperDeck", "UpperDeck", "upper", "Upper", "upperSeats", "UpperSeats"]
    for key in upper_keys:
        if key in seat_layout and seat_layout[key]:
            upper_deck_data = seat_layout[key]
            break
    
    upper_deck = _process_deck(upper_deck_data, "Upper")
    
    # If no deck structure, try flat seats array
    if not lower_deck and not upper_deck:
        seats_keys = ["seats", "Seats", "seatList", "SeatList", "allSeats"]
        for key in seats_keys:
            if key in seat_layout and seat_layout[key]:
                lower_deck = _process_deck(seat_layout[key], "Lower")
                break
    
    # Count seats
    all_seats = []
    if lower_deck and lower_deck.get("seats"):
        all_seats.extend(lower_deck["seats"])
    if upper_deck and upper_deck.get("seats"):
        all_seats.extend(upper_deck["seats"])
    
    total_seats = len(all_seats)
    available_seats = sum(1 for s in all_seats if s.get("is_available"))
    booked_seats = sum(1 for s in all_seats if s.get("is_booked"))
    
    # Extract bus info from various possible locations
    bus_type = (
        seat_layout.get("busType") or
        seat_layout.get("BusType") or
        api_response.get("busType") or
        api_response.get("BusType") or
        ""
    )
    operator_name = (
        seat_layout.get("travels") or
        seat_layout.get("Travels") or
        seat_layout.get("operatorName") or
        api_response.get("Travels") or
        api_response.get("operatorName") or
        ""
    )
    
    # Extract timing
    boarding_time = (
        seat_layout.get("boardingTime") or
        seat_layout.get("BoardingTime") or
        seat_layout.get("departureTime") or
        ""
    )
    dropping_time = (
        seat_layout.get("droppingTime") or
        seat_layout.get("DroppingTime") or
        seat_layout.get("arrivalTime") or
        ""
    )
    
    # Extract fare details
    fare_details = (
        seat_layout.get("fareDetails") or
        seat_layout.get("FareDetails") or
        seat_layout.get("fares") or
        seat_layout.get("Fares") or
        []
    )
    
    layout_info = {
        "bus_id": bus_id,
        "bus_type": bus_type,
        "operator_name": operator_name,
        "total_seats": total_seats,
        "available_seats": available_seats,
        "booked_seats": booked_seats,
        "lower_deck": lower_deck,
        "upper_deck": upper_deck,
        "boarding_point": boarding_point,
        "dropping_point": dropping_point,
        "boarding_time": boarding_time,
        "dropping_time": dropping_time,
        "fare_details": fare_details if isinstance(fare_details, list) else [],
    }
    
    # Determine success based on whether we found any seats
    success = total_seats > 0
    
    if success:
        message = f"Found {available_seats} available seats out of {total_seats}"
    else:
        message = "Seat layout not available for this bus. This may be due to the bus operator not providing seat data through this API."
    
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
) -> Dict[str, Any]:
    """Call EaseMyTrip seat bind/layout API.
    
    Args:
        source_id: Source city ID
        destination_id: Destination city ID
        journey_date: Journey date in YYYY-MM-DD format
        bus_id: Bus ID from search results
        route_id: Route ID from search results
        engine_id: Engine ID from search results
        boarding_point_id: Selected boarding point ID
        dropping_point_id: Selected dropping point ID
    
    Returns:
        Dict containing seat layout information
        
    API Endpoint (from docA):
        POST http://busapi.easemytrip.com/v1/api/detail/SeatBind/
    
    Request payload (from docA):
        {
            "sourceId": "733",
            "destinationId": "757",
            "date": "08-11-2025",
            "busId": "5904671",
            "routeId": "12345",
            "engineId": 4,
            "boardingPointId": "303",
            "droppingPointId": "139",
            "key": "...",
            "version": "1"
        }
        
    Note: Some bus operators (like IntrCity SmartBus with engineId=13) may not 
    provide seat layout data through this API. In such cases, the seat layout 
    will show 0 seats.
    """
    client = BusApiClient()
    
    # Convert date format for API
    api_date = _convert_date_to_api_format(journey_date)
    
    # Build payload as per docA
    payload = {
        "sourceId": source_id,
        "destinationId": destination_id,
        "date": api_date,
        "busId": bus_id,
        "routeId": route_id,
        "engineId": engine_id,
        "boardingPointId": boarding_point_id,
        "droppingPointId": dropping_point_id,
        "key": BUS_API_KEY,
        "version": "1",
    }
    
    try:
        data = await client.search(SEAT_BIND_API_URL, payload)
    except Exception as e:
        return {
            "success": False,
            "message": f"API Error: {str(e)}",
            "layout": None,
            "raw_response": None,
        }
    
    # Check if response is error string
    if isinstance(data, str):
        return {
            "success": False,
            "message": data,
            "layout": None,
            "raw_response": data,
        }
    
    # Check for API error response
    error_msg = data.get("error") or data.get("Error") or data.get("errorMessage") or data.get("ErrorMessage")
    if error_msg:
        return {
            "success": False,
            "message": str(error_msg),
            "layout": None,
            "raw_response": data,
        }
    
    # Process the response
    return process_seat_layout_response(
        data,
        bus_id,
        boarding_point_id,
        dropping_point_id,
    )