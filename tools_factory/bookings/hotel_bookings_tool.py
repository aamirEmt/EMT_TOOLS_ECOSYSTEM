"""Hotel Bookings Tool"""
from typing import Dict, Any
import logging

from ..base import BaseTool, ToolMetadata
from .hotel_bookings_service import HotelBookingsService
from .hotel_bookings_renderer import render_hotel_bookings
from .booking_schema import GetBookingsInput
from tools_factory.base_schema import ToolResponseFormat
from emt_client.auth.session_manager import SessionManager

logger = logging.getLogger(__name__)


class GetHotelBookingsTool(BaseTool):
    """Tool for fetching hotel bookings"""

    def __init__(self, session_manager: SessionManager):
        """
        Initialize with SessionManager for multi-user support.

        Args:
            session_manager: SessionManager to look up user sessions by session_id
        """
        super().__init__()
        self.session_manager = session_manager
    
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
            # Extract runtime flags (internal)
            session_id = kwargs.pop("_session_id", None)
            limit = kwargs.pop("_limit", None)
            user_type = kwargs.pop("_user_type", "website")
            render_html = user_type.lower() == "website"

            # Validate session_id is provided
            if not session_id:
                return ToolResponseFormat(
                    response_text="session_id is required. Please login first to get a session_id.",
                    is_error=True
                )

            # Get session-specific token provider
            token_provider = self.session_manager.get_session(session_id)

            if not token_provider:
                return ToolResponseFormat(
                    response_text="Invalid or expired session. Please login again.",
                    is_error=True
                )

            # Create service with session-specific provider
            service = HotelBookingsService(token_provider)
            result = await service.get_hotel_bookings()
            
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
            
            raw_response = result.get("raw_response", {})

            # Render HTML for website
            html_content = None
            if render_html:
                hotel_data = raw_response.get("HotelDetails") if raw_response else None
                if hotel_data:
                    html_content = render_hotel_bookings(hotel_data)

            return ToolResponseFormat(
                response_text=response_text,
                structured_content={
                    "uid": uid,
                    "total": len(bookings),
                    "bookings": bookings,
                    "raw_response": raw_response,
                },
                html=html_content,
            )

        except Exception as e:
            logger.error("Error executing get_hotel_bookings", exc_info=True)
            return ToolResponseFormat(
                response_text=f"❌ Error fetching hotel bookings: {str(e)}",
                is_error=True
            )
