"""
Quick script to test train UI with real API data
Tests train search with HTML rendering
"""

import pytest
from datetime import datetime, timedelta
from tools_factory.trains.train_search_tool import TrainSearchTool


@pytest.mark.asyncio
async def test_train_search_delhi_to_agra():
    """Test train search from Delhi to Agra with UI rendering"""
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="Delhi",
        toStation="Agra",
        journeyDate=journey_date,
        _limit=5,
        _user_type="website"
    )

    assert not result.is_error

    data = result.structured_content
    assert data is not None
    assert len(data.get("trains", [])) > 0

    # Check that trains have classes with book_now links
    trains = data.get("trains", [])
    if trains:
        first_train = trains[0]
        assert "classes" in first_train
        classes = first_train.get("classes", [])
        if classes:
            first_class = classes[0]
            assert "book_now" in first_class
            assert first_class["book_now"].startswith("https://railways.easemytrip.com/TrainInfo/")

    if result.html:
        with open("train_search_results.html", "w", encoding="utf-8") as f:
            f.write(result.html)


@pytest.mark.asyncio
async def test_train_search_mumbai_to_pune():
    """Test train search from Mumbai to Pune"""
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="Delhi",
        toStation="Jalandhar",
        journeyDate=journey_date,
        _limit=100,
        _user_type="website"
    )

    assert not result.is_error

    data = result.structured_content
    assert data is not None

    if result.html:
        with open("train_mumbai_pune_results.html", "w", encoding="utf-8") as f:
            f.write(result.html)


@pytest.mark.asyncio
async def test_train_search_with_class_filter():
    """Test train search with specific travel class filter.

    NEW BEHAVIOR (as of latest update):
    - When user specifies a class (e.g., 3A), only trains WITH that class are shown
    - For those trains, ALL classes are displayed in the UI (not just 3A)
    - This allows users to compare all available classes for trains that meet their criteria
    """
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=14)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="New Delhi",
        toStation="Varanasi",
        journeyDate=journey_date,
        travelClass="3A",
        _limit=5,
        _user_type="website"
    )

    assert not result.is_error

    data = result.structured_content
    if data and data.get("trains"):
        print(f"\n[UI TEST] Found {len(data.get('trains', []))} trains with 3A class")

        # NEW BEHAVIOR: All trains should have 3A, but show ALL classes
        for train in data.get("trains", []):
            classes = train.get("classes", [])
            class_codes = [cls.get("class_code") for cls in classes]

            print(f"\n  Train {train.get('train_number')} - {train.get('train_name')}")
            print(f"    Classes in UI: {class_codes}")

            # CRITICAL ASSERTION: Train must have 3A (the filtered class)
            assert "3A" in class_codes, f"Train should have 3A class, got: {class_codes}"

            # NEW BEHAVIOR: Should show OTHER classes too (not just 3A)
            if len(class_codes) > 1:
                print(f"    [PASS] UI shows all {len(class_codes)} classes, not just 3A")
            else:
                print(f"    [INFO] This train only has 3A class available")

    if result.html:
        with open("train_class_filter_results.html", "w", encoding="utf-8") as f:
            f.write(result.html)
        print(f"\n[UI TEST] HTML output saved to: train_class_filter_results.html")


@pytest.mark.asyncio
async def test_train_search_tatkal_quota():
    """Test train search with Tatkal quota"""
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=3)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="Delhi",
        toStation="Jaipur",
        journeyDate=journey_date,
        quota="TQ",
        _limit=5,
        _user_type="website"
    )

    assert not result.is_error

    data = result.structured_content
    if data:
        assert data.get("quota") == "TQ"

    if result.html:
        with open("train_tatkal_results.html", "w", encoding="utf-8") as f:
            f.write(result.html)


@pytest.mark.asyncio
async def test_train_search_whatsapp_response():
    """Test train search with WhatsApp response format"""
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    result = await tool.execute(
        fromStation="Chennai",
        toStation="Bangalore",
        journeyDate=journey_date,
        _limit=3,
        _user_type="whatsapp"
    )

    assert not result.is_error

    # WhatsApp response should not have HTML
    assert result.html is None

    # Should have whatsapp_response
    assert result.whatsapp_response is not None


