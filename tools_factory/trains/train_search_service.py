"""Train Search API Logic.

This module handles all train search operations including:
- Searching trains via EaseMyTrip Railways API
- Processing train results
- Extracting class-wise availability and fares
"""

import asyncio
import logging
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

logger = logging.getLogger(__name__)


def _parse_time_to_time_object(time_str: str) -> Optional[datetime.time]:
    """
    Parse 24-hour format time string (e.g., "14:30", "20:40") to datetime.time object.

    Returns None if parsing fails (logs warning, doesn't crash).
    """
    if not time_str:
        return None

    try:
        dt = datetime.strptime(time_str.strip(), "%H:%M")
        return dt.time()
    except ValueError:
        logger.warning(f"Failed to parse 24-hour time: {time_str}")
        return None


def _matches_time_filter(
    train_time_str: str,
    min_time_str: Optional[str] = None,
    max_time_str: Optional[str] = None,
) -> bool:
    """
    Check if train time (24-hour from API) matches user time range (24-hour).

    Args:
        train_time_str: API time like "20:40", "15:00"
        min_time_str: User input like "14:00" (optional)
        max_time_str: User input like "18:00" (optional)

    Returns:
        True if matches filter (or no filter), False otherwise

    Edge Cases:
        - If train time can't be parsed, return True (don't filter out)
        - If no filters specified, return True
        - Ranges are inclusive (>= min AND <= max)
    """
    # No filter = always match
    if not min_time_str and not max_time_str:
        return True

    # Parse train time (24-hour format from API)
    train_time = _parse_time_to_time_object(train_time_str)

    # Can't parse train time? Don't filter it out (graceful degradation)
    if train_time is None:
        return True

    # Check minimum time constraint
    if min_time_str:
        min_time = _parse_time_to_time_object(min_time_str)
        if min_time and train_time < min_time:
            return False

    # Check maximum time constraint
    if max_time_str:
        max_time = _parse_time_to_time_object(max_time_str)
        if max_time and train_time > max_time:
            return False

    return True


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
        https://railways.easemytrip.com/TrainListInfo/Delhi-All-Stations-(NDLS)-to-Bhubaneswar-(BBS)/2/03-02-2026
    """
    try:
        # Format station names: replace spaces with hyphens
        from_formatted = from_station.replace(" ", "-")
        to_formatted = to_station.replace(" ", "-")

        return f"https://railways.easemytrip.com/TrainListInfo/{from_formatted}-to-{to_formatted}/2/{journey_date}"
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
        class_quota = class_info.get("quota", "")
        class_quota_name = class_info.get("quotaName", "")

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
            quota=class_quota or quota,  # Use class-specific quota if available, otherwise use default
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
                quota=class_quota,
                quota_name=class_quota_name,
            )
        )

    return classes


def _process_single_train(
    train: Dict[str, Any],
    preferred_class: Optional[str] = None,
    quota: str = "GN",
    departure_time_min: Optional[str] = None,
    departure_time_max: Optional[str] = None,
    arrival_time_min: Optional[str] = None,
    arrival_time_max: Optional[str] = None,
) -> Optional[TrainInfo]:
    """
    Process a single train entry from API response, applying class and time filters.

    Returns None if train doesn't match filters.
    """
    train_class_wise_fare = train.get("TrainClassWiseFare", [])

    # Extract train context for deeplink generation
    from_station_name = train.get("fromStnName", "")
    to_station_name = train.get("toStnName", "")
    train_number = train.get("trainNumber", "")
    from_station_code = train.get("fromStnCode", "")
    to_station_code = train.get("toStnCode", "")
    departure_date = train.get("departuredate", "")

    # Extract time fields
    departure_time = train.get("departureTime", "")
    arrival_time = train.get("arrivalTime", "")

    # Apply departure time filter
    if not _matches_time_filter(
        departure_time,
        min_time_str=departure_time_min,
        max_time_str=departure_time_max,
    ):
        return None  # Exclude train

    # Apply arrival time filter
    if not _matches_time_filter(
        arrival_time,
        min_time_str=arrival_time_min,
        max_time_str=arrival_time_max,
    ):
        return None  # Exclude train

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
        departure_time=departure_time,
        arrival_time=arrival_time,
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
    departure_time_min: Optional[str] = None,
    departure_time_max: Optional[str] = None,
    arrival_time_min: Optional[str] = None,
    arrival_time_max: Optional[str] = None,
) -> Dict[str, Any]:
    """Process raw train search response with time filtering.

    Args:
        search_response: Raw API response from EaseMyTrip Railways
        preferred_class: Optional class filter (1A, 2A, 3A, SL, etc.)
        quota: Booking quota (GN, TQ, SS, LD)
        departure_time_min: Filter trains departing at or after this time (HH:MM)
        departure_time_max: Filter trains departing at or before this time (HH:MM)
        arrival_time_min: Filter trains arriving at or after this time (HH:MM)
        arrival_time_max: Filter trains arriving at or before this time (HH:MM)

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
            departure_time_min=departure_time_min,
            departure_time_max=departure_time_max,
            arrival_time_min=arrival_time_min,
            arrival_time_max=arrival_time_max,
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
    departure_time_min: Optional[str] = None,
    departure_time_max: Optional[str] = None,
    arrival_time_min: Optional[str] = None,
    arrival_time_max: Optional[str] = None,
) -> Dict[str, Any]:
    """Call EaseMyTrip train search API with time filtering.

    Args:
        from_station: Origin station - can be just name ("Jammu") or with code ("Jammu Tawi (JAT)")
        to_station: Destination station - can be just name ("Delhi") or with code ("Delhi All Stations (NDLS)")
        journey_date: Journey date in DD-MM-YYYY format
        travel_class: Optional preferred class (1A, 2A, 3A, SL, etc.)
        quota: Booking quota (GN, TQ, SS, LD)
        departure_time_min: Filter trains departing at or after this time (HH:MM)
        departure_time_max: Filter trains departing at or before this time (HH:MM)
        arrival_time_min: Filter trains arriving at or after this time (HH:MM)
        arrival_time_max: Filter trains arriving at or before this time (HH:MM)

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

    # Process results with time filters (Tap To Refresh is handled client-side)
    processed_data = process_train_results(
        data,
        travel_class,
        quota,
        departure_time_min=departure_time_min,
        departure_time_max=departure_time_max,
        arrival_time_min=arrival_time_min,
        arrival_time_max=arrival_time_max,
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


# Configuration for availability checking
MAX_CONCURRENT_AVAILABILITY_CHECKS = 5   # Balance speed vs API load
MAX_TRAINS_TO_CHECK = 20                 # Prevent timeout on large results

logger = logging.getLogger(__name__)


async def check_and_filter_trains_by_availability(
    trains: List[Dict[str, Any]],
    travel_class: str,
    journey_date: str,
    quota: str = "GN",
    max_concurrent: int = MAX_CONCURRENT_AVAILABILITY_CHECKS,
    max_trains: int = MAX_TRAINS_TO_CHECK,
) -> List[Dict[str, Any]]:
    """
    Check real-time availability for each train in the specified class.
    Filter to only trains with RAC/AVAILABLE/WAITLIST status.
    Enrich results with status and booking_link.

    Args:
        trains: List of processed train dictionaries from search
        travel_class: Class code to check (e.g., "3A", "SL")
        journey_date: Journey date in DD-MM-YYYY format
        quota: Booking quota (default: "GN")
        max_concurrent: Max parallel availability checks (default: 5)
        max_trains: Max trains to check (default: 20)

    Returns:
        Filtered list of trains with availability_status and booking_link added
    """
    from .Train_AvailabilityCheck.availability_check_service import AvailabilityCheckService

    # Limit trains to check (performance)
    trains_to_check = trains[:max_trains]

    # Create availability check service
    avail_service = AvailabilityCheckService()

    # Semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)

    async def check_single_train(train: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check availability for a single train and return enriched data."""
        async with semaphore:
            try:
                # Get train route info
                train_no = train.get("train_number")
                from_code = train.get("from_station_code")
                to_code = train.get("to_station_code")

                # Call availability check service
                result = await avail_service.check_availability_multiple_classes(
                    train_no=train_no,
                    classes=[travel_class],  # Check only the requested class
                    journey_date=journey_date,
                    quota=quota,
                )

                if not result.get("success"):
                    logger.warning(f"Availability check failed for train {train_no}: {result.get('error')}")
                    return None

                # Extract class info
                classes = result.get("classes", [])
                if not classes:
                    logger.info(f"No availability data for train {train_no} class {travel_class}")
                    return None

                class_info = classes[0]  # We only checked one class
                status = class_info.get("status", "")

                # Filter by status (only RAC/AVAILABLE/WAITLIST)
                status_upper = status.upper()
                is_bookable = (
                    "AVAILABLE" in status_upper or
                    "WL" in status_upper or
                    "WAITLIST" in status_upper or
                    "RAC" in status_upper
                )

                if not is_bookable:
                    logger.info(f"Train {train_no} class {travel_class} not bookable: {status}")
                    return None

                # Build booking link
                route_info = result.get("route_info", {})
                booking_link = _build_booking_link(
                    train_no=train_no,
                    class_code=travel_class,
                    from_code=route_info.get("from_station_code", from_code),
                    to_code=route_info.get("to_station_code", to_code),
                    quota=quota,
                    journey_date=journey_date,
                    from_display=train.get("from_station_name", ""),
                    to_display=train.get("to_station_name", ""),
                )

                # Enrich train data
                enriched_train = {**train}  # Copy
                enriched_train["availability_status"] = status
                enriched_train["booking_link"] = booking_link
                enriched_train["fare"] = class_info.get("fare")

                return enriched_train

            except Exception as e:
                logger.error(f"Error checking availability for train {train.get('train_number')}: {e}")
                return None

    # Check all trains in parallel
    tasks = [check_single_train(train) for train in trains_to_check]
    results = await asyncio.gather(*tasks)

    # Filter out None results (failed checks or non-bookable)
    filtered_trains = [r for r in results if r is not None]

    logger.info(f"Availability check: {len(trains_to_check)} trains checked, {len(filtered_trains)} bookable")

    return filtered_trains


