"""Real API tests for OTP Login Tool.

These tests make actual API calls and verify real responses.
NO MOCKING - Real API integration tests.

File: tests/test_otp_login.py

Run with:
    pytest tests/test_otp_login.py -v -s

Flow:
    1. test_send_otp  -> sends OTP to a real phone number, stores session_id
    2. test_verify_otp -> (manual) verify with the OTP received on the phone
"""

import pytest
from tools_factory.factory import get_tool_factory
from tools_factory.base_schema import ToolResponseFormat

pytestmark = pytest.mark.integration


# ============================================================================
# TOOL REGISTRATION & METADATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_otp_login_tool_exists():
    """Test that otp_login tool is registered."""
    factory = get_tool_factory()
    tool = factory.get_tool("otp_login")

    assert tool is not None
    assert tool.get_metadata().name == "otp_login"


@pytest.mark.asyncio
async def test_otp_login_tool_metadata():
    """Test otp_login tool metadata."""
    factory = get_tool_factory()
    tool = factory.get_tool("otp_login")
    metadata = tool.get_metadata()

    assert metadata.category == "authentication"
    assert "otp" in metadata.tags
    assert "login" in metadata.tags
    assert "action" in metadata.input_schema["properties"]
    assert "phone_or_email" in metadata.input_schema["properties"]
    assert "otp_code" in metadata.input_schema["properties"]


@pytest.mark.asyncio
async def test_otp_login_in_auth_category():
    """Test that otp_login appears in authentication category."""
    factory = get_tool_factory()
    auth_tools = factory.get_tools_by_category("authentication")

    tool_names = [t.get_metadata().name for t in auth_tools]
    assert "otp_login" in tool_names


# ============================================================================
# VALIDATION / ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_send_otp_missing_phone():
    """Test send_otp action with missing phone_or_email."""
    factory = get_tool_factory()
    tool = factory.get_tool("otp_login")

    result = await tool.execute(action="send_otp")
    assert result.is_error is True
    assert "phone_or_email" in result.response_text.lower()


@pytest.mark.asyncio
async def test_verify_otp_missing_otp_code():
    """Test verify_otp action with missing otp_code."""
    factory = get_tool_factory()
    tool = factory.get_tool("otp_login")

    result = await tool.execute(action="verify_otp", _session_id="fake-session-id")
    assert result.is_error is True
    assert "otp_code" in result.response_text.lower()


@pytest.mark.asyncio
async def test_verify_otp_missing_session():
    """Test verify_otp action without session_id."""
    factory = get_tool_factory()
    tool = factory.get_tool("otp_login")

    result = await tool.execute(action="verify_otp", otp_code="123456")
    assert result.is_error is True
    assert "session" in result.response_text.lower()


@pytest.mark.asyncio
async def test_verify_otp_invalid_session():
    """Test verify_otp action with an invalid/expired session_id."""
    factory = get_tool_factory()
    tool = factory.get_tool("otp_login")

    result = await tool.execute(
        action="verify_otp",
        otp_code="123456",
        _session_id="nonexistent-session-id"
    )
    assert result.is_error is True
    assert "invalid" in result.response_text.lower() or "expired" in result.response_text.lower()


@pytest.mark.asyncio
async def test_invalid_action():
    """Test with an invalid action value."""
    factory = get_tool_factory()
    tool = factory.get_tool("otp_login")

    result = await tool.execute(action="invalid_action")
    assert result.is_error is True
    assert "send_otp" in result.response_text or "verify_otp" in result.response_text


@pytest.mark.asyncio
async def test_missing_action():
    """Test with no action provided."""
    factory = get_tool_factory()
    tool = factory.get_tool("otp_login")

    result = await tool.execute(phone_or_email="9876543210")
    assert result.is_error is True


# ============================================================================
# REAL API TESTS - SEND OTP
# ============================================================================

