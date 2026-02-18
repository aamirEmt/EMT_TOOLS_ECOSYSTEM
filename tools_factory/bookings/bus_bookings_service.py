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
        for status_key in ["Upcoming", "Completed", "Cancelled", "Rejected", "Locked"]:
            bus_list = bus.get(status_key) or []
            for b in bus_list:
                d = b.get("Details") or {}

                departure_date = d.get("DepartureDate") or b.get("DateOfJourney") or d.get("BdTime") or ""
                departure_time = d.get("DepartureTime1") or d.get("DepartureTime") or d.get("BdTime") or ""
                arrival_date = d.get("ArrivalDate") or ""
                arrival_time = d.get("ArrivalTime") or d.get("Droptime") or ""

                departure = f"{departure_date} {departure_time}".strip()
                arrival = f"{arrival_date} {arrival_time}".strip()

                results.append({
                    "type": "Bus",
                    "status": b.get("Status") or status_key,
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


def build_whatsapp_bus_bookings_response(bookings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build WhatsApp-formatted response for bus bookings."""
    items = []
    for b in bookings:
        route = b.get("route")
        if not route and b.get("source") and b.get("destination"):
            route = f"{b['source']} → {b['destination']}"

        items.append({
            "status": b.get("status"),
            "booking_id": b.get("booking_id"),
            "route": route,
            "journey_date": b.get("journey_date"),
            "departure": b.get("departure"),
            "arrival": b.get("arrival"),
            "operator": b.get("operator"),
            "bus_type": b.get("bus_type"),
        })

    return {
        "type": "bus_bookings",
        "total": len(items),
        "bookings": items,
    }