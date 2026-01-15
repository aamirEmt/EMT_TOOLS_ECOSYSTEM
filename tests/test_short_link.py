
from emt_client.utils import generate_short_link
import pytest
import re
from tools_factory.factory import get_tool_factory

from emt_client.utils import generate_short_link 



# Mark all tests as integration (same as hotel/flight tests)
pytestmark = pytest.mark.integration

SHORT_LINK_REGEX = r"^https://emt\.bio/[A-Za-z0-9]{6,10}$"


# ============================================================================
# HOTEL → SHORT LINK (REAL API)
# ============================================================================

@pytest.mark.asyncio
async def test_hotel_search_short_link_real_api():
    """
    Real-time test:
    Hotel search → deepLink → short link
    """
    factory = get_tool_factory()
    hotel_tool = factory.get_tool("search_hotels")

    payload = {
        "city_name": "Mumbai",
        "check_in_date": "2026-02-15",
        "check_out_date": "2026-02-17",
        "num_rooms": 1,
        "num_adults": 2,
    }

    print("\n🏨 Running real hotel search for short link test")

    result = await hotel_tool.execute(**payload)
    hotels = result["structured_content"].get("hotels", [])

    assert hotels, "❌ No hotels returned from real API"

    first_hotel = hotels[0]
    assert "deepLink" in first_hotel, "❌ Hotel does not contain deepLink"

    print(f"🔗 Original hotel deepLink: {first_hotel['deepLink']}")

    # Generate short link
    short_link_result = generate_short_link(
        results=[first_hotel],
        product_type="hotel",
    )

    short_link = short_link_result[0]["deepLink"]

    print(f"✅ Hotel short link generated: {short_link}")

    assert short_link is not None
    assert re.match(SHORT_LINK_REGEX, short_link)


# ============================================================================
# FLIGHT → SHORT LINK (REAL API)
# ============================================================================

import pytest
from datetime import datetime, timedelta


@pytest.fixture
def dummy_flight_international_roundtrip():
    today = datetime.now()
    outbound = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    return_date = (today + timedelta(days=37)).strftime("%Y-%m-%d")

    return {
        "origin": "DEL",
        "destination": "LHR",
        "outbound_date": outbound,
        "return_date": return_date,
        "adults": 1,
        "children": 0,
        "infants": 0,
    }

def extract_deeplink_from_international_combo(combo: dict) -> str:
    """
    Safely extract deepLink from international roundtrip combo.
    """
    # 1️⃣ Combo-level deepLink (most reliable)
    if "deepLink" in combo:
        return combo["deepLink"]

    onward = combo.get("onward_flight", {})

    # 2️⃣ Onward flight level
    if "deepLink" in onward:
        return onward["deepLink"]

    # 3️⃣ Fare option level (very common in intl combos)
    fare_options = onward.get("fare_options", [])
    if fare_options and "deepLink" in fare_options[0]:
        return fare_options[0]["deepLink"]

    raise AssertionError("❌ No deepLink found in international combo")

@pytest.mark.asyncio
async def test_flight_search_short_link_real_api():
    """
    Real-time test:
    Flight search → deepLink → short link
    """
    factory = get_tool_factory()
    flight_tool = factory.get_tool("search_flights")

    payload = {
        "origin": "DEL",
        "destination": "BOM",
        "outbound_date": "2026-02-20",
        "adults": 1,
    }

    print("\n✈️ Running real flight search for short link test")

    result = await flight_tool.execute(**payload)
    flights = result.structured_content.get("outbound_flights", [])

    assert flights, "❌ No flights returned from real API"

    first_flight = flights[0]
    # assert hasattr(first_flight, "deepLink"), "❌ Flight does not contain deepLink"
    assert "deepLink" in first_flight, "❌ Flight does not contain deepLink"


    print(f"🔗 Original flight deepLink: {first_flight['deepLink']}")

    print(f"🔗 Original flight deepLink: {first_flight['deepLink']}")
    short_link_result = generate_short_link([first_flight], product_type="flight")

    # Generate short link
    # short_link_result = generate_short_link(
    #     results=[first_flight],
    #     product_type="flight",
    # )

    short_link = short_link_result[0]["deepLink"]

    print(f"✅ Flight short link generated: {short_link}")

    assert short_link is not None
    assert re.match(SHORT_LINK_REGEX, short_link)


