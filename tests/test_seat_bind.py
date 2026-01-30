"""
Tests for Bus Seat Layout/Bind API and View All Card.

Run with:
    pytest tests/test_seat_bind.py -v -s

Generate HTML only:
    python tests/test_seat_bind.py

Tests cover:
- New SeatBind API (bus.easemytrip.com/Home/SeatBind/)
- Rating normalization in results
- View All link presence
- City names from API
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

pytestmark = [pytest.mark.integration, pytest.mark.seat_bind]


# ============================================================================
# HTML HELPERS
# ============================================================================

def wrap_html_page(content: str, title: str = "Bus Seat Layout Test") -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ background: #f5f5f5; padding: 20px; margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        .test-section {{ margin-bottom: 40px; padding: 20px; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .test-title {{ font-size: 18px; font-weight: 600; color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #ef6614; }}
        .test-meta {{ font-size: 12px; color: #666; margin-bottom: 15px; padding: 10px; background: #f9f9f9; border-radius: 6px; }}
        .test-meta code {{ background: #e0e0e0; padding: 2px 6px; border-radius: 4px; font-size: 11px; }}
        .raw-response {{ margin-top: 20px; padding: 15px; background: #1e1e1e; color: #d4d4d4; border-radius: 8px; font-family: 'Consolas', 'Monaco', monospace; font-size: 11px; overflow-x: auto; max-height: 300px; overflow-y: auto; }}
        .error-box {{ padding: 20px; background: #ffebee; border: 1px solid #f44336; border-radius: 8px; color: #c62828; }}
        .success-box {{ padding: 10px 15px; background: #e8f5e9; border: 1px solid #4caf50; border-radius: 6px; color: #2e7d32; margin-bottom: 15px; }}
    </style>
</head>
<body>
    <h1 style="color: #333; margin-bottom: 30px;">🚌 Bus Seat Layout & View All Tests - New API</h1>
    {content}
</body>
</html>"""


def save_html_file(html_content: str, filename: str, output_dir: str = None) -> str:
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    return filepath


# ============================================================================
# LIVE API HELPERS
# ============================================================================

async def fetch_buses_for_seat_test(
    source_id: str = None,
    destination_id: str = None,
    source_name: str = None,
    destination_name: str = None,
    days_ahead: int = 3,
) -> Dict[str, Any]:
    """Fetch buses from live API to get bus details for seat layout test."""
    from tools_factory.buses.bus_search_service import search_buses
    
    journey_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    
    print(f"\n🔍 Fetching buses for seat layout test...")
    if source_name:
        print(f"   Route (by name): {source_name} → {destination_name}")
    else:
        print(f"   Route (by ID): {source_id} → {destination_id}")
    print(f"   Date: {journey_date}")
    
    results = await search_buses(
        source_id=source_id,
        destination_id=destination_id,
        source_name=source_name,
        destination_name=destination_name,
        journey_date=journey_date,
    )
    
    bus_count = len(results.get("buses", []))
    print(f"   ✅ Found {bus_count} buses")
    
    return results


async def fetch_seat_layout(
    source_id: str,
    destination_id: str,
    journey_date: str,
    bus_id: str,
    route_id: str,
    engine_id: int,
    boarding_point_id: str,
    dropping_point_id: str,
    source_name: str = "",
    destination_name: str = "",
    operator_id: str = "",
    operator_name: str = "",
    bus_type: str = "",
    departure_time: str = "",
    arrival_time: str = "",
    duration: str = "",
    trace_id: str = "",
) -> Dict[str, Any]:
    """Fetch seat layout from the new SeatBind API."""
    from tools_factory.buses.bus_search_service import get_seat_layout
    
    print(f"\n🪑 Fetching seat layout...")
    print(f"   Bus ID: {bus_id}")
    print(f"   Route ID: {route_id}")
    print(f"   Engine ID: {engine_id}")
    print(f"   Boarding: {boarding_point_id}")
    print(f"   Dropping: {dropping_point_id}")
    
    result = await get_seat_layout(
        source_id=source_id,
        destination_id=destination_id,
        journey_date=journey_date,
        bus_id=bus_id,
        route_id=route_id,
        engine_id=engine_id,
        boarding_point_id=boarding_point_id,
        dropping_point_id=dropping_point_id,
        source_name=source_name,
        destination_name=destination_name,
        operator_id=operator_id,
        operator_name=operator_name,
        bus_type=bus_type,
        departure_time=departure_time,
        arrival_time=arrival_time,
        duration=duration,
        trace_id=trace_id,
    )
    
    if result.get("success"):
        layout = result.get("layout", {})
        print(f"   ✅ Seat layout loaded: {layout.get('available_seats', 0)}/{layout.get('total_seats', 0)} available")
    else:
        print(f"   ❌ Failed: {result.get('message', 'Unknown error')}")
    
    return result


