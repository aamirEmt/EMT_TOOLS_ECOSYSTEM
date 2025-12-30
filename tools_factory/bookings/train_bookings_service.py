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
            auth = await self.token_provider.get_token()
            email = user_info.get("email") or user_info.get("phone")  
            ip = self.token_provider.get_ip()  # Get hardcoded IP from session
            
            logger.info(f"Train bookings - Auth: {bool(auth)}, Email: {email}, IP: {ip}")
            
            if not auth or not email:
                return {
                    "success": False,
                    "error": "INVALID_SESSION"
                }
            
            result = await self.client.fetch_bookings(auth, email, ip)
            
            if not result.get("success"):
                return result
            
            data = result.get("data", {})
            trains = self.extract_trains(data)
            
            return {
                "success": True,
                "email": email,
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