@pytest.mark.asyncio
async def test_send_otp_real_api():
    """Test sending OTP to a real phone number.

    This makes an actual API call to EaseMyTrip.
    The OTP will be sent to the phone number provided.
    """
    factory = get_tool_factory()
    tool = factory.get_tool("otp_login")

    phone_number = "9717423747"

    print(f"\n Sending OTP to: {phone_number}")

    result: ToolResponseFormat = await tool.execute(
        action="send_otp",
        phone_or_email=phone_number
    )

    print(f"Response text: {result.response_text}")
    print(f"Structured content: {result.structured_content}")
    print(f"Is error: {result.is_error}")

    assert result.is_error is False, f"Send OTP failed: {result.response_text}"
    assert result.structured_content is not None

    data = result.structured_content
    assert "session_id" in data, "Response should contain session_id"
    assert data["session_id"] is not None, "session_id should not be None"

    session_id = data["session_id"]
    print(f"Session ID: {session_id}")
    print(f"OTP sent successfully! Check your phone for the OTP.")


@pytest.mark.asyncio
async def test_send_otp_returns_session_for_verify():
    """Test that send_otp creates a session that can be used for verify."""
    factory = get_tool_factory()
    tool = factory.get_tool("otp_login")
    session_manager = factory.get_session_manager()

    phone_number = "9717423747"

    result = await tool.execute(
        action="send_otp",
        phone_or_email=phone_number
    )

    if result.is_error:
        pytest.skip(f"Send OTP failed (API issue): {result.response_text}")

    session_id = result.structured_content["session_id"]

    # Verify the session exists in session manager
    token_provider = session_manager.get_session(session_id)
    assert token_provider is not None, "Session should exist after send_otp"

    # Verify OTP pending state is set
    otp_token = token_provider.get_otp_token()
    otp_phone = token_provider.get_otp_phone_or_email()

    assert otp_token is not None, "OTP token should be stored in session"
    assert otp_phone == phone_number, f"Phone should be stored: expected {phone_number}, got {otp_phone}"

    print(f"\nSession created: {session_id}")
    print(f"OTP token stored: {otp_token[:20]}...")
    print(f"Phone stored: {otp_phone}")


# ============================================================================
# FULL FLOW TEST (SEND + VERIFY) - requires manual OTP input
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires manual OTP input - run manually with: pytest tests/test_otp_login.py::test_full_otp_flow -v -s --no-header -k full")
async def test_full_otp_flow():
    """Full OTP login flow: send OTP -> enter OTP -> verify.

    Run manually:
        pytest tests/test_otp_login.py::test_full_otp_flow -v -s

    This will:
    1. Send OTP to the phone number
    2. Wait for you to enter the OTP
    3. Verify the OTP and authenticate
    """
    factory = get_tool_factory()
    tool = factory.get_tool("otp_login")

    phone_number = "9717423747"

    # Step 1: Send OTP
    print(f"\n--- Step 1: Sending OTP to {phone_number} ---")
    send_result = await tool.execute(
        action="send_otp",
        phone_or_email=phone_number
    )

    print(f"Response: {send_result.response_text}")
    assert send_result.is_error is False, f"Send OTP failed: {send_result.response_text}"

    session_id = send_result.structured_content["session_id"]
    print(f"Session ID: {session_id}")

    # Step 2: Get OTP from user
    print(f"\n--- Step 2: Enter OTP ---")
    otp_code = input("Enter the OTP received on your phone: ").strip()

    # Step 3: Verify OTP
    print(f"\n--- Step 3: Verifying OTP '{otp_code}' ---")
    verify_result = await tool.execute(
        action="verify_otp",
        otp_code=otp_code,
        _session_id=session_id
    )

    print(f"Response: {verify_result.response_text}")
    print(f"Structured content: {verify_result.structured_content}")

    assert verify_result.is_error is False, f"Verify OTP failed: {verify_result.response_text}"

    data = verify_result.structured_content
    assert "user" in data
    assert "session" in data

    user = data["user"]
    session = data["session"]

    print(f"\nLogin successful!")
    print(f"Name: {user.get('name')}")
    print(f"Email: {user.get('email')}")
    print(f"Phone: {user.get('phone')}")
    print(f"UID: {user.get('uid')}")
    print(f"Authenticated: {session.get('logged_in')}")
    print(f"Auth token present: {session.get('auth') is not None}")