def _build_booking_link(
    train_no: str,
    class_code: str,
    from_code: str,
    to_code: str,
    quota: str,
    journey_date: str,
    from_display: str,
    to_display: str,
) -> str:
    """
    Build booking URL for EaseMyTrip railways.

    Reuses pattern from availability_check_renderer.py lines 358-392.

    Args:
        train_no: Train number
        class_code: Class code
        from_code: Origin station code
        to_code: Destination station code
        quota: Quota code
        journey_date: Journey date in DD-MM-YYYY format
        from_display: Full from station display
        to_display: Full to station display

    Returns:
        Booking URL
    """
    # Convert date format: DD-MM-YYYY -> DD/MM/YYYY -> D-M-YYYY
    date_with_slashes = journey_date.replace("-", "/")
    date_parts = date_with_slashes.split("/")
    date_formatted = f"{int(date_parts[0])}-{int(date_parts[1])}-{date_parts[2]}"

    # Extract station names and convert to URL format
    from_name = from_display.split("(")[0].strip().replace(" ", "-") if "(" in from_display else from_code
    to_name = to_display.split("(")[0].strip().replace(" ", "-") if "(" in to_display else to_code

    return f"https://railways.easemytrip.com/TrainInfo/{from_name}-to-{to_name}/{class_code}/{train_no}/{from_code}/{to_code}/{quota}/{date_formatted}"


