"""Integration test - Login then check all bookings (Flights, Hotels, Trains, Buses)"""
import pytest
import asyncio
from tools_factory.factory import get_tool_factory


# ============================================================================
# REPLACE WITH YOUR ACTUAL PHONE NUMBER
# ============================================================================
YOUR_PHONE_NUMBER = "santoshkr86420@gmail.com"  # ← CHANGE THIS TO YOUR ACTUAL PHONE NUMBER
YOUR_IP_ADDRESS = "49.249.40.58"
# ============================================================================


@pytest.mark.asyncio
async def test_full_booking_workflow():
    """
    Full workflow test:
    1. Login with phone number
    2. Fetch flight bookings
    3. Fetch hotel bookings
    4. Fetch train bookings
    5. Fetch bus bookings
    """
    factory = get_tool_factory()
    
    # ========================
    # STEP 1: LOGIN
    # ========================
    print("\n" + "="*80)
    print("STEP 1: LOGGING IN")
    print("="*80)
    
    login_tool = factory.get_tool("login_user")
    assert login_tool is not None, "Login tool not found"
    
    login_result = await login_tool.execute(
        phone_number=YOUR_PHONE_NUMBER,
        ip_address=YOUR_IP_ADDRESS
    )
    
    print(f"\nLogin Result:")
    print(f"  Success: {login_result.get('success')}")
    print(f"  Error: {login_result.get('error', 'None')}")
    if login_result.get('success'):
        print(f"  User Info: {login_result.get('user_info', {})}")
    
    assert login_result.get("success") is True, f"Login failed: {login_result.get('error')}"
    print("✅ Login successful!")
    
    
    # ========================
    # STEP 2: FETCH FLIGHT BOOKINGS
    # ========================
    print("\n" + "="*80)
    print("STEP 2: FETCHING FLIGHT BOOKINGS")
    print("="*80)
    
    flight_tool = factory.get_tool("get_flight_bookings")
    assert flight_tool is not None, "Flight bookings tool not found"
    
    flight_result = await flight_tool.execute()
    
    print(f"\nFlight Bookings Result:")
    print(f"  Success: {flight_result.get('success')}")
    print(f"  Error: {flight_result.get('error', 'None')}")
    print(f"  Email: {flight_result.get('email')}")
    print(f"  Total: {flight_result.get('total', 0)}")
    
    if flight_result.get('success'):
        bookings = flight_result.get('bookings', [])
        print(f"\n  Bookings ({len(bookings)}):")
        for i, booking in enumerate(bookings, 1):
            print(f"    {i}. {booking.get('status')} | {booking.get('source')} → {booking.get('destination')}")
            print(f"       Booking ID: {booking.get('booking_id')}")
            print(f"       Flight: {booking.get('flight_number')} | Depart: {booking.get('departure')}")
    else:
        print(f"  ⚠️  Error: {flight_result.get('error')}")
    
    assert flight_result.get("success") is True, f"Flight bookings fetch failed: {flight_result.get('error')}"
    print("✅ Flight bookings fetched!")
    
    
    # ========================
    # STEP 3: FETCH HOTEL BOOKINGS
    # ========================
    print("\n" + "="*80)
    print("STEP 3: FETCHING HOTEL BOOKINGS")
    print("="*80)
    
    hotel_tool = factory.get_tool("get_hotel_bookings")
    assert hotel_tool is not None, "Hotel bookings tool not found"
    
    hotel_result = await hotel_tool.execute()
    
    print(f"\nHotel Bookings Result:")
    print(f"  Success: {hotel_result.get('success')}")
    print(f"  Error: {hotel_result.get('error', 'None')}")
    print(f"  Email: {hotel_result.get('email')}")
    print(f"  Total: {hotel_result.get('total', 0)}")
    
    if hotel_result.get('success'):
        bookings = hotel_result.get('bookings', [])
        print(f"\n  Bookings ({len(bookings)}):")
        for i, booking in enumerate(bookings, 1):
            print(f"    {i}. {booking.get('status')} | {booking.get('hotel_name')}")
            print(f"       Booking ID: {booking.get('booking_id')}")
            print(f"       Check-in: {booking.get('checkin')} | Check-out: {booking.get('checkout')}")
            print(f"       Rooms: {booking.get('rooms')} | Guests: {booking.get('guests')}")
    else:
        print(f"  ⚠️  Error: {hotel_result.get('error')}")
    
    assert hotel_result.get("success") is True, f"Hotel bookings fetch failed: {hotel_result.get('error')}"
    print("✅ Hotel bookings fetched!")
    
    
    # ========================
    # STEP 4: FETCH TRAIN BOOKINGS
    # ========================
    print("\n" + "="*80)
    print("STEP 4: FETCHING TRAIN BOOKINGS")
    print("="*80)
    
    train_tool = factory.get_tool("get_train_bookings")
    assert train_tool is not None, "Train bookings tool not found"
    
    train_result = await train_tool.execute()
    
    print(f"\nTrain Bookings Result:")
    print(f"  Success: {train_result.get('success')}")
    print(f"  Error: {train_result.get('error', 'None')}")
    print(f"  Email: {train_result.get('email')}")
    print(f"  Total: {train_result.get('total', 0)}")
    
    if train_result.get('success'):
        bookings = train_result.get('bookings', [])
        print(f"\n  Bookings ({len(bookings)}):")
        for i, booking in enumerate(bookings, 1):
            print(f"    {i}. {booking.get('status')} | {booking.get('source')} → {booking.get('destination')}")
            print(f"       Booking ID: {booking.get('booking_id')}")
            print(f"       PNR: {booking.get('pnr')} | Depart: {booking.get('departure')}")
    else:
        print(f"  ⚠️  Error: {train_result.get('error')}")
    
    assert train_result.get("success") is True, f"Train bookings fetch failed: {train_result.get('error')}"
    print("✅ Train bookings fetched!")
    
    
    # ========================
    # STEP 5: FETCH BUS BOOKINGS
    # ========================
    print("\n" + "="*80)
    print("STEP 5: FETCHING BUS BOOKINGS")
    print("="*80)
    
    bus_tool = factory.get_tool("get_bus_bookings")
    assert bus_tool is not None, "Bus bookings tool not found"
    
    bus_result = await bus_tool.execute()
    
    print(f"\nBus Bookings Result:")
    print(f"  Success: {bus_result.get('success')}")
    print(f"  Error: {bus_result.get('error', 'None')}")
    print(f"  Email: {bus_result.get('email')}")
    print(f"  Total: {bus_result.get('total', 0)}")
    
    if bus_result.get('success'):
        bookings = bus_result.get('bookings', [])
        print(f"\n  Bookings ({len(bookings)}):")
        for i, booking in enumerate(bookings, 1):
            print(f"    {i}. {booking.get('status')} | {booking.get('source')} → {booking.get('destination')}")
            print(f"       Booking ID: {booking.get('booking_id')}")
            print(f"       Route: {booking.get('route')} | Type: {booking.get('bus_type')}")
            print(f"       Operator: {booking.get('operator')} | Journey: {booking.get('journey_date')}")
    else:
        print(f"  ⚠️  Error: {bus_result.get('error')}")
    
    assert bus_result.get("success") is True, f"Bus bookings fetch failed: {bus_result.get('error')}"
    print("✅ Bus bookings fetched!")
    
    
    # ========================
    # SUMMARY
    # ========================
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n✅ All tests passed!")
    print(f"\nBookings Summary:")
    print(f"  • Flights: {flight_result.get('total', 0)}")
    print(f"  • Hotels: {hotel_result.get('total', 0)}")
    print(f"  • Trains: {train_result.get('total', 0)}")
    print(f"  • Buses: {bus_result.get('total', 0)}")
    print(f"  • Total: {flight_result.get('total', 0) + hotel_result.get('total', 0) + train_result.get('total', 0) + bus_result.get('total', 0)}")
    print("\n" + "="*80)


