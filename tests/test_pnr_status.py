"""Real API tests for Train PNR Status Tool.

These tests make actual API calls and verify real responses.
NO MOCKING - Real API integration tests.

File: tests/test_pnr_status.py

Run with:
    pytest tests/test_pnr_status.py -v -s

Mark as integration tests:
    pytest -m integration
"""

import pytest
from tools_factory.factory import get_tool_factory
from tools_factory.base_schema import ToolResponseFormat
from tools_factory.trains.Train_PnrStatus.pnr_status_service import encrypt_pnr
from tools_factory.trains.Train_PnrStatus.pnr_status_tool import TrainPnrStatusTool

# Mark all tests in this file as integration tests (slow)
pytestmark = pytest.mark.integration


# ============================================================================
# TEST FIXTURES - DUMMY PAYLOADS
# ============================================================================

@pytest.fixture
def sample_pnr_number():
    """Sample PNR number for testing (may or may not be valid)."""
    return "2611143617"


@pytest.fixture
def invalid_pnr_short():
    """Invalid PNR - too short."""
    return "123456"


@pytest.fixture
def invalid_pnr_long():
    """Invalid PNR - too long."""
    return "12345678901234"


@pytest.fixture
def invalid_pnr_with_letters():
    """Invalid PNR - contains letters."""
    return "ABC1234567"


@pytest.fixture
def pnr_with_spaces():
    """PNR with spaces (should be cleaned)."""
    return "261 114 3617"


@pytest.fixture
def pnr_with_hyphens():
    """PNR with hyphens (should be cleaned)."""
    return "261-114-3617"


# ============================================================================
# ENCRYPTION TESTS
# ============================================================================

def test_encrypt_pnr_basic():
    """Test PNR encryption function."""
    pnr = "2611143617"
    encrypted = encrypt_pnr(pnr)

    print(f"\n Encrypting PNR: {pnr}")
    print(f"   Encrypted: {encrypted}")

    assert encrypted is not None
    assert isinstance(encrypted, str)
    assert len(encrypted) > 0

    # Should be base64 encoded
    import base64
    try:
        decoded = base64.b64decode(encrypted)
        assert len(decoded) > 0
        print(f"   Base64 decoded length: {len(decoded)} bytes")
    except Exception as e:
        pytest.fail(f"Encrypted PNR is not valid base64: {e}")


def test_encrypt_pnr_consistency():
    """Test that encryption is consistent for same input."""
    pnr = "1234567890"

    encrypted1 = encrypt_pnr(pnr)
    encrypted2 = encrypt_pnr(pnr)

    print(f"\n Testing encryption consistency for PNR: {pnr}")
    print(f"   First encryption: {encrypted1}")
    print(f"   Second encryption: {encrypted2}")

    # Same input should produce same output (deterministic encryption with fixed IV)
    assert encrypted1 == encrypted2


def test_encrypt_pnr_different_inputs():
    """Test that different PNRs produce different encrypted outputs."""
    pnr1 = "1234567890"
    pnr2 = "0987654321"

    encrypted1 = encrypt_pnr(pnr1)
    encrypted2 = encrypt_pnr(pnr2)

    print(f"\n Testing different inputs produce different outputs")
    print(f"   PNR {pnr1} -> {encrypted1}")
    print(f"   PNR {pnr2} -> {encrypted2}")

    assert encrypted1 != encrypted2


# ============================================================================
# INPUT VALIDATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_pnr_validation_valid_input(sample_pnr_number):
    """Test that valid 10-digit PNR passes validation."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_pnr_status")

    print(f"\n Testing valid PNR input: {sample_pnr_number}")

    result = await tool.execute(pnrNumber=sample_pnr_number)

    # Should not have validation error
    if result.is_error:
        error_details = result.structured_content
        # Check if it's a validation error or API error
        if error_details and error_details.get("error") == "VALIDATION_ERROR":
            pytest.fail(f"Valid PNR should pass validation: {error_details}")
        else:
            # API error is acceptable (PNR might not exist)
            print(f"   API returned: {result.response_text}")
    else:
        print(f"   PNR status retrieved successfully")


@pytest.mark.asyncio
async def test_pnr_validation_too_short(invalid_pnr_short):
    """Test that PNR shorter than 10 digits fails validation."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_pnr_status")

    print(f"\n Testing invalid PNR (too short): {invalid_pnr_short}")

    result = await tool.execute(pnrNumber=invalid_pnr_short)

    assert result.is_error is True
    assert "VALIDATION_ERROR" in str(result.structured_content) or "10 digits" in result.response_text.lower()
    print(f"   Correctly rejected: {result.response_text}")


