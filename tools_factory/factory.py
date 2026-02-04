from tools_factory.base import BaseTool
from tools_factory.flights.flight_search_tool import FlightSearchTool
from tools_factory.hotels.hotel_search_tool import HotelSearchTool
from tools_factory.login.login_tool import LoginTool
from tools_factory.bookings.flight_bookings_tool import GetFlightBookingsTool
from tools_factory.bookings.hotel_bookings_tool import GetHotelBookingsTool
from tools_factory.bookings.train_bookings_tool import GetTrainBookingsTool
from tools_factory.bookings.bus_bookings_tool import GetBusBookingsTool
from emt_client.auth.session_manager import SessionManager
from typing import Dict, Optional, List


class ToolFactory:
    """Central factory for managing and creating tools"""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self.session_manager = SessionManager()  # Per-user session isolation
        self._register_default_tools()

    def _register_default_tools(self):
        """Register all available tools"""
        # Search tools (no session needed)
        self.register_tool(FlightSearchTool())
        self.register_tool(HotelSearchTool())

        # Login tool with session manager for multi-user support
        login_tool = LoginTool(self.session_manager)
        self.register_tool(login_tool)

        # Booking tools with session manager (require session_id parameter)
        self.register_tool(GetFlightBookingsTool(self.session_manager))
        self.register_tool(GetHotelBookingsTool(self.session_manager))
        self.register_tool(GetTrainBookingsTool(self.session_manager))
        self.register_tool(GetBusBookingsTool(self.session_manager))
    
    def register_tool(self, tool: BaseTool):
        """Register a tool"""
        self._tools[tool.metadata.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a specific tool by name"""
        return self._tools.get(name)
    
    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """Get all tools in a category"""
        return [
            tool for tool in self._tools.values()
            if tool.metadata.category == category
        ]
    
    def get_tools_by_tags(self, tags: List[str]) -> List[BaseTool]:
        """Get tools matching any of the given tags"""
        return [
            tool for tool in self._tools.values()
            if tool.metadata.tags and any(tag in tool.metadata.tags for tag in tags)
        ]
    
    def get_tools_by_names(self, names: List[str]) -> List[BaseTool]:
        """Get specific tools by names"""
        return [
            self._tools[name] for name in names
            if name in self._tools
        ]
    
    def list_all_tools(self) -> List[BaseTool]:
        """Get all available tools"""
        return list(self._tools.values())

    def get_session_manager(self) -> SessionManager:
        """Get the session manager for direct session manipulation"""
        return self.session_manager

# ====================
# TOOL REGISTRY (Singleton)
# ====================

_tool_factory_instance = None

def get_tool_factory() -> ToolFactory:
    """Get the global tool factory instance"""
    global _tool_factory_instance
    if _tool_factory_instance is None:
        _tool_factory_instance = ToolFactory()
    return _tool_factory_instance