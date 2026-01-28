"""
Real API test cases for Tap To Refresh availability functionality.

These tests make actual API calls to EaseMyTrip Railways APIs.
Run with: pytest tests/test_tap_to_refresh_real_api.py -v -s
"""

import pytest
from datetime import datetime, timedelta

from emt_client.clients.train_client import TrainApiClient
from tools_factory.trains.train_search_tool import TrainSearchTool
from tools_factory.trains.train_search_service import search_trains
from tools_factory.trains.train_renderer import render_train_results


# ============================================================================
# Real API Tests - TrainApiClient.check_availability
# ============================================================================

class TestCheckAvailabilityRealAPI:
    """Real API tests for check_availability method."""

    @pytest.mark.asyncio
    async def test_check_availability_delhi_to_bhubaneswar(self):
        """Test real availability check for Delhi to Bhubaneswar route."""
        client = TrainApiClient()

        journey_date = (datetime.now() + timedelta(days=8)).strftime("%d/%m/%Y")

        result = await client.check_availability(
            train_no="12816",  # Puri Express
            class_code="3A",
            quota="GN",
            from_station_code="ANVT",
            to_station_code="BBS",
            journey_date=journey_date,
            from_display="Delhi All Stations (NDLS)",
            to_display="Bhubaneswar (BBS)"
        )

        print(f"\n=== Availability Check Result ===")
        print(f"Train: 12816 (Puri Express)")
        print(f"Route: ANVT -> BBS")
        print(f"Class: 3A")
        print(f"Date: {journey_date}")
        print(f"Response: {result}")

        # Verify response structure
        assert result is not None
        assert "avlDayList" in result or "error" in str(result).lower()

        if "avlDayList" in result and result["avlDayList"]:
            avl = result["avlDayList"][0]
            print(f"Availability Status: {avl.get('availablityStatusNew', 'N/A')}")
            print(f"Creation Time: {result.get('creationTime', 'N/A')}")

    @pytest.mark.asyncio
    async def test_check_availability_multiple_classes(self):
        """Test availability check for multiple classes on same train."""
        client = TrainApiClient()

        journey_date = (datetime.now() + timedelta(days=10)).strftime("%d/%m/%Y")
        classes_to_check = ["SL", "3A", "2A", "1A"]

        print(f"\n=== Multi-Class Availability Check ===")
        print(f"Train: 12301 (Rajdhani Express)")
        print(f"Route: NDLS -> HWH")
        print(f"Date: {journey_date}")

        for class_code in classes_to_check:
            try:
                result = await client.check_availability(
                    train_no="12301",
                    class_code=class_code,
                    quota="GN",
                    from_station_code="NDLS",
                    to_station_code="HWH",
                    journey_date=journey_date,
                    from_display="New Delhi (NDLS)",
                    to_display="Howrah Jn (HWH)"
                )

                status = "N/A"
                if result.get("avlDayList"):
                    status = result["avlDayList"][0].get("availablityStatusNew", "N/A")

                print(f"  {class_code}: {status}")

            except Exception as e:
                print(f"  {class_code}: Error - {e}")

    @pytest.mark.asyncio
    async def test_check_availability_tatkal_quota(self):
        """Test availability check with Tatkal quota."""
        client = TrainApiClient()

        # Tatkal opens 1 day before journey
        journey_date = (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y")

        result = await client.check_availability(
            train_no="12952",  # Mumbai Rajdhani
            class_code="3A",
            quota="TQ",  # Tatkal quota
            from_station_code="NDLS",
            to_station_code="BCT",
            journey_date=journey_date,
            from_display="New Delhi (NDLS)",
            to_display="Mumbai Central (BCT)"
        )

        print(f"\n=== Tatkal Availability Check ===")
        print(f"Train: 12952 (Mumbai Rajdhani)")
        print(f"Quota: TQ (Tatkal)")
        print(f"Date: {journey_date}")
        print(f"Response: {result}")

        assert result is not None


# ============================================================================
# Real API Tests - Train Search with Tap To Refresh
# ============================================================================

class TestTrainSearchWithRefresh:
    """Real API tests for train search that may return Tap To Refresh status."""

    @pytest.mark.asyncio
    async def test_search_route_with_stale_availability(self):
        """Test search on route that commonly has stale availability data."""
        journey_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        # Delhi to Bhubaneswar often has "Tap To Refresh" or "N/A" status
        result = await search_trains(
            from_station="Delhi",
            to_station="Bhubaneswar",
            journey_date=journey_date,
            quota="GN"
        )

        print(f"\n=== Train Search Results ===")
        print(f"Route: Delhi -> Bhubaneswar")
        print(f"Date: {journey_date}")
        print(f"Total trains: {result.get('total_count', 0)}")

        # Check for Tap To Refresh or N/A statuses
        tap_to_refresh_count = 0
        na_count = 0
        valid_count = 0

        for train in result.get("trains", []):
            print(f"\n  Train: {train['train_number']} - {train['train_name']}")
            for cls in train.get("classes", []):
                status = cls.get("availability_status", "")
                print(f"    {cls['class_code']}: {status}")

                if status == "Tap To Refresh":
                    tap_to_refresh_count += 1
                elif status == "N/A" or not status:
                    na_count += 1
                else:
                    valid_count += 1

        print(f"\n=== Status Summary ===")
        print(f"Tap To Refresh: {tap_to_refresh_count}")
        print(f"N/A: {na_count}")
        print(f"Valid statuses: {valid_count}")

        assert result is not None
        assert "trains" in result

    @pytest.mark.asyncio
    async def test_search_and_render_with_refresh_button(self):
        """Test that HTML renders refresh button for N/A or Tap To Refresh statuses."""
        journey_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        result = await search_trains(
            from_station="Mumbai",
            to_station="Chennai",
            journey_date=journey_date,
            quota="GN"
        )

        if result.get("trains"):
            html = render_train_results(result)

            # Save HTML for manual inspection
            with open("test_tap_to_refresh_output.html", "w", encoding="utf-8") as f:
                f.write(html)

            print(f"\n=== Rendered HTML Analysis ===")
            print(f"HTML saved to: test_tap_to_refresh_output.html")

            refresh_button_count = html.count('class="class-refresh-btn"')
            print(f"Refresh buttons in HTML: {refresh_button_count}")

            # Check if JavaScript is included
            has_js = "refreshAvailability" in html
            print(f"JavaScript function included: {has_js}")

            assert has_js, "JavaScript refresh function should be in HTML"

    @pytest.mark.asyncio
    async def test_full_tool_execution_with_html(self):
        """Test full TrainSearchTool execution and HTML output."""
        tool = TrainSearchTool()

        journey_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")

        result = await tool.execute(
            fromStation="Jammu",
            toStation="Delhi",
            journeyDate=journey_date,
            _limit=5,
            _user_type="website"
        )

        print(f"\n=== TrainSearchTool Result ===")
        print(f"Route: Jammu -> Delhi")
        print(f"Is Error: {result.is_error}")
        print(f"Response Text: {result.response_text}")

        if result.structured_content:
            trains = result.structured_content.get("trains", [])
            print(f"Trains found: {len(trains)}")

            for train in trains[:3]:  # Print first 3
                print(f"\n  {train['train_number']} - {train['train_name']}")
                for cls in train.get("classes", []):
                    status = cls.get("availability_status", "N/A")
                    needs_refresh = status in ["N/A", "Tap To Refresh", "Check Online", ""]
                    refresh_indicator = " [NEEDS REFRESH]" if needs_refresh else ""
                    print(f"    {cls['class_code']}: {status}{refresh_indicator}")

        if result.html:
            with open("test_tool_output.html", "w", encoding="utf-8") as f:
                f.write(result.html)
            print(f"\nHTML saved to: test_tool_output.html")

        assert not result.is_error


# ============================================================================
# Real API Tests - Specific Routes Known for Refresh Issues
# ============================================================================

class TestKnownRefreshRoutes:
    """Test routes that are known to frequently return Tap To Refresh status."""

    @pytest.mark.asyncio
    async def test_long_distance_route_delhi_chennai(self):
        """Long distance routes often have stale availability."""
        tool = TrainSearchTool()

        journey_date = (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d")

        result = await tool.execute(
            fromStation="New Delhi",
            toStation="Chennai",
            journeyDate=journey_date,
            _limit=10,
            _user_type="website"
        )

        print(f"\n=== Delhi to Chennai (Long Distance) ===")
        self._print_availability_summary(result)

        if result.html:
            with open("test_delhi_chennai.html", "w", encoding="utf-8") as f:
                f.write(result.html)

    @pytest.mark.asyncio
    async def test_popular_route_delhi_mumbai(self):
        """Popular routes with high demand."""
        tool = TrainSearchTool()

        journey_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")

        result = await tool.execute(
            fromStation="Delhi",
            toStation="Mumbai",
            journeyDate=journey_date,
            _limit=8,
            _user_type="website"
        )

        print(f"\n=== Delhi to Mumbai (Popular Route) ===")
        self._print_availability_summary(result)

        if result.html:
            with open("test_delhi_mumbai.html", "w", encoding="utf-8") as f:
                f.write(result.html)

    @pytest.mark.asyncio
    async def test_regional_route_kolkata_patna(self):
        """Regional routes."""
        tool = TrainSearchTool()

        journey_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        result = await tool.execute(
            fromStation="Kolkata",
            toStation="Patna",
            journeyDate=journey_date,
            _limit=8,
            _user_type="website"
        )

        print(f"\n=== Kolkata to Patna (Regional) ===")
        self._print_availability_summary(result)

        if result.html:
            with open("test_kolkata_patna.html", "w", encoding="utf-8") as f:
                f.write(result.html)

    def _print_availability_summary(self, result):
        """Helper to print availability summary."""
        if result.is_error:
            print(f"Error: {result.response_text}")
            return

        if not result.structured_content:
            print("No data")
            return

        trains = result.structured_content.get("trains", [])
        print(f"Total trains: {len(trains)}")

        status_counts = {
            "tap_to_refresh": 0,
            "na": 0,
            "available": 0,
            "waitlist": 0,
            "rac": 0,
            "regret": 0,
            "other": 0
        }

        for train in trains:
            for cls in train.get("classes", []):
                status = cls.get("availability_status", "").upper()
                if "TAP TO REFRESH" in status:
                    status_counts["tap_to_refresh"] += 1
                elif status == "N/A" or not status:
                    status_counts["na"] += 1
                elif "AVAILABLE" in status:
                    status_counts["available"] += 1
                elif "WL" in status:
                    status_counts["waitlist"] += 1
                elif "RAC" in status:
                    status_counts["rac"] += 1
                elif "REGRET" in status or "NOT AVAILABLE" in status:
                    status_counts["regret"] += 1
                else:
                    status_counts["other"] += 1

        print(f"\nAvailability Summary:")
        print(f"  Available: {status_counts['available']}")
        print(f"  Waitlist: {status_counts['waitlist']}")
        print(f"  RAC: {status_counts['rac']}")
        print(f"  Regret/Not Available: {status_counts['regret']}")
        print(f"  Tap To Refresh: {status_counts['tap_to_refresh']}")
        print(f"  N/A: {status_counts['na']}")
        print(f"  Other: {status_counts['other']}")

        needs_refresh = status_counts["tap_to_refresh"] + status_counts["na"]
        total = sum(status_counts.values())
        if total > 0:
            print(f"\n  Classes needing refresh: {needs_refresh}/{total} ({needs_refresh*100//total}%)")


# ============================================================================
# Real API Tests - Direct Availability API Call
# ============================================================================

class TestDirectAvailabilityAPI:
    """Direct tests against the AvailToCheck API endpoint."""

    @pytest.mark.asyncio
    async def test_availability_api_response_structure(self):
        """Verify the API response structure matches expected format."""
        client = TrainApiClient()

        journey_date = (datetime.now() + timedelta(days=5)).strftime("%d/%m/%Y")

        result = await client.check_availability(
            train_no="12259",  # Sealdah Duronto
            class_code="3A",
            quota="GN",
            from_station_code="SDAH",
            to_station_code="NDLS",
            journey_date=journey_date,
            from_display="Sealdah (SDAH)",
            to_display="New Delhi (NDLS)"
        )

        print(f"\n=== API Response Structure ===")
        print(f"Keys in response: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")

        if isinstance(result, dict):
            # Check expected fields
            assert "avlDayList" in result or isinstance(result, str), "Response should have avlDayList or be error string"

            if "avlDayList" in result and result["avlDayList"]:
                avl = result["avlDayList"][0]
                print(f"\navlDayList[0] keys: {list(avl.keys())}")
                print(f"availablityStatusNew: {avl.get('availablityStatusNew')}")
                print(f"availablityDate: {avl.get('availablityDate')}")

            if "creationTime" in result:
                print(f"creationTime: {result['creationTime']}")

            if "totalFare" in result:
                print(f"totalFare: {result['totalFare']}")

    @pytest.mark.asyncio
    async def test_availability_with_different_quotas(self):
        """Test availability API with different quota types."""
        client = TrainApiClient()

        journey_date = (datetime.now() + timedelta(days=3)).strftime("%d/%m/%Y")
        quotas = [("GN", "General"), ("TQ", "Tatkal"), ("SS", "Senior Citizen"), ("LD", "Ladies")]

        print(f"\n=== Availability by Quota ===")
        print(f"Train: 12002 (Shatabdi)")
        print(f"Date: {journey_date}")

        for quota_code, quota_name in quotas:
            try:
                result = await client.check_availability(
                    train_no="12002",
                    class_code="CC",  # Chair Car
                    quota=quota_code,
                    from_station_code="NDLS",
                    to_station_code="BCT",
                    journey_date=journey_date,
                    from_display="New Delhi (NDLS)",
                    to_display="Bhopal Jn (BPL)"
                )

                status = "N/A"
                if isinstance(result, dict) and result.get("avlDayList"):
                    status = result["avlDayList"][0].get("availablityStatusNew", "N/A")

                print(f"  {quota_name} ({quota_code}): {status}")

            except Exception as e:
                print(f"  {quota_name} ({quota_code}): Error - {str(e)[:50]}")
