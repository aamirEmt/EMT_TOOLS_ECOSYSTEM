import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from emt_client.config import FLIGHT_BASE_URL, PAYMENT_CHECKOUT_BASE_URL
from emt_client.utils import gen_trace_id


class PriceLockService:
    """Service layer that reprices a flight and creates a price lock."""

    def __init__(self) -> None:
        self.reprice_endpoint = f"{FLIGHT_BASE_URL}/AirAvail_Lights/AirReprice_L"
        self.lock_endpoint = f"{FLIGHT_BASE_URL}/Book/GenrateTransactionWithReprice"
        self.checkout_base = PAYMENT_CHECKOUT_BASE_URL
        self._js_context = None

    def _load_js_context(self):
        """Load and cache the JS converter used to rebuild the segment payload."""
        try:
            from py_mini_racer import py_mini_racer
        except ImportError as exc:  # pragma: no cover - env dependency
            raise RuntimeError(
                "py-mini-racer is required for price locking. Install it with `pip install py-mini-racer`."
            ) from exc

        if self._js_context is None:
            js_path = Path(__file__).resolve().parent / "repricing_script.js"
            js_code = js_path.read_text(encoding="utf-8")
            ctx = py_mini_racer.MiniRacer()
            ctx.eval(js_code)
            self._js_context = ctx

        return self._js_context

    @staticmethod
    def _normalize_search_response(search_response: Dict[str, Any]) -> Dict[str, Any]:
        """Handle wrapped tool responses that might contain structured_content."""
        if "structured_content" in search_response and isinstance(
            search_response.get("structured_content"), dict
        ):
            return search_response["structured_content"]
        return search_response

    @staticmethod
    def _extract_raw_search(search_response: Dict[str, Any]) -> Dict[str, Any]:
        """Pull the raw EMT search response if available."""
        raw = search_response.get("raw")
        if isinstance(raw, dict):
            return raw
        return search_response

    @staticmethod
    def _build_raw_segment_map(raw_search: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        mapping: Dict[str, Dict[str, Any]] = {}
        for journey_index, journey in enumerate(raw_search.get("j", []) or []):
            for segment in journey.get("s", []) or []:
                seg_key = segment.get("SK")
                if seg_key:
                    mapping[seg_key] = {
                        "segment": segment,
                        "journey_index": journey_index,
                    }
        return mapping

    @staticmethod
    def _pick_flights(search_response: Dict[str, Any], direction: str) -> List[Dict[str, Any]]:
        """
        Pick flights based on direction, with fallbacks:
        - First try the requested direction list.
        - If empty, fall back to whichever list has flights.
        - If still empty, fall back to international combos (best-effort).
        """
        if direction == "return":
            flights = search_response.get("return_flights") or []
        else:
            flights = search_response.get("outbound_flights") or []

        if not flights:
            flights = (
                search_response.get("outbound_flights")
                or search_response.get("return_flights")
                or []
            )

        if not flights:
            flights = search_response.get("international_combos") or []

        return flights

    @staticmethod
    def _ensure_processed_flights(
        structured: Dict[str, Any],
        raw_search: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        If processed flight lists are missing, try to derive them from the raw search
        using the shared flight search processing logic. This mirrors the original
        lock_script behavior that depended on processed outbound flights.
        """
        has_outbound = bool(structured.get("outbound_flights"))
        has_return = bool(structured.get("return_flights"))
        if has_outbound or has_return:
            return structured

        try:
            from tools_factory.flights.flight_search_service import process_flight_results

            processed = process_flight_results(
                raw_search,
                structured.get("is_roundtrip", False),
                structured.get("is_international", False),
                structured,
            )
            structured.setdefault("outbound_flights", processed.get("outbound_flights", []))
            structured.setdefault("return_flights", processed.get("return_flights", []))
            structured.setdefault("international_combos", processed.get("international_combos", []))
        except Exception:
            # If processing fails, just return structured as-is; caller will error with a clear message.
            return structured

        return structured

    @staticmethod
    def _passenger_counts(search_response: Dict[str, Any]) -> Dict[str, int]:
        passengers = search_response.get("passengers") or {}
        try:
            adults = int(passengers.get("adults", 1) or 1)
        except Exception:
            adults = 1
        try:
            children = int(passengers.get("children", 0) or 0)
        except Exception:
            children = 0
        try:
            infants = int(passengers.get("infants", 0) or 0)
        except Exception:
            infants = 0
        return {"adults": adults, "children": children, "infants": infants}

    @staticmethod
    def _safe_fare_index(raw_segment: Dict[str, Any], requested_index: int) -> int:
        raw_fares = raw_segment.get("lstFr") or []
        if not raw_fares:
            return 0
        return min(max(requested_index, 0), max(len(raw_fares) - 1, 0))

    def _build_new_segment(
        self,
        *,
        raw_segment: Dict[str, Any],
        raw_search: Dict[str, Any],
        origin: str,
        destination: str,
        passengers: Dict[str, int],
        is_roundtrip: bool,
        fare_index: int,
    ) -> Dict[str, Any]:
        ctx = self._load_js_context()
        safe_index = self._safe_fare_index(raw_segment, fare_index)
        js_result = ctx.call(
            "ConvertSegFinal",
            raw_segment,
            raw_search,
            origin,
            destination,
            "",
            "",
            passengers["adults"],
            passengers["children"],
            passengers["infants"],
            "",
            is_roundtrip,
            safe_index,
        )
        if isinstance(js_result, str):
            return json.loads(js_result)
        if isinstance(js_result, dict):
            return js_result
        raise RuntimeError("Unexpected segment conversion result")

    @staticmethod
    def _build_reprice_payload(
        new_segment: Dict[str, Any],
        raw_search: Dict[str, Any],
        journey_index: int,
        passengers: Dict[str, int],
        login_key: str,
    ) -> Dict[str, Any]:
        lst_search_req: List[Dict[str, Any]] = []
        try:
            if raw_search.get("SQ"):
                lst_search_req = [raw_search.get("SQ", [])[journey_index]]
        except Exception:
            lst_search_req = []

        return {
            "Res": {
                "jrneys": [{"segs": [new_segment]}],
                "TraceID": gen_trace_id(),
                "lstSearchReq": lst_search_req,
                "adt": passengers["adults"],
                "chd": passengers["children"],
                "inf": passengers["infants"],
                "displayFareAmt": 0,
                "DisplayFareKey": "",
            },
            "RepriceStep": 1,
            "IsHD": "true",
            "LoginKey": login_key,
            "userid": "",
            "SegKey": "",
            "IPAddress": "",
            "adt": passengers["adults"],
            "chd": passengers["children"],
            "inf": passengers["infants"],
            "AgentCode": "",
            "IsWLAPP": "false",
            "brandFareKey": "",
            "cVID": "",
            "cID": "",
            "UUID": "",
        }

    @staticmethod
    def _extract_seg_key(reprice_response: Dict[str, Any]) -> Optional[str]:
        journeys = reprice_response.get("jrneys") or reprice_response.get("journeys") or []
        if not journeys:
            return None
        segments = journeys[0].get("segs") or journeys[0].get("Segments") or []
        if not segments:
            return None
        return (
            segments[0].get("segKey")
            or segments[0].get("SegKey")
            or segments[0].get("segment_key")
        )

    @staticmethod
    def _extract_lock_amount(
        reprice_response: Dict[str, Any],
        fallback_fare: Optional[float],
    ) -> float:
        journeys = reprice_response.get("jrneys") or []
        segments = journeys[0].get("segs") if journeys else None
        fare = {}
        if segments and isinstance(segments, list) and segments:
            fare = segments[0].get("Fare") or {}
        raw_amount = (
            fare.get("TtlFrWthMkp")
            or fare.get("TtlFr")
            or fare.get("TTLFr")
            or fallback_fare
            or 0
        )
        try:
            return float(raw_amount)
        except Exception:
            return float(fallback_fare or 0)

    @staticmethod
    def _fallback_fare_from_flight(selected_flight: Dict[str, Any], fare_index: int) -> Optional[float]:
        fares = selected_flight.get("fare_options") or []
        if not fares:
            return None
        if fare_index < 0 or fare_index >= len(fares):
            return float(fares[0].get("total_fare", 0) or fares[0].get("base_fare", 0) or 0)
        return float(fares[fare_index].get("total_fare", 0) or fares[fare_index].get("base_fare", 0) or 0)

    @staticmethod
    def _build_lock_payload(seg_key: str, login_key: str, lock_amount: float) -> Dict[str, Any]:
        return {
            "IsLock": True,
            "LockAmount": lock_amount,
            "LockPeriod": "8Hours",
            "SegKey": seg_key,
            "LoginKey": login_key,
            "TransRefId": "",
            "IpAddress": "",
            "IsWLAPP": False,
            "cVID": "",
            "cID": "",
            "Travs": {
                "AdtTrv": [{"EmlAdd": "", "LName": "", "fName": "", "Title": ""}],
                "ChdTrv": [],
                "InfTrv": [],
            },
        }

    @staticmethod
    async def _post_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            if not response.text:
                return {}
            return response.json()

    async def lock_price(
        self,
        *,
        login_key: str,
        flight_index: int,
        fare_index: int,
        search_response: Dict[str, Any],
        direction: str,
    ) -> Dict[str, Any]:
        """Run reprice + lock for a selected flight."""
        structured = self._normalize_search_response(search_response)
        raw_search = self._extract_raw_search(structured)
        structured = self._ensure_processed_flights(structured, raw_search)
        flights = self._pick_flights(structured, direction)

        if not flights:
            raise ValueError(f"No flights found for direction '{direction}'.")

        if flight_index < 0 or flight_index >= len(flights):
            raise IndexError(f"flight_index {flight_index} is out of range. Available flights: {len(flights)}")

        selected_flight = flights[flight_index]
        segment_key = selected_flight.get("segment_key") or selected_flight.get("segmentKey")
        if not segment_key:
            raise ValueError("Selected flight is missing a segment key needed for repricing.")

        raw_segment_map = self._build_raw_segment_map(raw_search)
        if segment_key not in raw_segment_map:
            raise ValueError("Raw segment data not found for the selected flight.")

        raw_info = raw_segment_map[segment_key]
        passengers = self._passenger_counts(structured)
        is_roundtrip = bool(structured.get("is_roundtrip"))

        new_segment = self._build_new_segment(
            raw_segment=raw_info["segment"],
            raw_search=raw_search,
            origin=selected_flight.get("origin") or structured.get("origin") or "",
            destination=selected_flight.get("destination") or structured.get("destination") or "",
            passengers=passengers,
            is_roundtrip=is_roundtrip,
            fare_index=fare_index,
        )

        reprice_payload = self._build_reprice_payload(
            new_segment,
            raw_search,
            raw_info["journey_index"],
            passengers,
            login_key,
        )
        reprice_response = await self._post_json(self.reprice_endpoint, reprice_payload)

        seg_key_repriced = self._extract_seg_key(reprice_response)
        if not seg_key_repriced:
            raise RuntimeError("Reprice response did not return a segKey.")

        lock_amount = self._extract_lock_amount(
            reprice_response,
            self._fallback_fare_from_flight(selected_flight, fare_index),
        )

        lock_payload = self._build_lock_payload(seg_key_repriced, login_key, lock_amount)
        lock_response = await self._post_json(self.lock_endpoint, lock_payload)

        price_lock_id = lock_response.get("PriceLockID") or lock_response.get("PriceLockId")
        checkout_url = (
            f"{self.checkout_base}?orderid={price_lock_id}" if price_lock_id else None
        )

        return {
            "selectedFlightIndex": flight_index,
            "fareIndex": fare_index,
            "direction": direction,
            "journeyIndex": raw_info["journey_index"],
            "segKey": seg_key_repriced,
            "lockAmount": lock_amount,
            "priceLockId": price_lock_id,
            "checkoutUrl": checkout_url,
            "repriceResponse": reprice_response,
            "lockResponse": lock_response,
            "selectedFlight": selected_flight,
        }
