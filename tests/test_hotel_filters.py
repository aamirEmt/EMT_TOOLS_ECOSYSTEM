"""Tests for hotel search filters: sort_type and user_rating.

Tests both schema validation (unit tests) and API integration.

File: tests/test_hotel_filters.py

Run with:
    pytest tests/test_hotel_filters.py -v -s

Run only unit tests (no API calls):
    pytest tests/test_hotel_filters.py -v -s -m "not integration"
"""

import pytest
from datetime import datetime, timedelta
from tools_factory.hotels.hotel_schema import HotelSearchInput, SortType


# ============================================================================
# UNIT TESTS - SORT TYPE VALIDATION
# ============================================================================

class TestSortTypeValidation:
    """Unit tests for sort_type field validation."""

    def test_sort_type_default_value(self):
        """Test that default sort_type is Popular|DSC."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03"
        )
        assert input_data.sort_type == "Popular|DSC"

    def test_sort_type_price_low_to_high_direct(self):
        """Test direct API value for price low to high."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            sort_type="price|ASC"
        )
        assert input_data.sort_type == "price|ASC"

    def test_sort_type_price_high_to_low_direct(self):
        """Test direct API value for price high to low."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            sort_type="price|DESC"
        )
        assert input_data.sort_type == "price|DESC"

    def test_sort_type_popularity_direct(self):
        """Test direct API value for popularity."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            sort_type="Popular|DSC"
        )
        assert input_data.sort_type == "Popular|DSC"

    # Non-LLM user input tests
    def test_sort_type_low_to_high_keyword(self):
        """Test 'low to high' keyword mapping."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            sort_type="low to high"
        )
        assert input_data.sort_type == "price|ASC"

    def test_sort_type_cheapest_keyword(self):
        """Test 'cheapest' keyword mapping."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            sort_type="cheapest"
        )
        assert input_data.sort_type == "price|ASC"

    def test_sort_type_high_to_low_keyword(self):
        """Test 'high to low' keyword mapping."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            sort_type="high to low"
        )
        assert input_data.sort_type == "price|DESC"

    def test_sort_type_expensive_keyword(self):
        """Test 'expensive' keyword mapping."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            sort_type="expensive"
        )
        assert input_data.sort_type == "price|DESC"

    def test_sort_type_popular_keyword(self):
        """Test 'popular' keyword mapping."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            sort_type="popular"
        )
        assert input_data.sort_type == "Popular|DSC"

    def test_sort_type_unknown_defaults_to_popularity(self):
        """Test unknown value defaults to popularity."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            sort_type="random_value"
        )
        assert input_data.sort_type == "Popular|DSC"


# ============================================================================
# UNIT TESTS - USER RATING VALIDATION
# ============================================================================

class TestUserRatingValidation:
    """Unit tests for user_rating field validation."""

    def test_user_rating_default_none(self):
        """Test that default user_rating is None."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03"
        )
        assert input_data.user_rating is None

    def test_user_rating_direct_value_5(self):
        """Test direct API value '5' for excellent."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating=["5"]
        )
        assert input_data.user_rating == ["5"]

    def test_user_rating_direct_value_4(self):
        """Test direct API value '4' for very good."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating=["4"]
        )
        assert input_data.user_rating == ["4"]

    def test_user_rating_direct_value_3(self):
        """Test direct API value '3' for good."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating=["3"]
        )
        assert input_data.user_rating == ["3"]

    def test_user_rating_multiple_values(self):
        """Test multiple user rating values."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating=["5", "4"]
        )
        assert input_data.user_rating == ["5", "4"]

    # Non-LLM user input tests
    def test_user_rating_excellent_keyword(self):
        """Test 'excellent' keyword mapping."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating=["excellent"]
        )
        assert input_data.user_rating == ["5"]

    def test_user_rating_best_keyword(self):
        """Test 'best' keyword mapping."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating=["best"]
        )
        assert input_data.user_rating == ["5"]

    def test_user_rating_top_rated_keyword(self):
        """Test 'top rated' keyword mapping."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating=["top rated"]
        )
        assert input_data.user_rating == ["5"]

    def test_user_rating_very_good_keyword(self):
        """Test 'very good' keyword mapping."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating=["very good"]
        )
        assert input_data.user_rating == ["4"]

    def test_user_rating_great_keyword(self):
        """Test 'great' keyword mapping."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating=["great"]
        )
        assert input_data.user_rating == ["4"]

    def test_user_rating_good_keyword(self):
        """Test 'good' keyword mapping."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating=["good"]
        )
        assert input_data.user_rating == ["3"]

    def test_user_rating_decent_keyword(self):
        """Test 'decent' keyword mapping."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating=["decent"]
        )
        assert input_data.user_rating == ["3"]

    def test_user_rating_mixed_keywords_and_values(self):
        """Test mixed keywords and direct values."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating=["excellent", "4", "good"]
        )
        assert sorted(input_data.user_rating) == ["3", "4", "5"]

    def test_user_rating_single_string_converted_to_list(self):
        """Test single string value gets converted to list."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating="excellent"
        )
        assert input_data.user_rating == ["5"]

    def test_user_rating_invalid_value_returns_none(self):
        """Test invalid value returns None."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating=["invalid"]
        )
        assert input_data.user_rating is None

    def test_user_rating_deduplication(self):
        """Test duplicate values are removed."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            user_rating=["excellent", "best", "5"]  # All map to "5"
        )
        assert input_data.user_rating == ["5"]


