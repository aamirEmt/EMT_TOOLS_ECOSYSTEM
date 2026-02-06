"""
Quick script to test PNR Status UI with real API data
Tests PNR status check with HTML rendering

File: tests/test_pnr_status_ui.py

Run with:
    pytest tests/test_pnr_status_ui.py -v -s
"""

import pytest
from tools_factory.trains.Train_PnrStatus.pnr_status_tool import TrainPnrStatusTool


@pytest.mark.asyncio
async def test_pnr_status_ui_basic():
    """Test PNR status UI rendering with a sample PNR."""
    tool = TrainPnrStatusTool()

    # Sample PNR number (may or may not be valid in the system)
    pnr_number = "2611143617"

    print(f"\n[UI TEST] Testing PNR status UI for: {pnr_number}")

    result = await tool.execute(
        pnrNumber=pnr_number,
        _user_type="website",
        _limit=1
    )

    print(f"   Response: {result.response_text}")
    print(f"   Is Error: {result.is_error}")

    if not result.is_error:
        assert result.html is not None, "Should have HTML for website user"

        # Verify HTML contains expected elements
        html = result.html
        assert "pnr-status-card" in html, "HTML should have pnr-status-card class"
        assert "pnr-header" in html, "HTML should have pnr-header"
        assert "passenger-table" in html, "HTML should have passenger-table"

        # Save HTML for manual inspection
        with open("pnr_status_ui_basic.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\n[UI TEST] HTML saved to: pnr_status_ui_basic.html")

        # Print structured data
        if result.structured_content and "pnr_info" in result.structured_content:
            pnr_info = result.structured_content["pnr_info"]
            print(f"\n[UI TEST] PNR Info:")
            print(f"   Train: {pnr_info.get('train_name')} ({pnr_info.get('train_number')})")
            print(f"   Date: {pnr_info.get('date_of_journey')}")
            print(f"   Route: {pnr_info.get('source_station_name')} -> {pnr_info.get('destination_station_name')}")
            print(f"   Class: {pnr_info.get('class_name') or pnr_info.get('journey_class')}")
            print(f"   Chart: {pnr_info.get('chart_status')}")
            print(f"   Passengers: {len(pnr_info.get('passengers', []))}")
    else:
        print(f"\n[UI TEST] API returned error - this is expected for invalid/expired PNR")
        print(f"   Error: {result.response_text}")


@pytest.mark.asyncio
async def test_pnr_status_ui_passenger_display():
    """Test that passenger details are correctly displayed in UI."""
    tool = TrainPnrStatusTool()

    pnr_number = "2611143617"

    print(f"\n[UI TEST] Testing passenger display for PNR: {pnr_number}")

    result = await tool.execute(
        pnrNumber=pnr_number,
        _user_type="website",
        _limit=1
    )

    if not result.is_error and result.structured_content:
        pnr_info = result.structured_content.get("pnr_info", {})
        passengers = pnr_info.get("passengers", [])

        print(f"\n   Found {len(passengers)} passengers:")

        for p in passengers:
            print(f"\n   Passenger {p.get('serial_number')}:")
            print(f"      Booking Status: {p.get('booking_status')}")
            print(f"      Current Status: {p.get('current_status')}")
            print(f"      Coach: {p.get('coach')}")
            print(f"      Berth: {p.get('berth_number')}")
            print(f"      Berth Type: {p.get('berth_type')}")

        # Check HTML contains passenger rows
        if result.html:
            for p in passengers:
                serial = str(p.get('serial_number'))
                booking_status = p.get('booking_status')

                # HTML should contain passenger info
                assert serial in result.html or f"P{serial}" in result.html, \
                    f"HTML should contain passenger serial number {serial}"

                if booking_status and booking_status != "N/A":
                    assert booking_status in result.html, \
                        f"HTML should contain booking status {booking_status}"

            print(f"\n[UI TEST] Passenger display verified in HTML")

            # Save HTML
            with open("pnr_status_ui_passengers.html", "w", encoding="utf-8") as f:
                f.write(result.html)
            print(f"[UI TEST] HTML saved to: pnr_status_ui_passengers.html")
    else:
        print(f"   API Error or no data: {result.response_text}")


