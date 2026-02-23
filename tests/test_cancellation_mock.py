"""
Automated test suite for cancellation flow using mock API client.

Run: pytest tests/test_cancellation_mock.py -v
Run specific: pytest tests/test_cancellation_mock.py -k "hotel_happy" -v
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from tests.mock_cancellation_client import MockMyBookingsClient
from tools_factory.cancellation.cancellation_tool import CancellationTool, _sessions
from tools_factory.cancellation.cancellation_service import CancellationService

pytestmark = pytest.mark.asyncio


# ============================================================
# Fixtures
# ============================================================

def _create_service_with_mock(scenario: str) -> CancellationService:
    """Create a CancellationService with a mock client."""
    service = CancellationService()
    service.client = MockMyBookingsClient(scenario)
    return service


async def _run_flow(scenario: str, user_type: str = "website"):
    """Run the full start action and return the result + service."""
    service = _create_service_with_mock(scenario)

    tool = CancellationTool()

    # Patch get_user_service to return our mock service
    with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
        # Also patch the initial login call in _handle_start which creates its own service
        with patch.object(CancellationService, "__init__", lambda self: None):
            # Directly call the service login first (as _handle_start does)
            login_result = await service.guest_login(booking_id="EMT_TEST_001", email="test@example.com")

            result = await tool.execute(
                action="start",
                booking_id="EMT_TEST_001",
                email="test@example.com",
                _user_type=user_type,
            )

    return result, service


async def _execute_action(scenario: str, action: str, user_type: str = "website", **extra_kwargs):
    """Execute a single action with a mock service."""
    service = _create_service_with_mock(scenario)

    # Pre-populate service state (as if start was already called)
    service._bid = "MOCK_BID_123"
    service._transaction_screen_id = "MOCK_SCREEN_456"
    service._booking_id = "EMT_TEST_001"
    service._email = "test@example.com"
    service._emt_screen_id = "MOCK_SCREEN_456"

    # Set transaction type from scenario
    login_resp = service.client._responses.get("guest_login", {})
    ids = login_resp.get("Ids", {})
    service._transaction_type = ids.get("TransactionType", "Hotel")

    tool = CancellationTool()

    with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
        result = await tool.execute(
            action=action,
            booking_id="EMT_TEST_001",
            email="test@example.com",
            _user_type=user_type,
            **extra_kwargs,
        )

    return result, service


# ============================================================
# HOTEL TESTS
# ============================================================

class TestHotelHappyPath:
    async def test_start_returns_booking_details(self):
        result, service = await _execute_action("hotel_happy_path", "start")
        assert not result.is_error
        assert result.structured_content is not None
        sc = result.structured_content
        assert "booking_details" in sc
        rooms = sc["booking_details"].get("rooms", [])
        assert len(rooms) >= 1
        assert rooms[0]["room_type"] == "Deluxe Double Room"

    async def test_start_renders_html_for_website(self):
        result, _ = await _execute_action("hotel_happy_path", "start", user_type="website")
        assert result.html is not None
        assert "booking-details-carousel" in result.html or "round-trip-selector" in result.html

    async def test_start_no_html_for_whatsapp(self):
        result, _ = await _execute_action("hotel_happy_path", "start", user_type="whatsapp")
        assert result.html is None
        assert result.whatsapp_response is not None

    async def test_whatsapp_response_has_rooms(self):
        result, _ = await _execute_action("hotel_happy_path", "start", user_type="whatsapp")
        wr = result.whatsapp_response
        assert wr is not None
        wj = wr.get("whatsapp_json", {})
        assert wj["status"] == "booking_details"
        assert wj["transaction_type"] == "Hotel"
        assert wj.get("rooms") is not None
        assert len(wj["rooms"]) >= 1

    async def test_verify_otp_success(self):
        result, _ = await _execute_action("hotel_happy_path", "verify_otp", otp="123456")
        assert not result.is_error
        assert "verified" in result.response_text.lower() or "confirmed" in result.response_text.lower()

    async def test_send_otp_success(self):
        result, _ = await _execute_action("hotel_happy_path", "send_otp")
        assert not result.is_error
        assert "otp" in result.response_text.lower()

    async def test_confirm_success(self):
        result, _ = await _execute_action(
            "hotel_happy_path", "confirm",
            otp="654321", room_id="R001", transaction_id="TXN_H001",
        )
        assert not result.is_error
        assert "cancelled" in result.response_text.lower() or "cancel" in result.response_text.lower()

    async def test_confirm_returns_html_for_website(self):
        result, _ = await _execute_action(
            "hotel_happy_path", "confirm", user_type="website",
            otp="654321", room_id="R001", transaction_id="TXN_H001",
        )
        assert result.html is not None

    async def test_confirm_whatsapp_has_refund_info(self):
        result, _ = await _execute_action(
            "hotel_happy_path", "confirm", user_type="whatsapp",
            otp="654321", room_id="R001", transaction_id="TXN_H001",
        )
        wr = result.whatsapp_response
        assert wr is not None
        wj = wr.get("whatsapp_json", {})
        assert wj["status"] == "cancelled"
        assert wj.get("refund_info") is not None


class TestHotelMultiRoom:
    async def test_multiple_rooms_returned(self):
        result, _ = await _execute_action("hotel_multi_room", "start")
        assert not result.is_error
        rooms = result.structured_content["booking_details"]["rooms"]
        assert len(rooms) == 2


class TestHotelAlreadyCancelled:
    async def test_already_cancelled_detected(self):
        result, _ = await _execute_action("hotel_already_cancelled", "start")
        assert not result.is_error
        sc = result.structured_content
        assert sc.get("all_cancelled") is True or sc["booking_details"].get("all_cancelled") is True


class TestHotelInvalidOtp:
    async def test_verify_otp_fails(self):
        result, _ = await _execute_action("hotel_invalid_otp", "verify_otp", otp="wrong")
        assert result.is_error
        assert "invalid" in result.response_text.lower() or "otp" in result.response_text.lower()

    async def test_verify_otp_whatsapp_error(self):
        result, _ = await _execute_action("hotel_invalid_otp", "verify_otp", user_type="whatsapp", otp="wrong")
        assert result.is_error
        wr = result.whatsapp_response
        assert wr is not None
        assert wr["whatsapp_json"]["status"] == "error"


class TestHotelCancelFail:
    async def test_confirm_fails(self):
        result, _ = await _execute_action(
            "hotel_cancel_fail", "confirm",
            otp="654321", room_id="R001", transaction_id="TXN_H001",
        )
        assert result.is_error
        assert "failed" in result.response_text.lower()


class TestHotelOtpSendFail:
    async def test_send_otp_fails(self):
        result, _ = await _execute_action("hotel_otp_send_fail", "send_otp")
        assert result.is_error
        assert "failed" in result.response_text.lower()


# ============================================================
# TRAIN TESTS
# ============================================================

class TestTrainHappyPath:
    async def test_start_returns_passengers(self):
        result, _ = await _execute_action("train_happy_path", "start")
        assert not result.is_error
        sc = result.structured_content
        passengers = sc["booking_details"]["passengers"]
        assert len(passengers) == 3
        assert passengers[0]["name"] == "Amit Kumar"

    async def test_start_returns_train_info(self):
        result, _ = await _execute_action("train_happy_path", "start")
        train_info = result.structured_content["booking_details"]["train_info"]
        assert train_info["train_name"] == "Rajdhani Express"
        assert train_info["train_number"] == "12301"

    async def test_start_renders_html(self):
        result, _ = await _execute_action("train_happy_path", "start", user_type="website")
        assert result.html is not None
        assert "train-cancel-carousel" in result.html

    async def test_whatsapp_response_has_passengers(self):
        result, _ = await _execute_action("train_happy_path", "start", user_type="whatsapp")
        wr = result.whatsapp_response
        assert wr is not None
        wj = wr["whatsapp_json"]
        assert wj["transaction_type"] == "Train"
        assert wj.get("passengers") is not None
        assert len(wj["passengers"]) == 3

    async def test_confirm_success(self):
        result, _ = await _execute_action(
            "train_happy_path", "confirm",
            otp="654321",
            pax_ids=["canidout(PAX001)", "canidout(PAX002)"],
            reservation_id="RES_12345",
            pnr_number="4521367890",
            total_passenger=2,
        )
        assert not result.is_error
        assert "cancelled" in result.response_text.lower()

    async def test_confirm_whatsapp(self):
        result, _ = await _execute_action(
            "train_happy_path", "confirm", user_type="whatsapp",
            otp="654321",
            pax_ids=["canidout(PAX001)"],
            reservation_id="RES_12345",
            pnr_number="4521367890",
            total_passenger=1,
        )
        wr = result.whatsapp_response
        assert wr is not None
        assert wr["whatsapp_json"]["status"] == "cancelled"


class TestTrainAlreadyCancelled:
    async def test_all_cancelled(self):
        result, _ = await _execute_action("train_already_cancelled", "start")
        sc = result.structured_content
        assert sc.get("all_cancelled") is True or sc["booking_details"].get("all_cancelled") is True


class TestTrainInvalidOtp:
    async def test_verify_otp_fails(self):
        result, _ = await _execute_action("train_invalid_otp", "verify_otp", otp="wrong")
        assert result.is_error


# ============================================================
# BUS TESTS
# ============================================================

class TestBusHappyPath:
    async def test_start_returns_passengers(self):
        result, _ = await _execute_action("bus_happy_path", "start")
        assert not result.is_error
        sc = result.structured_content
        passengers = sc["booking_details"]["passengers"]
        assert len(passengers) == 2

    async def test_start_returns_bus_info(self):
        result, _ = await _execute_action("bus_happy_path", "start")
        bus_info = result.structured_content["booking_details"]["bus_info"]
        assert bus_info["source"] == "Delhi"
        assert bus_info["destination"] == "Jaipur"

    async def test_start_renders_html(self):
        result, _ = await _execute_action("bus_happy_path", "start", user_type="website")
        assert result.html is not None
        assert "bus-cancel-carousel" in result.html

    async def test_whatsapp_response_has_seats(self):
        result, _ = await _execute_action("bus_happy_path", "start", user_type="whatsapp")
        wr = result.whatsapp_response
        assert wr is not None
        wj = wr["whatsapp_json"]
        assert wj["transaction_type"] == "Bus"
        assert wj.get("seats") is not None
        assert len(wj["seats"]) == 2

    async def test_confirm_success(self):
        result, _ = await _execute_action(
            "bus_happy_path", "confirm",
            otp="654321", seats="L5",
        )
        assert not result.is_error
        assert "cancelled" in result.response_text.lower()

    async def test_confirm_whatsapp(self):
        result, _ = await _execute_action(
            "bus_happy_path", "confirm", user_type="whatsapp",
            otp="654321", seats="L5",
        )
        wr = result.whatsapp_response
        assert wr is not None
        assert wr["whatsapp_json"]["status"] == "cancelled"


class TestBusAlreadyCancelled:
    async def test_all_cancelled(self):
        result, _ = await _execute_action("bus_already_cancelled", "start")
        sc = result.structured_content
        assert sc.get("all_cancelled") is True or sc["booking_details"].get("all_cancelled") is True


# ============================================================
# CROSS-MODULE TESTS
# ============================================================

class TestAutoDetection:
    async def test_hotel_id_routes_to_train(self):
        """User asks for hotel cancel but booking is actually train."""
        result, _ = await _execute_action("hotel_id_but_train", "start")
        assert not result.is_error
        sc = result.structured_content
        # Should have train-specific data (passengers, not rooms)
        assert "passengers" in sc.get("booking_details", {})


# ============================================================
# EDGE CASE TESTS
# ============================================================

class TestEdgeCases:
    async def test_network_error_on_login(self):
        """Service handles network errors gracefully."""
        service = _create_service_with_mock("hotel_happy_path")
        service.client.override_with_error("guest_login", "Connection timeout")

        result = await service.guest_login("EMT_TEST", "test@test.com")
        assert result["success"] is False
        assert "error" in result.get("error", "").lower() or result.get("message", "") != ""

    async def test_missing_otp_for_verify(self):
        """verify_otp without OTP returns error."""
        tool = CancellationTool()
        result = await tool.execute(
            action="verify_otp",
            booking_id="EMT_TEST_001",
            email="test@example.com",
            _user_type="website",
        )
        assert result.is_error
        assert "otp" in result.response_text.lower()

    async def test_missing_fields_for_confirm(self):
        """confirm without required fields returns error."""
        service = _create_service_with_mock("hotel_happy_path")
        service._transaction_type = "Hotel"

        tool = CancellationTool()
        with patch("tools_factory.cancellation.cancellation_tool.get_user_service", return_value=service):
            result = await tool.execute(
                action="confirm",
                booking_id="EMT_TEST_001",
                email="test@example.com",
                otp="123456",
                # Missing room_id and transaction_id
                _user_type="website",
            )
        assert result.is_error

    async def test_unknown_action(self):
        """Unknown action returns error."""
        tool = CancellationTool()
        result = await tool.execute(
            action="invalid_action",
            booking_id="EMT_TEST_001",
            email="test@example.com",
            _user_type="website",
        )
        assert result.is_error
        assert "unknown" in result.response_text.lower()


# ============================================================
# WHATSAPP VERIFY/SEND_OTP TESTS
# ============================================================

class TestWhatsappOtpFlow:
    async def test_verify_otp_whatsapp_success(self):
        result, _ = await _execute_action("hotel_happy_path", "verify_otp", user_type="whatsapp", otp="123456")
        assert not result.is_error
        wr = result.whatsapp_response
        assert wr is not None
        assert wr["whatsapp_json"]["status"] == "otp_verified"

    async def test_send_otp_whatsapp_success(self):
        result, _ = await _execute_action("hotel_happy_path", "send_otp", user_type="whatsapp")
        assert not result.is_error
        wr = result.whatsapp_response
        assert wr is not None
        assert wr["whatsapp_json"]["status"] == "otp_sent"

    async def test_verify_otp_website_no_whatsapp(self):
        result, _ = await _execute_action("hotel_happy_path", "verify_otp", user_type="website", otp="123456")
        assert not result.is_error
        assert result.whatsapp_response is None

    async def test_send_otp_website_no_whatsapp(self):
        result, _ = await _execute_action("hotel_happy_path", "send_otp", user_type="website")
        assert not result.is_error
        assert result.whatsapp_response is None


# ============================================================
# CALL TRACKING TESTS
# ============================================================

class TestCallTracking:
    async def test_mock_client_records_calls(self):
        client = MockMyBookingsClient("hotel_happy_path")
        await client.guest_login("EMT123", "test@test.com")
        await client.verify_guest_login_otp("BID", "123456", "Hotel")

        client.assert_called("guest_login", times=1)
        client.assert_called("verify_guest_login_otp", times=1)

        login_call = client.get_calls("guest_login")[0]
        assert login_call["kwargs"]["booking_id"] == "EMT123"
        assert login_call["kwargs"]["email"] == "test@test.com"

    async def test_override_response(self):
        client = MockMyBookingsClient("hotel_happy_path")
        client.override("verify_guest_login_otp", {"isVerify": "false", "Message": "Expired OTP"})

        result = await client.verify_guest_login_otp("BID", "old_otp")
        assert result["isVerify"] == "false"
        assert "Expired" in result["Message"]

    async def test_override_with_error(self):
        client = MockMyBookingsClient("hotel_happy_path")
        client.override_with_error("guest_login", "Server is down")

        with pytest.raises(Exception, match="Server is down"):
            await client.guest_login("EMT123", "test@test.com")


# ============================================================
# Flight Cancellation Tests
# ============================================================
class TestFlightCancellation:
    """Test flight cancellation redirect flow."""

    async def test_start_with_otp_required_website(self):
        """Flight start with OTP required should render OTP verification card for website."""
        result, service = await _run_flow("flight_happy_path", user_type="website")
        assert not result.is_error
        assert "OTP" in result.response_text
        assert result.html is not None
        assert "booking-details-carousel" in result.html
        assert "hc-verify-otp-btn" in result.html  # Has verify button
        assert "hc-login-otp-input" in result.html  # Has OTP input field
        assert "verify-otp" in result.html  # Has verify-otp step

    async def test_start_with_otp_required_chatbot(self):
        """Flight start with OTP required in chatbot mode should return text only."""
        result, service = await _run_flow("flight_happy_path", user_type="chatbot")
        assert not result.is_error
        assert "OTP" in result.response_text
        assert result.html is None  # No HTML for chatbot

    async def test_start_no_otp_redirect_immediately(self):
        """Flight start without OTP should show redirect immediately."""
        result, service = await _run_flow("flight_no_otp_required", user_type="website")
        assert not result.is_error
        assert result.html is not None
        assert "booking-details-carousel" in result.html
        assert "CancelFlightDetails" in result.html
        assert "MOCK_BID_123" in result.html

    async def test_start_no_otp_chatbot_text(self):
        """Flight start without OTP in chatbot mode should return text with URL."""
        result, service = await _run_flow("flight_no_otp_required", user_type="chatbot")
        assert not result.is_error
        assert "CancelFlightDetails" in result.response_text
        assert "MOCK_BID_123" in result.response_text
        assert result.html is None

    async def test_start_no_otp_whatsapp(self):
        """Flight start without OTP in WhatsApp mode should include redirect_url."""
        result, service = await _run_flow("flight_no_otp_required", user_type="whatsapp")
        assert not result.is_error
        assert result.whatsapp_response is not None
        wa = result.whatsapp_response
        assert wa["whatsapp_json"]["transaction_type"] == "Flight"
        assert wa["whatsapp_json"]["redirect_url"] is not None
        assert "CancelFlightDetails" in wa["whatsapp_json"]["redirect_url"]

    async def test_verify_otp_returns_redirect(self):
        """After OTP verified, flight should return redirect card."""
        result, service = await _execute_action(
            "flight_happy_path", "verify_otp", user_type="website", otp="123456"
        )
        assert not result.is_error
        assert result.html is not None
        assert "booking-details-carousel" in result.html
        assert "CancelFlightDetails" in result.html

    async def test_verify_otp_invalid(self):
        """Invalid OTP for flight should show error."""
        result, service = await _execute_action(
            "flight_invalid_otp", "verify_otp", user_type="website", otp="wrong"
        )
        assert result.is_error
        assert "Invalid" in result.response_text or "OTP" in result.response_text

    async def test_verify_otp_whatsapp_redirect(self):
        """After OTP verified in WhatsApp, flight should return redirect_url."""
        result, service = await _execute_action(
            "flight_happy_path", "verify_otp", user_type="whatsapp", otp="123456"
        )
        assert not result.is_error
        assert result.whatsapp_response is not None
        assert "CancelFlightDetails" in result.whatsapp_response["whatsapp_json"]["redirect_url"]

    async def test_send_otp_blocked(self):
        """Flight should reject send_otp action."""
        result, service = await _execute_action(
            "flight_happy_path", "send_otp", user_type="website"
        )
        assert result.is_error
        assert "redirect" in result.response_text.lower() or "not require" in result.response_text.lower()

    async def test_confirm_blocked(self):
        """Flight should reject confirm action."""
        result, service = await _execute_action(
            "flight_happy_path", "confirm", user_type="website", otp="123456"
        )
        assert result.is_error
        assert "redirect" in result.response_text.lower() or "website" in result.response_text.lower()

    async def test_start_whatsapp_otp_required(self):
        """Flight start with OTP required in WhatsApp should ask for OTP."""
        result, service = await _run_flow("flight_happy_path", user_type="whatsapp")
        assert not result.is_error
        assert "OTP" in result.response_text
        assert result.whatsapp_response is not None
        assert result.whatsapp_response["whatsapp_json"]["transaction_type"] == "Flight"

# ============================================================
# Refresh Session Routing Tests (Dual OTP Bug Fix)
# ============================================================

class TestRefreshSessionRouting:
    """
    Test suite to verify _refresh_session() routes to correct endpoints.
    
    This prevents the dual OTP bug where hotel OTP was sent for all booking types.
    """
    
    async def test_flight_refresh_session_calls_flight_endpoint(self):
        """Verify _refresh_session() routes to flight endpoint for flight bookings."""
        service = _create_service_with_mock("flight_happy_path")
        
        # Login to set transaction type
        await service.guest_login("EMT_FLIGHT_001", "test@example.com")
        assert service._transaction_type == "Flight"
        
        # Call refresh - should use flight endpoint
        await service._refresh_session("EMT_FLIGHT_001", "test@example.com")
        
        # Verify flight endpoint was called
        flight_calls = service.client.get_calls("fetch_flight_booking_details")
        assert len(flight_calls) >= 1, "Flight endpoint should be called during refresh"
        
        # Verify hotel endpoint was NOT called
        hotel_calls = service.client.get_calls("fetch_booking_details")
        # Note: Should be 0, but login might call it once. Check it's not called during refresh
        assert len(hotel_calls) == 0, "Hotel endpoint should NOT be called for flight refresh"
    
    async def test_train_refresh_session_calls_train_endpoint(self):
        """Verify _refresh_session() routes to train endpoint for train bookings."""
        service = _create_service_with_mock("train_happy_path")
        
        # Login to set transaction type
        await service.guest_login("EMT_TRAIN_001", "test@example.com")
        assert service._transaction_type == "Train"
        
        # Call refresh
        await service._refresh_session("EMT_TRAIN_001", "test@example.com")
        
        # Verify train endpoint was called
        train_calls = service.client.get_calls("fetch_train_booking_details")
        assert len(train_calls) >= 1, "Train endpoint should be called during refresh"
        
        # Verify hotel endpoint was NOT called
        hotel_calls = service.client.get_calls("fetch_booking_details")
        assert len(hotel_calls) == 0, "Hotel endpoint should NOT be called for train refresh"
    
    async def test_bus_refresh_session_calls_bus_endpoint(self):
        """Verify _refresh_session() routes to bus endpoint for bus bookings."""
        service = _create_service_with_mock("bus_happy_path")
        
        # Login to set transaction type
        await service.guest_login("EMT_BUS_001", "test@example.com")
        assert service._transaction_type == "Bus"
        
        # Call refresh
        await service._refresh_session("EMT_BUS_001", "test@example.com")
        
        # Verify bus endpoint was called
        bus_calls = service.client.get_calls("fetch_bus_booking_details")
        assert len(bus_calls) >= 1, "Bus endpoint should be called during refresh"
        
        # Verify hotel endpoint was NOT called
        hotel_calls = service.client.get_calls("fetch_booking_details")
        assert len(hotel_calls) == 0, "Hotel endpoint should NOT be called for bus refresh"
    
    async def test_hotel_refresh_session_calls_hotel_endpoint(self):
        """Verify _refresh_session() still works for hotel bookings (backward compatibility)."""
        service = _create_service_with_mock("hotel_happy_path")
        
        # Login to set transaction type
        await service.guest_login("EMT_HOTEL_001", "test@example.com")
        assert service._transaction_type == "Hotel" or service._transaction_type is None
        
        # Call refresh
        await service._refresh_session("EMT_HOTEL_001", "test@example.com")
        
        # Verify hotel endpoint was called
        hotel_calls = service.client.get_calls("fetch_booking_details")
        assert len(hotel_calls) >= 1, "Hotel endpoint should be called during refresh"
    
    async def test_unknown_transaction_type_defaults_to_hotel(self):
        """Verify unknown transaction types default to hotel endpoint."""
        service = _create_service_with_mock("hotel_happy_path")
        
        # Manually set unknown transaction type
        await service.guest_login("EMT_TEST_001", "test@example.com")
        service._transaction_type = "CarRental"  # Unknown type
        
        # Call refresh
        await service._refresh_session("EMT_TEST_001", "test@example.com")
        
        # Verify hotel endpoint was called as fallback
        hotel_calls = service.client.get_calls("fetch_booking_details")
        assert len(hotel_calls) >= 1, "Hotel endpoint should be called for unknown types"
    
    async def test_flight_send_otp_no_dual_otp(self):
        """
        Regression test: Verify flight OTP send doesn't trigger hotel OTP.
        
        This is the main bug fix validation - ensure calling send_flight_cancellation_otp()
        only triggers flight OTP, not hotel OTP as well.
        """
        service = _create_service_with_mock("flight_happy_path")
        
        # Login and fetch details
        await service.guest_login("EMT_FLIGHT_001", "test@example.com")
        await service.fetch_flight_booking_details(service._bid)
        
        # Clear call log to track only OTP sends
        service.client.call_log.clear()
        
        # Send flight OTP
        result = await service.send_flight_cancellation_otp(
            booking_id="EMT_FLIGHT_001",
            email="test@example.com"
        )
        
        # Verify success
        assert result["success"], f"Flight OTP send failed: {result.get('message')}"
        
        # Verify only flight OTP was called
        flight_otp_calls = service.client.get_calls("send_flight_cancellation_otp")
        assert len(flight_otp_calls) == 1, "Flight OTP should be called exactly once"
        
        # Verify hotel OTP was NOT called (this is the bug fix!)
        hotel_otp_calls = service.client.get_calls("send_cancellation_otp")
        assert len(hotel_otp_calls) == 0, "Hotel OTP should NOT be called for flight bookings"
        
        # Verify hotel details fetch was NOT called during OTP send
        hotel_fetch_calls = service.client.get_calls("fetch_booking_details")
        assert len(hotel_fetch_calls) == 0, "Hotel fetch should NOT be called for flight OTP send"