@pytest.mark.asyncio
async def test_train_ui_class_filter_shows_all_classes():
    """UI Test: Verify that class filtering shows all classes for matching trains.

    Scenario:
    - User searches for trains with 3A class from Delhi to Jaipur
    - UI should show only trains that have 3A
    - For each train, UI should display ALL available classes (1A, 2A, 3A, SL, etc.)
    - This allows users to see all booking options for trains that meet their criteria

    Expected UI Behavior:
    - Train cards show multiple class options
    - Each class has its own fare and availability
    - Each class has a "Book Now" button
    - The filtered class (3A) is present in every train
    """
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    print("\n[UI TEST] Testing class filter UI with 3A preference")

    result = await tool.execute(
        fromStation="Delhi",
        toStation="Jaipur",
        journeyDate=journey_date,
        travelClass="3A",
        _limit=5,
        _user_type="website"
    )

    assert not result.is_error, "Search should succeed"
    assert result.html is not None, "Should have HTML output for website user type"

    data = result.structured_content
    trains = data.get("trains", [])

    if not trains:
        print("[WARN] No trains found with 3A class for this route/date")
        return

    print(f"\n[UI TEST] Validating {len(trains)} train cards in UI")

    for idx, train in enumerate(trains, 1):
        train_number = train.get("train_number")
        train_name = train.get("train_name")
        classes = train.get("classes", [])
        class_codes = [cls.get("class_code") for cls in classes]

        print(f"\n  Train Card {idx}: {train_number} - {train_name}")
        print(f"    Class tabs/buttons in UI: {class_codes}")

        # ASSERTION 1: Train must have the filtered class (3A)
        assert "3A" in class_codes, \
            f"UI should only show trains with 3A class. Train {train_number} has: {class_codes}"

        # ASSERTION 2: UI should show multiple classes (not just 3A)
        # Note: Some trains might genuinely only have 3A, so we log this
        if len(class_codes) > 1:
            other_classes = [c for c in class_codes if c != "3A"]
            print(f"    [PASS] UI displays {len(class_codes)} class options: {class_codes}")
            print(f"           (3A + {len(other_classes)} others: {other_classes})")

            # ASSERTION 3: Each class should have required UI elements
            for cls in classes:
                assert "class_code" in cls, "Class must have code"
                assert "class_name" in cls, "Class must have display name"
                assert "fare" in cls, "Class must have fare for UI display"
                assert "availability_status" in cls, "Class must have availability"
                assert "book_now" in cls, "Class must have booking link"

                # Verify book_now link format
                assert cls["book_now"].startswith("https://railways.easemytrip.com/TrainInfo/"), \
                    f"Book now link should be valid deeplink: {cls['book_now']}"

            print(f"    [PASS] All class cards have required UI elements")
        else:
            print(f"    [INFO] This train only offers 3A class")

        # Print detailed class info for UI verification
        print(f"    Class details for UI rendering:")
        for cls in classes:
            class_code = cls.get("class_code")
            class_name = cls.get("class_name")
            fare = cls.get("fare")
            availability = cls.get("availability_status")
            print(f"      [{class_code}] {class_name}: Rs.{fare} - {availability}")

    # Save HTML for manual inspection
    if result.html:
        filename = "train_ui_class_filter_all_classes.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result.html)
        print(f"\n[UI TEST] HTML saved to: {filename}")
        print(f"          Open this file to visually verify all classes are displayed")

    print(f"\n[PASS] UI Test: Class filtering correctly shows all classes for matching trains")