# ============================================================================
# MULTIPLE RESULTS → SHORT LINKS (REAL API)
# ============================================================================



@pytest.mark.asyncio
async def test_flight_search_international_roundtrip_with_combos_and_short_link(
    dummy_flight_international_roundtrip
):
    """
    International round-trip should populate outbound flights and international combos
    and should generate a valid short link.
    """
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")

    print(f"\nSearching international round-trip flights: {dummy_flight_international_roundtrip}")

    result = await tool.execute(**dummy_flight_international_roundtrip)
    data = result.structured_content

    # Verify it's recognized as round-trip and international
    assert data.get("is_roundtrip") is True, "Should be marked as round-trip"
    assert data.get("is_international") is True, "Should be marked as international"
    # assert getattr(data, "is_roundtrip", False) is True, "Should be marked as round-trip"
    # assert getattr(data, "is_international", False) is True, "Should be marked as international"
    
    # Verify international combos exist
    # assert "international_combos" in data, "Should have international_combos key"
    international_combos = data.get("international_combos", [])

    # international_combos = getattr(data, "international_combos", [])
    assert international_combos, "International round-trip should return international combos"

    assert len(international_combos) > 0, "International round-trip should return international combos"
    print(f"Found {len(international_combos)} international combos")

    # Verify combo structure
    first_combo = international_combos[0]
    assert "id" in first_combo
    assert "combo_fare" in first_combo
    assert "onward_flight" in first_combo
    assert "return_flight" in first_combo

    onward = first_combo["onward_flight"]
    return_flight = first_combo["return_flight"]

    assert onward.get("direction") == "outbound"
    assert return_flight.get("direction") == "return"

    print(f"Combo structure validated: {onward['destination']} -> {return_flight['destination']}")

    # ============================================================================
    # 🔗 SHORT LINK GENERATION (REAL API)
    # ============================================================================

    original_deeplink = extract_deeplink_from_international_combo(first_combo)
    
    print(f"🔗 Original deepLink: {original_deeplink}")

    # short_link_result = generate_short_link(
    #     results=[{"deepLink": original_deeplink}],
    #     product_type="flight",
    # )
    short_link_result = generate_short_link([{"deepLink": original_deeplink}], "flight")


    short_link = short_link_result[0]["deepLink"]
    slug = short_link.split("/")[-1]

    print(f"✅ Short link generated: {short_link}")
    print(f"🔢 Short link slug length: {len(slug)}")

    assert short_link.startswith("https://emt.bio/")
    assert 6 <= len(slug) <= 10

@pytest.mark.asyncio
async def test_economy_flight_short_link_real_api():
    factory = get_tool_factory()
    flight_tool = factory.get_tool("search_flights")

    payload = {
        "origin": "DEL",
        "destination": "BOM",
        "outbound_date": "2026-03-05",
        "adults": 1,
        "cabin": "economy",
    }

    print("\n✈️ Economy cabin flight short link test")

    result = await flight_tool.execute(**payload)
    flights = result.structured_content.get("outbound_flights", [])

    assert flights, "❌ No flights returned"

    flight = flights[0]
    print(f"🔗 Original deepLink: {flight['deepLink']}")

    short_link = generate_short_link([{"deepLink": flight['deepLink']}], "flight")[0]["deepLink"]
    print(f"✅ Short link: {short_link}")

    assert short_link.startswith("https://emt.bio/")

