"""Train Bookings Tool """
from typing import Dict, Any
import logging

from pydantic import ValidationError
from ..base import BaseTool, ToolMetadata
from .train_bookings_service import TrainBookingsService, build_whatsapp_train_bookings_response
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
            name="fetch_train_booking_details",
            description="Fetch all train bookings for the logged-in user. If user is not logged in, tell them to provide their phone number or email to login via OTP.",
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
            is_whatsapp = user_type.lower() == "whatsapp"

            try:
                payload = GetBookingsInput.model_validate(kwargs)
            except ValidationError as exc:
                return ToolResponseFormat(
                    response_text="Invalid booking input",
                    structured_content={"error": "VALIDATION_ERROR", "details": exc.errors()},
                    is_error=True,
                )

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
            user_account = token_provider.get_email() or token_provider.get_phone() or result.get("uid")

            # Filter by status if provided
            # In TrainDetails API, cancelled bookings are stored under "Refunded" key
            if payload.status:
                train_status_match = "Refunded" if payload.status == "Cancelled" else payload.status
                bookings = [b for b in bookings if b.get("status", "").lower() == train_status_match.lower()]

            if not bookings:
                return ToolResponseFormat(
                    response_text=f"No train bookings found for account {user_account}.",
                    structured_content={
                        "account": user_account,
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
                f"Account: {user_account}\n"
                f"Total bookings: {len(bookings)}\n\n"
                + "\n".join(lines)
            )
            
            raw_response = result.get("raw_response", {})

            # Filter raw_response for renderer if status filter is applied
            if payload.status and raw_response:
                # In TrainDetails API, cancelled bookings are stored under "Refunded" key
                train_status_key = "Refunded" if payload.status == "Cancelled" else payload.status
                train_details = raw_response.get("TrainDetails") or {}
                filtered_details = {k: v for k, v in train_details.items() if k.lower() == train_status_key.lower()}
                raw_response = dict(raw_response)
                raw_response["TrainDetails"] = filtered_details

            # Render HTML for website
            html_content = None
            if render_html:
                train_data = raw_response.get("TrainDetails") if raw_response else None
                if train_data:
                    html_content = render_train_bookings(train_data)

            # Build WhatsApp response if needed
            whatsapp_response = None
            if is_whatsapp:
                whatsapp_response = build_whatsapp_train_bookings_response(bookings)

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
            logger.error("Error executing get_train_bookings", exc_info=True)
            return ToolResponseFormat(
                response_text=f"❌ Error fetching train bookings: {str(e)}",
                is_error=True
            )