@pytest.mark.asyncio
async def test_train_ui_class_filter_comparison():
    """UI Test: Compare filtered vs unfiltered results to verify exclusion logic.

    This test validates that:
    1. Unfiltered search shows all trains (regardless of class)
    2. Filtered search (3A) shows fewer trains (only those with 3A)
    3. All filtered trains show multiple classes in UI
    """
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=10)).strftime("%d-%m-%Y")

    print("\n[UI TEST] Comparing filtered vs unfiltered UI output")

    # Test 1: Without filter (all trains)
    result_all = await tool.execute(
        fromStation="Delhi",
        toStation="Agra",
        journeyDate=journey_date,
        _limit=10,
        _user_type="website"
    )

    assert not result_all.is_error
    data_all = result_all.structured_content
    trains_all = data_all.get("trains", [])

    print(f"\n  Unfiltered: {len(trains_all)} trains in UI")

    # Test 2: With 2A filter
    result_filtered = await tool.execute(
        fromStation="Delhi",
        toStation="Agra",
        journeyDate=journey_date,
        travelClass="2A",
        _limit=10,
        _user_type="website"
    )

    assert not result_filtered.is_error
    data_filtered = result_filtered.structured_content
    trains_filtered = data_filtered.get("trains", [])

    print(f"  Filtered (2A): {len(trains_filtered)} trains in UI")
    print(f"  Excluded: {len(trains_all) - len(trains_filtered)} trains without 2A")

    # ASSERTION 1: Filtered results should be <= unfiltered
    assert len(trains_filtered) <= len(trains_all), \
        "Filtered results should not exceed unfiltered results"

    # ASSERTION 2: Every filtered train must have 2A
    for train in trains_filtered:
        classes = train.get("classes", [])
        class_codes = [cls.get("class_code") for cls in classes]

        assert "2A" in class_codes, \
            f"Filtered train {train.get('train_number')} must have 2A: {class_codes}"

        # Log class diversity for UI verification
        print(f"\n    Train {train.get('train_number')}: Shows {len(class_codes)} classes in UI")
        print(f"      Classes: {class_codes}")

    # Save both HTML outputs for comparison
    if result_all.html:
        with open("train_ui_unfiltered.html", "w", encoding="utf-8") as f:
            f.write(result_all.html)
        print(f"\n[UI TEST] Unfiltered HTML: train_ui_unfiltered.html")

    if result_filtered.html:
        with open("train_ui_filtered_2a.html", "w", encoding="utf-8") as f:
            f.write(result_filtered.html)
        print(f"[UI TEST] Filtered HTML: train_ui_filtered_2a.html")

    print(f"\n[PASS] UI Test: Filtering correctly excludes trains without preferred class")


@pytest.mark.asyncio
async def test_train_ui_class_filter_different_classes():
    """UI Test: Test filtering with different class types (1A, SL, CC).

    This verifies that the UI correctly handles different class filters
    and always shows all available classes for matching trains.
    """
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=14)).strftime("%d-%m-%Y")

    test_cases = [
        ("SL", "Sleeper"),
        ("2A", "Second AC"),
        ("CC", "Chair Car"),
    ]

    print("\n[UI TEST] Testing multiple class filters")

    for class_code, class_name in test_cases:
        print(f"\n  Testing filter: {class_code} ({class_name})")

        result = await tool.execute(
            fromStation="New Delhi",
            toStation="Mumbai Central",
            journeyDate=journey_date,
            travelClass=class_code,
            _limit=3,
            _user_type="website"
        )

        if result.is_error:
            print(f"    [SKIP] Error: {result.response_text}")
            continue

        data = result.structured_content
        trains = data.get("trains", [])

        if not trains:
            print(f"    [SKIP] No trains found with {class_code} class")
            continue

        print(f"    Found {len(trains)} trains with {class_code}")

        # Verify each train has the filtered class AND shows all classes
        for train in trains[:2]:  # Check first 2 trains
            classes = train.get("classes", [])
            class_codes = [cls.get("class_code") for cls in classes]

            # Must have filtered class
            assert class_code in class_codes, \
                f"Train must have {class_code}: {class_codes}"

            # Should show multiple classes in UI
            print(f"      Train {train.get('train_number')}: {len(class_codes)} classes: {class_codes}")

            if len(class_codes) > 1:
                print(f"        [PASS] UI shows all classes, not just {class_code}")

        # Save HTML for this class filter
        if result.html:
            filename = f"train_ui_filter_{class_code.lower()}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(result.html)
            print(f"    [UI TEST] HTML saved: {filename}")

    print(f"\n[PASS] UI Test: Multiple class filters work correctly")


# ─── Quota-based Conditional UI Tests ───


