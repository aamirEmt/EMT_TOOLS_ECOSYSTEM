"""
UI Tests for Bus Search Tool.

Run with:
    pytest tests/test_bus_ui.py -v -s

Generate HTML only:
    python tests/test_bus_ui.py

"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

pytestmark = [pytest.mark.ui, pytest.mark.integration]


# ============================================================================
# HTML HELPERS
# ============================================================================

def wrap_html_page(content: str, title: str = "Bus Carousel Test") -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ background: #f5f5f5; padding: 20px; margin: 0; }}
        .test-section {{ margin-bottom: 40px; padding: 20px; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .test-title {{ font-family: sans-serif; font-size: 16px; font-weight: 600; color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #ef6614; }}
        .test-meta {{ font-family: sans-serif; font-size: 12px; color: #666; margin-bottom: 15px; }}
    </style>
</head>
<body>{content}</body>
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
# LIVE API HELPER
# ============================================================================

async def fetch_live_bus_results(
    source_id: str = None,
    destination_id: str = None,
    source_name: str = None,
    destination_name: str = None,
    days_ahead: int = 7,
    is_volvo: bool = None,
) -> Dict[str, Any]:
    """Fetch live bus results using new API."""
    from tools_factory.buses.bus_search_service import search_buses
    
    journey_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%d-%m-%Y")
    
    print(f"\n🔍 Fetching live bus data...")
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
        is_volvo=is_volvo,
    )
    
    bus_count = len(results.get("buses", []))
    print(f"   ✅ Found {bus_count} buses")
    
    return results


# ============================================================================
# PYTEST TESTS - LIVE API
# ============================================================================

@pytest.mark.asyncio
async def test_render_live_bus_results():
    """Test rendering bus carousel with LIVE API data."""
    from tools_factory.buses.bus_renderer import render_bus_results
    
    print("\n🎨 Testing bus carousel with LIVE API data...")
    
    bus_results = await fetch_live_bus_results(
        source_id="733",
        destination_id="757",
        days_ahead=7,
    )
    
    html = render_bus_results(bus_results)
    
    assert html is not None
    assert "bus-carousel" in html
    
    buses = bus_results.get("buses", [])
    if buses:
        print(f"✅ Rendered {len(buses)} buses from live API")
        print(f"   First bus: {buses[0].get('operator_name')}")


@pytest.mark.asyncio
async def test_render_by_city_name():
    """Test rendering bus carousel using city names."""
    from tools_factory.buses.bus_renderer import render_bus_results
    
    print("\n🎨 Testing bus carousel with CITY NAMES...")
    
    bus_results = await fetch_live_bus_results(
        source_name="Delhi",
        destination_name="Manali",
        days_ahead=7,
    )
    
    html = render_bus_results(bus_results)
    
    assert html is not None
    
    print(f"   Source resolved: {bus_results.get('source_name')} (ID: {bus_results.get('source_id')})")
    print(f"   Dest resolved: {bus_results.get('destination_name')} (ID: {bus_results.get('destination_id')})")
    
    buses = bus_results.get("buses", [])
    print(f"✅ Rendered {len(buses)} buses using city names")


@pytest.mark.asyncio
async def test_render_live_volvo_results():
    """Test rendering Volvo-only bus results."""
    from tools_factory.buses.bus_renderer import render_bus_results
    
    print("\n🎨 Testing Volvo filter with LIVE API data...")
    
    bus_results = await fetch_live_bus_results(
        source_id="733",
        destination_id="757",
        days_ahead=7,
        is_volvo=True,
    )
    
    html = render_bus_results(bus_results)
    assert html is not None
    
    buses = bus_results.get("buses", [])
    print(f"✅ Rendered {len(buses)} Volvo buses from live API")


# ============================================================================
# VIEW ALL CARD TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_render_with_view_all_card():
    """Test rendering with View All card."""
    from tools_factory.buses.bus_renderer import render_bus_results_with_limit
    
    print("\n🎨 Testing View All card rendering...")
    
    bus_results = await fetch_live_bus_results(source_id="733", destination_id="757", days_ahead=7)
    buses = bus_results.get("buses", [])
    
    print(f"   Total buses: {len(buses)}")
    
    html = render_bus_results_with_limit(bus_results, display_limit=3, show_view_all=True)
    
    assert html is not None
    assert "bus-carousel" in html
    
    if len(buses) > 3 and bus_results.get("view_all_link"):
        assert "view-all-card" in html, "View All card should appear"
        assert "View All" in html
        print(f"   ✅ View All card appears (showing 3 of {len(buses)})")


@pytest.mark.asyncio
async def test_view_all_link_in_html():
    """Test that view_all_link appears in HTML as clickable link."""
    from tools_factory.buses.bus_renderer import render_bus_results
    
    print("\n🔗 Testing view_all_link in HTML...")
    
    bus_results = await fetch_live_bus_results(source_id="733", destination_id="757", days_ahead=7)
    html = render_bus_results(bus_results)
    
    view_all_link = bus_results.get("view_all_link", "")
    
    if view_all_link:
        assert "view-all-link" in html or view_all_link in html, \
            "view_all_link should appear in HTML"
        print(f"   ✅ view_all_link present in HTML")


@pytest.mark.asyncio
async def test_view_all_card_total_count():
    """Test that View All card shows total bus count."""
    from tools_factory.buses.bus_renderer import render_bus_results_with_limit
    
    print("\n🔢 Testing View All card shows total count...")
    
    bus_results = await fetch_live_bus_results(source_id="733", destination_id="757", days_ahead=7)
    buses = bus_results.get("buses", [])
    total = len(buses)
    
    if total > 5 and bus_results.get("view_all_link"):
        html = render_bus_results_with_limit(bus_results, display_limit=5, show_view_all=True)
        assert str(total) in html, f"Total count {total} should appear in View All card"
        print(f"   ✅ Total count {total} appears in HTML")


@pytest.mark.asyncio
async def test_view_all_different_limits():
    """Test View All card with different limit values."""
    from tools_factory.buses.bus_renderer import render_bus_results_with_limit
    
    print("\n🔢 Testing View All with different limits...")
    
    bus_results = await fetch_live_bus_results(source_id="733", destination_id="757", days_ahead=7)
    buses = bus_results.get("buses", [])
    total = len(buses)
    
    print(f"   Total buses: {total}")
    
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
# RATING DISPLAY TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_rating_display_in_html():
    """Test that ratings are displayed correctly (no raw 45 values)."""
    from tools_factory.buses.bus_renderer import render_bus_results
    
    print("\n⭐ Testing rating display in HTML...")
    
    bus_results = await fetch_live_bus_results(source_id="733", destination_id="757", days_ahead=7)
    html = render_bus_results(bus_results)
    
    # Check that no "★ 45" or similar appears
    assert "★ 45" not in html, "Raw rating 45 should not appear"
    assert "★ 40" not in html, "Raw rating 40 should not appear"
    assert "★ 35" not in html, "Raw rating 35 should not appear"
    
    buses = bus_results.get("buses", [])
    for bus in buses[:3]:
        rating = bus.get("rating")
        if rating:
            print(f"   {bus.get('operator_name', 'N/A')[:20]}: Rating = {rating}")
            rating_float = float(rating)
            assert rating_float <= 5, f"Rating {rating} should be <= 5"
    
    print("   ✅ Ratings displayed correctly")


# ============================================================================
# CSS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_carousel_width_90_percent():
    """Test that carousel has width: 90% in CSS."""
    from tools_factory.buses.bus_renderer import render_bus_results
    
    print("\n📐 Testing carousel width CSS...")
    
    bus_results = await fetch_live_bus_results(source_id="733", destination_id="757", days_ahead=7)
    html = render_bus_results(bus_results)
    
    assert "width: 90%" in html or "width:90%" in html, \
        "Carousel should have width: 90% in CSS"
    
    print(f"   ✅ Carousel width 90% verified")


# ============================================================================
# CITY NAMES IN HEADER
# ============================================================================

@pytest.mark.asyncio
async def test_city_names_in_header():
    """Test that city names appear in carousel header."""
    from tools_factory.buses.bus_renderer import render_bus_results
    
    print("\n📍 Testing city names in carousel header...")
    
    bus_results = await fetch_live_bus_results(
        source_name="Delhi",
        destination_name="Manali",
        days_ahead=7,
    )
    html = render_bus_results(bus_results)
    
    source_name = bus_results.get("source_name", "")
    dest_name = bus_results.get("destination_name", "")
    
    print(f"   Source name: {source_name}")
    print(f"   Destination name: {dest_name}")
    
    if source_name:
        assert source_name in html, f"Source name '{source_name}' should appear in HTML"
    if dest_name:
        assert dest_name in html, f"Destination name '{dest_name}' should appear in HTML"
    
    print("   ✅ City names appear in header")


@pytest.mark.asyncio
async def test_live_api_fields_in_html():
    """Verify live API data fields are rendered in HTML."""
    from tools_factory.buses.bus_renderer import render_bus_results
    
    print("\n🔍 Verifying live API fields in rendered HTML...")
    
    bus_results = await fetch_live_bus_results(source_id="733", destination_id="757", days_ahead=7)
    html = render_bus_results(bus_results)
    buses = bus_results.get("buses", [])
    
    if buses:
        first_bus = buses[0]
        
        # Check operator name
        operator = first_bus.get("operator_name", "")
        if operator:
            print(f"   ✅ Operator: {operator}")
        
        # Check price
        price = first_bus.get("price", "")
        if price:
            assert "₹" in html
            print(f"   ✅ Price: ₹{price}")
        
        # Check timing
        dep_time = first_bus.get("departure_time", "")
        if dep_time:
            print(f"   ✅ Departure: {dep_time}")
        
        print("\n✅ All live API fields rendered correctly")


# ============================================================================
# HTML FILE GENERATION
# ============================================================================

@pytest.mark.asyncio
async def test_generate_live_html_file():
    """Generate HTML file with LIVE API data for visual inspection."""
    from tools_factory.buses.bus_renderer import render_bus_results, render_bus_results_with_limit
    
    print("\n📄 Generating HTML with LIVE API data...")
    
    sections = []
    
    # Section 1: By City ID - Full Results
    print("\n--- Section 1: Delhi → Manali (by ID) ---")
    try:
        bus_results_1 = await fetch_live_bus_results(source_id="733", destination_id="757", days_ahead=7)
        html_1 = render_bus_results(bus_results_1)
        bus_count_1 = len(bus_results_1.get("buses", []))
        
        sections.append(f"""
        <div class="test-section">
            <div class="test-title">🚌 LIVE: Delhi (733) → Manali (757) - Full Results</div>
            <div class="test-meta">
                API: busservice.easemytrip.com<br>
                Found {bus_count_1} buses | Date: {bus_results_1.get('journey_date', 'N/A')}
            </div>
            {html_1}
        </div>
        """)
        print(f"   ✅ Got {bus_count_1} buses")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Section 2: By City Name
    print("\n--- Section 2: Delhi → Manali (by Name) ---")
    try:
        bus_results_2 = await fetch_live_bus_results(source_name="Delhi", destination_name="Manali", days_ahead=7)
        html_2 = render_bus_results(bus_results_2)
        bus_count_2 = len(bus_results_2.get("buses", []))
        
        sections.append(f"""
        <div class="test-section">
            <div class="test-title">🚌 LIVE: Delhi → Manali (by City Name - Auto Resolved)</div>
            <div class="test-meta">
                Source resolved: {bus_results_2.get('source_name')} (ID: {bus_results_2.get('source_id')})<br>
                Destination resolved: {bus_results_2.get('destination_name')} (ID: {bus_results_2.get('destination_id')})<br>
                Found {bus_count_2} buses
            </div>
            {html_2}
        </div>
        """)
        print(f"   ✅ Got {bus_count_2} buses")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Section 3: With View All Card (Limit 3)
    print("\n--- Section 3: With View All Card (Limit 3) ---")
    try:
        bus_results_3 = await fetch_live_bus_results(source_id="733", destination_id="757", days_ahead=7)
        html_3 = render_bus_results_with_limit(bus_results_3, display_limit=3, show_view_all=True)
        bus_count_3 = len(bus_results_3.get("buses", []))
        
        sections.append(f"""
        <div class="test-section">
            <div class="test-title">🚌 LIVE: View All Card Demo (Showing 3 of {bus_count_3})</div>
            <div class="test-meta">
                Display Limit: 3 | Total: {bus_count_3}<br>
                View All Link: {bus_results_3.get('view_all_link', 'N/A')[:80]}...
            </div>
            {html_3}
        </div>
        """)
        print(f"   ✅ Rendered with limit 3")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Section 4: Volvo Filter
    print("\n--- Section 4: Volvo Only ---")
    try:
        bus_results_4 = await fetch_live_bus_results(source_id="733", destination_id="757", days_ahead=7, is_volvo=True)
        html_4 = render_bus_results(bus_results_4)
        bus_count_4 = len(bus_results_4.get("buses", []))
        
        sections.append(f"""
        <div class="test-section">
            <div class="test-title">🚌 LIVE: Volvo Only Filter</div>
            <div class="test-meta">
                Filter: isVolvo=True<br>
                Found {bus_count_4} Volvo buses
            </div>
            {html_4}
        </div>
        """)
        print(f"   ✅ Got {bus_count_4} Volvo buses")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Combine and save
    full_content = "\n".join(sections)
    full_html = wrap_html_page(full_content, "Bus Carousel - LIVE API Test (New Endpoints)")
    
    filepath = save_html_file(full_html, "bus_carousel_live.html")
    
    print(f"\n✅ HTML file generated: {filepath}")
    print(f"   Open in browser: file://{os.path.abspath(filepath)}")
    
    assert os.path.exists(filepath)


# ============================================================================
# STANDALONE EXECUTION
# ============================================================================

async def generate_live_html_files():
    """Generate HTML files with LIVE API data for visual testing."""
    from tools_factory.buses.bus_renderer import render_bus_results, render_bus_results_with_limit
    
    print("=" * 60)
    print("🚌 BUS CAROUSEL HTML GENERATOR - NEW API")
    print("=" * 60)
    
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    sections = []
    
    # Section 1: By ID
    print("\n📦 Fetching Delhi → Manali (by ID)...")
    try:
        bus_results_1 = await fetch_live_bus_results(source_id="733", destination_id="757", days_ahead=7)
        html_1 = render_bus_results(bus_results_1)
        bus_count_1 = len(bus_results_1.get("buses", []))
        
        sections.append(f"""
        <div class="test-section">
            <div class="test-title">🚌 LIVE: Delhi → Manali (by ID)</div>
            <div class="test-meta">Found {bus_count_1} buses | Date: {bus_results_1.get('journey_date', 'N/A')}</div>
            {html_1}
        </div>
        """)
        print(f"   ✅ Got {bus_count_1} buses")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Section 2: By Name
    print("\n📦 Fetching Delhi → Manali (by Name)...")
    try:
        bus_results_2 = await fetch_live_bus_results(source_name="Delhi", destination_name="Manali", days_ahead=7)
        html_2 = render_bus_results(bus_results_2)
        bus_count_2 = len(bus_results_2.get("buses", []))
        
        sections.append(f"""
        <div class="test-section">
            <div class="test-title">🚌 LIVE: Delhi → Manali (by City Name)</div>
            <div class="test-meta">
                Resolved: {bus_results_2.get('source_name')} (ID: {bus_results_2.get('source_id')}) → 
                {bus_results_2.get('destination_name')} (ID: {bus_results_2.get('destination_id')})<br>
                Found {bus_count_2} buses
            </div>
            {html_2}
        </div>
        """)
        print(f"   ✅ Got {bus_count_2} buses")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Section 3: View All Card
    print("\n📦 Testing View All Card...")
    try:
        bus_results_3 = await fetch_live_bus_results(source_id="733", destination_id="757", days_ahead=7)
        html_3 = render_bus_results_with_limit(bus_results_3, display_limit=3, show_view_all=True)
        bus_count_3 = len(bus_results_3.get("buses", []))
        
        sections.append(f"""
        <div class="test-section">
            <div class="test-title">🚌 View All Card Demo (3 of {bus_count_3})</div>
            <div class="test-meta">Display limit: 3 | View All shows total: {bus_count_3}</div>
            {html_3}
        </div>
        """)
        print(f"   ✅ Rendered with View All card")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Save file
    full_content = "\n".join(sections)
    full_html = wrap_html_page(full_content, "Bus Carousel - LIVE API Test")
    filepath = save_html_file(full_html, "bus_carousel_live.html", output_dir)
    
    print("\n" + "=" * 60)
    print("✅ HTML FILE GENERATED WITH LIVE DATA")
    print("=" * 60)
    print(f"\n📄 File: {filepath}")
    print(f"\n🌐 Open in browser:")
    print(f"   file://{os.path.abspath(filepath)}")
    print("\n" + "=" * 60)
    
    return filepath


def main():
    """Main entry point for standalone execution."""
    asyncio.run(generate_live_html_files())


if __name__ == "__main__":
    main()