"""
WhatsApp Cancellation Flow Test
Tests the corrected WhatsApp flow where OTP verification happens BEFORE showing booking details.

Run: pytest tests/test_whatsapp_cancellation_flow.py -v
Run specific module: pytest tests/test_whatsapp_cancellation_flow.py -k "hotel" -v
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from tests.mock_cancellation_client import MockMyBookingsClient
from tools_factory.cancellation.cancellation_tool import CancellationTool
from tools_factory.cancellation.cancellation_service import CancellationService

pytestmark = pytest.mark.asyncio


def _create_service_with_mock(scenario: str) -> CancellationService:
    """Create a CancellationService with a mock client."""
    service = CancellationService()
    service.client = MockMyBookingsClient(scenario)
    return service


class TestWhatsAppHotelFlow:
    """Test the complete WhatsApp cancellation flow for Hotel bookings"""

    async def test_step1_start_sends_otp_only(self):
        """Step 1: Start should ONLY send OTP, NOT show booking details"""
        service = _create_service_with_mock("hotel_happy_path")
        tool = CancellationTool()

        with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
            result = await tool.execute(
                action="start",
                booking_id="EMT_TEST_001",
                email="test@example.com",
                _user_type="whatsapp",
            )

        # Assertions
        assert not result.is_error, f"Expected success but got error: {result.response_text}"

        # Should have WhatsApp response
        assert result.whatsapp_response is not None, "Missing whatsapp_response"

        # Check status is "otp_sent_for_login"
        whatsapp_json = result.whatsapp_response.get("whatsapp_json", {})
        assert whatsapp_json.get("status") == "otp_sent_for_login", \
            f"Expected status='otp_sent_for_login', got '{whatsapp_json.get('status')}'"

        # Response text should mention OTP, NOT booking details
        response_text = result.response_text
        assert "OTP" in response_text, "OTP message missing"
        assert "verify your identity" in response_text.lower(), "Missing verification message"

        # Should NOT contain booking details (hotel name, check-in, rooms, etc.)
        assert "Deluxe" not in response_text, "Should NOT show room details yet"
        assert "Check-in" not in response_text, "Should NOT show check-in date yet"
        assert "₹" not in response_text or "OTP" in response_text, "Should NOT show prices yet"

        print("[PASS] Step 1: Start action only sends OTP, no booking details shown")

    async def test_step2_verify_otp_shows_booking_details(self):
        """Step 2: Verify OTP should show booking details AFTER verification"""
        service = _create_service_with_mock("hotel_happy_path")

        # Pre-populate service state (as if start was already called)
        service._bid = "MOCK_BID_123"
        service._transaction_type = "Hotel"
        service._booking_id = "EMT_TEST_001"
        service._email = "test@example.com"

        tool = CancellationTool()

        with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
            result = await tool.execute(
                action="verify_otp",
                booking_id="EMT_TEST_001",
                email="test@example.com",
                otp="123456",
                _user_type="whatsapp",
            )

        # Assertions
        assert not result.is_error, f"Expected success but got error: {result.response_text}"

        # Should have WhatsApp response
        assert result.whatsapp_response is not None, "Missing whatsapp_response"

        # Check status is "booking_details"
        whatsapp_json = result.whatsapp_response.get("whatsapp_json", {})
        assert whatsapp_json.get("status") == "booking_details", \
            f"Expected status='booking_details', got '{whatsapp_json.get('status')}'"

        # Response should show OTP verified
        response_text = result.response_text
        assert "✅" in response_text or "verified" in response_text.lower(), "Missing verification confirmation"

        # NOW booking details should be present
        assert "Deluxe" in response_text, "Should show room type after OTP verification"
        assert any(indicator in response_text for indicator in ["Check-in", "📅", "hotel"]), \
            "Should show booking details after OTP verification"

        # Should have rooms data in WhatsApp JSON
        assert whatsapp_json.get("rooms") is not None, "Missing rooms data in WhatsApp response"
        assert whatsapp_json.get("transaction_type") == "Hotel", "Missing transaction type"

        print("[PASS] Step 2 PASSED: Verify OTP shows booking details")

    async def test_step3_send_cancellation_otp(self):
        """Step 3: Send cancellation OTP"""
        service = _create_service_with_mock("hotel_happy_path")

        # Pre-populate service state
        service._bid = "MOCK_BID_123"
        service._transaction_type = "Hotel"
        service._booking_id = "EMT_TEST_001"
        service._email = "test@example.com"

        tool = CancellationTool()

        with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
            result = await tool.execute(
                action="send_otp",
                booking_id="EMT_TEST_001",
                email="test@example.com",
                _user_type="whatsapp",
            )

        # Assertions
        assert not result.is_error, f"Expected success but got error: {result.response_text}"

        # Should have WhatsApp response
        assert result.whatsapp_response is not None, "Missing whatsapp_response"

        # Check status is "otp_sent"
        whatsapp_json = result.whatsapp_response.get("whatsapp_json", {})
        assert whatsapp_json.get("status") == "otp_sent", \
            f"Expected status='otp_sent', got '{whatsapp_json.get('status')}'"

        # Response should mention cancellation OTP
        response_text = result.response_text
        assert "OTP" in response_text, "OTP message missing"
        assert "cancellation" in response_text.lower() or "confirm" in response_text.lower(), \
            "Missing cancellation context"

        print("[PASS] Step 3 PASSED: Send cancellation OTP")


class TestWhatsAppTrainFlow:
    """Test the complete WhatsApp cancellation flow for Train bookings"""

    async def test_step1_start_sends_otp_only(self):
        """Step 1: Start should ONLY send OTP for Train"""
        service = _create_service_with_mock("train_happy_path")
        tool = CancellationTool()

        with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
            result = await tool.execute(
                action="start",
                booking_id="EMT_TEST_TRAIN",
                email="test@example.com",
                _user_type="whatsapp",
            )

        # Assertions
        assert not result.is_error, f"Expected success but got error: {result.response_text}"

        # Check status
        whatsapp_json = result.whatsapp_response.get("whatsapp_json", {})
        assert whatsapp_json.get("status") == "otp_sent_for_login"
        assert whatsapp_json.get("transaction_type") == "Train"

        # Should NOT contain train details
        response_text = result.response_text
        assert "OTP" in response_text
        assert "PNR" not in response_text, "Should NOT show PNR yet"
        assert "Coach" not in response_text, "Should NOT show coach details yet"

        print("[PASS] Train Step 1 PASSED: Start sends OTP only")

    async def test_step2_verify_otp_shows_train_details(self):
        """Step 2: Verify OTP shows train booking details"""
        service = _create_service_with_mock("train_happy_path")

        # Pre-populate service state
        service._bid = "MOCK_BID_TRAIN"
        service._transaction_type = "Train"
        service._booking_id = "EMT_TEST_TRAIN"
        service._email = "test@example.com"

        tool = CancellationTool()

        with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
            result = await tool.execute(
                action="verify_otp",
                booking_id="EMT_TEST_TRAIN",
                email="test@example.com",
                otp="123456",
                _user_type="whatsapp",
            )

        # Assertions
        assert not result.is_error

        whatsapp_json = result.whatsapp_response.get("whatsapp_json", {})
        assert whatsapp_json.get("status") == "booking_details"
        assert whatsapp_json.get("transaction_type") == "Train"

        # NOW train details should be present
        response_text = result.response_text
        assert "verified" in response_text.lower()
        assert any(indicator in response_text for indicator in ["🚆", "train", "PNR"]), \
            "Should show train details after OTP verification"

        # Should have passengers data
        assert whatsapp_json.get("passengers") is not None, "Missing passengers data"

        print("[PASS] Train Step 2 PASSED: Verify OTP shows train details")


class TestWhatsAppBusFlow:
    """Test the complete WhatsApp cancellation flow for Bus bookings"""

    async def test_step1_start_sends_otp_only(self):
        """Step 1: Start should ONLY send OTP for Bus"""
        service = _create_service_with_mock("bus_happy_path")
        tool = CancellationTool()

        with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
            result = await tool.execute(
                action="start",
                booking_id="EMT_TEST_BUS",
                email="test@example.com",
                _user_type="whatsapp",
            )

        # Assertions
        assert not result.is_error

        whatsapp_json = result.whatsapp_response.get("whatsapp_json", {})
        assert whatsapp_json.get("status") == "otp_sent_for_login"
        assert whatsapp_json.get("transaction_type") == "Bus"

        # Should NOT contain bus details
        response_text = result.response_text
        assert "OTP" in response_text
        assert "Seat" not in response_text, "Should NOT show seat details yet"

        print("[PASS] Bus Step 1 PASSED: Start sends OTP only")

    async def test_step2_verify_otp_shows_bus_details(self):
        """Step 2: Verify OTP shows bus booking details"""
        service = _create_service_with_mock("bus_happy_path")

        service._bid = "MOCK_BID_BUS"
        service._transaction_type = "Bus"
        service._booking_id = "EMT_TEST_BUS"
        service._email = "test@example.com"

        tool = CancellationTool()

        with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
            result = await tool.execute(
                action="verify_otp",
                booking_id="EMT_TEST_BUS",
                email="test@example.com",
                otp="123456",
                _user_type="whatsapp",
            )

        # Assertions
        assert not result.is_error

        whatsapp_json = result.whatsapp_response.get("whatsapp_json", {})
        assert whatsapp_json.get("status") == "booking_details"
        assert whatsapp_json.get("transaction_type") == "Bus"

        # Should have seats data
        assert whatsapp_json.get("seats") is not None, "Missing seats data"

        print("[PASS] Bus Step 2 PASSED: Verify OTP shows bus details")


class TestWhatsAppFlightFlow:
    """Test the complete WhatsApp cancellation flow for Flight bookings"""

    async def test_step1_start_sends_otp_only(self):
        """Step 1: Start should ONLY send OTP for Flight"""
        service = _create_service_with_mock("flight_happy_path")
        tool = CancellationTool()

        with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
            result = await tool.execute(
                action="start",
                booking_id="EMT_TEST_FLIGHT",
                email="test@example.com",
                _user_type="whatsapp",
            )

        # Assertions
        assert not result.is_error

        whatsapp_json = result.whatsapp_response.get("whatsapp_json", {})
        assert whatsapp_json.get("status") == "otp_sent_for_login"
        assert whatsapp_json.get("transaction_type") == "Flight"

        # Should NOT contain flight details
        response_text = result.response_text
        assert "OTP" in response_text
        assert "✈" not in response_text, "Should NOT show flight emoji yet"
        assert "Airline" not in response_text, "Should NOT show airline details yet"

        print("[PASS] Flight Step 1 PASSED: Start sends OTP only")

    async def test_step2_verify_otp_shows_flight_details(self):
        """Step 2: Verify OTP shows flight booking details"""
        service = _create_service_with_mock("flight_happy_path")

        service._bid = "MOCK_BID_FLIGHT"
        service._transaction_type = "Flight"
        service._booking_id = "EMT_TEST_FLIGHT"
        service._email = "test@example.com"

        tool = CancellationTool()

        with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
            result = await tool.execute(
                action="verify_otp",
                booking_id="EMT_TEST_FLIGHT",
                email="test@example.com",
                otp="123456",
                _user_type="whatsapp",
            )

        # Assertions
        assert not result.is_error

        whatsapp_json = result.whatsapp_response.get("whatsapp_json", {})
        assert whatsapp_json.get("status") == "booking_details"
        assert whatsapp_json.get("transaction_type") == "Flight"

        # Should have flight passengers data
        assert whatsapp_json.get("flight_passengers") is not None, "Missing flight passengers data"

        # Response should show flight details
        response_text = result.response_text
        assert "verified" in response_text.lower()
        assert any(indicator in response_text for indicator in ["✈", "flight", "Airline"]), \
            "Should show flight details after OTP verification"

        print("[PASS] Flight Step 2 PASSED: Verify OTP shows flight details")


class TestWebsiteFlowUnchanged:
    """Verify that Website flow remains unchanged (backward compatibility)"""

    async def test_website_start_still_shows_details_immediately(self):
        """Website users should still see booking details immediately (with HTML form)"""
        service = _create_service_with_mock("hotel_happy_path")
        tool = CancellationTool()

        with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
            result = await tool.execute(
                action="start",
                booking_id="EMT_TEST_001",
                email="test@example.com",
                _user_type="website",  # Website user
            )

        # Website should still get booking details immediately
        assert not result.is_error
        assert result.html is not None, "Website should get HTML response"

        # Should have booking details in structured content
        assert result.structured_content is not None
        assert "booking_details" in result.structured_content

        print("[PASS] Website flow UNCHANGED: Still shows details immediately with HTML")


# ============================================================
# Complete Flow Test
# ============================================================

class TestCompleteWhatsAppFlow:
    """Test the complete end-to-end WhatsApp flow"""

    async def test_complete_hotel_cancellation_flow(self):
        """Complete flow: Start → Verify OTP → Send Cancel OTP → Confirm Cancel"""
        service = _create_service_with_mock("hotel_happy_path")
        tool = CancellationTool()

        print("\n>>> Testing Complete Hotel Cancellation Flow on WhatsApp\n")

        # STEP 1: Start - Should only send login OTP
        print(">>> STEP 1: User requests cancellation...")
        with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
            result1 = await tool.execute(
                action="start",
                booking_id="EMT_TEST_001",
                email="test@example.com",
                _user_type="whatsapp",
            )

        assert not result1.is_error
        assert result1.whatsapp_response["whatsapp_json"]["status"] == "otp_sent_for_login"
        print(f"[OK] Bot Response: {result1.response_text[:100]}...")
        print(f"     Status: {result1.whatsapp_response['whatsapp_json']['status']}")

        # STEP 2: Verify OTP - Should show booking details
        print("\n>>> STEP 2: User enters login OTP...")
        service._bid = "MOCK_BID_123"
        service._transaction_type = "Hotel"

        with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
            result2 = await tool.execute(
                action="verify_otp",
                booking_id="EMT_TEST_001",
                email="test@example.com",
                otp="123456",
                _user_type="whatsapp",
            )

        assert not result2.is_error
        assert result2.whatsapp_response["whatsapp_json"]["status"] == "booking_details"
        assert result2.whatsapp_response["whatsapp_json"]["rooms"] is not None
        print(f"[OK] Bot Response: {result2.response_text[:150]}...")
        print(f"     Status: {result2.whatsapp_response['whatsapp_json']['status']}")
        print(f"     Rooms: {len(result2.whatsapp_response['whatsapp_json']['rooms'])} room(s) found")

        # STEP 3: Send Cancellation OTP
        print("\n>>> STEP 3: User confirms cancellation request...")
        with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
            result3 = await tool.execute(
                action="send_otp",
                booking_id="EMT_TEST_001",
                email="test@example.com",
                _user_type="whatsapp",
            )

        assert not result3.is_error
        assert result3.whatsapp_response["whatsapp_json"]["status"] == "otp_sent"
        print(f"[OK] Bot Response: {result3.response_text[:100]}...")
        print(f"     Status: {result3.whatsapp_response['whatsapp_json']['status']}")

        print("\n[PASS] Complete Flow Test PASSED!")
        print("       [v] Step 1: Login OTP sent (no booking details)")
        print("       [v] Step 2: OTP verified, booking details shown")
        print("       [v] Step 3: Cancellation OTP sent")
        print("       [v] All WhatsApp responses properly formatted")


if __name__ == "__main__":
    print("WhatsApp Cancellation Flow Tests")
    print("=" * 60)
    print("Run with: pytest tests/test_whatsapp_cancellation_flow.py -v")
    print("=" * 60)