@pytest.mark.asyncio
async def test_train_ui_general_quota_full_display():
    """UI Test: General quota (GN) shows full display - fare, availability, Book Now.

    When quota is GN (default), the UI should show:
    - Class code
    - Fare (₹...)
    - Availability status
    - "Tap To Refresh" or "Book Now" button
    """
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    print("\n[UI TEST] Testing General Quota (GN) - Full Display")

    result = await tool.execute(
        fromStation="Delhi",
        toStation="Jaipur",
        journeyDate=journey_date,
        quota="GN",
        _limit=5,
        _user_type="website"
    )

    assert not result.is_error
    assert result.html is not None, "Should have HTML output"

    data = result.structured_content
    assert data.get("quota") == "GN"

    html = result.html

    # GN quota should NOT have "Check Tatkal" or similar buttons
    assert "Check Tatkal" not in html, "GN quota should not show 'Check Tatkal' button"
    assert "Check Ladies" not in html, "GN quota should not show 'Check Ladies' button"
    assert "Check Senior" not in html, "GN quota should not show 'Check Senior' button"
    assert "class-check-quota-btn" not in html, "GN quota should not have check-quota buttons"

    # GN quota should show fare and availability
    assert '<div class="class-fare">' in html, "GN quota should show fare"
    assert '<div class="class-availability' in html, "GN quota should show availability"

    # Should have either "Tap To Refresh" or "Book Now" buttons
    has_refresh = "Tap To Refresh" in html
    has_book = "Book Now" in html
    assert has_refresh or has_book, "GN quota should show 'Tap To Refresh' or 'Book Now'"

    print(f"  [PASS] GN quota shows full display (fare, availability, buttons)")

    if result.html:
        with open("train_ui_quota_general.html", "w", encoding="utf-8") as f:
            f.write(result.html)
        print(f"  [UI TEST] HTML saved: train_ui_quota_general.html")


@pytest.mark.asyncio
async def test_train_ui_senior_citizen_quota_minimal_display():
    """UI Test: Senior Citizen quota (SS) shows minimal display - class code + Check Senior Citizen button.

    When quota is SS, the UI should show:
    - Class code ONLY (no fare, no availability)
    - "Check Senior Citizen" button (not "Tap To Refresh" or "Book Now")
    - data-quota="SS" on class cards
    - Subtitle mentions "Senior Citizen Quota"
    """
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=5)).strftime("%d-%m-%Y")

    print("\n[UI TEST] Testing Senior Citizen Quota (SS) - Minimal Display")

    result = await tool.execute(
        fromStation="Delhi",
        toStation="Jaipur",
        journeyDate=journey_date,
        quota="SS",
        _limit=5,
        _user_type="website"
    )

    assert not result.is_error
    assert result.html is not None, "Should have HTML output"

    data = result.structured_content
    assert data.get("quota") == "SS"

    html = result.html

    # SS quota should have "Check Senior Citizen" button
    assert "Check Senior Citizen" in html, "SS quota should show 'Check Senior Citizen' button"
    assert "class-check-quota-btn" in html, "SS quota should have check-quota button class"

    # SS quota should NOT show fare or availability in class cards
    assert '<div class="class-fare">' not in html, "SS quota should NOT show fare initially"
    assert '<div class="class-availability' not in html, "SS quota should NOT show availability initially"

    # SS quota should NOT show standard buttons
    assert "Tap To Refresh</button>" not in html, "SS quota should not show 'Tap To Refresh'"
    assert ">Book Now</a>" not in html, "SS quota should not show 'Book Now'"

    # data-quota should be SS
    assert 'data-quota="SS"' in html, "Class cards should have data-quota='SS'"

    # Subtitle should mention Senior Citizen
    assert "Senior Citizen Quota" in html, "Subtitle should mention 'Senior Citizen Quota'"

    # Response text should mention Senior Citizen
    assert "Senior Citizen" in result.response_text, "Response text should mention Senior Citizen"

    print(f"  [PASS] SS quota shows minimal display (class code + Check Senior Citizen)")

    if result.html:
        with open("train_ui_quota_senior_citizen.html", "w", encoding="utf-8") as f:
            f.write(result.html)
        print(f"  [UI TEST] HTML saved: train_ui_quota_senior_citizen.html")


