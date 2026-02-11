"""Real API tests for Train Availability Check Tool.

These tests make actual API calls and verify real responses.
NO MOCKING - Real API integration tests.

File: tests/test_train_availability.py

Run with:
    uv run pytest tests/test_train_availability.py -v -s

Mark as integration tests:
    pytest -m integration
"""

import pytest
from datetime import datetime, timedelta
from tools_factory.factory import get_tool_factory
from tools_factory.base_schema import ToolResponseFormat

# Mark all tests in this file as integration tests (slow)
pytestmark = pytest.mark.integration


# ============================================================================
# TEST FIXTURES - DUMMY PAYLOADS
# ============================================================================

@pytest.fixture
def dummy_availability_check_nandankanan():
    """Dummy payload for Nandankanan Express availability check."""
    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%d-%m-%Y")

    return {
        "trainNo": "12816",
        "journeyDate": journey_date,
        "classes": ["3A", "2A", "1A", "SL"],
    }


@pytest.fixture
def dummy_availability_check_mewar():
    """Dummy payload for Mewar Express availability check."""
    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%d-%m-%Y")

    return {
        "trainNo": "12963",
        "journeyDate": journey_date,
        "classes": ["SL", "3A", "2A"],
    }


# ============================================================================
# TEST CASES - BASIC FUNCTIONALITY
# ============================================================================

@pytest.mark.asyncio
async def test_availability_check_website_mode(dummy_availability_check_nandankanan):
    """Test availability check for website user."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    assert tool is not None, "❌ Tool 'check_train_availability' not found in factory!"

    # Execute with website mode
    payload = {**dummy_availability_check_nandankanan, "_user_type": "website"}
    result = await tool.execute(**payload)

    # Assertions
    assert isinstance(result, ToolResponseFormat), "Should return ToolResponseFormat"
    assert not result.is_error, f"Should not have errors. Error: {result.response_text}"
    assert result.response_text, "Should have response text"
    assert result.html is not None, "Website mode should return HTML"
    assert len(result.html) > 0, "HTML should not be empty"
    assert "train-availability" in result.html, "HTML should contain train availability UI"

    # Check structured content
    assert result.structured_content is not None, "Should have structured content"
    assert "train_info" in result.structured_content, "Should have train info"
    assert "classes" in result.structured_content, "Should have classes"

    train_info = result.structured_content["train_info"]
    assert train_info.get("train_no"), "Should have train number"
    assert train_info.get("train_name"), "Should have train name"

    classes = result.structured_content["classes"]
    assert len(classes) > 0, "Should have at least one class"
    assert len(classes) == len(payload["classes"]), "Should have all requested classes"

    # Check each class has required fields
    for cls in classes:
        assert "class_code" in cls, "Class should have code"
        assert "status" in cls, "Class should have status"

    print(f"\n[PASS] Website Mode Test Passed")
    print(f"   Train: {train_info.get('train_name')} ({train_info.get('train_no')})")
    print(f"   Classes checked: {len(classes)}")
    for cls in classes:
        print(f"   - {cls['class_code']}: {cls['status']} (Rs.{cls.get('fare', 'N/A')})")


@pytest.mark.asyncio
async def test_availability_check_whatsapp_mode(dummy_availability_check_mewar):
    """Test availability check for WhatsApp user."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    # Execute with WhatsApp mode
    payload = {**dummy_availability_check_mewar, "_user_type": "whatsapp"}
    result = await tool.execute(**payload)

    # Assertions
    assert isinstance(result, ToolResponseFormat), "Should return ToolResponseFormat"
    assert not result.is_error, f"Should not have errors. Error: {result.response_text}"
    assert result.response_text, "Should have response text"
    assert result.whatsapp_response is not None, "WhatsApp mode should return WhatsApp response"
    assert result.html is None, "WhatsApp mode should not return HTML"
    assert result.structured_content is None, "WhatsApp mode should not return structured content"

    # Check WhatsApp response format
    wa_response = result.whatsapp_response
    assert wa_response.get("type") == "all_class_availability", "Should have correct type"
    assert wa_response.get("status") == "RESULT", "Should have RESULT status"
    assert wa_response.get("response_text"), "Should have response text"

    # Check data structure
    data = wa_response.get("data")
    assert data is not None, "Should have data"
    assert "train" in data, "Should have train info"
    assert "classes" in data, "Should have classes"

    train = data["train"]
    assert train.get("train_no"), "Should have train number"
    assert train.get("train_name"), "Should have train name"

    classes = data["classes"]
    assert len(classes) > 0, "Should have at least one class"
    assert len(classes) == len(payload["classes"]), "Should have all requested classes"

    # Check each class format
    for cls in classes:
        assert "class" in cls, "Class should have 'class' field"
        assert "status" in cls, "Class should have status"
        # fare can be None

    print(f"\n[PASS] WhatsApp Mode Test Passed")
    print(f"   Response: {wa_response.get('response_text')}")
    print(f"   Train: {train.get('train_name')} ({train.get('train_no')})")
    print(f"   Classes: {len(classes)}")
    for cls in classes:
        print(f"   - {cls['class']}: {cls['status']} (Rs.{cls.get('fare', 'N/A')})")


