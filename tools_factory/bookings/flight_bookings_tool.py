"""Flight Bookings Tool """
from typing import Dict, Any
import logging

from ..base import BaseTool, ToolMetadata
from .flight_bookings_service import FlightBookingsService, build_whatsapp_flight_bookings_response
from .flight_bookings_renderer import render_flight_bookings
from .booking_schema import GetBookingsInput
from tools_factory.base_schema import ToolResponseFormat
from emt_client.auth.session_manager import SessionManager

logger = logging.getLogger(__name__)


class GetFlightBookingsTool(BaseTool):
    """Tool for fetching flight bookings"""

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
            name="fetch_flight_booking_details",
            description="Fetch all flight bookings (Upcoming, Completed, Cancelled, Rejected, Locked) for the logged-in user.",
            input_schema=GetBookingsInput.model_json_schema(),
            output_template=None,
            category="bookings",
            tags=["bookings", "flight"]
        )
    
    async def execute(self, **kwargs) -> ToolResponseFormat:
        try:
            # Extract runtime flags (internal)
            session_id = kwargs.pop("_session_id", None)
            limit = kwargs.pop("_limit", None)
            user_type = kwargs.pop("_user_type", "website")
            render_html = user_type.lower() == "website"
            is_whatsapp = user_type.lower() == "whatsapp"

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
            service = FlightBookingsService(token_provider)
            result = await service.get_flight_bookings()
            
            if not result.get("success"):
                error_message = result.get("error", "Unknown error")
                return ToolResponseFormat(
                    response_text=f"❌ Failed to fetch flight bookings: {error_message}",
                    structured_content=result,
                    is_error=True
                )

            bookings = result.get("bookings", [])
            user_account = token_provider.get_email() or token_provider.get_phone() or result.get("uid")

            if not bookings:
                return ToolResponseFormat(
                    response_text=f"No flight bookings found for account {user_account}.",
                    structured_content={
                        "account": user_account,
                        "total": 0,
                        "bookings": []
                    }
                )
            
            lines = []
            for b in bookings:
                line = f"• {b.get('status')} | Booking ID: {b.get('booking_id')}"
                line += f" | {b.get('source')} → {b.get('destination')}"
                
                if b.get('flight_number'):
                    line += f" | Flight: {b.get('flight_number')}"
                
                if b.get('departure'):
                    line += f" | Departure: {b.get('departure')}"
                
                if b.get('arrival'):
                    line += f" | Arrival: {b.get('arrival')}"
                
                lines.append(line)
            
            response_text = (
                f"Bookings found \\n\\n"
                f"Account: {user_account}\n"
                f"Total bookings: {len(bookings)}\n\n"
                + "\n".join(lines)
            )
            
            raw_response = result.get("raw_response", {})

            # Render HTML for website
            html_content = None
            if render_html:
                flight_data = raw_response.get("FlightDetails") if raw_response else None
                if flight_data:
                    html_content = render_flight_bookings(flight_data)

            # Build WhatsApp response if needed
            whatsapp_response = None
            if is_whatsapp:
                whatsapp_response = build_whatsapp_flight_bookings_response(bookings)

            return ToolResponseFormat(
                response_text=response_text,
                structured_content=None if is_whatsapp else {
                    "account": user_account,
                    "total": len(bookings),
                    "bookings": bookings,
                },
                html=html_content,
                whatsapp_response=whatsapp_response,
            )

        except Exception as e:
            logger.error("Error executing get_flight_bookings", exc_info=True)
            return ToolResponseFormat(
                response_text=f"❌ Error fetching flight bookings: {str(e)}",
                is_error=True
            )