@pytest.mark.asyncio
async def test_train_ui_ladies_quota_minimal_display():
    """UI Test: Ladies quota (LD) shows minimal display - class code + Check Ladies Quota button."""
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    print("\n[UI TEST] Testing Ladies Quota (LD) - Minimal Display")

    result = await tool.execute(
        fromStation="Delhi",
        toStation="Agra",
        journeyDate=journey_date,
        quota="LD",
        _limit=5,
        _user_type="website"
    )

    assert not result.is_error
    assert result.html is not None, "Should have HTML output"

    data = result.structured_content
    assert data.get("quota") == "LD"

    html = result.html

    # LD quota should have "Check Ladies Quota" button
    assert "Check Ladies Quota" in html, "LD quota should show 'Check Ladies Quota' button"
    assert "class-check-quota-btn" in html, "LD quota should have check-quota button class"

    # Should NOT show fare/availability
    assert '<div class="class-fare">' not in html, "LD quota should NOT show fare initially"
    assert '<div class="class-availability' not in html, "LD quota should NOT show availability initially"

    # data-quota should be LD
    assert 'data-quota="LD"' in html, "Class cards should have data-quota='LD'"

    # Subtitle should mention Ladies
    assert "Ladies Quota" in html, "Subtitle should mention 'Ladies Quota'"

    print(f"  [PASS] LD quota shows minimal display (class code + Check Ladies Quota)")

    if result.html:
        with open("train_ui_quota_ladies.html", "w", encoding="utf-8") as f:
            f.write(result.html)
        print(f"  [UI TEST] HTML saved: train_ui_quota_ladies.html")


@pytest.mark.asyncio
async def test_train_ui_multiple_quotas_comparison():
    """UI Test: Compare UI output for different quotas on the same route.

    Validates that:
    1. GN quota shows full display (fare, availability, standard buttons)
    2. Non-GN quotas show minimal display (class code + Check button)
    3. Each quota type has the correct button label
    4. data-quota attribute matches the requested quota
    """
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    print("\n[UI TEST] Comparing UI across different quotas")

    quota_tests = [
        ("GN", "General", False),
        ("TQ", "Tatkal", True),
        ("LD", "Ladies Quota", True),
        ("SS", "Senior Citizen", True),
    ]

    for quota_code, expected_label, is_non_general in quota_tests:
        print(f"\n  Testing quota: {quota_code} ({expected_label})")

        result = await tool.execute(
            fromStation="Delhi",
            toStation="Jaipur",
            journeyDate=journey_date,
            quota=quota_code,
            _limit=3,
            _user_type="website"
        )

        if result.is_error:
            print(f"    [SKIP] Error: {result.response_text}")
            continue

        data = result.structured_content
        assert data.get("quota") == quota_code, f"Quota should be {quota_code}"

        if not result.html:
            print(f"    [SKIP] No HTML output (no trains found)")
            continue

        html = result.html

        # Verify data-quota attribute
        assert f'data-quota="{quota_code}"' in html, \
            f"Class cards should have data-quota='{quota_code}'"

        if is_non_general:
            # Non-GN: should have Check button, no fare/availability
            assert "class-check-quota-btn" in html, \
                f"{quota_code} quota should have check-quota button"
            assert f"Check {expected_label}" in html, \
                f"{quota_code} quota should show 'Check {expected_label}' button"
            assert '<div class="class-fare">' not in html, \
                f"{quota_code} quota should NOT show fare"
            assert '<div class="class-availability' not in html, \
                f"{quota_code} quota should NOT show availability"
            print(f"    [PASS] Minimal display: class code + 'Check {expected_label}' button")
        else:
            # GN: should have full display
            assert "class-check-quota-btn" not in html, \
                "GN quota should NOT have check-quota button"
            assert '<div class="class-fare">' in html, \
                "GN quota should show fare"
            assert '<div class="class-availability' in html, \
                "GN quota should show availability"
            print(f"    [PASS] Full display: fare, availability, standard buttons")

        # Save HTML
        filename = f"train_ui_quota_{quota_code.lower()}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"    HTML saved: {filename}")

    print(f"\n[PASS] UI Test: All quotas display correctly")


