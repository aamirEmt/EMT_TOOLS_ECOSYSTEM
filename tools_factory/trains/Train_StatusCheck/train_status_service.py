"""Train Status API Logic.

This module handles train status operations including:
- Fetching available trackable dates for a train
- Getting train status with station-wise schedule
- Processing and formatting train status data
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from emt_client.clients.train_client import TrainApiClient
from .train_status_schema import (
    TrainStatusInput,
    TrainDateInfo,
    StationSchedule,
    TrainStatusResponse,
    WhatsappStationInfo,
    WhatsappTrainStatusFormat,
    WhatsappTrainStatusFinalResponse,
)


async def get_train_trackable_dates(train_number: str) -> Dict[str, Any]:
    """
    Fetch available trackable dates for a train.

    API: GET https://solr.easemytrip.com/v1/api/auto/Train_GetDates/{train_number}

    Args:
        train_number: Indian Railways train number (e.g., "12618")

    Returns:
        Dict with train info and available dates list
    """
    client = TrainApiClient()

    try:
        data = await client.get_train_dates(train_number)

        if not data:
            return {
                "error": "TRAIN_NOT_FOUND",
                "message": f"No tracking information found for train {train_number}",
                "train_number": train_number,
                "available_dates": [],
                "total_dates": 0,
            }

        # Process DateList from API response
        date_list = data.get("DateList", [])

        if not date_list:
            return {
                "error": "NO_DATES_AVAILABLE",
                "message": f"No trackable dates available for train {train_number}",
                "train_number": train_number,
                "available_dates": [],
                "total_dates": 0,
            }

        available_dates = _process_date_list(date_list)

        return {
            "train_number": train_number,
            "available_dates": [d.model_dump() for d in available_dates],
            "total_dates": len(available_dates),
        }

    except Exception as e:
        return {
            "error": "API_ERROR",
            "message": str(e),
            "train_number": train_number,
            "available_dates": [],
            "total_dates": 0,
        }


def _process_date_list(date_list: List[Dict[str, Any]]) -> List[TrainDateInfo]:
    """Process raw date list from API into structured format."""
    processed_dates = []

    for date_item in date_list:
        try:
            # Extract fields from API response format
            date_value = date_item.get("DateValue", "")  # "29/01/2026"
            dates_iso = date_item.get("_dates", "")  # "2026-01-29"
            day_name = date_item.get("dayName", "")  # "Thursday"
            month_name = date_item.get("monthName", "")  # "Jan"
            date_no = date_item.get("dateNo", "")  # "29"
            year_no = date_item.get("yearNo", "")  # "2026"
            display_day = date_item.get("displayDay", "")  # "Today"

            # Convert to DD-MM-YYYY format
            if date_value:
                # Parse DD/MM/YYYY and convert to DD-MM-YYYY
                parts = date_value.split("/")
                if len(parts) == 3:
                    date_str = f"{parts[0]}-{parts[1]}-{parts[2]}"
                else:
                    date_str = date_value.replace("/", "-")
            elif dates_iso:
                # Parse YYYY-MM-DD and convert to DD-MM-YYYY
                dt = datetime.strptime(dates_iso, "%Y-%m-%d")
                date_str = dt.strftime("%d-%m-%Y")
            else:
                continue

            # Build formatted date
            formatted_date = f"{date_no} {month_name} {year_no}"

            processed_dates.append(
                TrainDateInfo(
                    date=date_str,
                    day_name=day_name,
                    formatted_date=formatted_date,
                    display_day=display_day if display_day else None,
                )
            )
        except Exception:
            continue

    return processed_dates


def validate_date_against_available(
    requested_date: str,
    available_dates: List[Dict[str, Any]],
) -> Tuple[bool, str]:
    """
    Validate if requested date is in available dates list.

    Args:
        requested_date: Date in DD-MM-YYYY format
        available_dates: List of available date dicts

    Returns:
        Tuple of (is_valid, message)
    """
    if not available_dates:
        return False, "No available dates found for this train"

    date_strings = [d.get("date", "") for d in available_dates]

    if requested_date in date_strings:
        return True, "Date is valid"

    # Suggest available dates
    suggestions = []
    for d in available_dates[:5]:
        display = d.get("display_day", "")
        formatted = d.get("formatted_date", d.get("date", ""))
        if display:
            suggestions.append(f"{formatted} ({display})")
        else:
            suggestions.append(formatted)

    suggestion_text = ", ".join(suggestions)
    return False, f"Date {requested_date} is not trackable. Available dates: {suggestion_text}"


async def get_train_autosuggest(train_number: str) -> Optional[Dict[str, Any]]:
    """
    Get train details from autosuggest API.

    API: POST https://autosuggest.easemytrip.com/api/auto/train_name

    Args:
        train_number: Train number (e.g., "12124")

    Returns:
        Train details dict with TrainName, TrainNo, SrcStnCode, DestStnCode
        or None if not found
    """
    client = TrainApiClient()

    try:
        data = await client.get_train_autosuggest(train_number)

        if data and isinstance(data, list) and len(data) > 0:
            # Return the first matching train
            return data[0]

        return None

    except Exception:
        return None


async def get_train_live_status(
    train_number: str,
    journey_date: str,
    train_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get train status with station-wise schedule.

    First fetches train details from autosuggest API, then calls live status API.

    API: POST https://railways.easemytrip.com/TrainService/TrainLiveStatus

    Args:
        train_number: Train number
        journey_date: Date in DD-MM-YYYY format
        train_name: Optional train name (will be fetched from autosuggest if not provided)

    Returns:
        Complete train status with all station schedules
    """
    client = TrainApiClient()

    # Convert date format from DD-MM-YYYY to DD/MM/YYYY for API
    api_date = journey_date.replace("-", "/")

    # Get train details from autosuggest API
    train_details = await get_train_autosuggest(train_number)

    # Build train identifier and station codes from autosuggest response
    if train_details:
        autosuggest_train_name = train_details.get("TrainName", "")
        autosuggest_train_no = train_details.get("TrainNo", train_number)
        from_station = train_details.get("SrcStnCode", "")
        dest_station = train_details.get("DestStnCode", "")

        # API expects format like "12124-Deccan Queen"
        train_identifier = f"{autosuggest_train_no}-{autosuggest_train_name}"
    else:
        # Fallback if autosuggest fails
        train_identifier = train_number
        if train_name:
            train_identifier = f"{train_number}-{train_name}"
        from_station = ""
        dest_station = ""

    try:
        data = await client.get_train_live_status(
            train_number=train_identifier,
            selected_date=api_date,
            from_station=from_station,
            dest_station=dest_station,
        )

        if not data:
            return {
                "error": "STATUS_NOT_AVAILABLE",
                "message": f"Train status not available for train {train_number} on {journey_date}",
            }

        # Check for API error message
        if data.get("ErrorMessage"):
            return {
                "error": "API_ERROR",
                "message": data.get("ErrorMessage"),
            }

        # Process the response
        return _process_train_status_response(data, train_number, journey_date)

    except Exception as e:
        return {
            "error": "API_ERROR",
            "message": str(e),
        }


