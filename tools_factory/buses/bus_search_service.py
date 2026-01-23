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

# Bus API endpoint from 
BUS_API_URL = "http://busapi.easemytrip.com/v1/api/detail/List/"

# API Key from 
BUS_API_KEY = "dsasa4gfdg4543gfdg6ghgf45325gfd"


def _convert_date_to_api_format(date_str: str) -> str:
    """Convert YYYY-MM-DD to dd-MM-yyyy format for Bus API.
    
    As per : SearchDate should be in date format 'dd-MM-yyyy'
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d-%m-%Y")
    except ValueError:
        return date_str


def _build_bus_deeplink(
    source_id: str,
    destination_id: str,
    journey_date: str,
    bus_id: str,
) -> str:
    """Build EaseMyTrip bus booking deeplink.
    
    Args:
        source_id: Source city ID (e.g., "733")
        destination_id: Destination city ID (e.g., "757")
        journey_date: Journey date in YYYY-MM-DD format
        bus_id: Bus ID from API response ("id" field in AvailableTrips)
    
    Returns:
        Booking URL for the bus
    """
    # Convert date from YYYY-MM-DD to dd-MM-yyyy for URL
    date_formatted = _convert_date_to_api_format(journey_date)
    
    return (
        f"https://www.easemytrip.com/bus/booking/"
        f"?src={source_id}&dest={destination_id}&date={date_formatted}&busId={bus_id}"
    )


def _extract_amenities(lst_amenities: List[Dict[str, Any]]) -> List[str]:
    """Extract amenity names from lstamenities array in API response ().
    
     example:
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
    """Process bdPoints array from API response ().
    
     example:
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
    """Process dpPoints array from API response ().
    
     example:
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
    """Process cancelPolicyList array from API response ().
    
     example:
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
    filter_volvo: Optional[bool] = None,
) -> Optional[BusInfo]:
    """Process a single bus entry from AvailableTrips array in API response ().
    
     AvailableTrips fields:
    - id, Travels, busType, departureTime, ArrivalTime, duration
    - AvailableSeats, price, fares, AC, nonAC, isVolvo
    - seater, sleeper, isSemiSleeper, rt, liveTrackingAvailable
    - isCancellable, mTicketEnabled, departureDate, arrivalDate
    - routeId, operatorid, engineId
    - bdPoints, dpPoints, lstamenities, cancelPolicyList
    """
    # Apply Volvo filter if specified (from  request: "isVolvo")
    is_volvo = bus.get("isVolvo", False)
    if filter_volvo is True and not is_volvo:
        return None

    # Get bus ID (from : "id" field)
    bus_id = str(bus.get("id", ""))
    
    # Build booking deeplink
    book_now = _build_bus_deeplink(
        source_id=source_id,
        destination_id=destination_id,
        journey_date=journey_date,
        bus_id=bus_id,
    )

    # Process nested arrays from 
    boarding_points = _process_boarding_points(bus.get("bdPoints", []))
    dropping_points = _process_dropping_points(bus.get("dpPoints", []))
    amenities = _extract_amenities(bus.get("lstamenities", []))
    cancellation_policy = _process_cancellation_policy(bus.get("cancelPolicyList", []))

    # Extract fares array (from : "fares": ["559", "549"])
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
    filter_volvo: Optional[bool] = None,
) -> Dict[str, Any]:
    """Process raw bus search response from API ().

    Args:
        search_response: Raw API response from EaseMyTrip Bus API
        source_id: Source city ID
        destination_id: Destination city ID
        journey_date: Journey date in YYYY-MM-DD format
        filter_volvo: Optional Volvo filter

    Returns:
        Dict containing processed bus list and metadata
        
     response fields used:
    - AvailableTrips: Array of bus objects
    - TotalTrips: Total number of trips
    - AcCount: Count of AC buses
    - NonAcCount: Count of Non-AC buses
    - MaxPrice, MinPrice: Price range
    - isBusAvailable: Boolean availability flag
    """
    buses = []
    
    # Get available trips from response (: "AvailableTrips" array)
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
) -> Dict[str, Any]:
    """Call EaseMyTrip bus search API.

    Args:
        source_id: Source city ID (e.g., "733" for Delhi) - from 
        destination_id: Destination city ID (e.g., "757" for Manali) - from 
        journey_date: Journey date in YYYY-MM-DD format
        is_volvo: Optional filter for Volvo buses (: "isVolvo")

    Returns:
        Dict containing processed bus search results
        
    API Endpoint (from ):
        POST http://busapi.easemytrip.com/v1/api/detail/List/
        
    Request payload (from ):
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

    # Convert date format for API (YYYY-MM-DD -> dd-MM-yyyy as per )
    api_date = _convert_date_to_api_format(journey_date)

    # Build payload exactly as per 
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

    # Check if buses are available (: "isBusAvailable" field)
    if not data.get("isBusAvailable", False):
        return {
            "error": "NO_BUSES",
            "message": "No buses available for this route and date",
            "buses": [],
            "total_count": 0,
            "is_bus_available": False,
        }

    # Process results
    processed_data = process_bus_results(
        data,
        source_id,
        destination_id,
        journey_date,
        is_volvo,
    )
    
    # Add search context to response
    processed_data["source_id"] = source_id
    processed_data["destination_id"] = destination_id
    processed_data["journey_date"] = journey_date
    processed_data["filter_volvo"] = is_volvo

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
    )

    return WhatsappBusFinalResponse(
        response_text=f"Found {len(options)} buses from {payload.source_id} to {payload.destination_id}",
        whatsapp_json=whatsapp_json,
    )