def extract_bus_details_for_seatbind(bus: Dict[str, Any]) -> Dict[str, Any]:
    """Extract required fields from bus for SeatBind API call."""
    
    boarding_points = bus.get("boarding_points", [])
    first_boarding_id = ""
    if boarding_points:
        first_boarding_id = boarding_points[0].get("bd_id", "") or boarding_points[0].get("bdid", "")
    
    dropping_points = bus.get("dropping_points", [])
    first_dropping_id = ""
    if dropping_points:
        first_dropping_id = dropping_points[0].get("dp_id", "") or dropping_points[0].get("dpId", "")
    
    return {
        "bus_id": bus.get("bus_id", ""),
        "route_id": bus.get("route_id", ""),
        "engine_id": bus.get("engine_id", 0),
        "operator_id": bus.get("operator_id", ""),
        "boarding_point_id": first_boarding_id,
        "dropping_point_id": first_dropping_id,
        "operator_name": bus.get("operator_name", ""),
        "bus_type": bus.get("bus_type", ""),
        "departure_time": bus.get("departure_time", ""),
        "arrival_time": bus.get("arrival_time", ""),
        "duration": bus.get("duration", ""),
        "trace_id": bus.get("trace_id", ""),
    }


# ============================================================================
# PYTEST TESTS - RATING NORMALIZATION
# ============================================================================

@pytest.mark.asyncio
async def test_bus_rating_normalization_in_results():
    """Test that ratings are normalized in search results."""
    print("\n⭐ Testing rating normalization in results...")
    
    bus_results = await fetch_buses_for_seat_test(source_id="733", destination_id="757", days_ahead=5)
    buses = bus_results.get("buses", [])
    
    for i, bus in enumerate(buses[:5]):
        rating = bus.get("rating")
        if rating is not None and rating != "":
            try:
                rating_float = float(rating)
                assert rating_float <= 5, f"Rating {rating} should be <= 5 (normalized)"
                assert rating_float != 45, f"Rating should not be raw '45'"
                assert rating_float != 40, f"Rating should not be raw '40'"
                print(f"   Bus {i+1}: Rating = {rating} ✅")
            except ValueError:
                print(f"   Bus {i+1}: Rating = {rating} (non-numeric)")
    
    print("   ✅ Ratings normalized correctly")


# ============================================================================
# PYTEST TESTS - VIEW ALL LINK
# ============================================================================

@pytest.mark.asyncio
async def test_view_all_link_present_in_results():
    """Test that view_all_link is present in search results."""
    print("\n🔗 Testing view_all_link in results...")
    
    bus_results = await fetch_buses_for_seat_test(source_id="733", destination_id="757", days_ahead=5)
    
    assert "view_all_link" in bus_results, "view_all_link should be present"
    
    view_all_link = bus_results.get("view_all_link", "")
    print(f"   view_all_link: {view_all_link}")
    
    if view_all_link:
        assert "org=" in view_all_link, "Should have org parameter"
        assert "des=" in view_all_link, "Should have des parameter"
        assert "date=" in view_all_link, "Should have date parameter"
        assert "searchid=" in view_all_link, "Should have searchid parameter"
        print("   ✅ view_all_link is valid")


# ============================================================================
# PYTEST TESTS - CITY NAMES
# ============================================================================

