"""Flight Bookings Tool - Following main.py pattern"""
from typing import Dict, Any
import logging

from ..base import BaseTool, ToolMetadata
from .flight_bookings_service import FlightBookingsService
from tools_factory.login.login_tool import LoginTool

logger = logging.getLogger(__name__)


class GetFlightBookingsTool(BaseTool):
    """Tool for fetching flight bookings"""
    
    def __init__(self, login_tool: LoginTool):
        super().__init__()
        self.service = FlightBookingsService(login_tool.service.token_provider)
    
    def get_metadata(self) -> ToolMetadata:
        """Metadata matching main.py pattern"""
        return ToolMetadata(
            name="get_flight_bookings",
            description="Fetch all flight bookings (Upcoming, Completed, Cancelled, Rejected, Locked) for the logged-in user.",
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            },
            output_template=None,
            category="bookings",
            tags=["bookings", "flight"]
        )
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute following main.py pattern"""
        try:
            result = await self.service.get_flight_bookings()
            
            if not result.get("success"):
                error_message = result.get("error", "Unknown error")
                return {
                    "success": False,
                    "error": error_message,
                    "text_content": f"❌ Failed to fetch flight bookings: {error_message}"
                }
            
            bookings = result.get("bookings", [])
            
            if not bookings:
                return {
                    "success": True,
                    "email": result.get("email"),
                    "total": 0,
                    "bookings": [],
                    "text_content": f"No flight bookings found for {result.get('email')}"
                }
            
            # Format bookings following main.py pattern
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
            logger.error(f"Error executing get flight bookings: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "text_content": f"❌ Error: {str(e)}"
            }
