"""Bus Bookings Tool"""
from typing import Dict, Any
import logging

from ..base import BaseTool, ToolMetadata
from .bus_bookings_service import BusBookingsService
from tools_factory.login.login_tool import LoginTool
from .booking_schema import GetBookingsInput
from tools_factory.base_schema import ToolResponseFormat

logger = logging.getLogger(__name__)


class GetBusBookingsTool(BaseTool):
    """Tool for fetching bus bookings"""
    
    def __init__(self, login_tool: LoginTool):
        super().__init__()
        self.service = BusBookingsService(login_tool.service.token_provider)
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="get_bus_bookings",
            description="Fetch all bus bookings for the logged-in user.",
            input_schema=GetBookingsInput.model_json_schema(),
            output_template=None,
            category="bookings",
            tags=["bookings", "bus"]
        )
    
    async def execute(self, **kwargs) -> ToolResponseFormat:
        try:
            result = await self.service.get_bus_bookings()
            
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
            
            return ToolResponseFormat(
                response_text=response_text,
                structured_content={
                    "uid": uid,
                    "total": len(bookings),
                    "bookings": bookings
                },
                is_error=False
            )
        
        except Exception as e:
            logger.error("Error executing get_bus_bookings", exc_info=True)
            return ToolResponseFormat(
                response_text=f"❌ Error fetching bus bookings: {str(e)}",
                is_error=True
            )