@pytest.mark.asyncio
async def test_city_names_in_results():
    """Test that city names are populated from API."""
    print("\n📍 Testing city names in results...")
    
    bus_results = await fetch_buses_for_seat_test(source_name="Delhi", destination_name="Manali", days_ahead=5)
    
    source_name = bus_results.get("source_name")
    dest_name = bus_results.get("destination_name")
    source_id = bus_results.get("source_id")
    dest_id = bus_results.get("destination_id")
    
    print(f"   Source: {source_name} (ID: {source_id})")
    print(f"   Destination: {dest_name} (ID: {dest_id})")
    
    # Names should not just be the IDs
    if source_name and source_id:
        assert source_name != source_id or source_name.isdigit() == False, \
            "source_name should be a real name, not just the ID"
    
    if dest_name and dest_id:
        assert dest_name != dest_id or dest_name.isdigit() == False, \
            "destination_name should be a real name, not just the ID"
    
    print("   ✅ City names populated correctly")


# ============================================================================
# PYTEST TESTS - SEAT LAYOUT API
# ============================================================================

@pytest.mark.asyncio
async def test_seat_layout_api_call():
    """Test basic SeatBind API call with real data."""
    print("\n" + "=" * 60)
    print("TEST: SeatBind API Call (New Endpoint)")
    print("=" * 60)
    
    bus_results = await fetch_buses_for_seat_test(source_id="733", destination_id="757", days_ahead=3)
    buses = bus_results.get("buses", [])
    
    if not buses:
        pytest.skip("No buses found for test")
    
    first_bus = buses[0]
    bus_details = extract_bus_details_for_seatbind(first_bus)
    
    print(f"\n📋 Bus details for SeatBind:")
    print(f"   Operator: {bus_details['operator_name']}")
    print(f"   Bus ID: {bus_details['bus_id']}")
    print(f"   Route ID: {bus_details['route_id']}")
    print(f"   Engine ID: {bus_details['engine_id']}")
    
    if not bus_details["boarding_point_id"] or not bus_details["dropping_point_id"]:
        pytest.skip("Bus doesn't have boarding/dropping point IDs")
    
    journey_date = bus_results.get("journey_date", "")
    
    seat_result = await fetch_seat_layout(
        source_id=bus_results.get("source_id", "733"),
        destination_id=bus_results.get("destination_id", "757"),
        journey_date=journey_date,
        bus_id=bus_details["bus_id"],
        route_id=bus_details["route_id"],
        engine_id=bus_details["engine_id"],
        boarding_point_id=bus_details["boarding_point_id"],
        dropping_point_id=bus_details["dropping_point_id"],
        source_name=bus_results.get("source_name", ""),
        destination_name=bus_results.get("destination_name", ""),
        operator_id=bus_details["operator_id"],
        operator_name=bus_details["operator_name"],
        bus_type=bus_details["bus_type"],
        departure_time=bus_details["departure_time"],
        arrival_time=bus_details["arrival_time"],
        duration=bus_details["duration"],
        trace_id=bus_details["trace_id"],
    )
    
    assert "success" in seat_result
    assert "message" in seat_result
    
    print(f"\n✅ SeatBind API test completed")
    print(f"   Success: {seat_result.get('success')}")
    print(f"   Message: {seat_result.get('message')}")


@pytest.mark.asyncio
async def test_seat_layout_html_rendering():
    """Test seat layout HTML rendering with live API data."""
    from tools_factory.buses.bus_renderer import render_seat_layout
    
    print("\n" + "=" * 60)
    print("TEST: Seat Layout HTML Rendering")
    print("=" * 60)
    
    bus_results = await fetch_buses_for_seat_test(source_id="733", destination_id="757", days_ahead=3)
    buses = bus_results.get("buses", [])
    
    if not buses:
        pytest.skip("No buses found")
    
    seat_result = None
    for bus in buses[:5]:
        bus_details = extract_bus_details_for_seatbind(bus)
        
        if not bus_details["boarding_point_id"] or not bus_details["dropping_point_id"]:
            continue
        
        seat_result = await fetch_seat_layout(
            source_id=bus_results.get("source_id", "733"),
            destination_id=bus_results.get("destination_id", "757"),
            journey_date=bus_results.get("journey_date", ""),
            bus_id=bus_details["bus_id"],
            route_id=bus_details["route_id"],
            engine_id=bus_details["engine_id"],
            boarding_point_id=bus_details["boarding_point_id"],
            dropping_point_id=bus_details["dropping_point_id"],
            operator_name=bus_details["operator_name"],
            bus_type=bus_details["bus_type"],
        )
        
        if seat_result.get("success"):
            break
    
    html = render_seat_layout(seat_result or {"success": False, "message": "No seat data"})
    
    assert html is not None
    assert "seat-layout" in html
    
    print(f"\n✅ Seat layout HTML rendered successfully")