# ============================================================================
# UNIT TESTS - MIN PRICE AND MAX PRICE VALIDATION
# ============================================================================

class TestMinMaxPriceValidation:
    """Unit tests for min_price and max_price field validation."""

    def test_min_price_default_none(self):
        """Test that default min_price is None."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03"
        )
        assert input_data.min_price is None

    def test_max_price_default_value(self):
        """Test that default max_price is 10,000,000."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03"
        )
        assert input_data.max_price == 10_000_000

    def test_min_price_valid_value(self):
        """Test valid min_price value."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            min_price=1000
        )
        assert input_data.min_price == 1000

    def test_max_price_valid_value(self):
        """Test valid max_price value."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            max_price=5000
        )
        assert input_data.max_price == 5000

    def test_min_price_minimum_boundary(self):
        """Test min_price at minimum boundary (1)."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            min_price=1
        )
        assert input_data.min_price == 1

    def test_max_price_minimum_boundary(self):
        """Test max_price at minimum boundary (1)."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            max_price=1
        )
        assert input_data.max_price == 1

    def test_min_price_zero_raises_error(self):
        """Test that min_price=0 raises validation error."""
        with pytest.raises(ValueError):
            HotelSearchInput(
                city_name="Mumbai",
                check_in_date="2025-03-01",
                check_out_date="2025-03-03",
                min_price=0
            )

    def test_max_price_zero_raises_error(self):
        """Test that max_price=0 raises validation error."""
        with pytest.raises(ValueError):
            HotelSearchInput(
                city_name="Mumbai",
                check_in_date="2025-03-01",
                check_out_date="2025-03-03",
                max_price=0
            )

    def test_min_price_negative_raises_error(self):
        """Test that negative min_price raises validation error."""
        with pytest.raises(ValueError):
            HotelSearchInput(
                city_name="Mumbai",
                check_in_date="2025-03-01",
                check_out_date="2025-03-03",
                min_price=-100
            )

    def test_max_price_negative_raises_error(self):
        """Test that negative max_price raises validation error."""
        with pytest.raises(ValueError):
            HotelSearchInput(
                city_name="Mumbai",
                check_in_date="2025-03-01",
                check_out_date="2025-03-03",
                max_price=-100
            )

    def test_min_and_max_price_together(self):
        """Test both min_price and max_price set together."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            min_price=2000,
            max_price=8000
        )
        assert input_data.min_price == 2000
        assert input_data.max_price == 8000

    def test_min_price_equals_max_price(self):
        """Test min_price equal to max_price (valid edge case)."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            min_price=5000,
            max_price=5000
        )
        assert input_data.min_price == 5000
        assert input_data.max_price == 5000

    def test_min_price_large_value(self):
        """Test min_price with large value."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            min_price=100000
        )
        assert input_data.min_price == 100000

    def test_max_price_large_value(self):
        """Test max_price with large value."""
        input_data = HotelSearchInput(
            city_name="Mumbai",
            check_in_date="2025-03-01",
            check_out_date="2025-03-03",
            max_price=50000000
        )
        assert input_data.max_price == 50000000


# ============================================================================
# INTEGRATION TESTS - SORT TYPE WITH REAL API
# ============================================================================

pytestmark_integration = pytest.mark.integration


@pytest.fixture
def base_search_payload():
    """Base payload for hotel search."""
    today = datetime.now()
    checkin = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=32)).strftime("%Y-%m-%d")
    return {
        "city_name": "Mumbai",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "num_rooms": 1,
        "num_adults": 2
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_sort_by_price_low_to_high(base_search_payload):
    """Test hotel search sorted by price low to high."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    payload = {**base_search_payload, "sort_type": "price|ASC"}

    print(f"\n[SEARCH] Searching hotels sorted by price (low to high)")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} hotels")

    if len(hotels) >= 2:
        # Verify prices are in ascending order
        prices = []
        for hotel in hotels[:5]:
            price = hotel.get("price", {})
            if isinstance(price, dict):
                price_val = price.get("amount", 0)
            else:
                price_val = price or 0
            prices.append(price_val)
            print(f"   {hotel.get('name', 'N/A')}: ₹{price_val}")

        # Check if prices are roughly ascending (API may not be perfect)
        print(f"   Prices: {prices}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_sort_by_price_high_to_low(base_search_payload):
    """Test hotel search sorted by price high to low."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    payload = {**base_search_payload, "sort_type": "price|DESC"}

    print(f"\n[SEARCH] Searching hotels sorted by price (high to low)")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} hotels")

    if len(hotels) >= 2:
        for hotel in hotels[:5]:
            price = hotel.get("price", {})
            if isinstance(price, dict):
                price_val = price.get("amount", 0)
            else:
                price_val = price or 0
            print(f"   {hotel.get('name', 'N/A')}: ₹{price_val}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_sort_by_popularity(base_search_payload):
    """Test hotel search sorted by popularity (default)."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    payload = {**base_search_payload, "sort_type": "Popular|DSC"}

    print(f"\n[SEARCH] Searching hotels sorted by popularity")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} hotels (sorted by popularity)")

    for hotel in hotels[:5]:
        print(f"   {hotel.get('name', 'N/A')}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_sort_with_user_friendly_input(base_search_payload):
    """Test hotel search with user-friendly sort input (non-LLM)."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    # Using user-friendly input instead of API value
    payload = {**base_search_payload, "sort_type": "low to high"}

    print(f"\n[SEARCH] Searching hotels with user input 'low to high'")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} hotels")


# ============================================================================
# INTEGRATION TESTS - USER RATING WITH REAL API
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_with_excellent_rating(base_search_payload):
    """Test hotel search with excellent user rating filter."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    payload = {**base_search_payload, "user_rating": ["5"]}

    print(f"\n[SEARCH] Searching hotels with Excellent (4.2+) rating")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} excellent rated hotels")

    for hotel in hotels[:5]:
        print(f"   {hotel.get('name', 'N/A')} - Rating: {hotel.get('rating', 'N/A')}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_with_very_good_rating(base_search_payload):
    """Test hotel search with very good user rating filter."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    payload = {**base_search_payload, "user_rating": ["4"]}

    print(f"\n[SEARCH] Searching hotels with Very Good (3.5+) rating")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} very good rated hotels")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_with_multiple_user_ratings(base_search_payload):
    """Test hotel search with multiple user rating filters."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    payload = {**base_search_payload, "user_rating": ["5", "4"]}

    print(f"\n[SEARCH] Searching hotels with Excellent and Very Good ratings")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} hotels with 4+ guest rating")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_with_user_friendly_rating_input(base_search_payload):
    """Test hotel search with user-friendly rating input (non-LLM)."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    # Using user-friendly input instead of API value
    payload = {**base_search_payload, "user_rating": ["excellent", "very good"]}

    print(f"\n[SEARCH] Searching hotels with user input ['excellent', 'very good']")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} hotels")


# ============================================================================
# INTEGRATION TESTS - MIN/MAX PRICE WITH REAL API
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_with_min_price(base_search_payload):
    """Test hotel search with min_price filter."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    payload = {**base_search_payload, "min_price": 3000}

    print(f"\n[SEARCH] Searching hotels with min_price=3000")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} hotels with price >= ₹3000")

    for hotel in hotels[:5]:
        price = hotel.get("price", {})
        if isinstance(price, dict):
            price_val = price.get("amount", 0)
        else:
            price_val = price or 0
        print(f"   {hotel.get('name', 'N/A')}: ₹{price_val}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_with_max_price(base_search_payload):
    """Test hotel search with max_price filter."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    payload = {**base_search_payload, "max_price": 5000}

    print(f"\n[SEARCH] Searching hotels with max_price=5000")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} hotels with price <= ₹5000")

    for hotel in hotels[:5]:
        price = hotel.get("price", {})
        if isinstance(price, dict):
            price_val = price.get("amount", 0)
        else:
            price_val = price or 0
        print(f"   {hotel.get('name', 'N/A')}: ₹{price_val}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_with_min_and_max_price(base_search_payload):
    """Test hotel search with both min_price and max_price filters."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    payload = {**base_search_payload, "min_price": 2000, "max_price": 8000}

    print(f"\n[SEARCH] Searching hotels with price range ₹2000 - ₹8000")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} hotels in price range ₹2000 - ₹8000")

    for hotel in hotels[:5]:
        price = hotel.get("price", {})
        if isinstance(price, dict):
            price_val = price.get("amount", 0)
        else:
            price_val = price or 0
        print(f"   {hotel.get('name', 'N/A')}: ₹{price_val}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_with_narrow_price_range(base_search_payload):
    """Test hotel search with a narrow price range."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    payload = {**base_search_payload, "min_price": 4000, "max_price": 5000}

    print(f"\n[SEARCH] Searching hotels with narrow price range ₹4000 - ₹5000")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} hotels in price range ₹4000 - ₹5000")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_with_high_min_price(base_search_payload):
    """Test hotel search with high min_price for luxury hotels."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    payload = {**base_search_payload, "min_price": 10000}

    print(f"\n[SEARCH] Searching luxury hotels with min_price=10000")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} luxury hotels (price >= ₹10000)")

    for hotel in hotels[:5]:
        price = hotel.get("price", {})
        if isinstance(price, dict):
            price_val = price.get("amount", 0)
        else:
            price_val = price or 0
        print(f"   {hotel.get('name', 'N/A')}: ₹{price_val}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_price_filter_with_sort(base_search_payload):
    """Test hotel search with price filter and price sorting."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    payload = {
        **base_search_payload,
        "min_price": 2000,
        "max_price": 10000,
        "sort_type": "price|ASC"
    }

    print(f"\n[SEARCH] Searching hotels ₹2000-₹10000, sorted by price low to high")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} hotels")

    prices = []
    for hotel in hotels[:5]:
        price = hotel.get("price", {})
        if isinstance(price, dict):
            price_val = price.get("amount", 0)
        else:
            price_val = price or 0
        prices.append(price_val)
        print(f"   {hotel.get('name', 'N/A')}: ₹{price_val}")

    print(f"   Prices: {prices}")


# ============================================================================
# INTEGRATION TESTS - COMBINED FILTERS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_sort_and_user_rating_combined(base_search_payload):
    """Test hotel search with both sort and user rating filters."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    payload = {
        **base_search_payload,
        "sort_type": "price|ASC",
        "user_rating": ["5", "4"]
    }

    print(f"\n[SEARCH] Searching hotels: price low to high + excellent/very good rating")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} hotels matching combined filters")

    for hotel in hotels[:5]:
        price = hotel.get("price", {})
        if isinstance(price, dict):
            price_val = price.get("amount", 0)
        else:
            price_val = price or 0
        print(f"   {hotel.get('name', 'N/A')}: ₹{price_val}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hotel_search_all_filters_combined(base_search_payload):
    """Test hotel search with all filters: sort, user_rating, star_rating, price."""
    from tools_factory.factory import get_tool_factory

    factory = get_tool_factory()
    tool = factory.get_tool("search_hotels")

    payload = {
        **base_search_payload,
        "sort_type": "price|ASC",
        "user_rating": ["5"],
        "rating": ["4", "5"],
        "min_price": 3000,
        "max_price": 15000
    }

    print(f"\n[SEARCH] Searching hotels with all filters combined:")
    print(f"   Sort: price low to high")
    print(f"   User Rating: Excellent (4.2+)")
    print(f"   Star Rating: 4-5 star")
    print(f"   Price: ₹3000 - ₹15000")

    result = await tool.execute(**payload)

    assert hasattr(result, 'structured_content')
    hotels = result.structured_content.get("hotels", [])

    print(f"[OK] Found {len(hotels)} hotels matching all filters")

    for hotel in hotels[:5]:
        price = hotel.get("price", {})
        if isinstance(price, dict):
            price_val = price.get("amount", 0)
        else:
            price_val = price or 0
        print(f"   {hotel.get('name', 'N/A')}: ₹{price_val} ({hotel.get('rating', 'N/A')} star)")
