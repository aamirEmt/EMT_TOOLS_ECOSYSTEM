"""Test script to check your bookings using phone number"""
import asyncio
from tools_factory.factory import get_tool_factory


async def check_my_bookings(phone_number: str, ip_address: str = "49.249.40.58"):
    """
    Test script to login and fetch all bookings
    
    Args:
        phone_number: Your phone number (e.g., "9876543210")
        ip_address: IP address (default: 49.249.40.58 - hardcoded from code)
    """
    factory = get_tool_factory()
    
    print("=" * 70)
    print("EMT BOOKINGS TEST SCRIPT")
    print("=" * 70)
    
    # Step 1: Login
    print(f"\n📱 Step 1: Logging in with phone: {phone_number}")
    print(f"Using IP address: {ip_address}")
    print("-" * 70)
    
    login_tool = factory.get_tool("login_user")
    login_result = await login_tool.execute(
        phone_number=phone_number,
        ip_address=ip_address
    )
    
    if not login_result.get("success"):
        print("❌ LOGIN FAILED!")
        print(f"Error: {login_result.get('error')}")
        print(f"\nFull response: {login_result}")
        return
    
    print("✅ LOGIN SUCCESSFUL!")
    print(login_result.get("text_content", ""))
    
    # Step 2: Get Flight Bookings
    print("\n" + "=" * 70)
    print("✈️  Step 2: Fetching Flight Bookings")
    print("-" * 70)
    
    flight_tool = factory.get_tool("get_flight_bookings")
    flight_result = await flight_tool.execute()
    
    if flight_result.get("success"):
        print(flight_result.get("text_content", ""))
        if flight_result.get("bookings"):
            print(f"\nTotal flight bookings found: {len(flight_result['bookings'])}")
    else:
        print(f"❌ Error: {flight_result.get('error')}")
    
    # Step 3: Get Hotel Bookings
    print("\n" + "=" * 70)
    print("🏨 Step 3: Fetching Hotel Bookings")
    print("-" * 70)
    
    hotel_tool = factory.get_tool("get_hotel_bookings")
    hotel_result = await hotel_tool.execute()
    
    if hotel_result.get("success"):
        print(hotel_result.get("text_content", ""))
        if hotel_result.get("bookings"):
            print(f"\nTotal hotel bookings found: {len(hotel_result['bookings'])}")
    else:
        print(f"❌ Error: {hotel_result.get('error')}")
    
    # Step 4: Get Train Bookings
    print("\n" + "=" * 70)
    print("🚂 Step 4: Fetching Train Bookings")
    print("-" * 70)
    
    train_tool = factory.get_tool("get_train_bookings")
    train_result = await train_tool.execute()
    
    if train_result.get("success"):
        print(train_result.get("text_content", ""))
        if train_result.get("bookings"):
            print(f"\nTotal train bookings found: {len(train_result['bookings'])}")
    else:
        print(f"❌ Error: {train_result.get('error')}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    # Get phone number from user
    print("\n" + "=" * 70)
    print("EMT TOOLS - BOOKINGS CHECKER")
    print("=" * 70)
    
    phone = input("\nEnter your phone number: ").strip()
    
    # Optional: get IP address (or use default)
    use_custom_ip = input("Use custom IP address? (y/n, default=n): ").strip().lower()
    
    if use_custom_ip == 'y':
        ip = input("Enter IP address: ").strip()
    else:
        ip = "127.0.0.1"
    
    print("\nStarting test...\n")
    
    # Run the async function
    asyncio.run(check_my_bookings(phone, ip))