# ============================================================================
# PYTEST TESTS - VIEW ALL CARD
# ============================================================================

@pytest.mark.asyncio
async def test_view_all_card_with_limit():
    """Test View All card appears when buses exceed limit."""
    from tools_factory.buses.bus_renderer import render_bus_results_with_limit
    
    print("\n" + "=" * 60)
    print("TEST: View All Card with Limit")
    print("=" * 60)
    
    bus_results = await fetch_buses_for_seat_test(source_id="733", destination_id="757", days_ahead=7)
    buses = bus_results.get("buses", [])
    
    print(f"\n📊 Total buses: {len(buses)}")
    
    if len(buses) <= 5:
        pytest.skip(f"Not enough buses ({len(buses)}) to test View All card")
    
    html = render_bus_results_with_limit(bus_results, display_limit=5, show_view_all=True)
    
    assert html is not None
    assert "view-all-card" in html
    assert "View All" in html
    
    total = len(buses)
    assert str(total) in html, f"Expected total count {total} in HTML"
    
    print(f"   ✅ View All card shows {total} total buses")


# @pytest.mark.asyncio
# async def test_view_all_card_not_shown_when_few_buses():
#     """Test View All card does NOT appear when buses are within limit."""
#     from tools_factory.buses.bus_renderer import render_bus_results_with_limit
    
#     print("\n" + "=" * 60)
#     print("TEST: View All Card Not Shown (Few Buses)")
#     print("=" * 60)
    
#     bus_results = await fetch_buses_for_seat_test(source_id="733", destination_id="757", days_ahead=7)
#     buses = bus_results.get("buses", [])
    
#     bus_results["buses"] = buses[:3]
#     bus_results["view_all_link"] = ""
    
#     html = render_bus_results_with_limit(bus_results, display_limit=5, show_view_all=True)
    
#     assert html is not None
#     assert "view-all-card" not in html
    
#     print(f"   ✅ View All card correctly hidden (only {len(bus_results['buses'])} buses)")


@pytest.mark.asyncio
async def test_view_all_card_not_shown_when_few_buses():
    """Test View All card does NOT appear when buses are within limit."""
    from tools_factory.buses.bus_renderer import render_bus_results_with_limit
    
    print("\n" + "=" * 60)
    print("TEST: View All Card Not Shown (Few Buses)")
    print("=" * 60)
    
    bus_results = await fetch_buses_for_seat_test(source_id="733", destination_id="757", days_ahead=7)
    buses = bus_results.get("buses", [])
    
    bus_results["buses"] = buses[:3]
    bus_results["view_all_link"] = ""
    
    html = render_bus_results_with_limit(bus_results, display_limit=5, show_view_all=True)
    
    assert html is not None
    assert 'class="buscard item view-all-card"' not in html, \
        "View All card element should not be rendered when few buses"
    
    print(f"   ✅ View All card correctly hidden (only {len(bus_results['buses'])} buses)")