@pytest.mark.asyncio
async def test_pnr_status_ui_status_colors():
    """Test that different statuses have correct CSS classes."""
    tool = TrainPnrStatusTool()

    pnr_number = "2611143617"

    print(f"\n[UI TEST] Testing status color classes for PNR: {pnr_number}")

    result = await tool.execute(
        pnrNumber=pnr_number,
        _user_type="website",
        _limit=1
    )

    if not result.is_error and result.html:
        html = result.html

        # Check for status CSS classes in HTML
        status_classes = [
            "status-confirmed",
            "status-waitlist",
            "status-rac",
            "status-cancelled",
            "status-nosb",
        ]

        found_classes = []
        for cls in status_classes:
            if cls in html:
                found_classes.append(cls)

        print(f"   Status classes found in HTML: {found_classes}")

        # Check chart status badge
        assert "chart-badge" in html, "HTML should have chart status badge"
        if "prepared" in html.lower():
            print(f"   Chart badge: prepared or not-prepared class present")

        # Save HTML for visual inspection
        with open("pnr_status_ui_colors.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\n[UI TEST] HTML saved to: pnr_status_ui_colors.html")
        print(f"   Open file to verify status colors visually")
    else:
        print(f"   API Error: {result.response_text}")


@pytest.mark.asyncio
async def test_pnr_status_ui_train_info():
    """Test that train information is correctly displayed."""
    tool = TrainPnrStatusTool()

    pnr_number = "2611143617"

    print(f"\n[UI TEST] Testing train info display for PNR: {pnr_number}")

    result = await tool.execute(
        pnrNumber=pnr_number,
        _user_type="website",
        _limit=1
    )

    if not result.is_error and result.structured_content:
        pnr_info = result.structured_content.get("pnr_info", {})

        # Check train info fields
        train_number = pnr_info.get("train_number", "")
        train_name = pnr_info.get("train_name", "")
        journey_date = pnr_info.get("date_of_journey", "")

        print(f"\n   Train Info:")
        print(f"      Number: {train_number}")
        print(f"      Name: {train_name}")
        print(f"      Journey Date: {journey_date}")

        if result.html:
            html = result.html

            # Verify train info appears in HTML
            if train_number:
                assert train_number in html, f"Train number {train_number} should be in HTML"
            if train_name:
                assert train_name in html, f"Train name {train_name} should be in HTML"
            if journey_date:
                assert journey_date in html, f"Journey date {journey_date} should be in HTML"

            print(f"\n   Train info verified in HTML")

            # Save HTML
            with open("pnr_status_ui_train_info.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[UI TEST] HTML saved to: pnr_status_ui_train_info.html")
    else:
        print(f"   API Error: {result.response_text}")


@pytest.mark.asyncio
async def test_pnr_status_ui_route_display():
    """Test that route (source to destination) is correctly displayed."""
    tool = TrainPnrStatusTool()

    pnr_number = "2611143617"

    print(f"\n[UI TEST] Testing route display for PNR: {pnr_number}")

    result = await tool.execute(
        pnrNumber=pnr_number,
        _user_type="website",
        _limit=1
    )

    if not result.is_error and result.structured_content:
        pnr_info = result.structured_content.get("pnr_info", {})

        source = pnr_info.get("source_station", "")
        source_name = pnr_info.get("source_station_name", "")
        dest = pnr_info.get("destination_station", "")
        dest_name = pnr_info.get("destination_station_name", "")

        print(f"\n   Route Info:")
        print(f"      From: {source_name} ({source})")
        print(f"      To: {dest_name} ({dest})")

        if result.html:
            html = result.html

            # Verify route info in HTML
            if source:
                assert source in html, f"Source station code {source} should be in HTML"
            if dest:
                assert dest in html, f"Destination station code {dest} should be in HTML"

            # Check for route arrow
            assert "route-arrow" in html or "&#8594;" in html or "->" in html, \
                "HTML should have route arrow indicator"

            print(f"\n   Route display verified in HTML")

            # Save HTML
            with open("pnr_status_ui_route.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[UI TEST] HTML saved to: pnr_status_ui_route.html")
    else:
        print(f"   API Error: {result.response_text}")