def build_whatsapp_train_response(
    payload: TrainSearchInput,
    train_results: Dict[str, Any],
    tatkal_note: str = "",
) -> WhatsappTrainFinalResponse:
    """Build WhatsApp-formatted response (routes to appropriate builder)."""
    if payload.travel_class:
        return _build_whatsapp_response_with_class(payload, train_results, tatkal_note)
    else:
        return _build_whatsapp_response_without_class(payload, train_results, tatkal_note)


def _build_whatsapp_response_with_class(
    payload: TrainSearchInput,
    train_results: Dict[str, Any],
    tatkal_note: str = "",
) -> WhatsappTrainFinalResponse:
    """
    Build WhatsApp response when class IS mentioned.
    Assumes trains have been filtered by availability and enriched with status/links.
    """
    import time

    trains = []
    travel_class = payload.travel_class

    for idx, train in enumerate(train_results.get("trains", []), start=1):
        # Extract class-specific info (should exist after availability check)
        class_info = next(
            (cls for cls in train.get("classes", []) if cls.get("class_code") == travel_class),
            {}
        )

        trains.append({
            "option_id": idx,
            "train_no": train.get("train_number"),
            "train_name": train.get("train_name"),
            "departure_time": train.get("departure_time"),
            "arrival_time": train.get("arrival_time"),
            "duration": train.get("duration"),
            "classes": [{
                "class": travel_class,
                "status": train.get("availability_status", "N/A"),
                "fare": train.get("fare") or class_info.get("fare"),
            }],
            "booking_link": train.get("booking_link", ""),
        })

    # Generate search_id (simple timestamp-based)
    search_id = f"SRCH_{int(time.time() * 1000)}"

    whatsapp_json = WhatsappTrainFormat(
        is_class_mentioned=True,
        trains=trains,
        search_context={
            "source": payload.from_station,
            "destination": payload.to_station,
            "date": payload.journey_date,
            "class": travel_class,
            "quota": payload.quota or "GN",
            "currency": train_results.get("currency", "INR"),
            "search_id": search_id,
        },
        currency=train_results.get("currency", "INR"),
        view_all_trains_url=train_results.get("view_all_link", ""),
    )

    response_text = f"Here are trains from {payload.from_station} to {payload.to_station} on {payload.journey_date} in {travel_class}."
    if tatkal_note:
        response_text += tatkal_note

    return WhatsappTrainFinalResponse(
        response_text=response_text,
        whatsapp_json=whatsapp_json,
    )