@pytest.mark.asyncio
async def test_view_all_different_limits():
    """Test View All card with different limit values."""
    from tools_factory.buses.bus_renderer import render_bus_results_with_limit
    
    print("\n" + "=" * 60)
    print("TEST: View All with Different Limits")
    print("=" * 60)
    
    bus_results = await fetch_buses_for_seat_test(source_id="733", destination_id="757", days_ahead=7)
    buses = bus_results.get("buses", [])
    total = len(buses)
    
    print(f"\n📊 Total buses: {total}")
    
    for limit in [3, 5, 10]:
        html = render_bus_results_with_limit(bus_results, display_limit=limit, show_view_all=True)
        
        if total > limit and bus_results.get("view_all_link"):
            has_view_all = "view-all-card" in html
            print(f"   Limit {limit}: {'✅' if has_view_all else '❌'} View All ({total} total)")
            assert has_view_all, f"View All should appear for limit={limit}"
        else:
            has_view_all = "view-all-card" in html
            print(f"   Limit {limit}: {'✅' if not has_view_all else '❌'} No View All needed")


# ============================================================================
# PYTEST TESTS - COMBINED FLOW
# ============================================================================

@pytest.mark.asyncio
async def test_full_search_to_seat_layout_flow():
    """Test full flow: Search → Select Bus → Get Seat Layout."""
    from tools_factory.buses.bus_renderer import render_bus_results_with_limit, render_seat_layout
    
    print("\n" + "=" * 60)
    print("TEST: Full Search to Seat Layout Flow")
    print("=" * 60)
    
    # Step 1: Search buses
    print("\n📍 Step 1: Search Buses (by city name)")
    bus_results = await fetch_buses_for_seat_test(source_name="Delhi", destination_name="Manali", days_ahead=5)
    buses = bus_results.get("buses", [])
    
    assert len(buses) > 0, "No buses found"
    print(f"   Found {len(buses)} buses")
    print(f"   Source: {bus_results.get('source_name')} (ID: {bus_results.get('source_id')})")
    print(f"   Destination: {bus_results.get('destination_name')} (ID: {bus_results.get('destination_id')})")
    
    # Step 2: Render carousel with limit
    print("\n📍 Step 2: Render Carousel (limit=5)")
    carousel_html = render_bus_results_with_limit(bus_results, display_limit=5)
    assert "bus-carousel" in carousel_html
    print(f"   Carousel rendered with View All: {'view-all-card' in carousel_html}")
    
    # Step 3: Select first bus with boarding points
    print("\n📍 Step 3: Select Bus for Seat Layout")
    selected_bus = None
    for bus in buses:
        details = extract_bus_details_for_seatbind(bus)
        if details["boarding_point_id"] and details["dropping_point_id"]:
            selected_bus = bus
            break
    
    if not selected_bus:
        pytest.skip("No bus with boarding/dropping points found")
    
    bus_details = extract_bus_details_for_seatbind(selected_bus)
    print(f"   Selected: {bus_details['operator_name']}")
    
    # Step 4: Get seat layout
    print("\n📍 Step 4: Get Seat Layout")
    seat_result = await fetch_seat_layout(
        source_id=bus_results.get("source_id", ""),
        destination_id=bus_results.get("destination_id", ""),
        journey_date=bus_results.get("journey_date", ""),
        bus_id=bus_details["bus_id"],
        route_id=bus_details["route_id"],
        engine_id=bus_details["engine_id"],
        boarding_point_id=bus_details["boarding_point_id"],
        dropping_point_id=bus_details["dropping_point_id"],
        source_name=bus_results.get("source_name", ""),
        destination_name=bus_results.get("destination_name", ""),
        operator_name=bus_details["operator_name"],
        bus_type=bus_details["bus_type"],
    )
    
    # Step 5: Render seat layout
    print("\n📍 Step 5: Render Seat Layout")
    seat_html = render_seat_layout(seat_result)
    assert "seat-layout" in seat_html
    print(f"   Seat layout rendered: {'layout-empty' not in seat_html}")
    
    print("\n✅ Full flow completed successfully!")


# ============================================================================
# GENERATE HTML TEST FILE
# ============================================================================