def _is_valid_time(value: str) -> bool:
    """Check if a string is a valid HH:MM time format (not a delay string like '11M Late')."""
    if not value or ":" not in value:
        return False
    parts = value.split(":")
    if len(parts) != 2:
        return False
    try:
        h, m = int(parts[0]), int(parts[1])
        return 0 <= h <= 23 and 0 <= m <= 59
    except ValueError:
        return False


def _convert_live_stations_to_schedule(
    live_stations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Convert LiveStationList format to stationList format for unified processing.

    Also extracts live tracking info: actual times, delays, current station.
    """
    converted = []

    for station in live_stations:
        # Extract scheduled and actual times
        sch_arr = station.get("schArrTime", "") or ""
        sch_dep = station.get("schDepTime", "") or ""
        act_arr = station.get("actArr", "") or ""
        act_dep = station.get("actDep", "") or ""

        # Get delay info
        delay_arr = station.get("delayArr", "") or ""
        delay_dep = station.get("delayDep", "") or ""

        # Check if this station is current/next
        is_current = station.get("isCurrentStation", False)
        is_next = station.get("isNextStation", False)

        # Only treat as actual times if they are valid HH:MM format
        # API can return delay strings like "11M Late" in actDep/actArr fields
        # Also check arr/dep fields: "false" means train hasn't actually arrived/departed
        # (API fills actArr/actDep with scheduled times even for upcoming stations)
        arr_confirmed = station.get("arr") != "false"
        dep_confirmed = station.get("dep") != "false"
        valid_act_arr = act_arr if (_is_valid_time(act_arr) and arr_confirmed) else None
        valid_act_dep = act_dep if (_is_valid_time(act_dep) and dep_confirmed) else None

        converted.append({
            "stationCode": station.get("stnCode", ""),
            "stationName": station.get("StationName", ""),
            "arrivalTime": sch_arr if sch_arr != "Source" else "",
            "departureTime": sch_dep,
            "actualArrival": valid_act_arr,
            "actualDeparture": valid_act_dep,
            "delayArrival": delay_arr,
            "delayDeparture": delay_dep,
            "haltTime": station.get("Halt", "--"),
            "dayCount": station.get("dayCnt", "1"),
            "distance": station.get("distance", ""),
            "plateform": station.get("pfNo", ""),
            "isCurrentStation": is_current,
            "isNextStation": is_next,
            "latitude": station.get("latitude"),
            "longitude": station.get("longitude"),
        })

    return converted


def _process_train_status_response(
    data: Dict[str, Any],
    train_number: str,
    journey_date: str,
) -> Dict[str, Any]:
    """Process raw train status API response."""

    # Extract train details
    train_details = data.get("_TrainDetails", {}) or {}
    train_name = train_details.get("TrainName", "") or ""
    train_type = train_details.get("TrainType", "") or ""
    total_halts = train_details.get("TotalHalts", "0") or "0"
    running_days_str = train_details.get("Running_Days", "") or ""

    # Extract running days from binary string (e.g., "0000010" = Saturday)
    runs_on = _parse_running_days(running_days_str)

    # Extract live tracking info (only available when train is running)
    is_live = False
    distance_travelled = data.get("DistanceTravelled", "") or ""
    remain_distance = data.get("RemainDistance", "") or ""
    distance_percentage = data.get("distancePercentage", "") or ""

    # API returns data in two formats:
    # 1. LiveStationList - when train is currently running (today's date with live tracking)
    # 2. trainScheduleList.stationList - for future/past dates (schedule only)

    station_list = []

    # Try LiveStationList first (for live tracking on today's date)
    live_stations = data.get("LiveStationList", [])
    if live_stations:
        station_list = _convert_live_stations_to_schedule(live_stations)
        is_live = True

    # Fall back to trainScheduleList (for future/past dates)
    if not station_list:
        schedule_list = data.get("trainScheduleList", {}) or {}
        station_list = schedule_list.get("stationList", []) or []

    if not station_list:
        return {
            "error": "NO_STATIONS",
            "message": "No station information available for this train",
        }

    # Process stations
    stations = _process_station_list(station_list)

    if not stations:
        return {
            "error": "NO_STATIONS",
            "message": "Could not process station information",
        }

    # Origin and destination from first and last stations
    origin = stations[0]
    destination = stations[-1]

    # Calculate journey duration
    journey_duration = _calculate_journey_duration(
        origin.departure_time,
        destination.arrival_time,
        origin.day,
        destination.day,
    )

    # Format journey date for display
    formatted_date = _format_journey_date(journey_date)

    # Use train number from response or fallback to input
    final_train_number = train_details.get("TrainNo", "") or train_number

    # Build a default train name if not available
    if not train_name and origin and destination:
        train_name = f"{origin.station_name} - {destination.station_name} Express"

    # Find current station for live tracking
    current_station_idx = None
    last_departed_idx = None
    for idx, s in enumerate(stations):
        if s.is_current_station:
            current_station_idx = idx
        if s.actual_departure:
            last_departed_idx = idx

    # If no explicit current station but we have departed stations, current is the last departed
    if current_station_idx is None and last_departed_idx is not None:
        current_station_idx = last_departed_idx

    # Next station = first station with is_next_station that hasn't departed
    # This is where the train is heading (gets train icon + glow in UI)
    next_station_idx = None
    for idx, s in enumerate(stations):
        if s.is_next_station and not s.actual_departure:
            next_station_idx = idx
            break

    return {
        "train_number": final_train_number,
        "train_name": train_name,
        "train_type": train_type,
        "runs_on": runs_on,
        "origin_station": origin.station_name,
        "origin_code": origin.station_code,
        "destination_station": destination.station_name,
        "destination_code": destination.station_code,
        "departure_time": origin.departure_time or "--",
        "arrival_time": destination.arrival_time or "--",
        "total_distance": destination.distance,
        "journey_duration": journey_duration,
        "journey_date": journey_date,
        "formatted_date": formatted_date,
        "stations": [s.model_dump() for s in stations],
        "total_halts": int(total_halts) if total_halts.isdigit() else len(stations),
        # Live tracking info
        "is_live": is_live,
        "distance_travelled": distance_travelled,
        "remain_distance": remain_distance,
        "distance_percentage": distance_percentage,
        "current_station_index": current_station_idx,
        "next_station_index": next_station_idx,
    }


def _parse_running_days(running_days_str: str) -> List[str]:
    """Parse running days from binary string format."""
    if not running_days_str or len(running_days_str) != 7:
        return []

    days = []
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for i, char in enumerate(running_days_str):
        if char == "1":
            days.append(day_names[i])

    return days if days else []


def _process_station_list(station_list: List[Dict[str, Any]]) -> List[StationSchedule]:
    """Process raw station list into structured format."""
    stations = []
    total_stations = len(station_list)

    for idx, station in enumerate(station_list):
        is_origin = idx == 0
        is_destination = idx == total_stations - 1

        # Extract times
        arrival_time = station.get("arrivalTime", "") or ""
        departure_time = station.get("departureTime", "") or ""

        # Handle origin (no arrival) and destination (no departure)
        if is_origin or arrival_time == "00:00":
            arrival_time = "--"
        if is_destination or departure_time == "00:00":
            departure_time = "--"

        # Extract halt time
        halt_time = station.get("haltTime", "") or "--"

        # Extract day count
        day_count = station.get("dayCount", "1") or "1"
        try:
            day = int(day_count)
        except (ValueError, TypeError):
            day = 1

        # Extract distance
        distance = station.get("distance", "") or ""

        # Extract live tracking fields
        actual_arrival = station.get("actualArrival")
        actual_departure = station.get("actualDeparture")
        delay_arrival = station.get("delayArrival", "") or ""
        delay_departure = station.get("delayDeparture", "") or ""
        is_current = station.get("isCurrentStation", False)
        is_next = station.get("isNextStation", False)

        stations.append(
            StationSchedule(
                station_code=station.get("stationCode", "") or "",
                station_name=station.get("stationName", "") or "",
                arrival_time=arrival_time if arrival_time else None,
                departure_time=departure_time if departure_time else None,
                halt_time=halt_time if halt_time != "--" else None,
                day=day,
                distance=distance if distance else None,
                platform=station.get("plateform", "") or None,
                is_origin=is_origin,
                is_destination=is_destination,
                actual_arrival=actual_arrival,
                actual_departure=actual_departure,
                delay_arrival=delay_arrival if delay_arrival else None,
                delay_departure=delay_departure if delay_departure else None,
                is_current_station=is_current,
                is_next_station=is_next,
            )
        )

    return stations


def _calculate_journey_duration(
    departure: Optional[str],
    arrival: Optional[str],
    dep_day: int,
    arr_day: int,
) -> Optional[str]:
    """Calculate total journey duration."""
    if not departure or not arrival or departure == "--" or arrival == "--":
        return None

    try:
        dep = datetime.strptime(departure, "%H:%M")
        arr = datetime.strptime(arrival, "%H:%M")

        # Calculate minutes difference
        dep_minutes = dep.hour * 60 + dep.minute
        arr_minutes = arr.hour * 60 + arr.minute

        # Add days difference
        days_diff = arr_day - dep_day
        total_minutes = arr_minutes - dep_minutes + (days_diff * 24 * 60)

        if total_minutes < 0:
            total_minutes += 24 * 60  # Handle overnight

        hours = total_minutes // 60
        minutes = total_minutes % 60

        if hours >= 24:
            days = hours // 24
            hours = hours % 24
            return f"{days}d {hours}h {minutes}m"

        return f"{hours}h {minutes}m"
    except Exception:
        return None


def _format_journey_date(date_str: str) -> str:
    """Format journey date for display."""
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str, "%d-%m-%Y")
        return dt.strftime("%d %b %Y, %A")
    except ValueError:
        return date_str


def build_whatsapp_train_status_response(
    payload: TrainStatusInput,
    status_result: Dict[str, Any],
) -> WhatsappTrainStatusFinalResponse:
    """Build WhatsApp-formatted response for train status."""

    # Simplified station list for WhatsApp - include key stations
    simplified_stations = []
    stations = status_result.get("stations", [])

    for i, station in enumerate(stations):
        # Include origin, destination, and every 3rd station in between
        if i == 0 or i == len(stations) - 1 or i % 3 == 0:
            simplified_stations.append(
                WhatsappStationInfo(
                    code=station.get("station_code", ""),
                    name=station.get("station_name", ""),
                    arrival=station.get("arrival_time"),
                    departure=station.get("departure_time"),
                    day=station.get("day", 1),
                )
            )

    whatsapp_json = WhatsappTrainStatusFormat(
        train_number=status_result.get("train_number", payload.train_number),
        train_name=status_result.get("train_name", ""),
        journey_date=status_result.get("journey_date", payload.journey_date or ""),
        origin=status_result.get("origin_station", ""),
        origin_code=status_result.get("origin_code", ""),
        destination=status_result.get("destination_station", ""),
        destination_code=status_result.get("destination_code", ""),
        departure_time=status_result.get("departure_time", ""),
        arrival_time=status_result.get("arrival_time", ""),
        total_stations=len(stations),
        stations=simplified_stations,
    )

    response_text = (
        f"Train {status_result.get('train_number')} - {status_result.get('train_name')}: "
        f"{status_result.get('origin_station')} ({status_result.get('departure_time')}) to "
        f"{status_result.get('destination_station')} ({status_result.get('arrival_time')})"
    )

    return WhatsappTrainStatusFinalResponse(
        response_text=response_text,
        whatsapp_json=whatsapp_json,
    )
