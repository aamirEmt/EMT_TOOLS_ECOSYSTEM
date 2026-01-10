from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

import pytest

from emt_client.utils import extract_first_city_code_country
from tools_factory.flights.flight_search_service import _build_view_all_link
from tools_factory.factory import get_tool_factory


def test_extract_first_city_code_country_parses_city_format():
    suggestions = [{"City": "Delhi (DEL)", "Country": "India"}]
    code, country, name = extract_first_city_code_country(suggestions)
    assert code == "DEL"
    assert country == "India"
    assert name == "Delhi"


def test_extract_first_city_code_country_falls_back_fields():
    suggestions = [{"CityName": "DXB", "Country": "UAE"}]
    code, country, name = extract_first_city_code_country(suggestions)
    assert code == "DXB"
    assert country == "UAE"
    assert name == "DXB"


def test_extract_first_city_code_country_handles_empty_name():
    suggestions = [{"City": " (DEL)", "Country": "India"}]
    code, country, name = extract_first_city_code_country(suggestions)
    assert code == "DEL"
    assert country == "India"
    assert name == "(DEL)"


def test_build_view_all_link_oneway_domestic_short_link(monkeypatch):
    def fake_short_link(results, product_type):
        assert product_type == "flight"
        assert results[0]["deepLink"].startswith(
            "https://www.easemytrip.com/flight-search/listing?"
        )
        return [{"deepLink": "https://emt.bio/abc123"}]

    monkeypatch.setattr(
        "tools_factory.flights.flight_search_service.generate_short_link",
        fake_short_link,
    )

    search_context = {
        "origin": "DEL",
        "destination": "BOM",
        "origin_name": "Delhi",
        "destination_name": "Mumbai",
        "origin_country": "India",
        "destination_country": "India",
        "outbound_date": "2026-01-19",
        "return_date": None,
        "passengers": {"adults": 1, "children": 0, "infants": 0},
        "cabin": 0,
        "is_international": False,
    }

    view_all = _build_view_all_link(search_context)
    assert view_all == "https://emt.bio/abc123"


def test_build_view_all_link_roundtrip_international_raw_link(monkeypatch):
    def raise_short_link(results, product_type):
        raise RuntimeError("shortener offline")

    monkeypatch.setattr(
        "tools_factory.flights.flight_search_service.generate_short_link",
        raise_short_link,
    )

    search_context = {
        "origin": "DEL",
        "destination": "DXB",
        "origin_name": "Delhi",
        "destination_name": "Dubai",
        "origin_country": "India",
        "destination_country": "United Arab Emirates",
        "outbound_date": "2026-01-19",
        "return_date": "2026-01-24",
        "passengers": {"adults": 1, "children": 0, "infants": 0},
        "cabin": 0,
        "is_international": True,
    }

    view_all = _build_view_all_link(search_context)
    parsed = urlparse(view_all)
    params = parse_qs(parsed.query)

    assert parsed.netloc == "www.easemytrip.com"
    assert params["isow"] == ["false"]
    assert params["isdm"] == ["false"]
    assert params["px"] == ["1-0-0"]
    assert params["cbn"] == ["0"]
    assert (
        params["srch"][0]
        == "DEL-Delhi-India|DXB-Dubai-United Arab Emirates|19/01/2026-24/01/2026"
    )


def test_build_view_all_link_roundtrip_domestic_raw_link(monkeypatch):
    def raise_short_link(results, product_type):
        raise RuntimeError("shortener offline")

    monkeypatch.setattr(
        "tools_factory.flights.flight_search_service.generate_short_link",
        raise_short_link,
    )

    search_context = {
        "origin": "DEL",
        "destination": "BOM",
        "origin_name": "Delhi",
        "destination_name": "Mumbai",
        "origin_country": "India",
        "destination_country": "India",
        "outbound_date": "2026-01-19",
        "return_date": "2026-01-21",
        "passengers": {"adults": 2, "children": 1, "infants": 0},
        "cabin": 2,
        "is_international": False,
    }

    view_all = _build_view_all_link(search_context)
    parsed = urlparse(view_all)
    params = parse_qs(parsed.query)

    assert params["isow"] == ["false"]
    assert params["isdm"] == ["true"]
    assert params["px"] == ["2-1-0"]
    assert params["cbn"] == ["2"]
    assert params["srch"][0] == "DEL-Delhi-India|BOM-Mumbai-India|19/01/2026-21/01/2026"


def test_build_view_all_link_international_oneway_raw_link(monkeypatch):
    def raise_short_link(results, product_type):
        raise RuntimeError("shortener offline")

    monkeypatch.setattr(
        "tools_factory.flights.flight_search_service.generate_short_link",
        raise_short_link,
    )

    search_context = {
        "origin": "DEL",
        "destination": "DXB",
        "origin_name": "Delhi",
        "destination_name": "Dubai",
        "origin_country": "India",
        "destination_country": "United Arab Emirates",
        "outbound_date": "2026-01-19",
        "return_date": None,
        "passengers": {"adults": 1, "children": 0, "infants": 0},
        "cabin": 0,
        "is_international": True,
    }

    view_all = _build_view_all_link(search_context)
    params = parse_qs(urlparse(view_all).query)

    assert params["isow"] == ["true"]
    assert params["isdm"] == ["false"]
    assert params["srch"][0] == "DEL-Delhi-India|DXB-Dubai-United Arab Emirates|19/01/2026"