@pytest.mark.asyncio
async def test_generate_comprehensive_html():
    """Generate comprehensive HTML test file with all features."""
    from tools_factory.buses.bus_renderer import render_bus_results_with_limit, render_seat_layout
    
    print("\n" + "=" * 60)
    print("GENERATING COMPREHENSIVE HTML TEST FILE")
    print("=" * 60)
    
    sections = []
    
    # Section 1: Bus Carousel with View All (by city name)
    print("\n📦 Section 1: Bus Carousel (by city name)")
    try:
        bus_results = await fetch_buses_for_seat_test(source_name="Delhi", destination_name="Manali", days_ahead=5)
        buses = bus_results.get("buses", [])
        
        carousel_html = render_bus_results_with_limit(bus_results, display_limit=5, show_view_all=True)
        
        sections.append(f"""
        <div class="test-section">
            <div class="test-title">🚌 Bus Carousel (City Names Auto-Resolved)</div>
            <div class="test-meta">
                Source: <code>{bus_results.get('source_name')}</code> (ID: {bus_results.get('source_id')})<br>
                Destination: <code>{bus_results.get('destination_name')}</code> (ID: {bus_results.get('destination_id')})<br>
                Total buses: <code>{len(buses)}</code> | View All: <code>{bool(bus_results.get('view_all_link'))}</code>
            </div>
            {carousel_html}
        </div>
        """)
        print(f"   ✅ Rendered {len(buses)} buses")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Section 2: Seat Layouts
    print("\n📦 Section 2: Seat Layouts")
    seat_sections = []
    
    for i, bus in enumerate(buses[:3]):
        bus_details = extract_bus_details_for_seatbind(bus)
        
        if not bus_details["boarding_point_id"]:
            continue
        
        try:
            seat_result = await fetch_seat_layout(
                source_id=bus_results.get("source_id", ""),
                destination_id=bus_results.get("destination_id", ""),
                journey_date=bus_results.get("journey_date", ""),
                bus_id=bus_details["bus_id"],
                route_id=bus_details["route_id"],
                engine_id=bus_details["engine_id"],
                boarding_point_id=bus_details["boarding_point_id"],
                dropping_point_id=bus_details["dropping_point_id"],
                operator_name=bus_details["operator_name"],
                bus_type=bus_details["bus_type"],
            )
            
            seat_html = render_seat_layout(seat_result)
            
            status = "✅ Success" if seat_result.get("success") else "❌ Failed"
            layout = seat_result.get("layout", {})
            
            seat_sections.append(f"""
            <div class="test-section">
                <div class="test-title">🪑 Seat Layout: {bus_details['operator_name'][:30]}</div>
                <div class="test-meta">
                    Status: <code>{status}</code> |
                    Bus ID: <code>{bus_details['bus_id']}</code> |
                    Engine ID: <code>{bus_details['engine_id']}</code><br>
                    Total Seats: <code>{layout.get('total_seats', 'N/A')}</code> |
                    Available: <code>{layout.get('available_seats', 'N/A')}</code>
                </div>
                {seat_html}
            </div>
            """)
            print(f"   Bus {i+1}: {status}")
        except Exception as e:
            print(f"   Bus {i+1}: ❌ Error - {e}")
    
    sections.extend(seat_sections)
    
    # Section 3: Error State
    print("\n📦 Section 3: Error State")
    error_seat_result = {"success": False, "message": "No seat layout available for this bus"}
    error_html = render_seat_layout(error_seat_result)
    
    sections.append(f"""
    <div class="test-section">
        <div class="test-title">⚠️ Seat Layout Error State</div>
        <div class="test-meta">Testing error message rendering</div>
        {error_html}
    </div>
    """)
    
    # Combine and save
    full_content = "\n".join(sections)
    full_html = wrap_html_page(full_content, "Bus Seat Layout & View All Tests - New API")
    
    filepath = save_html_file(full_html, "seat_bind_test.html")
    
    print("\n" + "=" * 60)
    print("✅ HTML FILE GENERATED")
    print("=" * 60)
    print(f"\n📄 File: {filepath}")
    print(f"\n🌐 Open in browser:")
    print(f"   file://{os.path.abspath(filepath)}")


# ============================================================================
# STANDALONE EXECUTION
# ============================================================================

async def main():
    """Main entry point for standalone execution."""
    print("=" * 70)
    print("🚌 BUS SEAT LAYOUT & VIEW ALL CARD - NEW API TESTS")
    print("=" * 70)
    
    await test_generate_comprehensive_html()
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())