"""Train Bookings Service """
from typing import Dict, Any, List
import logging

from emt_client.clients.booking_client import BookingApiClient
from emt_client.auth.login_auth import LoginTokenProvider

logger = logging.getLogger(__name__)


class TrainBookingsService:
    """Service for fetching train bookings"""
    
    def __init__(self, login_token_provider: LoginTokenProvider):
        self.token_provider = login_token_provider
        self.client = BookingApiClient(token_provider=self.token_provider)
    
    async def get_train_bookings(self) -> Dict[str, Any]:
        """Fetch train bookings"""
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
            
            logger.info(f"Train bookings - Action2Token: {bool(action2_token)}, UID: {uid}, IP: {ip}")
            
            if not action2_token or not uid:
                return {
                    "success": False,
                    "error": "INVALID_SESSION"
                }
            
            result = await self.client.fetch_bookings(action2_token, uid, ip)
            
            if not result.get("success"):
                return result
            
            data = result.get("data", {})
            trains = self.extract_trains(data)
            
            return {
                "success": True,
                "uid": uid,
                "total": len(trains),
                "bookings": trains,
                "raw_response": data
            }
        
        except Exception as e:
            logger.error(f"Error fetching train bookings: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_trains(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
    
        if not isinstance(data, dict):
            return results
        
        train = data.get("TrainDetails") or {}
        for t in train.get("trainJourneyDetails") or []:
            results.append({
                "type": "Train",
                "status": t.get("Status"),
                "booking_id": t.get("BookingRefNo"),
                "pnr": t.get("PnrNumber"),
                "source": t.get("Source"),
                "destination": t.get("Destination"),
                "departure": t.get("DepartureTime"),
                "arrival": t.get("ArrivalTime")
            })
        return results


def build_whatsapp_train_bookings_response(bookings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build WhatsApp-formatted response for train bookings."""
    items = []
    for b in bookings:
        route = None
        if b.get("source") and b.get("destination"):
            route = f"{b['source']} → {b['destination']}"

        items.append({
            "status": b.get("status"),
            "booking_id": b.get("booking_id"),
            "pnr": b.get("pnr"),
            "route": route,
            "departure": b.get("departure"),
            "arrival": b.get("arrival"),
        })

    return {
        "type": "train_bookings",
        "total": len(items),
        "bookings": items,
    }
