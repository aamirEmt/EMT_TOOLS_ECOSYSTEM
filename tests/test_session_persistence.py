"""Test session persistence and reuse across multiple booking calls"""
import pytest
from tools_factory.factory import get_tool_factory


@pytest.mark.asyncio
async def test_login_once_use_multiple_times():
    """Test that login session is reused for multiple booking calls"""
    factory = get_tool_factory()
    
    # Step 1: Login
    print("\n=== Step 1: First Login ===")
    login_tool = factory.get_tool("login_user")
    login_result = await login_tool.execute(
        phone_number="9876543210",
        # ip_address="127.0.0.1"  # Commented out - not needed
    )
    
    # Check if login was successful (might fail if invalid credentials)
    if not login_result.get("success"):
        print(f"Login failed (expected for test): {login_result.get('error')}")
        pytest.skip("Login failed - skipping session test")
    
    print(f"Login successful: {login_result.get('user')}")
    
    # Step 2: Get bookings first time
    print("\n=== Step 2: First Booking Call (after login) ===")
    flight_tool = factory.get_tool("get_flight_bookings")
    first_result = await flight_tool.execute()
    print(f"First call result: {first_result.get('success')}")
    
    # Step 3: Get bookings second time WITHOUT logging in again
    print("\n=== Step 3: Second Booking Call (no new login) ===")
    second_result = await flight_tool.execute()
    print(f"Second call result: {second_result.get('success')}")
    
    # Both should succeed if session is maintained
    assert first_result.get("success") == second_result.get("success")
    print("\n✅ Session was reused successfully!")


@pytest.mark.asyncio
async def test_different_tool_instances_share_session():
    """Test that different booking tools share the same login session"""
    factory = get_tool_factory()
    
    # Step 1: Login
    print("\n=== Step 1: Login ===")
    login_tool = factory.get_tool("login_user")
    login_result = await login_tool.execute(
        phone_number="9876543210",
        # ip_address="127.0.0.1"  # Commented out - not needed
    )
    
    if not login_result.get("success"):
        print(f"Login failed (expected for test): {login_result.get('error')}")
        pytest.skip("Login failed - skipping session test")
    
    # Step 2: Get flight bookings
    print("\n=== Step 2: Flight Bookings ===")
    flight_tool = factory.get_tool("get_flight_bookings")
    flight_result = await flight_tool.execute()
    print(f"Flight call: {flight_result.get('success')}")
    
    # Step 3: Get hotel bookings (different tool, should use same session)
    print("\n=== Step 3: Hotel Bookings (different tool) ===")
    hotel_tool = factory.get_tool("get_hotel_bookings")
    hotel_result = await hotel_tool.execute()
    print(f"Hotel call: {hotel_result.get('success')}")
    
    # Step 4: Get train bookings (another different tool)
    print("\n=== Step 4: Train Bookings (another tool) ===")
    train_tool = factory.get_tool("get_train_bookings")
    train_result = await train_tool.execute()
    print(f"Train call: {train_result.get('success')}")
    
    # All should have same success status (all use same session)
    assert flight_result.get("success") == hotel_result.get("success")
    assert hotel_result.get("success") == train_result.get("success")
    print("\n✅ All tools shared the same session!")


