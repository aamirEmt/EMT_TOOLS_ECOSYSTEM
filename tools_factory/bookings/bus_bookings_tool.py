"""Bus Bookings Tool"""
from typing import Dict, Any
import logging

from ..base import BaseTool, ToolMetadata
from .bus_bookings_service import BusBookingsService
from .bus_bookings_renderer import render_bus_bookings
from .booking_schema import GetBookingsInput
from tools_factory.base_schema import ToolResponseFormat
from emt_client.auth.session_manager import SessionManager

logger = logging.getLogger(__name__)


class GetBusBookingsTool(BaseTool):
    """Tool for fetching bus bookings"""

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
            name="fetch_bus_booking_details",
            description="Fetch all bus bookings for the logged-in user.",
            input_schema=GetBookingsInput.model_json_schema(),
            output_template=None,
            category="bookings",
            tags=["bookings", "bus"]
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
            service = BusBookingsService(token_provider)
            result = await service.get_bus_bookings()
            
            if not result.get("success"):
                error_message = result.get("error", "Unknown error")
                return ToolResponseFormat(
                    response_text=f"❌ Failed to fetch bus bookings: {error_message}",
                    structured_content=result,
                    is_error=True
                )
            
            bookings = result.get("bookings", [])
            uid = result.get("uid")

            if not bookings:
                return ToolResponseFormat(
                    response_text=f"No bus bookings found for account {uid}.",
                    structured_content={
                        "uid": uid,
                        "total": 0,
                        "bookings": []
                    },
                    is_error=False
                )
            
            lines = []
            for b in bookings:
                line = f"• {b.get('status')} | Booking ID: {b.get('booking_id')}"
                
                if b.get('route'):
                    line += f" | Route: {b.get('route')}"
                elif b.get('source') and b.get('destination'):
                    line += f" | {b.get('source')} → {b.get('destination')}"
                
                if b.get('journey_date'):
                    line += f" | Journey: {b.get('journey_date')}"
                
                if b.get('departure'):
                    line += f" | Departure: {b.get('departure')}"
                
                if b.get('arrival'):
                    line += f" | Arrival: {b.get('arrival')}"
                
                if b.get('operator'):
                    line += f" | Operator: {b.get('operator')}"
                
                if b.get('bus_type'):
                    line += f" | Type: {b.get('bus_type')}"
                
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
                bus_data = raw_response.get("BusDetails") if raw_response else None
                if bus_data:
                    html_content = render_bus_bookings(bus_data)

            return ToolResponseFormat(
                response_text=response_text,
                structured_content={
                    "uid": uid,
                    "total": len(bookings),
                    "bookings": bookings,
                },
                html=html_content,
                is_error=False
            )
        
        except Exception as e:
            logger.error("Error executing get_bus_bookings", exc_info=True)
            return ToolResponseFormat(
                response_text=f"❌ Error fetching bus bookings: {str(e)}",
                is_error=True
            )