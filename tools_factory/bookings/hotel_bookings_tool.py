"""Hotel Bookings Tool"""
from typing import Dict, Any
import logging

from ..base import BaseTool, ToolMetadata
from .hotel_bookings_service import HotelBookingsService
from tools_factory.login.login_tool import LoginTool
from .booking_schema import GetBookingsInput
from tools_factory.base_schema import ToolResponseFormat

logger = logging.getLogger(__name__)


class GetHotelBookingsTool(BaseTool):
    """Tool for fetching hotel bookings"""
    
    def __init__(self, login_tool: LoginTool):
        super().__init__()
        self.service = HotelBookingsService(login_tool.service.token_provider)
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="get_hotel_bookings",
            description="Fetch all hotel bookings (Upcoming, Completed, Cancelled, Pending) for the logged-in user.",
            input_schema=GetBookingsInput.model_json_schema(),
            output_template=None,
            category="bookings",
            tags=["bookings", "hotel"]
        )
    
    async def execute(self, **kwargs) -> ToolResponseFormat:
        try:
            result = await self.service.get_hotel_bookings()
            
            if not result.get("success"):
                error_message = result.get("error", "Unknown error")
                return ToolResponseFormat(
                    response_text=f"❌ Failed to fetch hotel bookings: {error_message}",
                    structured_content=result,
                    is_error=True
                )

            bookings = result.get("bookings", [])
            uid = result.get("uid")

            if not bookings:
                return ToolResponseFormat(
                    response_text=f"No hotel bookings found for account {uid}.",
                    structured_content={
                        "uid": uid,
                        "total": 0,
                        "bookings": []
                    }
                )

            
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
            
            response_text = (
                f"Bookings found \\n\\n"
                f"Account: {result.get('uid')}\n"
                f"Total bookings: {len(bookings)}\n\n"
                + "\n".join(lines)
            )
            
            return ToolResponseFormat(
                response_text=response_text,
                structured_content={
                    "uid": uid,
                    "total": len(bookings),
                    "bookings": bookings
                }
            )

        except Exception as e:
            logger.error("Error executing get_hotel_bookings", exc_info=True)
            return ToolResponseFormat(
                response_text=f"❌ Error fetching hotel bookings: {str(e)}",
                is_error=True
            )
