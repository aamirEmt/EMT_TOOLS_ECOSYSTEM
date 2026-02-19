"""Hotel Bookings Service """
from typing import Dict, Any, List
import logging

from emt_client.clients.booking_client import BookingApiClient
from emt_client.auth.login_auth import LoginTokenProvider

logger = logging.getLogger(__name__)


class HotelBookingsService:
    """Service for fetching hotel bookings"""
    
    def __init__(self, login_token_provider: LoginTokenProvider):
        self.token_provider = login_token_provider
        self.client = BookingApiClient(token_provider=self.token_provider)
    
    async def get_hotel_bookings(self) -> Dict[str, Any]:
        """Fetch hotel bookings"""
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
            
            logger.info(f"Hotel bookings - Action2Token: {bool(action2_token)}, UID: {uid}, IP: {ip}")
            
            if not action2_token or not uid:
                return {
                    "success": False,
                    "error": "INVALID_SESSION"
                }
            
            result = await self.client.fetch_bookings(action2_token, uid, ip)
            
            if not result.get("success"):
                return result
            
            data = result.get("data", {})
            hotels = self.extract_hotels(data)
            
            return {
                "success": True,
                "uid": uid,
                "total": len(hotels),
                "bookings": hotels,
                "raw_response": data
            }
        
        except Exception as e:
            logger.error(f"Error fetching hotel bookings: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_hotels(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        
        if not isinstance(data, dict):
            return results
        
        hotel = data.get("HotelDetails") or {}
        for status_key in ["Upcoming", "Completed", "Cancelled", "Pending"]:
            hotel_list = hotel.get(status_key) or []
            for h in hotel_list:
                results.append({
                    "type": "Hotel",
                    "status": status_key,
                    "booking_id": h.get("BookingRefNo"),
                    "hotel_name": h.get("HotelName"),
                    "checkin": h.get("CheckInDate"),
                    "checkout": h.get("CheckOutDate"),
                    "rooms": h.get("NoOfRooms"),
                    "guests": h.get("NoOfGuests")
                })

        return results


def build_whatsapp_hotel_bookings_response(bookings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build WhatsApp-formatted response for hotel bookings."""
    items = []
    for b in bookings:
        items.append({
            "status": b.get("status"),
            "booking_id": b.get("booking_id"),
            "hotel_name": b.get("hotel_name"),
            "checkin": b.get("checkin"),
            "checkout": b.get("checkout"),
            "rooms": b.get("rooms"),
            "guests": b.get("guests"),
        })

    return {
        "type": "hotel_bookings",
        "total": len(items),
        "bookings": items,
    }
