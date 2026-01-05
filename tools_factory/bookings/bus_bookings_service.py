"""Bus Bookings Service"""
from typing import Dict, Any, List
import logging

from emt_client.clients.booking_client import BookingApiClient
from emt_client.auth.login_auth import LoginTokenProvider

logger = logging.getLogger(__name__)


class BusBookingsService:
    """Service for fetching bus bookings"""
    
    def __init__(self, login_token_provider: LoginTokenProvider):
        self.token_provider = login_token_provider
        self.client = BookingApiClient(token_provider=self.token_provider)
    
    async def get_bus_bookings(self) -> Dict[str, Any]:
        """Fetch bus bookings"""
        try:
            if not self.token_provider.is_authenticated():
                return {
                    "success": False,
                    "error": "USER_NOT_LOGGED_IN"
                }
            
            user_info = self.token_provider.get_user_info()
            action2_token = self.token_provider.get_action2_token()
            uid = self.token_provider.get_uid()
            ip = self.token_provider.get_ip()  # Get hardcoded IP from session
            
            logger.info(f"Bus bookings - Action2Token: {bool(action2_token)}, UID: {uid}, IP: {ip}")
            
            if not action2_token or not uid:
                return {
                    "success": False,
                    "error": "INVALID_SESSION"
                }
            
            result = await self.client.fetch_bookings(action2_token, uid, ip)
            
            if not result.get("success"):
                return result
            
            data = result.get("data", {})
            buses = self.extract_buses(data)
            
            return {
                "success": True,
                "uid": uid,
                "total": len(buses),
                "bookings": buses,
                "raw_response": data
            }
        
        except Exception as e:
            logger.error(f"Error fetching bus bookings: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_buses(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        
        if not isinstance(data, dict):
            return results
        
        bus = data.get("BusDetails") or {}
        completed_bus_list = bus.get("Completed") or []
        for b in completed_bus_list:
            d = b.get("Details") or {}

            departure_date = d.get("DepartureDate") or b.get("DateOfJourney") or d.get("BdTime") or ""
            departure_time = d.get("DepartureTime1") or d.get("DepartureTime") or d.get("BdTime") or ""
            arrival_date = d.get("ArrivalDate") or ""
            arrival_time = d.get("ArrivalTime") or d.get("Droptime") or ""

            departure = f"{departure_date} {departure_time}".strip()
            arrival = f"{arrival_date} {arrival_time}".strip()

            results.append({
                "type": "Bus",
                "status": b.get("Status") or "Completed",
                "booking_id": b.get("BookingRefNo"),
                "route": b.get("TripDetails") or d.get("Route"),
                "journey_date": b.get("JourneyDate") or b.get("DateOfJourney"),
                "source": d.get("Source"),
                "destination": d.get("Destination"),
                "departure": departure,
                "arrival": arrival,
                "operator": d.get("TravelsOperator"),
                "bus_type": d.get("BusType")
            })
        
        return results