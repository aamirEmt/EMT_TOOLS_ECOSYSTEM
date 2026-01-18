"""Tests for login tool"""
import pytest
from tools_factory.factory import get_tool_factory


@pytest.mark.asyncio
async def test_login_tool_exists():
    """Test that login tool is registered"""
    factory = get_tool_factory()
    tool = factory.get_tool("login_user")
    
    assert tool is not None
    assert tool.get_metadata().name == "login_user"


@pytest.mark.asyncio
async def test_login_tool_metadata():
    """Test login tool metadata"""
    factory = get_tool_factory()
    tool = factory.get_tool("login_user")
    metadata = tool.get_metadata()
    
    assert metadata.category == "authentication"
    assert "login" in metadata.tags
    assert "phone_number" in metadata.input_schema["properties"]
    # assert "ip_address" in metadata.input_schema["properties"]  # Commented out - not needed


@pytest.mark.asyncio
async def test_login_missing_params():
    """Test login with missing parameters"""
    factory = get_tool_factory()
    tool = factory.get_tool("login_user")
    
    # Missing phone_number
    result = await tool.execute()  # ip_address="192.168.1.1"
    assert result.is_error is True
    assert "phone" in result.response_text.lower()
    
    # # Missing ip_address - no longer needed
    # result = await tool.execute(phone_number="9876543210")
    # assert result["success"] is False
    # assert "ip" in result["error"].lower()


@pytest.mark.asyncio
async def test_auth_tools_category():
    """Test getting all authentication tools"""
    factory = get_tool_factory()
    auth_tools = factory.get_tools_by_category("authentication")
    
    assert len(auth_tools) >= 1
    
    tool_names = [tool.get_metadata().name for tool in auth_tools]
    assert "login_user" in tool_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
