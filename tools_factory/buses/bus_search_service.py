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

BUS_API_URL = "http://busapi.easemytrip.com/v1/api/detail/List/"

BUS_API_KEY = "dsasa4gfdg4543gfdg6ghgf45325gfd"

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
    return CITY_ID_TO_NAME.get(city_id, city_id)


def _convert_date_to_api_format(date_str: str) -> str:
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
    date_formatted = _convert_date_to_api_format(journey_date)
    
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
    return _build_bus_listing_url(
        source_id=source_id,
        destination_id=destination_id,
        journey_date=journey_date,
        source_name=source_name,
        destination_name=destination_name,
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
    is_volvo = bus.get("isVolvo", False)
    if filter_volvo is True and not is_volvo:
        return None

    bus_id = str(bus.get("id", ""))
    
    book_now = _build_bus_deeplink(
        source_id=source_id,
        destination_id=destination_id,
        journey_date=journey_date,
        bus_id=bus_id,
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
    buses = []
    
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

    client = BusApiClient()

    api_date = _convert_date_to_api_format(journey_date)

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

    if isinstance(data, str):
        return {
            "error": "INVALID_SEARCH",
            "message": data,
            "buses": [],
            "total_count": 0,
            "is_bus_available": False,
        }

    if not data.get("isBusAvailable", False):
        return {
            "error": "NO_BUSES",
            "message": "No buses available for this route and date",
            "buses": [],
            "total_count": 0,
            "is_bus_available": False,
        }

    src_name = source_name or _get_city_name(source_id)
    dest_name = destination_name or _get_city_name(destination_id)

    processed_data = process_bus_results(
        data,
        source_id,
        destination_id,
        journey_date,
        src_name,
        dest_name,
        is_volvo,
    )
    
    processed_data["source_id"] = source_id
    processed_data["destination_id"] = destination_id
    processed_data["source_name"] = src_name
    processed_data["destination_name"] = dest_name
    processed_data["journey_date"] = journey_date
    processed_data["filter_volvo"] = is_volvo
    
    processed_data["view_all_link"] = _build_bus_listing_url(
        source_id=source_id,
        destination_id=destination_id,
        journey_date=journey_date,
        source_name=src_name,
        destination_name=dest_name,
    )

    return processed_data


def extract_bus_summary(bus: Dict[str, Any]) -> Dict[str, Any]:

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


SEAT_BIND_API_URL = "http://busapi.easemytrip.com/v1/api/detail/SeatBind/"


def _process_seat(seat: Dict[str, Any], deck_name: str) -> Optional[Dict[str, Any]]:

    if not seat:
        return None
    
    seat_status = (
        seat.get("seatStatus") or 
        seat.get("SeatStatus") or 
        seat.get("status") or 
        seat.get("Status") or 
        "Unknown"
    )
    seat_status_lower = str(seat_status).lower()
    
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
    
    seat_number = str(
        seat.get("seatNumber") or 
        seat.get("SeatNumber") or 
        seat.get("SeatNo") or 
        seat.get("seatNo") or 
        seat.get("number") or
        seat.get("name") or
        ""
    )
    
    seat_name = str(
        seat.get("seatName") or 
        seat.get("SeatName") or 
        seat.get("name") or
        seat_number
    )
    
    seat_type = (
        seat.get("seatType") or 
        seat.get("SeatType") or 
        seat.get("type") or
        "ST"
    )
    
    fare = str(
        seat.get("fare") or 
        seat.get("Fare") or 
        seat.get("SeatFare") or 
        seat.get("seatFare") or 
        seat.get("price") or
        "0"
    )
    
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
) -> Dict[str, Any]:

    if not api_response:
        return {
            "success": False,
            "message": "Empty API response",
            "layout": None,
            "raw_response": api_response,
        }
    
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
    
    if not seat_layout:
        seat_layout = api_response
    
    lower_deck_data = None
    lower_keys = ["lowerDeck", "LowerDeck", "lower", "Lower", "lowerSeats", "LowerSeats"]
    for key in lower_keys:
        if key in seat_layout and seat_layout[key]:
            lower_deck_data = seat_layout[key]
            break
    
    lower_deck = _process_deck(lower_deck_data, "Lower")
    
    upper_deck_data = None
    upper_keys = ["upperDeck", "UpperDeck", "upper", "Upper", "upperSeats", "UpperSeats"]
    for key in upper_keys:
        if key in seat_layout and seat_layout[key]:
            upper_deck_data = seat_layout[key]
            break
    
    upper_deck = _process_deck(upper_deck_data, "Upper")
    
    if not lower_deck and not upper_deck:
        seats_keys = ["seats", "Seats", "seatList", "SeatList", "allSeats"]
        for key in seats_keys:
            if key in seat_layout and seat_layout[key]:
                lower_deck = _process_deck(seat_layout[key], "Lower")
                break
    
    all_seats = []
    if lower_deck and lower_deck.get("seats"):
        all_seats.extend(lower_deck["seats"])
    if upper_deck and upper_deck.get("seats"):
        all_seats.extend(upper_deck["seats"])
    
    total_seats = len(all_seats)
    available_seats = sum(1 for s in all_seats if s.get("is_available"))
    booked_seats = sum(1 for s in all_seats if s.get("is_booked"))
    
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

    client = BusApiClient()
    
    api_date = _convert_date_to_api_format(journey_date)
    
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
    
    if isinstance(data, str):
        return {
            "success": False,
            "message": data,
            "layout": None,
            "raw_response": data,
        }
    
    error_msg = data.get("error") or data.get("Error") or data.get("errorMessage") or data.get("ErrorMessage")
    if error_msg:
        return {
            "success": False,
            "message": str(error_msg),
            "layout": None,
            "raw_response": data,
        }
    
    return process_seat_layout_response(
        data,
        bus_id,
        boarding_point_id,
        dropping_point_id,
    )