# ============================================================================
# END-TO-END: OTP LOGIN -> FETCH FLIGHT BOOKINGS
# ============================================================================

@pytest.mark.asyncio
async def test_otp_login_then_flight_bookings():
    """Full end-to-end: OTP login with email, then fetch flight bookings.

    Run manually:
        pytest tests/test_otp_login.py::test_otp_login_then_flight_bookings -v -s
    """
    factory = get_tool_factory()
    otp_tool = factory.get_tool("otp_login")
    bookings_tool = factory.get_tool("get_flight_bookings")

    # Step 1: Ask for email or phone
    print(f"\n{'='*60}")
    print(f"Step 1: Enter your email or phone number")
    print(f"{'='*60}")
    identifier = input("Enter email or phone: ").strip()

    # Step 2: Send OTP
    print(f"\n{'='*60}")
    print(f"Step 2: Sending OTP to {identifier}")
    print(f"{'='*60}")
    send_result = await otp_tool.execute(
        action="send_otp",
        phone_or_email=identifier
    )

    print(f"Response: {send_result.response_text}")
    assert send_result.is_error is False, f"Send OTP failed: {send_result.response_text}"

    session_id = send_result.structured_content["session_id"]
    print(f"Session ID: {session_id}")

    # Step 3: Get OTP from user
    print(f"\n{'='*60}")
    print(f"Step 3: Enter OTP received on your email/phone")
    print(f"{'='*60}")
    otp_code = input("Enter OTP: ").strip()

    # Step 4: Verify OTP
    print(f"\n{'='*60}")
    print(f"Step 4: Verifying OTP '{otp_code}'")
    print(f"{'='*60}")
    verify_result = await otp_tool.execute(
        action="verify_otp",
        otp_code=otp_code,
        session_id=session_id
    )

    print(f"Response: {verify_result.response_text}")
    assert verify_result.is_error is False, f"Verify OTP failed: {verify_result.response_text}"

    user = verify_result.structured_content.get("user", {})
    print(f"\nLogged in as: {user.get('name')} ({user.get('email')})")

    # Step 5: Fetch flight bookings using same session
    print(f"\n{'='*60}")
    print(f"Step 5: Fetching flight bookings with session {session_id}")
    print(f"{'='*60}")
    bookings_result = await bookings_tool.execute(
        _session_id=session_id
    )

    print(f"Response: {bookings_result.response_text}")
    print(f"Is error: {bookings_result.is_error}")

    assert bookings_result.is_error is False, f"Bookings failed: {bookings_result.response_text}"

    data = bookings_result.structured_content
    bookings = data.get("bookings", [])
    print(f"\nTotal bookings: {data.get('total', 0)}")

    for b in bookings:
        print(f"  {b.get('status')} | {b.get('booking_id')} | {b.get('source')} -> {b.get('destination')} | {b.get('departure')}")

    # Step 6: Fetch bus bookings using same session
    print(f"\n{'='*60}")
    print(f"Step 6: Fetching bus bookings with session {session_id}")
    print(f"{'='*60}")
    bus_bookings_tool = factory.get_tool("get_bus_bookings")
    bus_result = await bus_bookings_tool.execute(
        _session_id=session_id
    )

    print(f"Response: {bus_result.response_text}")
    print(f"Is error: {bus_result.is_error}")

    assert bus_result.is_error is False, f"Bus bookings failed: {bus_result.response_text}"

    bus_data = bus_result.structured_content
    bus_bookings = bus_data.get("bookings", [])
    print(f"\nTotal bus bookings: {bus_data.get('total', 0)}")

    for b in bus_bookings:
        print(f"  {b.get('status')} | {b.get('booking_id')} | {b.get('route')} | {b.get('operator')} | {b.get('departure')}")

    print(f"\n{'='*60}")
    print(f"End-to-end test PASSED!")
    print(f"{'='*60}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
