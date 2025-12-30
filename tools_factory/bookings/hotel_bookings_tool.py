"""Hotel Bookings Tool - Following main.py pattern"""
from typing import Dict, Any
import logging

from ..base import BaseTool, ToolMetadata
from .hotel_bookings_service import HotelBookingsService
from tools_factory.login.login_tool import LoginTool

logger = logging.getLogger(__name__)


class GetHotelBookingsTool(BaseTool):
    """Tool for fetching hotel bookings"""
    
    def __init__(self, login_tool: LoginTool):
        super().__init__()
        self.service = HotelBookingsService(login_tool.service.token_provider)
    
    def get_metadata(self) -> ToolMetadata:
        """Metadata matching main.py pattern"""
        return ToolMetadata(
            name="get_hotel_bookings",
            description="Fetch all hotel bookings (Upcoming, Completed, Cancelled, Pending) for the logged-in user.",
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            },
            output_template=None,
            category="bookings",
            tags=["bookings", "hotel"]
        )
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute following main.py pattern"""
        try:
            result = await self.service.get_hotel_bookings()
            
            if not result.get("success"):
                error_message = result.get("error", "Unknown error")
                return {
                    "success": False,
                    "error": error_message,
                    "text_content": f"❌ Failed to fetch hotel bookings: {error_message}"
                }
            
            bookings = result.get("bookings", [])
            
            if not bookings:
                return {
                    "success": True,
                    "email": result.get("email"),
                    "total": 0,
                    "bookings": [],
                    "text_content": f"No hotel bookings found for {result.get('email')}"
                }
            
            # Format bookings following main.py pattern
            lines = []
            for b in bookings:
                line = f"• {b.get('status')} | Booking ID: {b.get('booking_id')}"
                line += f" | Hotel: {b.get('hotel_name')}"
                
                if b.get('checkin'):
                    line += f" | Check-in: {b.get('checkin')}"
                
                if b.get('checkout'):
                    line += f" | Check-out: {b.get('checkout')}"
                
                if b.get('rooms'):
                    line += f" | Rooms: {b.get('rooms')}"
                
                if b.get('guests'):
                    line += f" | Guests: {b.get('guests')}"
                
                lines.append(line)
            
            text_content = (
                f"Bookings found \\n\\n"
                f"Account: {result.get('email')}\\n"
                f"Total bookings: {len(bookings)}\\n\\n"
                + "\\n".join(lines)
            )
            
            return {
                "success": True,
                "email": result.get("email"),
                "total": len(bookings),
                "bookings": bookings,
                "text_content": text_content,
                "structured_content": result
            }
        
        except Exception as e:
            logger.error(f"Error executing get hotel bookings: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "text_content": f"❌ Error: {str(e)}"
            }
