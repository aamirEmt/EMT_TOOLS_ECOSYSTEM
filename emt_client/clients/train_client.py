from .client import EMTClient
from emt_client.config import PNR_STATUS_URL, TRAIN_ROUTE_API_URL

AVAILABILITY_CHECK_URL = "https://railways.easemytrip.com/Train/AvailToCheck"
TRAIN_GET_DATES_URL = "https://solr.easemytrip.com/v1/api/auto/Train_GetDates"
TRAIN_LIVE_STATUS_URL = "https://railways.easemytrip.com/TrainService/TrainLiveStatus"
TRAIN_AUTOSUGGEST_URL = "https://autosuggest.easemytrip.com/api/auto/train_name?useby=popularu&key=jNUYK0Yj5ibO6ZVIkfTiFA=="


class TrainApiClient:
    """Train API client for EaseMyTrip railways service."""

    def __init__(self):
        # Train API doesn't require token injection like flights
        self.client = EMTClient(token_provider=None)

    async def search(self, url: str, payload: dict) -> dict:
        """Search trains between stations."""
        return await self.client.post(url, payload)

    async def check_availability(
        self,
        train_no: str,
        class_code: str,
        quota: str,
        from_station_code: str,
        to_station_code: str,
        journey_date: str,
        from_display: str,
        to_display: str,
    ) -> dict:
        """
        Check real-time availability for a specific train class.

        This is used to refresh availability when the initial search returns
        "Tap To Refresh" status.

        Args:
            train_no: Train number (e.g., "12816")
            class_code: Class code (e.g., "3A", "SL", "2A")
            quota: Quota code (e.g., "GN", "TQ")
            from_station_code: Origin station code (e.g., "ANVT")
            to_station_code: Destination station code (e.g., "BBS")
            journey_date: Date in DD/MM/YYYY format
            from_display: Full from station display (e.g., "Delhi All Stations (NDLS)") - not used in current API
            to_display: Full to station display (e.g., "BaniBihar (BNBH)") - not used in current API

        Returns:
            API response with avlDayList containing real availability
        """
        payload = {
            "cls": class_code,
            "trainNo": train_no,
            "quotaSelectdd": quota,
            "fromstation": from_station_code,
            "tostation": to_station_code,
            "e": journey_date,  # Just the date in DD/MM/YYYY format
            "lstSearch": {
                "SelectQuta": "",
                "arrivalTime": "",
                "atasOpted": "",
                "avlClasses": [
                    {"code": "", "Name": "", "TotalPrice": ""},
                    {"code": "", "Name": "", "TotalPrice": ""},
                    {"code": "", "Name": "", "TotalPrice": ""},
                    {"code": "", "Name": "", "TotalPrice": ""},
                    {"code": "", "Name": "", "TotalPrice": ""}
                ],
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
                "trainType": [
                    {"code": "", "Name": "", "TotalPrice": None}
                ],
                "JourneyDate": None,
                "ArrivalDate": "",
                "departuredate": "",
                "_TrainAvilFare": [],
                "DistanceFromSrc": "",
                "DistanceFromDest": "",
                "DeptTime_12": None,
                "ArrTime_12": None,
                "TrainClassWiseFare": [
                    {
                        "BerthType": None,
                        "EnqClassType": None,
                        "enqClass": "",
                        "enqClassName": "",
                        "from": None,
                        "quota": "",
                        "quotaName": "",
                        "to": None,
                        "totalFare": "",
                        "trainName": None,
                        "trainNo": None,
                        "departureTime": None,
                        "ArrivalTime": None,
                        "avlDayList": [
                            {
                                "availablityDate": "",
                                "availablityStatus": "",
                                "availablityType": "",
                                "currentBkgFlag": None,
                                "reason": None,
                                "reasonType": None,
                                "wlType": None,
                                "creationTime": None,
                                "totalFare": None,
                                "availablityStatusNew": ""
                            }
                        ],
                        "creationTime": None,
                        "totalCollectibleAmount": None,
                        "FileCreationTime": None,
                        "UpdationTime": ""
                    }
                ],
                "isCheckAvaibility": False,
                "isShowClass": False,
                "isShowQuota": False,
                "NearByStation": ""
            },
            "Searchsource": "",
            "Searchdestination": "",
            "tkn": "",
            "IPAdress": ""
        }
        return await self.client.post(AVAILABILITY_CHECK_URL, payload)

    async def check_route(
        self,
        train_no: str,
        from_station_code: str,
        to_station_code: str,
    ) -> dict:
        """
        Check train route/schedule via EaseMyTrip Railways API.

        Args:
            train_no: Train number (e.g., "12302")
            from_station_code: Origin station code (e.g., "NDLS")
            to_station_code: Destination station code (e.g., "HWH")

        Returns:
            API response with stationList containing route details
        """
        payload = {
            "TrainNo": train_no,
            "fromStnCode": from_station_code,
            "toStnCode": to_station_code,
            "fromdate": "11/11/1111",
        }
        return await self.client.post(TRAIN_ROUTE_API_URL, payload)

    async def check_pnr_status(self, encrypted_pnr: str) -> dict:
        """
        Check PNR status via EaseMyTrip Railways API.

        Args:
            encrypted_pnr: AES-128 CBC encrypted PNR (base64 encoded)

        Returns:
            API response with PNR status details
        """
        payload = {"pnrNumber": encrypted_pnr}
        return await self.client.post(PNR_STATUS_URL, payload)
    async def get_train_dates(self, train_number: str) -> dict:
        """
        Fetch available trackable dates for a train.

        Args:
            train_number: Train number (e.g., "12618")

        Returns:
            API response with DateList containing available dates
        """
        url = f"{TRAIN_GET_DATES_URL}/{train_number}"
        return await self.client.get(url)

    async def get_train_live_status(
        self,
        train_number: str,
        selected_date: str,
        search_type: str = "",
        from_station: str = "",
        dest_station: str = "",
    ) -> dict:
        """
        Get live train status with station-wise schedule.

        Args:
            train_number: Train number with name (e.g., "12306-Kolkata Rajdhni")
            selected_date: Date in DD/MM/YYYY format
            search_type: Search type (default empty)
            from_station: Optional source station code
            dest_station: Optional destination station code

        Returns:
            API response with train status and station list
        """
        payload = {
            "TrainNo": train_number,
            "selectedDate": selected_date,
            "Srchtype": search_type,
            "fromSrc": from_station,
            "DestStnCode": dest_station,
        }
        return await self.client.post(TRAIN_LIVE_STATUS_URL, payload)

    async def get_train_autosuggest(self, train_number: str) -> list:
        """
        Get train details from autosuggest API.

        Args:
            train_number: Train number (e.g., "12124")

        Returns:
            List of matching trains with details (TrainName, TrainNo, SrcStnCode, DestStnCode)
        """
        payload = {"request": train_number}
        return await self.client.post(TRAIN_AUTOSUGGEST_URL, payload)
