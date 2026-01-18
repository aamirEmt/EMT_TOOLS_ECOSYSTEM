"""Tests for booking tools"""
import pytest
from tools_factory.factory import get_tool_factory


@pytest.mark.asyncio
async def test_flight_bookings_tool_exists():
    """Test that flight bookings tool is registered"""
    factory = get_tool_factory()
    tool = factory.get_tool("get_flight_bookings")
    
    assert tool is not None
    assert tool.get_metadata().name == "get_flight_bookings"


@pytest.mark.asyncio
async def test_hotel_bookings_tool_exists():
    """Test that hotel bookings tool is registered"""
    factory = get_tool_factory()
    tool = factory.get_tool("get_hotel_bookings")
    
    assert tool is not None
    assert tool.get_metadata().name == "get_hotel_bookings"


@pytest.mark.asyncio
async def test_train_bookings_tool_exists():
    """Test that train bookings tool is registered"""
    factory = get_tool_factory()
    tool = factory.get_tool("get_train_bookings")
    
    assert tool is not None
    assert tool.get_metadata().name == "get_train_bookings"


@pytest.mark.asyncio
async def test_booking_tools_metadata():
    """Test booking tools metadata"""
    factory = get_tool_factory()
    
    flight_tool = factory.get_tool("get_flight_bookings")
    hotel_tool = factory.get_tool("get_hotel_bookings")
    train_tool = factory.get_tool("get_train_bookings")
    
    assert flight_tool.get_metadata().category == "bookings"
    assert hotel_tool.get_metadata().category == "bookings"
    assert train_tool.get_metadata().category == "bookings"
    
    assert "bookings" in flight_tool.get_metadata().tags
    assert "bookings" in hotel_tool.get_metadata().tags
    assert "bookings" in train_tool.get_metadata().tags


@pytest.mark.asyncio
async def test_bookings_require_login():
    """Test that booking tools require login"""
    factory = get_tool_factory()
    
    flight_tool = factory.get_tool("get_flight_bookings")
    hotel_tool = factory.get_tool("get_hotel_bookings")
    train_tool = factory.get_tool("get_train_bookings")
    bus_tool = factory.get_tool("get_bus_bookings")
    
    # Should fail without login
    flight_result = await flight_tool.execute()
    assert flight_result.structured_content["success"] is False
    assert "USER_NOT_LOGGED_IN" in flight_result.structured_content["error"]
    
    hotel_result = await hotel_tool.execute()
    assert hotel_result.structured_content["success"] is False
    assert "USER_NOT_LOGGED_IN" in hotel_result.structured_content["error"]
    
    train_result = await train_tool.execute()
    assert train_result.structured_content["success"] is False
    assert "USER_NOT_LOGGED_IN" in train_result.structured_content["error"] 
    bus_result = await bus_tool.execute()
    assert bus_result.structured_content["success"] is False
    assert "USER_NOT_LOGGED_IN" in bus_result.structured_content["error"]

@pytest.mark.asyncio
async def test_bookings_tools_category():
    """Test getting all booking tools by category"""
    factory = get_tool_factory()
    booking_tools = factory.get_tools_by_category("bookings")
    
    assert len(booking_tools) == 4
    
    tool_names = [tool.get_metadata().name for tool in booking_tools]
    assert "get_flight_bookings" in tool_names
    assert "get_hotel_bookings" in tool_names
    assert "get_train_bookings" in tool_names
    assert "get_bus_bookings" in tool_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
