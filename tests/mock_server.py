"""
Mock API server for interactive UI testing of the cancellation flow.

Serves fake API responses matching the real EaseMyTrip cancellation endpoints,
allowing full UI testing without touching real bookings.

Usage:
    python -m tests.mock_server
    # Or: python tests/mock_server.py
    # Then open tests/test_cancellation_ui_mock.html in a browser

Runs on http://localhost:8899
"""
import sys
import os
import copy

# Ensure project root is on sys.path so imports work when running directly
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from tests.mock_scenarios import (
    SCENARIOS,
    TRAIN_CANCEL_FAIL,
    BUS_CANCEL_FAIL,
    HOTEL_CANCEL_FAIL,
    FLIGHT_CANCEL_FAIL,
    _login_response,
    _verify_otp_success,
    _otp_send_success,
)
from tests.mock_cancellation_client import MockMyBookingsClient
from tools_factory.cancellation.cancellation_service import CancellationService

app = FastAPI(title="Cancellation Mock Server")

# Allow CORS for local HTML file testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Server state
# ============================================================
current_scenario: str = "hotel_happy_path"
call_log: list = []


def _get_scenario_data() -> dict:
    return copy.deepcopy(SCENARIOS.get(current_scenario, SCENARIOS["hotel_happy_path"]))


def _detect_module() -> str:
    """Detect hotel/train/bus/flight from current scenario name."""
    if current_scenario.startswith("flight"):
        return "Flight"
    if current_scenario.startswith("train"):
        return "Train"
    if current_scenario.startswith("bus"):
        return "Bus"
    # hotel_id_but_train scenario actually returns train
    scenario_data = SCENARIOS.get(current_scenario, {})
    login_resp = scenario_data.get("guest_login", {})
    ids = login_resp.get("Ids", {})
    return ids.get("TransactionType", "Hotel")


def _log_call(endpoint: str, body: dict, response: dict, status: int = 200):
    call_log.append({
        "endpoint": endpoint,
        "body": body,
        "response_status": status,
        "scenario": current_scenario,
    })


# ============================================================
# Mock control endpoints
# ============================================================
@app.post("/api/mock/set-scenario")
async def set_scenario(request: Request):
    global current_scenario
    body = await request.json()
    scenario = body.get("scenario", "hotel_happy_path")
    if scenario not in SCENARIOS:
        return JSONResponse(
            {"error": f"Unknown scenario: {scenario}", "available": list(SCENARIOS.keys())},
            status_code=400,
        )
    current_scenario = scenario
    return {"status": "ok", "scenario": current_scenario}


@app.get("/api/mock/scenarios")
async def list_scenarios():
    return {"scenarios": list(SCENARIOS.keys()), "current": current_scenario}


@app.get("/api/mock/call-log")
async def get_call_log():
    return {"calls": call_log}


@app.post("/api/mock/clear-log")
async def clear_log():
    global call_log
    call_log = []
    return {"status": "cleared"}


@app.get("/api/mock/booking-details-html")
async def get_booking_html():
    """
    Returns pre-rendered HTML for the current scenario's booking details.
    Uses CancellationService with MockMyBookingsClient to transform raw API
    data into the processed format the renderers expect, then renders HTML.
    """
    from tools_factory.cancellation.cancellation_renderer import (
        render_booking_details,
        render_train_booking_details,
        render_bus_booking_details,
        render_flight_booking_details,
    )

    module = _detect_module()
    bid = "MOCK_BID_123"
    booking_id = "MOCK_BOOKING"
    email = "test@mock.com"
    api_base_url = "http://localhost:8899"

    try:
        # Create a CancellationService with mock client injected
        svc = CancellationService()
        svc.client = MockMyBookingsClient(current_scenario)

        if module == "Flight":
            svc._booking_id = booking_id
            svc._email = email
            processed = await svc.fetch_flight_booking_details(bid)
            scenario_data = _get_scenario_data()
            login_resp = scenario_data.get("guest_login", {})
            is_otp_send = login_resp.get("Ids", {}).get("IsOtpSend", True)
            html = render_flight_booking_details(
                booking_details=processed,
                bid=bid,
                booking_id=booking_id,
                email=email,
                api_base_url=api_base_url,
                is_otp_send=is_otp_send,
            )
            return JSONResponse({"html": html, "module": module})

        if module == "Train":
            processed = await svc.fetch_train_booking_details(bid)
            html = render_train_booking_details(
                booking_details=processed,
                bid=bid,
                booking_id=booking_id,
                email=email,
                api_base_url=api_base_url,
            )
        elif module == "Bus":
            processed = await svc.fetch_bus_booking_details(bid)
            html = render_bus_booking_details(
                booking_details=processed,
                bid=bid,
                booking_id=booking_id,
                email=email,
                api_base_url=api_base_url,
            )
        else:
            processed = await svc.fetch_booking_details(bid)
            html = render_booking_details(
                booking_details=processed,
                bid=bid,
                booking_id=booking_id,
                email=email,
                api_base_url=api_base_url,
            )
        return JSONResponse({"html": html, "module": module})
    except Exception as e:
        import traceback
        return JSONResponse(
            {"error": str(e), "traceback": traceback.format_exc(), "module": module},
            status_code=500,
        )


