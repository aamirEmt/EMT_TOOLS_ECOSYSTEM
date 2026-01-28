"""Train Search API Logic.

This module handles all train search operations including:
- Searching trains via EaseMyTrip Railways API
- Processing train results
- Extracting class-wise availability and fares
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from emt_client.clients.train_client import TrainApiClient
from emt_client.utils import resolve_train_station
from emt_client.config import TRAIN_API_URL
from .train_schema import (
    TrainSearchInput,
    TrainClassAvailability,
    TrainInfo,
    WhatsappTrainFormat,
    WhatsappTrainFinalResponse,
)


def generate_view_all_link(
    from_station: str,
    to_station: str,
    journey_date: str,
) -> str:
    """
    Generate view all trains link for EaseMyTrip.

    Args:
        from_station: Full station display (e.g., "Delhi All Stations (NDLS)")
        to_station: Full station display (e.g., "Bhubaneswar (BBS)")
        journey_date: Journey date in DD-MM-YYYY format

    Returns:
        View all link URL

    Example:
        https://railways.easemytrip.com/TrainListInfo/Delhi-All-Stations-(NDLS)-to-Bhubaneswar-(BBS)/2/3-2-2026
    """
    try:
        # Format station names: replace spaces with hyphens
        from_formatted = from_station.replace(" ", "-")
        to_formatted = to_station.replace(" ", "-")

        # Remove leading zeros from date (DD-MM-YYYY -> D-M-YYYY)
        dt = datetime.strptime(journey_date, "%d-%m-%Y")
        date_formatted = f"{dt.day}-{dt.month}-{dt.year}"

        return f"https://railways.easemytrip.com/TrainListInfo/{from_formatted}-to-{to_formatted}/2/{date_formatted}"
    except Exception:
        return ""


def _build_train_deeplink(
    from_station_name: str,
    to_station_name: str,
    class_code: str,
    train_number: str,
    from_station_code: str,
    to_station_code: str,
    quota: str,
    departure_date: str,
) -> str:
    """Build EaseMyTrip train booking deeplink.

    URL format: https://railways.easemytrip.com/TrainInfo/{from}-to-{to}/{class}/{train}/{from_code}/{to_code}/{quota}/{date}
    Date format: DD-M-YYYY (e.g., 11-2-2026)
    """
    # Format station names: replace spaces with hyphens
    from_name_formatted = from_station_name.replace(" ", "-")
    to_name_formatted = to_station_name.replace(" ", "-")

    # Convert date from "29Jan2026" to "29-1-2026" format
    try:
        dt = datetime.strptime(departure_date, "%d%b%Y")
        date_formatted = f"{dt.day}-{dt.month}-{dt.year}"
    except ValueError:
        # Fallback: try to use as-is or return empty
        date_formatted = departure_date

    return (
        f"https://railways.easemytrip.com/TrainInfo/"
        f"{from_name_formatted}-to-{to_name_formatted}/"
        f"{class_code}/{train_number}/{from_station_code}/{to_station_code}/{quota}/{date_formatted}"
    )


def _get_running_days(train: Dict[str, Any]) -> List[str]:
    """Extract running days from train data."""
    days = []
    day_mapping = {
        "runningMon": "Mon",
        "runningTue": "Tue",
        "runningWed": "Wed",
        "runningThu": "Thu",
        "runningFri": "Fri",
        "runningSat": "Sat",
        "runningSun": "Sun",
    }
    for key, day_name in day_mapping.items():
        if train.get(key) == "Y":
            days.append(day_name)
    return days


def _process_class_availability(
    train_class_wise_fare: List[Dict[str, Any]],
    preferred_class: Optional[str] = None,
    from_station_name: str = "",
    to_station_name: str = "",
    train_number: str = "",
    from_station_code: str = "",
    to_station_code: str = "",
    quota: str = "GN",
    departure_date: str = "",
) -> Optional[List[TrainClassAvailability]]:
    """Process TrainClassWiseFare to extract class availability info.

    Note: "Tap To Refresh" is now handled client-side with a button in the UI.

    If preferred_class is specified, checks if the train has that class.
    If the train has the preferred class, returns ALL classes for that train.
    If the train doesn't have the preferred class, returns None to exclude the train.
    """
    # If preferred class is specified, first check if this train has it
    if preferred_class:
        has_preferred_class = any(
            class_info.get("enqClass", "").upper() == preferred_class.upper()
            for class_info in train_class_wise_fare
        )
        if not has_preferred_class:
            return None  # Train doesn't have preferred class, exclude it

    classes = []

    for class_info in train_class_wise_fare:
        class_code = class_info.get("enqClass", "")
        class_name = class_info.get("enqClassName", "")
        fare = class_info.get("totalFare") or "0"
        fare_updated = class_info.get("UpdationTime") or ""

        # Get availability from avlDayList
        availability_status = "N/A"
        avl_day_list = class_info.get("avlDayList", [])
        if avl_day_list and len(avl_day_list) > 0:
            availability_status = avl_day_list[0].get("availablityStatusNew", "N/A")

        # Note: "Tap To Refresh" is now handled client-side with a button
        # The UI will show a refresh button for N/A, Tap To Refresh, or empty status

        # Generate book_now deeplink for this class
        book_now = _build_train_deeplink(
            from_station_name=from_station_name,
            to_station_name=to_station_name,
            class_code=class_code,
            train_number=train_number,
            from_station_code=from_station_code,
            to_station_code=to_station_code,
            quota=quota,
            departure_date=departure_date,
        )

        classes.append(
            TrainClassAvailability(
                class_code=class_code,
                class_name=class_name,
                fare=fare,
                availability_status=availability_status,
                fare_updated=fare_updated,
                book_now=book_now,
            )
        )

    return classes


def _process_single_train(
    train: Dict[str, Any],
    preferred_class: Optional[str] = None,
    quota: str = "GN",
) -> Optional[TrainInfo]:
    """Process a single train entry from API response."""
    train_class_wise_fare = train.get("TrainClassWiseFare", [])

    # Extract train context for deeplink generation
    from_station_name = train.get("fromStnName", "")
    to_station_name = train.get("toStnName", "")
    train_number = train.get("trainNumber", "")
    from_station_code = train.get("fromStnCode", "")
    to_station_code = train.get("toStnCode", "")
    departure_date = train.get("departuredate", "")

    # Process class availability with deeplink context
    # Returns None if preferred_class is specified but train doesn't have it
    classes = _process_class_availability(
        train_class_wise_fare,
        preferred_class,
        from_station_name=from_station_name,
        to_station_name=to_station_name,
        train_number=train_number,
        from_station_code=from_station_code,
        to_station_code=to_station_code,
        quota=quota,
        departure_date=departure_date,
    )

    # If classes is None, train doesn't have preferred class - skip it
    # If classes is empty list, no classes available at all - skip it
    if classes is None or not classes:
        return None

    return TrainInfo(
        train_number=train.get("trainNumber", ""),
        train_name=train.get("trainName", ""),
        from_station_code=train.get("fromStnCode", ""),
        from_station_name=train.get("fromStnName", ""),
        to_station_code=train.get("toStnCode", ""),
        to_station_name=train.get("toStnName", ""),
        departure_time=train.get("departureTime", ""),
        arrival_time=train.get("arrivalTime", ""),
        duration=train.get("duration", ""),
        distance=train.get("distance", ""),
        departure_date=train.get("departuredate", ""),
        arrival_date=train.get("ArrivalDate", ""),
        running_days=_get_running_days(train),
        classes=classes,
    )


def process_train_results(
    search_response: Dict[str, Any],
    preferred_class: Optional[str] = None,
    quota: str = "GN",
) -> Dict[str, Any]:
    """Process raw train search response.

    Args:
        search_response: Raw API response from EaseMyTrip Railways
        preferred_class: Optional class filter (1A, 2A, 3A, SL, etc.)
        quota: Booking quota (GN, TQ, SS, LD)

    Returns:
        Dict containing processed train list and quota info
    """
    trains = []
    quota_list = search_response.get("quotaList", [])
    train_list = search_response.get("trainBtwnStnsList", [])

    if not train_list:
        return {
            "trains": [],
            "quota_list": quota_list,
            "total_count": 0,
        }

    for train in train_list:
        processed_train = _process_single_train(
            train,
            preferred_class,
            quota,
        )
        if processed_train:
            trains.append(processed_train.model_dump())

    return {
        "trains": trains,
        "quota_list": quota_list,
        "total_count": len(trains),
    }


def _needs_station_resolution(station: str) -> bool:
    """Check if station string needs resolution (doesn't have code in parentheses)."""
    return "(" not in station or ")" not in station


async def search_trains(
    from_station: str,
    to_station: str,
    journey_date: str,
    travel_class: Optional[str] = None,
    quota: str = "GN",
) -> Dict[str, Any]:
    """Call EaseMyTrip train search API.

    Args:
        from_station: Origin station - can be just name ("Jammu") or with code ("Jammu Tawi (JAT)")
        to_station: Destination station - can be just name ("Delhi") or with code ("Delhi All Stations (NDLS)")
        journey_date: Journey date in DD-MM-YYYY format
        travel_class: Optional preferred class (1A, 2A, 3A, SL, etc.)
        quota: Booking quota (GN, TQ, SS, LD)

    Returns:
        Dict containing processed train search results
    """
    client = TrainApiClient()

    # Resolve station names to "Station Name (CODE)" format if needed
    if _needs_station_resolution(from_station):
        from_station = await resolve_train_station(from_station)

    if _needs_station_resolution(to_station):
        to_station = await resolve_train_station(to_station)

    # Convert date format from DD-MM-YYYY to DD/MM/YYYY for API
    api_date = journey_date.replace("-", "/")

    payload = {
        "fromSec": from_station,
        "toSec": to_station,
        "fromdate": api_date,
        "couponCode": "",
    }

    try:
        data = await client.search(TRAIN_API_URL, payload)
    except Exception as e:
        return {
            "error": "API_ERROR",
            "message": str(e),
            "trains": [],
            "quota_list": [],
            "total_count": 0,
        }

    # Check if response is error string
    if isinstance(data, str):
        return {
            "error": "INVALID_SEARCH",
            "message": data,
            "trains": [],
            "quota_list": [],
            "total_count": 0,
        }

    # Process results (Tap To Refresh is handled client-side)
    processed_data = process_train_results(
        data,
        travel_class,
        quota,
    )
    processed_data["from_station"] = from_station
    processed_data["to_station"] = to_station
    processed_data["journey_date"] = journey_date
    processed_data["travel_class"] = travel_class
    processed_data["quota"] = quota

    # Generate view all link
    view_all_link = generate_view_all_link(
        from_station=from_station,
        to_station=to_station,
        journey_date=journey_date,
    )
    processed_data["view_all_link"] = view_all_link

    return processed_data


def extract_train_summary(train: Dict[str, Any]) -> Dict[str, Any]:
    """Extract summary info from processed train data."""
    classes = train.get("classes", [])

    # Find cheapest class
    cheapest_fare = None
    cheapest_class = None
    for cls in classes:
        try:
            fare = float(cls.get("fare", 0))
            if cheapest_fare is None or fare < cheapest_fare:
                cheapest_fare = fare
                cheapest_class = cls
        except (ValueError, TypeError):
            continue

    return {
        "train_number": train.get("train_number"),
        "train_name": train.get("train_name"),
        "from_station": train.get("from_station_name"),
        "to_station": train.get("to_station_name"),
        "departure_time": train.get("departure_time"),
        "arrival_time": train.get("arrival_time"),
        "duration": train.get("duration"),
        "cheapest_fare": cheapest_fare,
        "cheapest_class": cheapest_class.get("class_name") if cheapest_class else None,
        "availability": cheapest_class.get("availability_status") if cheapest_class else "N/A",
        "classes_available": len(classes),
    }


def build_whatsapp_train_response(
    payload: TrainSearchInput,
    train_results: Dict[str, Any],
) -> WhatsappTrainFinalResponse:
    """Build WhatsApp-formatted response for train search results."""
    options = []

    for idx, train in enumerate(train_results.get("trains", []), start=1):
        summary = extract_train_summary(train)
        classes_info = []

        for cls in train.get("classes", []):
            classes_info.append({
                "class_code": cls.get("class_code"),
                "class_name": cls.get("class_name"),
                "fare": cls.get("fare"),
                "availability": cls.get("availability_status"),
            })

        options.append({
            "option_id": idx,
            "train_number": summary["train_number"],
            "train_name": summary["train_name"],
            "from_station": summary["from_station"],
            "to_station": summary["to_station"],
            "departure_time": summary["departure_time"],
            "arrival_time": summary["arrival_time"],
            "duration": summary["duration"],
            "date": payload.journey_date,
            "classes": classes_info,
            "cheapest_fare": summary["cheapest_fare"],
        })

    whatsapp_json = WhatsappTrainFormat(
        options=options,
        currency=train_results.get("currency", "INR"),
    )

    return WhatsappTrainFinalResponse(
        response_text=f"Here are the best train options from {payload.from_station} to {payload.to_station}",
        whatsapp_json=whatsapp_json,
    )