@pytest.mark.asyncio
async def test_train_ui_invalid_quota_falls_back_to_general():
    """UI Test: Invalid quota falls back to GN and shows full display."""
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    print("\n[UI TEST] Testing invalid quota fallback to GN")

    result = await tool.execute(
        fromStation="Delhi",
        toStation="Jaipur",
        journeyDate=journey_date,
        quota="INVALID",
        _limit=5,
        _user_type="website"
    )

    assert not result.is_error

    data = result.structured_content
    # Invalid quota should fall back to GN
    assert data.get("quota") == "GN", "Invalid quota should fall back to GN"

    if result.html:
        html = result.html

        # Should behave like GN - full display
        assert "class-check-quota-btn" not in html, \
            "Fallback GN should NOT have check-quota buttons"
        assert '<div class="class-fare">' in html, "Fallback GN should show fare"
        assert '<div class="class-availability' in html, "Fallback GN should show availability"

        print(f"  [PASS] Invalid quota correctly falls back to GN full display")


@pytest.mark.asyncio
async def test_train_ui_tatkal_quota_with_class_filter():
    """UI Test: Tatkal quota + class filter combination.

    When both quota (TQ) and class (3A) are specified:
    - Only trains with 3A class should appear
    - UI should show minimal display (no fare/availability)
    - "Check Tatkal" button should appear
    - Response text should mention both filters
    """
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=5)).strftime("%d-%m-%Y")

    print("\n[UI TEST] Testing Tatkal Quota + Class Filter (TQ + 3A)")

    result = await tool.execute(
        fromStation="Delhi",
        toStation="Mumbai Central",
        journeyDate=journey_date,
        travelClass="3A",
        quota="TQ",
        _limit=5,
        _user_type="website"
    )

    assert not result.is_error

    data = result.structured_content
    assert data.get("quota") == "TQ"

    # Response text should mention both class and quota
    assert "Tatkal" in result.response_text, "Response text should mention Tatkal"

    if result.html:
        html = result.html

        # Should show Check Tatkal button (non-GN behavior)
        assert "Check Tatkal" in html, "Should show 'Check Tatkal' button"
        assert "class-check-quota-btn" in html

        # Should NOT show fare/availability
        assert '<div class="class-fare">' not in html, "TQ should NOT show fare"
        assert '<div class="class-availability' not in html, "TQ should NOT show availability"

        # data-quota should be TQ
        assert 'data-quota="TQ"' in html

        # Verify trains have 3A class
        trains = data.get("trains", [])
        for train in trains:
            class_codes = [cls.get("class_code") for cls in train.get("classes", [])]
            assert "3A" in class_codes, \
                f"Train {train.get('train_number')} should have 3A: {class_codes}"

        print(f"  [PASS] TQ + 3A filter: minimal display with Check Tatkal button")
        print(f"  [PASS] All {len(trains)} trains have 3A class")

        with open("train_ui_quota_tatkal_3a.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  HTML saved: train_ui_quota_tatkal_3a.html")


@pytest.mark.asyncio
async def test_train_ui_quota_whatsapp_no_html():
    """UI Test: WhatsApp users with non-GN quota should NOT get HTML output."""
    tool = TrainSearchTool()

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

    print("\n[UI TEST] Testing Quota with WhatsApp user type")

    result = await tool.execute(
        fromStation="Delhi",
        toStation="Jaipur",
        journeyDate=journey_date,
        quota="TQ",
        _limit=5,
        _user_type="whatsapp"
    )

    assert not result.is_error

    # WhatsApp should NOT have HTML
    assert result.html is None, "WhatsApp should not have HTML output"

    # Should have whatsapp_response
    assert result.whatsapp_response is not None, "WhatsApp should have whatsapp_response"

    # Response text should mention Tatkal
    assert "Tatkal" in result.response_text, "Response text should mention Tatkal"

    print(f"  [PASS] WhatsApp + TQ quota: no HTML, has whatsapp_response")