def _build_whatsapp_response_without_class(
    payload: TrainSearchInput,
    train_results: Dict[str, Any],
    tatkal_note: str = "",
) -> WhatsappTrainFinalResponse:
    """
    Build WhatsApp response when class NOT mentioned.
    Shows all trains with all available classes (existing logic).
    """
    import time

    options = []

    for idx, train in enumerate(train_results.get("trains", []), start=1):
        summary = extract_train_summary(train)
        classes_info = []

        for cls in train.get("classes", []):
            classes_info.append({
                "class": cls.get("class_code"),
                "fare": cls.get("fare"),
            })

        options.append({
            "option_id": idx,
            "train_no": summary["train_number"],
            "train_name": summary["train_name"],
            "departure_time": summary["departure_time"],
            "arrival_time": summary["arrival_time"],
            "duration": summary["duration"],
            "classes": classes_info,
        })

    # Generate search_id
    search_id = f"SRCH_{int(time.time() * 1000)}"

    whatsapp_json = WhatsappTrainFormat(
        is_class_mentioned=False,
        options=options,
        search_context={
            "source": payload.from_station,
            "destination": payload.to_station,
            "date": payload.journey_date,
            "class": None,
            "quota": payload.quota or "GN",
            "currency": train_results.get("currency", "INR"),
            "search_id": search_id,
        },
        currency=train_results.get("currency", "INR"),
        view_all_trains_url=train_results.get("view_all_link", ""),
    )

    response_text = f"Here are trains from {payload.from_station} to {payload.to_station} on {payload.journey_date}."
    if tatkal_note:
        response_text += tatkal_note

    return WhatsappTrainFinalResponse(
        response_text=response_text,
        whatsapp_json=whatsapp_json,
    )