@pytest.mark.asyncio
async def test_pnr_status_ui_class_quota_chips():
    """Test that class and quota are displayed as info chips."""
    tool = TrainPnrStatusTool()

    pnr_number = "2611143617"

    print(f"\n[UI TEST] Testing class/quota chips for PNR: {pnr_number}")

    result = await tool.execute(
        pnrNumber=pnr_number,
        _user_type="website",
        _limit=1
    )

    if not result.is_error and result.structured_content:
        pnr_info = result.structured_content.get("pnr_info", {})

        journey_class = pnr_info.get("journey_class", "")
        class_name = pnr_info.get("class_name", "")
        quota = pnr_info.get("quota", "")
        quota_name = pnr_info.get("quota_name", "")

        print(f"\n   Class/Quota Info:")
        print(f"      Class: {class_name or journey_class}")
        print(f"      Quota: {quota_name or quota}")

        if result.html:
            html = result.html

            # Check for info-chip class
            assert "info-chip" in html, "HTML should have info-chip elements"

            # Verify class and quota appear
            if journey_class:
                assert journey_class in html, f"Journey class {journey_class} should be in HTML"
            if quota:
                assert quota in html, f"Quota {quota} should be in HTML"

            print(f"\n   Class/quota chips verified in HTML")

            # Save HTML
            with open("pnr_status_ui_chips.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[UI TEST] HTML saved to: pnr_status_ui_chips.html")
    else:
        print(f"   API Error: {result.response_text}")


@pytest.mark.asyncio
async def test_pnr_status_ui_fare_display():
    """Test that fare information is displayed when available."""
    tool = TrainPnrStatusTool()

    pnr_number = "2611143617"

    print(f"\n[UI TEST] Testing fare display for PNR: {pnr_number}")

    result = await tool.execute(
        pnrNumber=pnr_number,
        _user_type="website",
        _limit=1
    )

    if not result.is_error and result.structured_content:
        pnr_info = result.structured_content.get("pnr_info", {})

        booking_fare = pnr_info.get("booking_fare")
        ticket_fare = pnr_info.get("ticket_fare")

        print(f"\n   Fare Info:")
        print(f"      Booking Fare: {booking_fare}")
        print(f"      Ticket Fare: {ticket_fare}")

        if result.html and (booking_fare or ticket_fare):
            html = result.html

            # Check fare section
            assert "fare-section" in html or "fare-amount" in html, \
                "HTML should have fare section when fare is available"

            fare_value = ticket_fare or booking_fare
            if fare_value:
                assert fare_value in html, f"Fare value {fare_value} should be in HTML"

            print(f"\n   Fare display verified in HTML")

            # Save HTML
            with open("pnr_status_ui_fare.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[UI TEST] HTML saved to: pnr_status_ui_fare.html")
    else:
        print(f"   API Error or no fare info: {result.response_text}")


@pytest.mark.asyncio
async def test_pnr_status_whatsapp_vs_website():
    """Compare WhatsApp vs Website output formats."""
    tool = TrainPnrStatusTool()

    pnr_number = "2611143617"

    print(f"\n[UI TEST] Comparing WhatsApp vs Website formats for PNR: {pnr_number}")

    # Website format
    result_website = await tool.execute(
        pnrNumber=pnr_number,
        _user_type="website",
        _limit=1
    )

    # WhatsApp format
    result_whatsapp = await tool.execute(
        pnrNumber=pnr_number,
        _user_type="whatsapp",
        _limit=1
    )

    print(f"\n   Website Response:")
    print(f"      Has HTML: {result_website.html is not None}")
    print(f"      Has Structured Content: {result_website.structured_content is not None}")
    print(f"      Has WhatsApp Response: {result_website.whatsapp_response is not None}")

    print(f"\n   WhatsApp Response:")
    print(f"      Has HTML: {result_whatsapp.html is not None}")
    print(f"      Has Structured Content: {result_whatsapp.structured_content is not None}")
    print(f"      Has WhatsApp Response: {result_whatsapp.whatsapp_response is not None}")

    if not result_website.is_error:
        # Website should have HTML, no WhatsApp
        assert result_website.html is not None, "Website should have HTML"
        assert result_website.whatsapp_response is None, "Website should not have WhatsApp response"

    if not result_whatsapp.is_error:
        # WhatsApp should have WhatsApp response, no HTML
        assert result_whatsapp.html is None, "WhatsApp should not have HTML"
        assert result_whatsapp.whatsapp_response is not None, "WhatsApp should have WhatsApp response"

        # Check WhatsApp structure
        wa_response = result_whatsapp.whatsapp_response
        print(f"\n   WhatsApp JSON structure:")
        print(f"      Type: {wa_response.get('type')}")
        print(f"      PNR: {wa_response.get('pnr_number')}")
        print(f"      Train: {wa_response.get('train_info')}")
        print(f"      Route: {wa_response.get('route')}")
        print(f"      Passengers: {len(wa_response.get('passengers', []))}")

    print(f"\n[UI TEST] Format comparison complete")


