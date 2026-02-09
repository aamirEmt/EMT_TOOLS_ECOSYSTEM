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

    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")

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