# ============================================================
# Cancellation API endpoints (matching real chatbot routes)
# ============================================================

@app.post("/api/hotel-cancel/verify-otp")
async def verify_otp(request: Request):
    body = await request.json()
    scenario_data = _get_scenario_data()
    otp = body.get("otp", "")

    # Use scenario's verify response
    response = scenario_data.get("verify_guest_login_otp", _verify_otp_success())
    _log_call("/api/hotel-cancel/verify-otp", body, response)
    return response


@app.post("/api/hotel-cancel/send-otp")
async def send_otp(request: Request):
    body = await request.json()
    scenario_data = _get_scenario_data()

    # Determine correct OTP send method based on module
    module = _detect_module()
    if module == "Flight":
        response = scenario_data.get("send_flight_cancellation_otp", _otp_send_success())
    elif module == "Train":
        response = scenario_data.get("send_train_cancellation_otp", _otp_send_success())
    elif module == "Bus":
        response = scenario_data.get("send_bus_cancellation_otp", _otp_send_success())
    else:
        response = scenario_data.get("send_cancellation_otp", _otp_send_success())

    _log_call("/api/hotel-cancel/send-otp", body, response)
    return response


@app.post("/api/hotel-cancel/resend-login-otp")
async def resend_login_otp(request: Request):
    body = await request.json()
    scenario_data = _get_scenario_data()
    response = scenario_data.get("guest_login", _login_response())
    _log_call("/api/hotel-cancel/resend-login-otp", body, response)
    return {"status": True, "message": "OTP resent successfully"}


@app.post("/api/hotel-cancel/confirm")
async def confirm_cancellation(request: Request):
    body = await request.json()
    scenario_data = _get_scenario_data()
    module = _detect_module()

    if module == "Flight":
        raw_response = scenario_data.get("cancel_flight", FLIGHT_CANCEL_FAIL)
    elif module == "Train":
        raw_response = scenario_data.get("cancel_train", TRAIN_CANCEL_FAIL)
    elif module == "Bus":
        raw_response = scenario_data.get("cancel_bus", BUS_CANCEL_FAIL)
    else:
        raw_response = scenario_data.get("request_cancellation", HOTEL_CANCEL_FAIL)

    # Return direct API response (same format as real API)
    _log_call("/api/hotel-cancel/confirm", body, raw_response)
    return raw_response


@app.post("/api/hotel-cancel/flight-details")
async def flight_details(request: Request):
    """
    Fetch flight booking details after OTP verification.
    Returns rendered HTML for the full flight cancellation widget.
    Called by the flight template JS after successful login OTP verification.
    """
    from tools_factory.cancellation.cancellation_renderer import render_flight_booking_details

    body = await request.json()
    booking_id = body.get("booking_id", "MOCK_BOOKING")
    email = body.get("email", "test@mock.com")
    bid = "MOCK_BID_123"
    api_base_url = "http://localhost:8899"

    try:
        svc = CancellationService()
        svc.client = MockMyBookingsClient(current_scenario)
        svc._booking_id = booking_id
        svc._email = email

        processed = await svc.fetch_flight_booking_details(bid)
        html = render_flight_booking_details(
            booking_details=processed,
            bid=bid,
            booking_id=booking_id,
            email=email,
            api_base_url=api_base_url,
            is_otp_send=False,
        )
        _log_call("/api/hotel-cancel/flight-details", body, {"html": "(rendered)"})
        return JSONResponse({"html": html})
    except Exception as e:
        import traceback
        return JSONResponse(
            {"error": str(e), "traceback": traceback.format_exc()},
            status_code=500,
        )


# ============================================================
# Entry point
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  Cancellation Mock Server")
    print("  http://localhost:8899")
    print("  Scenarios:", list(SCENARIOS.keys()))
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8899)
