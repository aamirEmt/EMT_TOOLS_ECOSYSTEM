"""Train Availability Check Service - Business logic for checking availability across multiple classes."""

import asyncio
import logging
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime

from emt_client.clients.train_client import TrainApiClient
from .availability_check_schema import ClassAvailabilityInfo


logger = logging.getLogger(__name__)

# Train name autosuggest API
TRAIN_NAME_API_URL = "https://autosuggest.easemytrip.com/api/auto/train_name?useby=popularu&key=jNUYK0Yj5ibO6ZVIkfTiFA=="


async def fetch_train_details(train_no: str) -> Optional[Dict[str, str]]:
    """
    Fetch train details (name and route) from autosuggest API.

    Args:
        train_no: Train number (e.g., "12963")

    Returns:
        Dictionary with train_name, from_station_code, to_station_code, or None if not found
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                TRAIN_NAME_API_URL,
                json={"request": train_no}
            )
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                train_info = data[0]
                return {
                    "train_name": train_info.get("TrainName", f"Train {train_no}"),
                    "from_station_code": train_info.get("SrcStnCode", ""),
                    "from_station_name": train_info.get("SrcStnName", ""),
                    "to_station_code": train_info.get("DestStnCode", ""),
                    "to_station_name": train_info.get("DestStnName", ""),
                }

            return None

    except Exception as e:
        logger.error(f"Error fetching train details for {train_no}: {e}")
        return None


class AvailabilityCheckService:
    """Service for checking train availability across multiple classes."""

    def __init__(self):
        self.client = TrainApiClient()

    async def check_availability_multiple_classes(
        self,
        train_no: str,
        classes: List[str],
        journey_date: str,
        quota: str = "GN",
    ) -> Dict[str, Any]:
        """
        Check availability for multiple classes in parallel.

        Args:
            train_no: Train number (e.g., "12963")
            classes: List of class codes to check (e.g., ["3A", "2A", "1A"])
            journey_date: Journey date in DD-MM-YYYY format
            quota: Quota code (GN, TQ, etc.)

        Returns:
            Dictionary with success, train_info, and classes list
        """
        # Fetch train details to get route information
        train_details = await fetch_train_details(train_no)

        if not train_details:
            return {
                "success": False,
                "error": f"Could not fetch details for train {train_no}. Please verify the train number.",
                "train_info": None,
                "classes": [],
            }

        from_station_code = train_details["from_station_code"]
        to_station_code = train_details["to_station_code"]
        from_station_display = train_details.get("from_station_name", from_station_code)
        to_station_display = train_details.get("to_station_name", to_station_code)

        # Convert date format: DD-MM-YYYY -> DD/MM/YYYY for API
        api_date = journey_date.replace("-", "/")

        # Create tasks for parallel execution
        tasks = [
            self._check_single_class(
                train_no=train_no,
                class_code=class_code,
                from_station_code=from_station_code,
                to_station_code=to_station_code,
                journey_date=api_date,
                quota=quota,
                from_station_display=from_station_display,
                to_station_display=to_station_display,
            )
            for class_code in classes
        ]

        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        class_availability = []
        train_info = None

        for i, result in enumerate(results):
            class_code = classes[i]

            if isinstance(result, Exception):
                # API call failed for this class
                logger.error(f"Failed to check class {class_code}: {result}")
                class_availability.append(
                    ClassAvailabilityInfo(
                        class_code=class_code,
                        status="ERROR - Please try again",
                        fare=None,
                    )
                )
                continue

            if result.get("success"):
                class_info = result["class_info"]
                class_availability.append(class_info)

                # Extract train info from first successful response
                if train_info is None and result.get("train_info"):
                    train_info = result["train_info"]

        # If no train info was extracted from API, use fetched train details
        if train_info is None:
            train_info = {
                "train_no": train_no,
                "train_name": train_details.get("train_name", f"Train {train_no}"),
            }

        return {
            "success": True,
            "train_info": train_info,
            "classes": [c.model_dump() for c in class_availability],
            "route_info": {
                "from_station_code": from_station_code,
                "from_station_name": from_station_display,
                "to_station_code": to_station_code,
                "to_station_name": to_station_display,
            },
        }

    async def _check_single_class(
        self,
        train_no: str,
        class_code: str,
        from_station_code: str,
        to_station_code: str,
        journey_date: str,
        quota: str,
        from_station_display: str,
        to_station_display: str,
    ) -> Dict[str, Any]:
        """
        Check availability for a single class.

        Args:
            train_no: Train number
            class_code: Class code to check
            from_station_code: Origin station code
            to_station_code: Destination station code
            journey_date: Date in DD/MM/YYYY format (already converted)
            quota: Quota code
            from_station_display: Full from station display
            to_station_display: Full to station display

        Returns:
            Dictionary with success, class_info, and train_info
        """
        try:
            response = await self.client.check_availability(
                train_no=train_no,
                class_code=class_code,
                quota=quota,
                from_station_code=from_station_code,
                to_station_code=to_station_code,
                journey_date=journey_date,
                from_display=from_station_display,
                to_display=to_station_display,
            )

            # Extract availability status
            status = "N/A"
            fare = None
            fare_updated = None

            if response.get("avlDayList") and len(response["avlDayList"]) > 0:
                avl_day = response["avlDayList"][0]
                status = avl_day.get("availablityStatusNew", "N/A")

            if response.get("totalFare"):
                try:
                    fare = int(float(response["totalFare"]))
                except (ValueError, TypeError):
                    fare = None

            if response.get("creationTime"):
                fare_updated = response["creationTime"]

            # Extract train info (if available)
            train_info = None
            if response.get("trainName") and response.get("trainNo"):
                train_info = {
                    "train_no": response["trainNo"],
                    "train_name": response["trainName"],
                }

            return {
                "success": True,
                "class_info": ClassAvailabilityInfo(
                    class_code=class_code,
                    status=status,
                    fare=fare,
                    fare_updated=fare_updated,
                ),
                "train_info": train_info,
            }

        except Exception as e:
            logger.error(f"Error checking availability for class {class_code}: {e}")
            return {
                "success": False,
                "error": str(e),
            }


def build_whatsapp_availability_response(
    train_info: Dict[str, Any],
    classes: List[Dict[str, Any]],
    journey_date: str,
    route_info: Dict[str, Any],
    quota: str = "GN",
) -> Dict[str, Any]:
    """
    Build WhatsApp-formatted response matching requirements.

    Args:
        train_info: Dictionary with train_no and train_name
        classes: List of class availability dictionaries
        journey_date: Journey date in DD-MM-YYYY format
        route_info: Dictionary with station codes and names
        quota: Quota code (default: "GN")

    Returns:
        WhatsApp-formatted response dictionary
    """
    # Import booking link builder from renderer
    from .availability_check_renderer import _build_book_url

    # Extract station info
    from_station_code = route_info.get("from_station_code", "")
    to_station_code = route_info.get("to_station_code", "")
    from_station_display = route_info.get("from_station_name", from_station_code)
    to_station_display = route_info.get("to_station_name", to_station_code)

    # Convert journey date to API format (DD-MM-YYYY -> DD/MM/YYYY)
    journey_date_api = journey_date.replace("-", "/")

    # Format classes for WhatsApp (matching exact requirements format)
    whatsapp_classes = []
    for cls in classes:
        # Build booking link for this class
        booking_link = _build_book_url(
            train_no=train_info["train_no"],
            class_code=cls["class_code"],
            from_code=from_station_code,
            to_code=to_station_code,
            quota=quota,
            journey_date=journey_date_api,
            from_display=from_station_display,
            to_display=to_station_display,
        )

        whatsapp_classes.append({
            "class": cls["class_code"],
            "status": cls["status"],
            "fare": cls.get("fare"),
            "booking_link": booking_link,
        })

    # Format journey date for display (DD-MM-YYYY -> DD Mon YYYY)
    formatted_date = _format_date_display(journey_date)

    # Build response matching exact requirements
    return {
        "type": "all_class_availability",
        "status": "RESULT",
        "response_text": f"Here is availability in {train_info['train_name']} on {formatted_date}.",
        "data": {
            "train": {
                "train_no": train_info["train_no"],
                "train_name": train_info["train_name"],
            },
            "classes": whatsapp_classes,
        },
    }


def _format_date_display(date_str: str) -> str:
    """
    Format date for display.

    Args:
        date_str: Date in DD-MM-YYYY format

    Returns:
        Date formatted as "DD Mon YYYY" (e.g., "25 Feb 2026")
    """
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        return date_obj.strftime("%d %b %Y")
    except Exception:
        # Return as-is if parsing fails
        return date_str