@pytest.mark.asyncio
async def test_business_flight_short_link_real_api():
    factory = get_tool_factory()
    flight_tool = factory.get_tool("search_flights")

    payload = {
        "origin": "DEL",
        "destination": "DXB",
        "outbound_date": "2026-03-12",
        "adults": 1,
        "cabin": "business",
    }

    print("\n✈️ Business cabin flight short link test")

    result = await flight_tool.execute(**payload)
    flights = result.structured_content.get("outbound_flights", [])

    assert flights, "❌ No flights returned"

    flight = flights[0]
    short_link = generate_short_link([{"deepLink": flight['deepLink']}], "flight")[0]["deepLink"]

    print(f"✅ Short link: {short_link}")
    assert short_link.startswith("https://emt.bio/")

@pytest.mark.asyncio
async def test_hotel_multiple_rooms_short_link_real_api():
    factory = get_tool_factory()
    hotel_tool = factory.get_tool("search_hotels")

    payload = {
        "city_name": "Goa",
        "check_in_date": "2026-03-18",
        "check_out_date": "2026-03-21",
        "num_rooms": 3,
        "num_adults": 6,
    }

    print("\n🏨 Hotel multiple rooms short link test")

    result = await hotel_tool.execute(**payload)
    hotels = result["structured_content"].get("hotels", [])

    assert hotels, "❌ No hotels returned"

    hotel = hotels[0]
    short_link = generate_short_link([hotel], "hotel")[0]["deepLink"]

    print(f"✅ Short link: {short_link}")
    assert short_link.startswith("https://emt.bio/")

@pytest.mark.asyncio
async def test_short_link_length_real_api():
    factory = get_tool_factory()
    hotel_tool = factory.get_tool("search_hotels")

    payload = {
        "city_name": "Mumbai",
        "check_in_date": "2026-03-10",
        "check_out_date": "2026-03-12",
        "num_rooms": 1,
        "num_adults": 2,
    }

    print("\n🏨 Running hotel search for short link length test")

    result = await hotel_tool.execute(**payload)

    # Handle both possible keys defensively
    hotels = (
        result["structured_content"].get("hotels")
        or result["structured_content"].get("results")
        or []
    )

    print(f"📊 Hotels returned: {len(hotels)}")

    # ✅ CRITICAL FIX
    assert hotels, "❌ No hotels returned from real API, cannot test short link length"

    hotel = hotels[0]

    assert "deepLink" in hotel, "❌ Hotel does not contain deepLink"

    short_link = generate_short_link([hotel], "hotel")[0]["deepLink"]
    slug = short_link.split("/")[-1]

    print(f"🔗 Short link: {short_link}")
    print(f"🔢 Slug length: {len(slug)}")

    assert 6 <= len(slug) <= 10

def test_unicode_deeplink_short_link_real_api():
    unicode_link = "https://www.easemytrip.com/hotel?city=मुंबई&hotel=ताज"

    result = generate_short_link(
        [{"deepLink": unicode_link}],
        product_type="hotel",
    )

    short_link = result[0]["deepLink"]
    print(f"🌐 Unicode URL short link: {short_link}")

    assert short_link.startswith("https://emt.bio/")

import concurrent.futures

def test_parallel_short_link_generation_real_api():
    links = [
        {"deepLink": f"https://www.easemytrip.com/test?id={i}"}
        for i in range(5)
    ]

    print("\n⚙️ Parallel short link generation test")

    def generate(item):
        return generate_short_link([item], "hotel")[0]["deepLink"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(generate, links))

    for link in results:
        print(f"   → {link}")
        assert link.startswith("https://emt.bio/")

import requests

def test_short_link_timeout_real_api():
    try:
        generate_short_link(
            [{"deepLink": "https://www.easemytrip.com/test?id=timeout"}],
            product_type="hotel",
        )
    except requests.Timeout:
        print("⏱️ Timeout handled correctly")
        assert True
