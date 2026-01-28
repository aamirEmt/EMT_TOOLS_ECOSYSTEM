from .client import EMTClient

AVAILABILITY_CHECK_URL = "https://railways.easemytrip.com/Train/AvailToCheck"


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
            from_display: Full from station display (e.g., "Delhi All Stations (NDLS)")
            to_display: Full to station display (e.g., "BaniBihar (BNBH)")

        Returns:
            API response with avlDayList containing real availability
        """
        payload = {
            "cls": class_code,
            "trainNo": train_no,
            "quotaSelectdd": quota,
            "fromstation": from_station_code,
            "tostation": to_station_code,
            "e": f"{journey_date}|{from_display}|{to_display}",
        }
        return await self.client.post(AVAILABILITY_CHECK_URL, payload)