@pytest.mark.asyncio
async def test_pnr_validation_too_long(invalid_pnr_long):
    """Test that PNR longer than 10 digits fails validation."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_pnr_status")

    print(f"\n Testing invalid PNR (too long): {invalid_pnr_long}")

    result = await tool.execute(pnrNumber=invalid_pnr_long)

    assert result.is_error is True
    print(f"   Correctly rejected: {result.response_text}")


@pytest.mark.asyncio
async def test_pnr_validation_with_letters(invalid_pnr_with_letters):
    """Test that PNR with non-digit characters fails validation."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_pnr_status")

    print(f"\n Testing invalid PNR (with letters): {invalid_pnr_with_letters}")

    result = await tool.execute(pnrNumber=invalid_pnr_with_letters)

    assert result.is_error is True
    print(f"   Correctly rejected: {result.response_text}")


@pytest.mark.asyncio
async def test_pnr_validation_with_spaces(pnr_with_spaces):
    """Test that PNR with spaces is cleaned and accepted."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_pnr_status")

    print(f"\n Testing PNR with spaces: '{pnr_with_spaces}'")

    result = await tool.execute(pnrNumber=pnr_with_spaces)

    # Should clean spaces and process
    if result.is_error:
        error_details = result.structured_content
        if error_details and error_details.get("error") == "VALIDATION_ERROR":
            pytest.fail(f"PNR with spaces should be cleaned and accepted: {error_details}")
        else:
            print(f"   API response (PNR cleaned): {result.response_text}")
    else:
        print(f"   PNR with spaces was cleaned and processed successfully")


@pytest.mark.asyncio
async def test_pnr_validation_with_hyphens(pnr_with_hyphens):
    """Test that PNR with hyphens is cleaned and accepted."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_pnr_status")

    print(f"\n Testing PNR with hyphens: '{pnr_with_hyphens}'")

    result = await tool.execute(pnrNumber=pnr_with_hyphens)

    # Should clean hyphens and process
    if result.is_error:
        error_details = result.structured_content
        if error_details and error_details.get("error") == "VALIDATION_ERROR":
            pytest.fail(f"PNR with hyphens should be cleaned and accepted: {error_details}")
        else:
            print(f"   API response (PNR cleaned): {result.response_text}")
    else:
        print(f"   PNR with hyphens was cleaned and processed successfully")


# ============================================================================
# API RESPONSE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_pnr_status_api_call(sample_pnr_number):
    """Test actual API call for PNR status."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_pnr_status")

    print(f"\n Making real API call for PNR: {sample_pnr_number}")

    result = await tool.execute(pnrNumber=sample_pnr_number)

    print(f"   Response: {result.response_text}")
    print(f"   Is Error: {result.is_error}")

    # Response should have expected structure
    assert result.response_text is not None
    assert isinstance(result.response_text, str)

    if not result.is_error and result.structured_content:
        pnr_info = result.structured_content.get("pnr_info", {})
        if pnr_info:
            print(f"\n   PNR Info Retrieved:")
            print(f"      Train: {pnr_info.get('train_name')} ({pnr_info.get('train_number')})")
            print(f"      Date: {pnr_info.get('date_of_journey')}")
            print(f"      Route: {pnr_info.get('source_station')} -> {pnr_info.get('destination_station')}")
            print(f"      Class: {pnr_info.get('journey_class')}")
            print(f"      Chart: {pnr_info.get('chart_status')}")

            passengers = pnr_info.get("passengers", [])
            print(f"      Passengers: {len(passengers)}")
            for p in passengers:
                print(f"         P{p.get('serial_number')}: {p.get('booking_status')} -> {p.get('current_status')}")


@pytest.mark.asyncio
async def test_pnr_status_response_structure(sample_pnr_number):
    """Test that successful PNR response has correct structure."""
    tool = TrainPnrStatusTool()

    result = await tool.execute(pnrNumber=sample_pnr_number)

    print(f"\n Testing response structure for PNR: {sample_pnr_number}")

    if not result.is_error:
        data = result.structured_content
        assert data is not None

        if "pnr_info" in data:
            pnr_info = data["pnr_info"]

            # Check required fields
            required_fields = [
                "pnr_number",
                "train_number",
                "train_name",
                "date_of_journey",
                "source_station",
                "destination_station",
                "journey_class",
                "chart_status",
                "passengers",
            ]

            for field in required_fields:
                assert field in pnr_info, f"Missing required field: {field}"
                print(f"   {field}: {pnr_info.get(field)}")

            # Check passengers structure
            passengers = pnr_info.get("passengers", [])
            if passengers:
                first_passenger = passengers[0]
                passenger_fields = [
                    "serial_number",
                    "booking_status",
                    "current_status",
                ]
                for field in passenger_fields:
                    assert field in first_passenger, f"Missing passenger field: {field}"

            print(f"\n   Response structure verified")
    else:
        print(f"   API Error: {result.response_text}")


# ============================================================================
# WHATSAPP FORMAT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_pnr_status_whatsapp_format(sample_pnr_number):
    """Test PNR status returns WhatsApp formatted response."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_pnr_status")

    print(f"\n Testing WhatsApp format for PNR: {sample_pnr_number}")

    result: ToolResponseFormat = await tool.execute(
        pnrNumber=sample_pnr_number,
        _user_type="whatsapp"
    )

    if not result.is_error:
        assert result.whatsapp_response is not None, "Should have WhatsApp response"
        assert result.html is None, "WhatsApp response should not have HTML"

        whatsapp_data = result.whatsapp_response
        print(f"   WhatsApp response received")

        # Check WhatsApp format structure
        assert "type" in whatsapp_data
        assert whatsapp_data["type"] == "pnr_status"

        if "pnr_number" in whatsapp_data:
            print(f"   PNR: {whatsapp_data.get('pnr_number')}")
            print(f"   Train: {whatsapp_data.get('train_info')}")
            print(f"   Route: {whatsapp_data.get('route')}")
            print(f"   Passengers: {whatsapp_data.get('passengers')}")
    else:
        print(f"   API Error: {result.response_text}")


