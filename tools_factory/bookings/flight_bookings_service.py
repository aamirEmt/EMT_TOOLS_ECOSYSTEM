"""Flight Bookings Service"""
from typing import Dict, Any, List
import logging

from emt_client.clients.booking_client import BookingApiClient
from emt_client.auth.login_auth import LoginTokenProvider

logger = logging.getLogger(__name__)


class FlightBookingsService:
    """Service for fetching flight bookings"""
    
    def __init__(self, login_token_provider: LoginTokenProvider):
        self.token_provider = login_token_provider
        self.client = BookingApiClient(token_provider=self.token_provider)
    
    async def get_flight_bookings(self) -> Dict[str, Any]:
        """Fetch flight bookings"""
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
            
            logger.info(f"Flight bookings - Action2Token: {bool(action2_token)}, UID: {uid}, IP: {ip}")
            
            if not action2_token or not uid:
                return {
                    "success": False,
                    "error": "INVALID_SESSION"
                }
            
            result = await self.client.fetch_bookings(action2_token, uid, ip)
            
            if not result.get("success"):
                return result
            
            data = result.get("data", {})
            flights = self.extract_flights(data)
            
            return {
                "success": True,
                "uid": uid,
                "total": len(flights),
                "bookings": flights,
                "raw_response": data
            }
        
        except Exception as e:
            logger.error(f"Error fetching flight bookings: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_flights(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        
        if not isinstance(data, dict):
            return results
        
        flight = data.get("FlightDetails") or {}
        for status_key in ["Upcoming", "Completed", "Cancelled", "Rejected", "Locked"]:
            flights_list = flight.get(status_key) or []
            for f in flights_list:
                results.append({
                    "type": "Flight",
                    "status": status_key,
                    "booking_id": f.get("BookingRefNo"),
                    "source": f.get("Source"),
                    "destination": f.get("Destination"),
                    "departure": f.get("DepartureTime"),
                    "arrival": f.get("ArrivalTime"),
                    "flight_number": f.get("FlightNumber")
                })

        return results


def build_whatsapp_flight_bookings_response(bookings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build WhatsApp-formatted response for flight bookings."""
    items = []
    for b in bookings:
        route = None
        if b.get("source") and b.get("destination"):
            route = f"{b['source']} → {b['destination']}"

        items.append({
            "status": b.get("status"),
            "booking_id": b.get("booking_id"),
            "route": route,
            "flight_number": b.get("flight_number"),
            "departure": b.get("departure"),
            "arrival": b.get("arrival"),
        })

    return {
        "type": "flight_bookings",
        "total": len(items),
        "bookings": items,
    }