def test_build_view_all_link_passenger_defaults(monkeypatch):
    def raise_short_link(results, product_type):
        raise RuntimeError("shortener offline")

    monkeypatch.setattr(
        "tools_factory.flights.flight_search_service.generate_short_link",
        raise_short_link,
    )

    search_context = {
        "origin": "DEL",
        "destination": "BOM",
        "origin_name": "Delhi",
        "destination_name": "Mumbai",
        "origin_country": "India",
        "destination_country": "India",
        "outbound_date": "2026-01-19",
        "return_date": None,
        "passengers": {},
        "cabin": 0,
        "is_international": False,
    }

    view_all = _build_view_all_link(search_context)
    params = parse_qs(urlparse(view_all).query)
    assert params["px"] == ["1-0-0"]


def test_build_view_all_link_negative_passengers_clamped(monkeypatch):
    def raise_short_link(results, product_type):
        raise RuntimeError("shortener offline")

    monkeypatch.setattr(
        "tools_factory.flights.flight_search_service.generate_short_link",
        raise_short_link,
    )

    search_context = {
        "origin": "DEL",
        "destination": "BOM",
        "origin_name": "Delhi",
        "destination_name": "Mumbai",
        "origin_country": "India",
        "destination_country": "India",
        "outbound_date": "2026-01-19",
        "return_date": None,
        "passengers": {"adults": -2, "children": -1, "infants": -3},
        "cabin": 0,
        "is_international": False,
    }

    view_all = _build_view_all_link(search_context)
    params = parse_qs(urlparse(view_all).query)
    assert params["px"] == ["1-0-0"]


def test_build_view_all_link_falls_back_to_raw_link_on_empty_short_link(monkeypatch):
    def empty_short_link(results, product_type):
        return [{"deepLink": ""}]

    monkeypatch.setattr(
        "tools_factory.flights.flight_search_service.generate_short_link",
        empty_short_link,
    )

    search_context = {
        "origin": "DEL",
        "destination": "BOM",
        "origin_name": "Delhi",
        "destination_name": "Mumbai",
        "origin_country": "India",
        "destination_country": "India",
        "outbound_date": "2026-01-19",
        "return_date": None,
        "passengers": {"adults": 1, "children": 0, "infants": 0},
        "cabin": 0,
        "is_international": False,
    }

    view_all = _build_view_all_link(search_context)
    assert view_all.startswith("https://www.easemytrip.com/flight-search/listing?")


def test_build_view_all_link_date_passthrough(monkeypatch):
    def raise_short_link(results, product_type):
        raise RuntimeError("shortener offline")

    monkeypatch.setattr(
        "tools_factory.flights.flight_search_service.generate_short_link",
        raise_short_link,
    )

    search_context = {
        "origin": "DEL",
        "destination": "BOM",
        "origin_name": "Delhi",
        "destination_name": "Mumbai",
        "origin_country": "India",
        "destination_country": "India",
        "outbound_date": "19/01/2026",
        "return_date": None,
        "passengers": {"adults": 1, "children": 0, "infants": 0},
        "cabin": 0,
        "is_international": False,
    }

    view_all = _build_view_all_link(search_context)
    params = parse_qs(urlparse(view_all).query)
    assert params["srch"][0] == "DEL-Delhi-India|BOM-Mumbai-India|19/01/2026"


def test_build_view_all_link_location_fallbacks(monkeypatch):
    def raise_short_link(results, product_type):
        raise RuntimeError("shortener offline")

    monkeypatch.setattr(
        "tools_factory.flights.flight_search_service.generate_short_link",
        raise_short_link,
    )

    search_context = {
        "origin": "DEL",
        "destination": "BOM",
        "origin_name": "",
        "destination_name": "",
        "origin_country": "",
        "destination_country": "",
        "outbound_date": "2026-01-19",
        "return_date": None,
        "passengers": {"adults": 1, "children": 0, "infants": 0},
        "cabin": 0,
        "is_international": False,
    }

    view_all = _build_view_all_link(search_context)
    params = parse_qs(urlparse(view_all).query)
    assert params["srch"][0] == "DEL-DEL|BOM-BOM|19/01/2026"


def test_build_view_all_link_missing_required_fields(monkeypatch):
    def raise_short_link(results, product_type):
        raise AssertionError("shortener should not be called")

    monkeypatch.setattr(
        "tools_factory.flights.flight_search_service.generate_short_link",
        raise_short_link,
    )

    search_context = {
        "origin": "DEL",
        "destination": "BOM",
        "outbound_date": "",
    }

    assert _build_view_all_link(search_context) == ""


@pytest.mark.asyncio
@pytest.mark.integration
async def test_flight_view_all_real_api_domestic_oneway():
    factory = get_tool_factory()
    tool = factory.get_tool("search_flights")

    outbound = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    payload = {
        "origin": "DEL",
        "destination": "BOM",
        "outbound_date": outbound,
        "adults": 1,
    }

    result = await tool.execute(**payload)
    data = result["structured_content"]

    view_all = data.get("viewAll")
    assert view_all, "viewAll should be present in response"
    assert view_all.startswith("https://emt.bio/") or view_all.startswith(
        "https://www.easemytrip.com/flight-search/listing?"
    )