@pytest.mark.asyncio
async def test_pnr_status_website_format(sample_pnr_number):
    """Test PNR status returns HTML for website users."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_pnr_status")

    print(f"\n Testing website format for PNR: {sample_pnr_number}")

    result: ToolResponseFormat = await tool.execute(
        pnrNumber=sample_pnr_number,
        _user_type="website"
    )

    if not result.is_error:
        assert result.html is not None, "Website response should have HTML"
        assert result.structured_content is not None, "Website response should have structured content"
        assert result.whatsapp_response is None, "Website response should not have WhatsApp format"

        print(f"   HTML response received (length: {len(result.html)} chars)")
        print(f"   Structured content present: Yes")
    else:
        print(f"   API Error: {result.response_text}")


# ============================================================================
# TOOL METADATA TESTS
# ============================================================================

def test_tool_metadata():
    """Test that tool metadata is correctly defined."""
    tool = TrainPnrStatusTool()
    metadata = tool.get_metadata()

    print(f"\n Checking tool metadata")
    print(f"   Name: {metadata.name}")
    print(f"   Category: {metadata.category}")
    print(f"   Tags: {metadata.tags}")

    assert metadata.name == "check_pnr_status"
    assert metadata.category == "travel"
    assert "pnr" in metadata.tags
    assert "train" in metadata.tags
    assert metadata.description is not None
    assert len(metadata.description) > 0


def test_tool_registered_in_factory():
    """Test that tool is registered in the factory."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_pnr_status")

    print(f"\n Checking tool registration")

    assert tool is not None, "Tool should be registered in factory"
    assert isinstance(tool, TrainPnrStatusTool)

    print(f"   Tool found: {tool.metadata.name}")
    print(f"   Tool type: {type(tool).__name__}")


def test_tool_in_travel_category():
    """Test that tool appears in travel category."""
    factory = get_tool_factory()
    travel_tools = factory.get_tools_by_category("travel")

    print(f"\n Checking tool in travel category")

    tool_names = [t.metadata.name for t in travel_tools]
    print(f"   Travel tools: {tool_names}")

    assert "check_pnr_status" in tool_names, "Tool should be in travel category"


def test_tool_findable_by_tags():
    """Test that tool can be found by tags."""
    factory = get_tool_factory()
    pnr_tools = factory.get_tools_by_tags(["pnr"])

    print(f"\n Checking tool findable by tags")

    tool_names = [t.metadata.name for t in pnr_tools]
    print(f"   Tools with 'pnr' tag: {tool_names}")

    assert "check_pnr_status" in tool_names, "Tool should be findable by 'pnr' tag"


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_pnr_status_response_time(sample_pnr_number):
    """Test that PNR status check completes in reasonable time."""
    import time

    factory = get_tool_factory()
    tool = factory.get_tool("check_pnr_status")

    print(f"\n Testing response time for PNR: {sample_pnr_number}")

    start = time.time()
    result = await tool.execute(pnrNumber=sample_pnr_number)
    elapsed = time.time() - start

    print(f"   Response time: {elapsed:.2f} seconds")
    print(f"   Response: {result.response_text[:100]}...")

    # Should complete within 15 seconds
    assert elapsed < 15, f"PNR check took too long: {elapsed}s"


# ============================================================================
# EDGE CASES
# ============================================================================

@pytest.mark.asyncio
async def test_pnr_all_zeros():
    """Test PNR with all zeros (likely invalid)."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_pnr_status")

    pnr = "0000000000"
    print(f"\n Testing PNR with all zeros: {pnr}")

    result = await tool.execute(pnrNumber=pnr)

    # Should either fail validation or return API error
    print(f"   Response: {result.response_text}")
    print(f"   Is Error: {result.is_error}")


@pytest.mark.asyncio
async def test_pnr_missing_input():
    """Test PNR status with missing input."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_pnr_status")

    print(f"\n Testing missing PNR input")

    result = await tool.execute()

    assert result.is_error is True
    print(f"   Correctly rejected: {result.response_text}")


@pytest.mark.asyncio
async def test_pnr_empty_string():
    """Test PNR status with empty string."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_pnr_status")

    print(f"\n Testing empty PNR string")

    result = await tool.execute(pnrNumber="")

    assert result.is_error is True
    print(f"   Correctly rejected: {result.response_text}")