def test_generate_pnr_html_from_sample_data():
    """Generate HTML files from sample PNR data without API calls."""
    from tools_factory.trains.Train_PnrStatus.pnr_status_renderer import render_pnr_status

    # Sample PNR data for different scenarios
    sample_data_scenarios = [
        {
            "filename": "pnr_confirmed_sample.html",
            "data": {
                "pnr_number": "2345678901",
                "train_name": "Rajdhani Express",
                "train_number": "12301",
                "date_of_journey": "15-Feb-2026",
                "source_station": "NDLS",
                "source_station_name": "New Delhi",
                "destination_station": "HWH",
                "destination_station_name": "Howrah Junction",
                "boarding_point": "NDLS",
                "journey_class": "3A",
                "class_name": "AC 3 Tier",
                "quota": "GN",
                "quota_name": "General Quota",
                "chart_status": "Chart Prepared",
                "booking_fare": "1250",
                "ticket_fare": "1250",
                "passengers": [
                    {
                        "serial_number": 1,
                        "booking_status": "CNF/B3/45",
                        "current_status": "CNF/B3/45",
                        "coach": "B3",
                        "berth_number": "45",
                        "berth_type": "LB"
                    },
                    {
                        "serial_number": 2,
                        "booking_status": "CNF/B3/46",
                        "current_status": "CNF/B3/46",
                        "coach": "B3",
                        "berth_number": "46",
                        "berth_type": "MB"
                    }
                ]
            }
        },
        {
            "filename": "pnr_waitlist_sample.html",
            "data": {
                "pnr_number": "3456789012",
                "train_name": "Shatabdi Express",
                "train_number": "12002",
                "date_of_journey": "20-Feb-2026",
                "source_station": "NDLS",
                "source_station_name": "New Delhi",
                "destination_station": "BCT",
                "destination_station_name": "Mumbai Central",
                "boarding_point": "NDLS",
                "journey_class": "CC",
                "class_name": "AC Chair Car",
                "quota": "GN",
                "quota_name": "General Quota",
                "chart_status": "Chart Not Prepared",
                "booking_fare": "1850",
                "ticket_fare": "1850",
                "passengers": [
                    {
                        "serial_number": 1,
                        "booking_status": "WL/15",
                        "current_status": "WL/8",
                        "coach": None,
                        "berth_number": None,
                        "berth_type": None
                    }
                ]
            }
        },
        {
            "filename": "pnr_rac_sample.html",
            "data": {
                "pnr_number": "4567890123",
                "train_name": "Duronto Express",
                "train_number": "12259",
                "date_of_journey": "18-Feb-2026",
                "source_station": "NDLS",
                "source_station_name": "New Delhi",
                "destination_station": "CSTM",
                "destination_station_name": "Mumbai CST",
                "boarding_point": "NDLS",
                "journey_class": "2A",
                "class_name": "AC 2 Tier",
                "quota": "TQ",
                "quota_name": "Tatkal Quota",
                "chart_status": "Chart Not Prepared",
                "booking_fare": "2450",
                "ticket_fare": "2450",
                "passengers": [
                    {
                        "serial_number": 1,
                        "booking_status": "RAC/25",
                        "current_status": "RAC/12",
                        "coach": "A1",
                        "berth_number": "12",
                        "berth_type": "RAC"
                    }
                ]
            }
        },
        {
            "filename": "pnr_mixed_status_sample.html",
            "data": {
                "pnr_number": "5678901234",
                "train_name": "Garib Rath Express",
                "train_number": "12909",
                "date_of_journey": "25-Feb-2026",
                "source_station": "BCT",
                "source_station_name": "Mumbai Central",
                "destination_station": "ADI",
                "destination_station_name": "Ahmedabad Junction",
                "boarding_point": "BCT",
                "journey_class": "3A",
                "class_name": "AC 3 Tier",
                "quota": "GN",
                "quota_name": "General Quota",
                "chart_status": "Chart Prepared",
                "booking_fare": "1875",
                "ticket_fare": "1875",
                "passengers": [
                    {
                        "serial_number": 1,
                        "booking_status": "WL/5",
                        "current_status": "CNF/B1/23",
                        "coach": "B1",
                        "berth_number": "23",
                        "berth_type": "SU"
                    },
                    {
                        "serial_number": 2,
                        "booking_status": "WL/6",
                        "current_status": "CNF/B1/24",
                        "coach": "B1",
                        "berth_number": "24",
                        "berth_type": "SL"
                    },
                    {
                        "serial_number": 3,
                        "booking_status": "WL/7",
                        "current_status": "RAC/5",
                        "coach": "B2",
                        "berth_number": "5",
                        "berth_type": "RAC"
                    }
                ]
            }
        }
    ]

    print(f"\n[UI TEST] Generating HTML files from sample data")

    for scenario in sample_data_scenarios:
        filename = scenario["filename"]
        data = scenario["data"]

        # Generate HTML using the renderer
        html_content = render_pnr_status(data)

        # Create a complete HTML page
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PNR Status - {data['pnr_number']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
            margin: 0;
        }}
        .container {{
            max-width: 700px;
            margin: 0 auto;
        }}
        h1 {{
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 28px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }}
        .note {{
            background: rgba(255, 255, 255, 0.95);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚂 Indian Railways PNR Status</h1>
        <div class="note">
            This is a sample PNR status generated for testing purposes.
            <br>Scenario: {filename.replace('.html', '').replace('_', ' ').title()}
        </div>
        {html_content}
    </div>
</body>
</html>
"""

        # Save the HTML file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_html)

        print(f"   ✓ Generated: {filename}")
        print(f"      PNR: {data['pnr_number']}")
        print(f"      Train: {data['train_name']} ({data['train_number']})")
        print(f"      Passengers: {len(data['passengers'])}")

    print(f"\n[UI TEST] Successfully generated {len(sample_data_scenarios)} HTML files")
    print(f"   Open these files in a browser to preview different PNR scenarios")


@pytest.mark.asyncio
async def test_pnr_status_ui_error_display():
    """Test UI display when PNR is invalid."""
    tool = TrainPnrStatusTool()

    # Use an obviously invalid PNR
    invalid_pnr = "0000000000"

    print(f"\n[UI TEST] Testing error display for invalid PNR: {invalid_pnr}")

    result = await tool.execute(
        pnrNumber=invalid_pnr,
        _user_type="website",
        _limit=1
    )

    print(f"   Is Error: {result.is_error}")
    print(f"   Response: {result.response_text}")

    # Should handle error gracefully
    assert result.response_text is not None
    assert len(result.response_text) > 0

    if result.is_error:
        # Error response should not have HTML (or have error HTML)
        print(f"   Error handled correctly")
        if result.structured_content:
            print(f"   Error details: {result.structured_content}")


@pytest.mark.asyncio
async def test_pnr_status_real_api_2729257223():
    """Real API test with PNR 2729257223 - generates HTML output."""
    tool = TrainPnrStatusTool()

    pnr_number = "2729257223"

    print(f"\n[REAL API TEST] Testing PNR: {pnr_number}")
    print(f"   Calling real API...")

    result = await tool.execute(
        pnrNumber=pnr_number,
        _user_type="website",
        _limit=1
    )

    print(f"\n   API Response:")
    print(f"      Is Error: {result.is_error}")
    print(f"      Response Text: {result.response_text}")

    if not result.is_error:
        assert result.html is not None, "Should have HTML for website user"

        # Verify HTML structure
        html = result.html
        assert "pnr-status-card" in html, "HTML should have pnr-status-card class"
        print(f"      ✓ HTML structure validated")

        # Create full HTML page
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PNR Status - {pnr_number}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
            margin: 0;
        }}
        .container {{
            max-width: 700px;
            margin: 0 auto;
        }}
        h1 {{
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 28px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }}
        .test-info {{
            background: rgba(255, 255, 255, 0.95);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            color: #666;
            font-size: 14px;
        }}
        .test-info strong {{
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚂 Indian Railways PNR Status</h1>
        <div class="test-info">
            <strong>Real API Test Result</strong><br>
            PNR Number: {pnr_number}<br>
            Test Date: February 6, 2026
        </div>
        {html}
    </div>
</body>
</html>
"""

        # Save HTML files
        filename = f"pnr_status_2729257223.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_html)
        print(f"\n   ✓ Full HTML page saved: {filename}")

        # Also save component only
        component_filename = f"pnr_status_2729257223_component.html"
        with open(component_filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"   ✓ Component HTML saved: {component_filename}")

        # Print structured data if available
        if result.structured_content and "pnr_info" in result.structured_content:
            pnr_info = result.structured_content["pnr_info"]
            print(f"\n   PNR Details:")
            print(f"      Train: {pnr_info.get('train_name', 'N/A')} ({pnr_info.get('train_number', 'N/A')})")
            print(f"      Date: {pnr_info.get('date_of_journey', 'N/A')}")
            print(f"      Route: {pnr_info.get('source_station_name', 'N/A')} → {pnr_info.get('destination_station_name', 'N/A')}")
            print(f"      Class: {pnr_info.get('class_name') or pnr_info.get('journey_class', 'N/A')}")
            print(f"      Chart: {pnr_info.get('chart_status', 'N/A')}")
            
            passengers = pnr_info.get('passengers', [])
            print(f"      Passengers: {len(passengers)}")
            for p in passengers:
                coach = p.get('coach', '-')
                berth = p.get('berth_number', '-')
                berth_loc = f"{coach}/{berth}" if coach and coach != '-' else '-'
                print(f"         P{p.get('serial_number')}: {p.get('current_status', 'N/A')} | Berth: {berth_loc}")

        print(f"\n   🎉 Test completed successfully!")
        print(f"   Open {filename} in a browser to view the rendered PNR status")

    else:
        print(f"\n   ⚠️  API returned error (PNR may be invalid/expired)")
        print(f"   Error message: {result.response_text}")
        
        # Still save error response if HTML exists
        if result.html:
            error_filename = f"pnr_status_2729257223_error.html"
            with open(error_filename, "w", encoding="utf-8") as f:
                f.write(result.html)
            print(f"   Error HTML saved: {error_filename}")


@pytest.mark.asyncio
async def test_pnr_status_ui_full_render():
    """Complete UI test with full HTML output for manual verification."""
    tool = TrainPnrStatusTool()

    pnr_number = "2611143617"

    print(f"\n[UI TEST] Full render test for PNR: {pnr_number}")

    result = await tool.execute(
        pnrNumber=pnr_number,
        _user_type="website",
        _limit=1
    )

    if not result.is_error and result.html:
        # Create a complete HTML page for viewing
        full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PNR Status - {pnr_number}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            margin: 0;
        }}
        .container {{
            max-width: 700px;
            margin: 0 auto;
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>PNR Status Check</h1>
        {result.html}
    </div>
</body>
</html>
"""

        # Save complete HTML page
        with open("pnr_status_ui_full.html", "w", encoding="utf-8") as f:
            f.write(full_html)

        print(f"\n[UI TEST] Complete HTML page saved to: pnr_status_ui_full.html")
        print(f"   Open this file in a browser to verify the UI rendering")

        # Also save just the component HTML
        with open("pnr_status_ui_component.html", "w", encoding="utf-8") as f:
            f.write(result.html)

        print(f"[UI TEST] Component HTML saved to: pnr_status_ui_component.html")

        # Print summary
        if result.structured_content and "pnr_info" in result.structured_content:
            pnr_info = result.structured_content["pnr_info"]
            print(f"\n[UI TEST] Rendered PNR Info Summary:")
            print(f"   PNR: {pnr_info.get('pnr_number')}")
            print(f"   Train: {pnr_info.get('train_name')} ({pnr_info.get('train_number')})")
            print(f"   Date: {pnr_info.get('date_of_journey')}")
            print(f"   Route: {pnr_info.get('source_station')} -> {pnr_info.get('destination_station')}")
            print(f"   Class: {pnr_info.get('class_name') or pnr_info.get('journey_class')}")
            print(f"   Chart: {pnr_info.get('chart_status')}")
            print(f"   Passengers: {len(pnr_info.get('passengers', []))}")

            for p in pnr_info.get("passengers", []):
                berth = f"{p.get('coach', '-')}/{p.get('berth_number', '-')}" if p.get('coach') else "-"
                print(f"      P{p.get('serial_number')}: {p.get('current_status')} ({berth})")

    else:
        print(f"   API Error or no HTML: {result.response_text}")
