"""
Train utility functions for fetching availability status.
"""

import asyncio
import aiohttp
from typing import Dict, Any, List


async def _fetch_class_availability(
    session_id: str,
    train_number: str,
    class_code: str,
    from_station_code: str,
    to_station_code: str,
    journey_date: str,
    quota: str = "GN",
) -> Dict[str, Any]:
    """
    Fetch availability for a single class.

    Args:
        session_id: Session ID for the request
        train_number: Train number
        class_code: Class code (e.g., 'SL', '3A', '2A')
        from_station_code: Source station code
        to_station_code: Destination station code
        journey_date: Journey date in DD/MM/YYYY format
        quota: Quota type (default 'GN')

    Returns:
        Dict with class_code and availability_status
    """
    url = "https://railways.easemytrip.com/Train/AvailToCheck"

    payload = {
        "cls": class_code,
        "trainNo": train_number,
        "quotaSelectdd": quota,
        "fromstation": from_station_code,
        "tostation": to_station_code,
        "e": journey_date,
        "lstSearch": {
            "SelectQuta": "",
            "arrivalTime": "",
            "atasOpted": "",
            "avlClasses": [{"code": "", "Name": "", "TotalPrice": ""}],
            "departureTime": "",
            "distance": "",
            "duration": "",
            "flexiFlag": "",
            "fromStnName": "",
            "fromStnCode": "",
            "runningFri": "",
            "runningMon": "",
            "runningSat": "",
            "runningSun": "",
            "runningThu": "",
            "runningTue": "",
            "runningWed": "",
            "toStnCode": "",
            "toStnName": "",
            "trainName": "",
            "trainNumber": "",
            "trainType": [{"code": "", "Name": "", "TotalPrice": None}],
            "JourneyDate": None,
            "ArrivalDate": "",
            "departuredate": "",
            "_TrainAvilFare": [],
            "DistanceFromSrc": "",
            "DistanceFromDest": "",
            "DeptTime_12": None,
            "ArrTime_12": None,
            "TrainClassWiseFare": [],
            "isCheckAvaibility": False,
            "isShowClass": False,
            "isShowQuota": False,
            "NearByStation": "",
        },
        "Searchsource": "",
        "Searchdestination": "",
        "tkn": "",
        "IPAdress": "",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                data = await response.json()

                availability_status = "N/A"
                fare = None
                fare_updated = None

                if data.get("avlDayList") and len(data["avlDayList"]) > 0:
                    availability_status = data["avlDayList"][0].get(
                        "availablityStatusNew", "N/A"
                    )

                if data.get("totalFare"):
                    fare = data["totalFare"]

                if data.get("creationTime"):
                    fare_updated = data["creationTime"]

                return {
                    "class_code": class_code,
                    "availability_status": availability_status,
                    "fare": fare,
                    "fare_updated": fare_updated,
                }

    except Exception as e:
        return {
            "class_code": class_code,
            "availability_status": "N/A",
            "fare": None,
            "fare_updated": None,
            "error": str(e),
        }


async def fetch_train_availability(
    train_number: str,
    from_station_code: str,
    to_station_code: str,
    classes: List[str],
    journey_date: str,
    session_id: str = "",
    quota: str = "GN",
) -> Dict[str, Any]:
    """
    Fetch availability status for all classes of a train.

    Args:
        train_number: Train number
        from_station_code: Source station code
        to_station_code: Destination station code
        classes: List of class codes (e.g., ["3A", "2A", "SL"])
        journey_date: Journey date in DD/MM/YYYY format
        session_id: Session ID (optional, not used yet)
        quota: Quota type (default 'GN')

    Returns:
        Dict with train_number and classes list containing availability info
    """
    if not classes:
        return {
            "train_number": train_number,
            "classes": [],
        }

    tasks = [
        _fetch_class_availability(
            session_id=session_id,
            train_number=train_number,
            class_code=class_code,
            from_station_code=from_station_code,
            to_station_code=to_station_code,
            journey_date=journey_date,
            quota=quota,
        )
        for class_code in classes
        if class_code
    ]

    results = await asyncio.gather(*tasks)

    return {
        "train_number": train_number,
        "classes": list(results),
    }
