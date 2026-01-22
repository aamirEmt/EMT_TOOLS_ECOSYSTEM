"""Train Bookings Tool """
from typing import Dict, Any
import logging

from ..base import BaseTool, ToolMetadata
from .train_bookings_service import TrainBookingsService
from tools_factory.login.login_tool import LoginTool
from .booking_schema import GetBookingsInput
from tools_factory.base_schema import ToolResponseFormat
logger = logging.getLogger(__name__)


class GetTrainBookingsTool(BaseTool):
    """Tool for fetching train bookings"""
    
    def __init__(self, login_tool: LoginTool):
        super().__init__()
        self.service = TrainBookingsService(login_tool.service.token_provider)
    
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
            result = await self.service.get_train_bookings()
            
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
            
            return ToolResponseFormat(
                response_text=response_text,
                structured_content={
                    "uid": uid,
                    "total": len(bookings),
                    "bookings": bookings
                }
            )
        
        except Exception as e:
            logger.error("Error executing get_train_bookings", exc_info=True)
            return ToolResponseFormat(
                response_text=f"❌ Error fetching train bookings: {str(e)}",
                is_error=True
            )