# ============================================================================
# TEST CASES - INPUT VALIDATION
# ============================================================================

@pytest.mark.asyncio
async def test_validation_invalid_date_format():
    """Test that invalid date format is rejected."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    payload = {
        "trainNo": "12816",
        "journeyDate": "2026-02-12",  # Wrong format (YYYY-MM-DD instead of DD-MM-YYYY)
        "classes": ["3A"],
    }

    result = await tool.execute(**payload)

    # Should return validation error
    assert result.is_error, "Should be an error"
    assert "VALIDATION_ERROR" in str(result.structured_content.get("error", "")), "Should be validation error"

    print(f"\n[PASS] Invalid Date Format Test Passed")
    print(f"   Error caught: {result.response_text}")


@pytest.mark.asyncio
async def test_validation_empty_classes():
    """Test that empty classes list is rejected."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%d-%m-%Y")

    payload = {
        "trainNo": "12816",
        "journeyDate": journey_date,
        "classes": [],  # Empty list
    }

    result = await tool.execute(**payload)

    # Should return validation error
    assert result.is_error, "Should be an error"
    assert "VALIDATION_ERROR" in str(result.structured_content.get("error", "")), "Should be validation error"

    print(f"\n[PASS] Empty Classes Test Passed")
    print(f"   Error caught: {result.response_text}")


@pytest.mark.asyncio
async def test_validation_invalid_class_code():
    """Test that invalid class codes are rejected."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%d-%m-%Y")

    payload = {
        "trainNo": "12816",
        "journeyDate": journey_date,
        "classes": ["3A", "INVALID_CLASS"],  # Invalid class
    }

    result = await tool.execute(**payload)

    # Should return validation error
    assert result.is_error, "Should be an error"
    assert "VALIDATION_ERROR" in str(result.structured_content.get("error", "")), "Should be validation error"

    print(f"\n[PASS] Invalid Class Code Test Passed")
    print(f"   Error caught: {result.response_text}")


# ============================================================================
# TEST CASES - DIFFERENT QUOTAS
# ============================================================================

@pytest.mark.asyncio
async def test_availability_check_general_quota(dummy_availability_check_nandankanan):
    """Test availability check with General quota (default)."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    # Use default General quota
    payload = {**dummy_availability_check_nandankanan}
    result = await tool.execute(**payload)

    # Should work without errors
    assert not result.is_error, f"Should not have errors. Error: {result.response_text}"
    assert result.response_text, "Should have response text"

    print(f"\n[PASS] General Quota Test Passed")
    print(f"   Response: {result.response_text}")


# ============================================================================
# TEST CASES - MULTIPLE CLASSES
# ============================================================================

@pytest.mark.asyncio
async def test_availability_check_all_classes():
    """Test availability check with all major travel classes."""
    factory = get_tool_factory()
    tool = factory.get_tool("check_train_availability")

    today = datetime.now()
    journey_date = (today + timedelta(days=7)).strftime("%d-%m-%Y")

    payload = {
        "trainNo": "12816",
        "journeyDate": journey_date,
        "classes": ["1A", "2A", "3A", "SL", "2S", "CC"],  # All major classes
    }

    result = await tool.execute(**payload)

    # Should work without errors
    assert not result.is_error, f"Should not have errors. Error: {result.response_text}"

    classes = result.structured_content.get("classes", [])
    assert len(classes) == len(payload["classes"]), "Should return all requested classes"

    print(f"\n[PASS] All Classes Test Passed")
    print(f"   Classes checked: {len(classes)}")
    for cls in classes:
        print(f"   - {cls['class_code']}: {cls['status']}")
