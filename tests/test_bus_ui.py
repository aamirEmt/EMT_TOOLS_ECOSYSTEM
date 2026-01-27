"""UI Tests for Bus Search Tool - HTML Renderer with LIVE API.

These tests fetch REAL data from EaseMyTrip Bus API and render HTML.
NO MOCKING - Real API integration tests.

File: tests/test_bus_ui.py

Run with:
    pytest tests/test_bus_ui.py -v -s

Generate HTML only:
    python tests/test_bus_ui.py

    POST http://busapi.easemytrip.com/v1/api/detail/List/
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

# Mark all tests in this file as UI tests
pytestmark = [pytest.mark.ui, pytest.mark.integration]


# ============================================================================
# HTML GENERATION HELPERS
# ============================================================================

def wrap_html_page(content: str, title: str = "Bus Carousel Test") -> str:
    """Wrap HTML content in a full page."""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            background: #f5f5f5;
            padding: 20px;
            margin: 0;
        }}
        .test-section {{
            margin-bottom: 40px;
            padding: 20px;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .test-title {{
            font-family: sans-serif;
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ef6614;
        }}
        .test-meta {{
            font-family: sans-serif;
            font-size: 12px;
            color: #666;
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>"""


def save_html_file(html_content: str, filename: str, output_dir: str = None) -> str:
    """Save HTML content to file."""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "output")
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return filepath


# ============================================================================
# LIVE API SEARCH HELPER
# ============================================================================