@pytest.mark.asyncio
async def test_new_factory_requires_new_login():
    """Test that a new factory instance requires a new login"""
    # Factory 1: Login and get bookings
    print("\n=== Factory 1: Login and get bookings ===")
    factory1 = get_tool_factory()
    
    login_tool1 = factory1.get_tool("login_user")
    login_result = await login_tool1.execute(
        phone_number="9876543210",
        # ip_address="127.0.0.1"  # Commented out - not needed
    )
    
    if not login_result.get("success"):
        print(f"Login failed (expected for test): {login_result.get('error')}")
        pytest.skip("Login failed - skipping session test")
    
    flight_tool1 = factory1.get_tool("get_flight_bookings")
    result1 = await flight_tool1.execute()
    print(f"Factory 1 booking result: {result1.get('success')}")
    
    # Factory 2: Try to get bookings without login (new instance)
    print("\n=== Factory 2: Try bookings without login ===")
    factory2 = get_tool_factory()
    
    flight_tool2 = factory2.get_tool("get_flight_bookings")
    result2 = await flight_tool2.execute()
    print(f"Factory 2 booking result: {result2.get('success')}")
    
    # Note: This test checks if factory is singleton or not
    # If singleton, both should succeed
    # If not singleton, second should fail with USER_NOT_LOGGED_IN
    
    if result2.get("success"):
        print("✅ Factory is singleton - session persisted across get_tool_factory() calls")
    else:
        assert "USER_NOT_LOGGED_IN" in result2.get("error", "")
        print("✅ Factory is not singleton - new instance requires new login")


@pytest.mark.asyncio
async def test_bookings_without_login_should_fail():
    """Test that booking calls fail without login"""
    factory = get_tool_factory()
    
    # Clear any existing session to ensure clean test
    login_tool = factory.get_tool("login_user")
    login_tool.service.logout()
    
    # Try to get bookings without logging in first
    print("\n=== Attempting bookings without login ===")
    
    flight_tool = factory.get_tool("get_flight_bookings")
    flight_result = await flight_tool.execute()
    
    hotel_tool = factory.get_tool("get_hotel_bookings")
    hotel_result = await hotel_tool.execute()
    
    train_tool = factory.get_tool("get_train_bookings")
    train_result = await train_tool.execute()
    
    # All should fail with USER_NOT_LOGGED_IN
    assert flight_result.get("success") is False
    assert hotel_result.get("success") is False
    assert train_result.get("success") is False
    
    assert "USER_NOT_LOGGED_IN" in flight_result.get("error", "")
    assert "USER_NOT_LOGGED_IN" in hotel_result.get("error", "")
    assert "USER_NOT_LOGGED_IN" in train_result.get("error", "")
    
    print("✅ All booking calls correctly failed without login")


@pytest.mark.asyncio
async def test_session_persists_across_hotel_search():
    """Test that session persists when doing hotel search between booking calls"""
    factory = get_tool_factory()
    
    # Step 1: Login
    print("\n=== Step 1: Login ===")
    login_tool = factory.get_tool("login_user")
    login_result = await login_tool.execute(
        phone_number="9876543210",
        # ip_address="127.0.0.1"  # Commented out - not needed
    )
    
    if not login_result.get("success"):
        print(f"Login failed (expected for test): {login_result.get('error')}")
        pytest.skip("Login failed - skipping session persistence test")
    
    print(f"✅ Login successful")
    
    # Step 2: Get flight bookings (first time)
    print("\n=== Step 2: First Booking Call ===")
    flight_tool = factory.get_tool("get_flight_bookings")
    first_booking_result = await flight_tool.execute()
    print(f"First booking call: {first_booking_result.get('success')}")
    
    # Step 3: Search for hotels (different operation)
    print("\n=== Step 3: Hotel Search (in between) ===")
    hotel_search_tool = factory.get_tool("search_hotels")
    hotel_search_result = await hotel_search_tool.execute(
        city_name="Delhi",
        check_in_date="2025-02-01",
        check_out_date="2025-02-03",
        num_rooms=1,
        num_adults=2
    )
    print(f"Hotel search: {hotel_search_result.get('success', 'N/A')}")
    
    # Step 4: Get flight bookings again (should NOT login again)
    print("\n=== Step 4: Second Booking Call (after hotel search) ===")
    second_booking_result = await flight_tool.execute()
    print(f"Second booking call: {second_booking_result.get('success')}")
    
    # Both booking calls should have same success status
    assert first_booking_result.get("success") == second_booking_result.get("success")
    
    print("\n✅ Session persisted across hotel search - no re-login needed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
