"""Train Route Check Service - Business logic for checking train route/schedule."""

import logging
from typing import Dict, Any, List, Optional

from emt_client.clients.train_client import TrainApiClient
from tools_factory.trains.Train_AvailabilityCheck.availability_check_service import fetch_train_details
from .route_check_schema import StationStop

logger = logging.getLogger(__name__)


class TrainRouteCheckService:
    """Service for checking train route/schedule."""

    def __init__(self):
        self.client = TrainApiClient()

    async def check_route(
        self,
        train_no: str,
        from_station_code: Optional[str] = None,
        to_station_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Check train route/schedule.

        Args:
            train_no: Train number (e.g., "12302")
            from_station_code: Origin station code (optional, fetched if not provided)
            to_station_code: Destination station code (optional, fetched if not provided)

        Returns:
            Dictionary with success, train_info, and station_list
        """
        # Fetch station codes if not provided
        if not from_station_code or not to_station_code:
            train_details = await fetch_train_details(train_no)

            if not train_details:
                return {
                    "success": False,
                    "error": f"Could not fetch details for train {train_no}. Please verify the train number.",
                }

            from_station_code = from_station_code or train_details["from_station_code"]
            to_station_code = to_station_code or train_details["to_station_code"]

        try:
            response = await self.client.check_route(
                train_no=train_no,
                from_station_code=from_station_code,
                to_station_code=to_station_code,
            )
        except Exception as e:
            logger.error(f"Error checking route for train {train_no}: {e}")
            return {
                "success": False,
                "error": f"Could not fetch route for train {train_no}. Please try again.",
            }

        # Check for API errors
        if response.get("errorMessage"):
            return {
                "success": False,
                "error": response["errorMessage"],
            }

        station_list_raw = response.get("stationList", [])
        if not station_list_raw:
            return {
                "success": False,
                "error": f"No route information found for train {train_no}.",
            }

        # Parse station list
        station_list = []
        for station in station_list_raw:
            station_list.append(
                StationStop(
                    station_code=station.get("stationCode", ""),
                    station_name=station.get("stationName", ""),
                    arrival_time=station.get("arrivalTime", "--"),
                    departure_time=station.get("departureTime", "--"),
                    halt_time=station.get("haltTime", "--"),
                    day_count=station.get("dayCount", "1"),
                    distance=station.get("distance", "0"),
                    route_number=station.get("routeNumber", "1"),
                    stn_serial_number=station.get("stnSerialNumber", ""),
                )
            )

        # Extract running days
        running_days = _extract_running_days(response)

        return {
            "success": True,
            "train_info": {
                "train_no": response.get("trainNumber", train_no),
                "train_name": response.get("trainName", f"Train {train_no}"),
            },
            "station_from": response.get("stationFrom", from_station_code),
            "station_to": response.get("stationTo", to_station_code),
            "station_list": [s.model_dump() for s in station_list],
            "running_days": running_days,
            "total_stops": len(station_list),
        }


def _extract_running_days(response: Dict[str, Any]) -> List[str]:
    """Extract running days from API response."""
    days = []
    day_mapping = {
        "trainRunsOnMon": "Mon",
        "trainRunsOnTue": "Tue",
        "trainRunsOnWed": "Wed",
        "trainRunsOnThu": "Thu",
        "trainRunsOnFri": "Fri",
        "trainRunsOnSat": "Sat",
        "trainRunsOnSun": "Sun",
    }
    for key, day_name in day_mapping.items():
        if response.get(key) == "Y":
            days.append(day_name)
    return days


def build_whatsapp_route_response(
    train_info: Dict[str, Any],
    station_list: List[Dict[str, Any]],
    running_days: List[str],
) -> Dict[str, Any]:
    """
    Build WhatsApp-formatted response for train route.

    Args:
        train_info: Dictionary with train_no and train_name
        station_list: List of station stop dictionaries
        running_days: List of running day strings

    Returns:
        WhatsApp-formatted response dictionary
    """
    total_stops = len(station_list)

    # Build response text with first and last station
    if station_list:
        first = station_list[0]
        last = station_list[-1]
        response_text = (
            f"Route for {train_info['train_name']} ({train_info['train_no']}): "
            f"{first['station_name']} ({first['station_code']}) to "
            f"{last['station_name']} ({last['station_code']}), "
            f"{total_stops} stops."
        )
    else:
        response_text = f"No route information found for train {train_info['train_no']}."

    # Build WhatsApp stops list
    whatsapp_stops = []
    for station in station_list:
        whatsapp_stops.append({
            "station_code": station["station_code"],
            "station_name": station["station_name"],
            "arrival_time": station["arrival_time"],
            "departure_time": station["departure_time"],
            "halt_time": station["halt_time"],
            "day_count": station["day_count"],
            "distance": station["distance"],
        })

    return {
        "type": "train_route",
        "response_text": response_text,
        "data": {
            "train": {
                "train_no": train_info["train_no"],
                "train_name": train_info["train_name"],
            },
            "running_days": running_days,
            "total_stops": total_stops,
            "stops": whatsapp_stops,
        },
    }