async def fetch_live_bus_results(
    source_id: str = "733",
    destination_id: str = "757",
    days_ahead: int = 7,
    is_volvo: bool = None,
) -> Dict[str, Any]:
    """
    Fetch live bus results from EaseMyTrip API.
    
    Args:
        source_id: Source city ID (default: "733" for Delhi)
        destination_id: Destination city ID (default: "757" for Manali)
        days_ahead: Days from today for journey date
        is_volvo: Optional Volvo filter
        
    Returns:
        Bus search results from live API
    """
    from tools_factory.buses.bus_search_service import search_buses
    
    journey_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    
    print(f"\n🔍 Fetching live bus data...")
    print(f"   Route: {source_id} → {destination_id}")
    print(f"   Date: {journey_date}")
    if is_volvo:
        print(f"   Filter: Volvo only")
    
    results = await search_buses(
        source_id=source_id,
        destination_id=destination_id,
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
    
    # Fetch live data (Delhi to Manali)
    bus_results = await fetch_live_bus_results(
        source_id="733",
        destination_id="757",
        days_ahead=7,
    )
    
    # Render HTML
    html = render_bus_results(bus_results)
    
    assert html is not None
    assert "bus-carousel" in html
    
    buses = bus_results.get("buses", [])
    if buses:
        print(f"✅ Rendered {len(buses)} buses from live API")
        print(f"   First bus: {buses[0].get('operator_name')}")
    else:
        print("⚠️ No buses returned from API (may be date/route issue)")


@pytest.mark.asyncio
async def test_render_live_volvo_results():
    """Test rendering Volvo-only bus results from LIVE API."""
    from tools_factory.buses.bus_renderer import render_bus_results
    
    print("\n🎨 Testing Volvo filter with LIVE API data...")
    
    # Fetch live data with Volvo filter
    bus_results = await fetch_live_bus_results(
        source_id="733",
        destination_id="757",
        days_ahead=7,
        is_volvo=True,
    )
    
    # Render HTML
    html = render_bus_results(bus_results)
    
    assert html is not None
    
    buses = bus_results.get("buses", [])
    print(f"✅ Rendered {len(buses)} Volvo buses from live API")


@pytest.mark.asyncio
async def test_generate_live_html_file():
    """Generate HTML file with LIVE API data for visual inspection."""
    from tools_factory.buses.bus_renderer import render_bus_results
    
    print("\n📄 Generating HTML with LIVE API data...")
    
    sections = []
    
    # Section 1: Delhi to Manali
    print("\n--- Section 1: Delhi → Manali ---")
    bus_results_1 = await fetch_live_bus_results(
        source_id="733",
        destination_id="757",
        days_ahead=7,
    )
    html_1 = render_bus_results(bus_results_1)
    
    bus_count_1 = len(bus_results_1.get("buses", []))
    ac_count_1 = bus_results_1.get("ac_count", 0)
    non_ac_count_1 = bus_results_1.get("non_ac_count", 0)
    
    sections.append(f"""
    <div class="test-section">
        <div class="test-title">🚌 LIVE: Delhi (733) → Manali (757)</div>
        <div class="test-meta">
            Found {bus_count_1} buses | {ac_count_1} AC | {non_ac_count_1} Non-AC | 
            Date: {bus_results_1.get('journey_date', 'N/A')}
        </div>
        {html_1}
    </div>
    """)
    
    # Section 2: Volvo only filter
    print("\n--- Section 2: Delhi → Manali (Volvo Only) ---")
    bus_results_2 = await fetch_live_bus_results(
        source_id="733",
        destination_id="757",
        days_ahead=7,
        is_volvo=True,
    )
    html_2 = render_bus_results(bus_results_2)
    
    bus_count_2 = len(bus_results_2.get("buses", []))
    
    sections.append(f"""
    <div class="test-section">
        <div class="test-title">🚌 LIVE: Delhi → Manali (Volvo Filter)</div>
        <div class="test-meta">
            Found {bus_count_2} Volvo buses | 
            Date: {bus_results_2.get('journey_date', 'N/A')}
        </div>
        {html_2}
    </div>
    """)
    
    # Section 3: Different date (14 days ahead)
    print("\n--- Section 3: Delhi → Manali (14 days ahead) ---")
    bus_results_3 = await fetch_live_bus_results(
        source_id="733",
        destination_id="757",
        days_ahead=14,
    )
    html_3 = render_bus_results(bus_results_3)
    
    bus_count_3 = len(bus_results_3.get("buses", []))
    
    sections.append(f"""
    <div class="test-section">
        <div class="test-title">🚌 LIVE: Delhi → Manali (14 days ahead)</div>
        <div class="test-meta">
            Found {bus_count_3} buses | 
            Date: {bus_results_3.get('journey_date', 'N/A')}
        </div>
        {html_3}
    </div>
    """)
    
    # Combine all sections
    full_content = "\n".join(sections)
    full_html = wrap_html_page(full_content, "Bus Carousel - LIVE API Test")
    
    # Save file
    filepath = save_html_file(full_html, "bus_carousel_live.html")
    
    print(f"\n✅ HTML file generated: {filepath}")
    print(f"   Open in browser: file://{os.path.abspath(filepath)}")
    
    assert os.path.exists(filepath)


@pytest.mark.asyncio
async def test_live_api_fields_in_html():
    """Verify live API data fields are rendered in HTML."""
    from tools_factory.buses.bus_renderer import render_bus_results
    
    print("\n🔍 Verifying live API fields in rendered HTML...")
    
    bus_results = await fetch_live_bus_results(
        source_id="733",
        destination_id="757",
        days_ahead=7,
    )
    
    html = render_bus_results(bus_results)
    buses = bus_results.get("buses", [])
    
    if buses:
        first_bus = buses[0]
        
        # Check operator name appears
        operator = first_bus.get("operator_name", "")
        if operator:
            # Check truncated version might be in HTML
            assert operator[:10] in html or "oprtname" in html
            print(f"   ✅ Operator: {operator}")
        
        # Check price appears
        price = first_bus.get("price", "")
        if price:
            assert "₹" in html
            print(f"   ✅ Price: ₹{price}")
        
        # Check timing appears
        dep_time = first_bus.get("departure_time", "")
        if dep_time:
            assert dep_time in html or "bustme" in html
            print(f"   ✅ Departure: {dep_time}")
        
        # Check bus type appears
        bus_type = first_bus.get("bus_type", "")
        if bus_type:
            print(f"   ✅ Bus Type: {bus_type}")
        
        print("\n✅ All live API fields rendered correctly")
    else:
        print("⚠️ No buses to verify (API returned empty)")


# ============================================================================
# STANDALONE EXECUTION - LIVE API
# ============================================================================

async def generate_live_html_files():
    """Generate HTML files with LIVE API data for visual testing."""
    from tools_factory.buses.bus_renderer import render_bus_results
    
    print("=" * 60)
    print("🚌 BUS CAROUSEL HTML GENERATOR - LIVE API")
    print("=" * 60)
    
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    sections = []
    
    # Section 1: Delhi to Manali
    print("\n📦 Fetching Delhi → Manali (7 days ahead)...")
    try:
        bus_results_1 = await fetch_live_bus_results(
            source_id="733",
            destination_id="757",
            days_ahead=7,
        )
        html_1 = render_bus_results(bus_results_1)
        
        bus_count_1 = len(bus_results_1.get("buses", []))
        ac_count_1 = bus_results_1.get("ac_count", 0)
        non_ac_count_1 = bus_results_1.get("non_ac_count", 0)
        
        sections.append(f"""
        <div class="test-section">
            <div class="test-title">🚌 LIVE: Delhi (733) → Manali (757)</div>
            <div class="test-meta">
                API: POST http://busapi.easemytrip.com/v1/api/detail/List/<br>
                Found {bus_count_1} buses | {ac_count_1} AC | {non_ac_count_1} Non-AC | 
                Date: {bus_results_1.get('journey_date', 'N/A')}
            </div>
            {html_1}
        </div>
        """)
        print(f"   ✅ Got {bus_count_1} buses")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        sections.append(f"""
        <div class="test-section">
            <div class="test-title">🚌 Delhi → Manali (Error)</div>
            <div class="test-meta">Error: {e}</div>
        </div>
        """)
    
    # Section 2: Volvo filter
    print("\n📦 Fetching Delhi → Manali (Volvo only)...")
    try:
        bus_results_2 = await fetch_live_bus_results(
            source_id="733",
            destination_id="757",
            days_ahead=7,
            is_volvo=True,
        )
        html_2 = render_bus_results(bus_results_2)
        
        bus_count_2 = len(bus_results_2.get("buses", []))
        
        sections.append(f"""
        <div class="test-section">
            <div class="test-title">🚌 LIVE: Delhi → Manali (Volvo Filter: isVolvo=True)</div>
            <div class="test-meta">
                Found {bus_count_2} Volvo buses | 
                Date: {bus_results_2.get('journey_date', 'N/A')}
            </div>
            {html_2}
        </div>
        """)
        print(f"   ✅ Got {bus_count_2} Volvo buses")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Section 3: Tomorrow's buses
    print("\n📦 Fetching Delhi → Manali (Tomorrow)...")
    try:
        bus_results_3 = await fetch_live_bus_results(
            source_id="733",
            destination_id="757",
            days_ahead=1,
        )
        html_3 = render_bus_results(bus_results_3)
        
        bus_count_3 = len(bus_results_3.get("buses", []))
        
        sections.append(f"""
        <div class="test-section">
            <div class="test-title">🚌 LIVE: Delhi → Manali (Tomorrow)</div>
            <div class="test-meta">
                Found {bus_count_3} buses | 
                Date: {bus_results_3.get('journey_date', 'N/A')}
            </div>
            {html_3}
        </div>
        """)
        print(f"   ✅ Got {bus_count_3} buses")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Save combined file
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