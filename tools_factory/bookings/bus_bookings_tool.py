"""Bus Bookings Tool"""
from typing import Dict, Any
import logging

from ..base import BaseTool, ToolMetadata
from .bus_bookings_service import BusBookingsService
from tools_factory.login.login_tool import LoginTool
from .booking_schema import GetBookingsInput 

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
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            result = await self.service.get_bus_bookings()
            
            if not result.get("success"):
                error_message = result.get("error", "Unknown error")
                return {
                    "success": False,
                    "error": error_message,
                    "text_content": f"❌ Failed to fetch bus bookings: {error_message}"
                }
            
            bookings = result.get("bookings", [])
            
            if not bookings:
                return {
                    "success": True,
                    "uid": result.get("uid"),
                    "total": 0,
                    "bookings": [],
                    "text_content": f"No bus bookings found for {result.get('uid')}"
                }
            
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
            
            text_content = (
                f"Bookings found \\n\\n"
                f"Account: {result.get('uid')}\n"
                f"Total bookings: {len(bookings)}\n\n"
                + "\n".join(lines)
            )
            
            return {
                "success": True,
                "uid": result.get("uid"),
                "total": len(bookings),
                "bookings": bookings,
                "text_content": text_content,
                "structured_content": result
            }
        
        except Exception as e:
            logger.error(f"Error executing get bus bookings: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "text_content": f"❌ Error: {str(e)}"
            }