@pytest.mark.asyncio
async def test_login_only():
    """Test just the login step to verify credentials"""
    factory = get_tool_factory()
    
    login_tool = factory.get_tool("login_user")
    result = await login_tool.execute(
        phone_number=YOUR_PHONE_NUMBER,
        ip_address=YOUR_IP_ADDRESS
    )
    
    assert result.get("success") is True, f"Login failed: {result.get('error')}"
    print(f"✅ Login successful with phone {YOUR_PHONE_NUMBER}")
    print(f"   User: {result.get('user_info', {})}")


@pytest.mark.asyncio
async def test_all_booking_tools_exist():
    """Verify all 4 booking tools are registered"""
    factory = get_tool_factory()
    
    flight_tool = factory.get_tool("get_flight_bookings")
    hotel_tool = factory.get_tool("get_hotel_bookings")
    train_tool = factory.get_tool("get_train_bookings")
    bus_tool = factory.get_tool("get_bus_bookings")
    
    assert flight_tool is not None, "Flight bookings tool not found"
    assert hotel_tool is not None, "Hotel bookings tool not found"
    assert train_tool is not None, "Train bookings tool not found"
    assert bus_tool is not None, "Bus bookings tool not found"
    
    print("✅ All 4 booking tools are registered:")
    print(f"   1. {flight_tool.get_metadata().name}")
    print(f"   2. {hotel_tool.get_metadata().name}")
    print(f"   3. {train_tool.get_metadata().name}")
    print(f"   4. {bus_tool.get_metadata().name}")


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_bookings_integration.py -v -s
    pytest.main([__file__, "-v", "-s"])
