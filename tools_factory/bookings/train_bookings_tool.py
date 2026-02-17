"""Train Bookings Tool """
from typing import Dict, Any
import logging

from ..base import BaseTool, ToolMetadata
from .train_bookings_service import TrainBookingsService
from .train_bookings_renderer import render_train_bookings
from .booking_schema import GetBookingsInput
from tools_factory.base_schema import ToolResponseFormat
from emt_client.auth.session_manager import SessionManager

logger = logging.getLogger(__name__)


class GetTrainBookingsTool(BaseTool):
    """Tool for fetching train bookings"""

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
            name="get_train_bookings",
            description="Fetch all train bookings for the logged-in user.",
            input_schema=GetBookingsInput.model_json_schema(),
            output_template=None,
            category="bookings",
            tags=["bookings", "train"]
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
            service = TrainBookingsService(token_provider)
            result = await service.get_train_bookings()
            
            if not result.get("success"):
                error_message = result.get("error", "Unknown error")
                return ToolResponseFormat(
                    response_text=f"❌ Failed to fetch train bookings: {error_message}",
                    structured_content=result,
                    is_error=True
                )
            
            bookings = result.get("bookings", [])
            uid = result.get("uid")

            if not bookings:
                return ToolResponseFormat(
                    response_text=f"No train bookings found for account {uid}.",
                    structured_content={
                        "uid": uid,
                        "total": 0,
                        "bookings": []
                    }
                )
           
            lines = []
            for b in bookings:
                line = f"• {b.get('status')} | Booking ID: {b.get('booking_id')}"
                
                if b.get('pnr'):
                    line += f" | PNR: {b.get('pnr')}"
                
                line += f" | {b.get('source')} → {b.get('destination')}"
                
                if b.get('departure'):
                    line += f" | Departure: {b.get('departure')}"
                
                if b.get('arrival'):
                    line += f" | Arrival: {b.get('arrival')}"
                
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
                train_data = raw_response.get("TrainDetails") if raw_response else None
                if train_data:
                    html_content = render_train_bookings(train_data)

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
            logger.error("Error executing get_train_bookings", exc_info=True)
            return ToolResponseFormat(
                response_text=f"❌ Error fetching train bookings: {str(e)}",
                is_error=True
            )
