"""Hotel Cancellation Tools - Individual step tools + standalone orchestrator"""
from typing import Dict, Any
import logging
from pydantic import ValidationError

from ..base import BaseTool, ToolMetadata
from ..base_schema import ToolResponseFormat
from .hotel_cancellation_schema import (
    GuestLoginInput,
    FetchBookingDetailsInput,
    SendCancellationOtpInput,
    RequestCancellationInput,
    HotelCancellationFlowInput,
)
from .hotel_cancellation_service import HotelCancellationService
from .hotel_cancellation_renderer import render_booking_details

logger = logging.getLogger(__name__)


# ============================================================
# Shared Service Instance (maintains session across tool calls)
# ============================================================
_shared_service = None


def get_shared_service() -> HotelCancellationService:
    """Get or create the shared service instance for session persistence"""
    global _shared_service
    if _shared_service is None:
        _shared_service = HotelCancellationService()
    return _shared_service


# ============================================================
# Step 1: Guest Login
# ============================================================
class HotelCancellationGuestLoginTool(BaseTool):
    """Step 1: Guest login with booking ID + email"""

    def __init__(self):
        super().__init__()
        self.service = get_shared_service()

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="hotel_cancellation_guest_login",
            description=(
                "Step 1 of hotel cancellation: Authenticate as a guest using "
                "booking ID (BetId like EMT1624718) and email. Returns a bid "
                "token needed for all subsequent cancellation steps."
            ),
            input_schema=GuestLoginInput.model_json_schema(),
            category="cancellation",
            tags=["hotel", "cancellation", "login", "guest"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        kwargs.pop("_user_type", "website")
        kwargs.pop("_limit", None)

        try:
            input_data = GuestLoginInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid input for guest login",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        result = await self.service.guest_login(
            booking_id=input_data.booking_id,
            email=input_data.email,
        )

        if not result["success"]:
            return ToolResponseFormat(
                response_text=f"Guest login failed: {result['message']}",
                structured_content=result,
                is_error=True,
            )

        return ToolResponseFormat(
            response_text=(
                f"Guest login successful. Bid token obtained. "
                f"Proceed to fetch booking details using the bid token."
            ),
            structured_content=result,
        )


# ============================================================
# Step 2: Fetch Booking Details
# ============================================================
class HotelCancellationFetchDetailsTool(BaseTool):
    """Step 2: Fetch booking details (rooms, policies)"""

    def __init__(self):
        super().__init__()
        self.service = get_shared_service()

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="hotel_cancellation_fetch_details",
            description=(
                "Step 2 of hotel cancellation: Fetch booking details including "
                "hotel name, address, check-in/out dates, cancellation policy, "
                "and list of rooms. Requires bid token from Step 1 (guest login)."
            ),
            input_schema=FetchBookingDetailsInput.model_json_schema(),
            category="cancellation",
            tags=["hotel", "cancellation", "booking", "details"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        kwargs.pop("_user_type", "website")
        kwargs.pop("_limit", None)

        try:
            input_data = FetchBookingDetailsInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid input for booking details fetch",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        result = await self.service.fetch_booking_details(bid=input_data.bid)

        if not result["success"]:
            return ToolResponseFormat(
                response_text=f"Failed to fetch booking details: {result.get('error')}",
                structured_content=result,
                is_error=True,
            )

        rooms = result.get("rooms", [])
        room_lines = []
        for r in rooms:
            line = f"  - Room {r.get('room_no', 'N/A')}: {r.get('room_type', 'N/A')} (ID: {r.get('room_id')})"
            if r.get("cancellation_policy"):
                line += f" | Policy: {r['cancellation_policy']}"
            if r.get("amount"):
                line += f" | Amount: {r['amount']}"
            room_lines.append(line)

        text = (
            f"Booking has {len(rooms)} room(s):\n"
            + "\n".join(room_lines)
            + "\n\nAsk user which room(s) to cancel and the reason, then proceed to send OTP."
        )

        return ToolResponseFormat(
            response_text=text,
            structured_content=result,
        )


# ============================================================
# Step 3: Send Cancellation OTP
# ============================================================
class HotelCancellationSendOtpTool(BaseTool):
    """Step 3: Send cancellation OTP"""

    def __init__(self):
        super().__init__()
        self.service = get_shared_service()

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="hotel_cancellation_send_otp",
            description=(
                "Step 3 of hotel cancellation: Send OTP for cancellation "
                "verification. Requires booking_id and email (auto-refreshes "
                "session). Call this after user selects room(s) and provides "
                "a cancellation reason."
            ),
            input_schema=SendCancellationOtpInput.model_json_schema(),
            category="cancellation",
            tags=["hotel", "cancellation", "otp"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        kwargs.pop("_user_type", "website")
        kwargs.pop("_limit", None)

        try:
            input_data = SendCancellationOtpInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid input for OTP request",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        result = await self.service.send_cancellation_otp(
            booking_id=input_data.booking_id,
            email=input_data.email,
        )

        if not result["success"]:
            return ToolResponseFormat(
                response_text=f"Failed to send OTP: {result['message']}",
                structured_content=result,
                is_error=True,
            )

        return ToolResponseFormat(
            response_text=f"OTP sent successfully. {result['message']} Ask the user for the OTP.",
            structured_content=result,
        )


# ============================================================
# Step 4: Request Cancellation
# ============================================================
class HotelCancellationRequestTool(BaseTool):
    """Step 4: Submit cancellation request"""

    def __init__(self):
        super().__init__()
        self.service = get_shared_service()

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="hotel_cancellation_request",
            description=(
                "Step 4 of hotel cancellation: Submit the final cancellation "
                "request with OTP, room ID, transaction ID, reason, and remark. "
                "Requires booking_id and email (auto-refreshes session)."
            ),
            input_schema=RequestCancellationInput.model_json_schema(),
            category="cancellation",
            tags=["hotel", "cancellation", "request", "confirm"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        kwargs.pop("_user_type", "website")
        kwargs.pop("_limit", None)

        try:
            input_data = RequestCancellationInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid cancellation request input",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        result = await self.service.request_cancellation(
            booking_id=input_data.booking_id,
            email=input_data.email,
            otp=input_data.otp,
            room_id=input_data.room_id,
            transaction_id=input_data.transaction_id,
            is_pay_at_hotel=input_data.is_pay_at_hotel,
            payment_url=input_data.payment_url or "",
            reason=input_data.reason,
            remark=input_data.remark,
        )

        if not result["success"]:
            return ToolResponseFormat(
                response_text=f"Cancellation failed: {result['message']}",
                structured_content=result,
                is_error=True,
            )

        refund_text = ""
        if result.get("refund_info"):
            ri = result["refund_info"]
            refund_text = (
                f"\nRefund amount: {ri.get('refund_amount', 'N/A')}"
                f"\nCancellation charges: {ri.get('cancellation_charges', 'N/A')}"
            )

        return ToolResponseFormat(
            response_text=f"Cancellation successful! {result['message']}{refund_text}",
            structured_content=result,
        )


# ============================================================
# Combined Flow Tool (standalone + chatbot shortcut)
# ============================================================
class HotelCancellationFlowTool(BaseTool):
    """
    Complete hotel booking cancellation flow.

    Website mode: Returns interactive HTML/JS application for the full flow.
    Chatbot/WhatsApp mode: Runs Steps 1+2 (login + fetch details) and returns
    room list for user selection.
    """

    def __init__(self):
        super().__init__()
        self.service = get_shared_service()

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="hotel_cancellation_flow",
            description=(
                "Complete hotel booking cancellation flow for chatbots. "
                "Automatically authenticates guest and fetches booking details. "
                "Returns room information for user selection. "
                "Use _user_type='website' only for HTML UI testing. "
                "Requires booking ID (BetId like EMT1624718) and email address."
            ),
            input_schema=HotelCancellationFlowInput.model_json_schema(),
            category="cancellation",
            tags=["hotel", "cancellation", "flow", "interactive"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        user_type = kwargs.pop("_user_type", "chatbot")
        kwargs.pop("_limit", None)
        render_html = user_type.lower() == "website"
        is_whatsapp = user_type.lower() == "whatsapp"

        try:
            input_data = HotelCancellationFlowInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid input for cancellation flow",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        # Website mode: fetch booking details and render as display-only HTML
        if render_html:
            # Run login + fetch details (same as chatbot mode)
            login_result = await self.service.guest_login(
                booking_id=input_data.booking_id,
                email=input_data.email,
            )

            if not login_result["success"]:
                return ToolResponseFormat(
                    response_text=f"Guest login failed: {login_result['message']}",
                    structured_content=login_result,
                    is_error=True,
                )

            bid = login_result["ids"]["bid"]
            details_result = await self.service.fetch_booking_details(bid=bid)

            if not details_result["success"]:
                return ToolResponseFormat(
                    response_text=f"Failed to fetch booking details: {details_result.get('error')}",
                    structured_content=details_result,
                    is_error=True,
                )

            # Add booking_id to details for display
            details_result["booking_id"] = input_data.booking_id

            # Render booking details as HTML carousel
            html = render_booking_details(details_result)

            return ToolResponseFormat(
                response_text=f"Booking details for {input_data.booking_id}",
                structured_content={
                    "booking_details": details_result,
                    "bid": bid,
                },
                html=html,
            )

        # Chatbot/WhatsApp mode: auto-run Step 1 + Step 2
        login_result = await self.service.guest_login(
            booking_id=input_data.booking_id,
            email=input_data.email,
        )

        if not login_result["success"]:
            return ToolResponseFormat(
                response_text=f"Guest login failed: {login_result['message']}",
                structured_content=login_result,
                is_error=True,
            )

        bid = login_result["ids"]["bid"]
        details_result = await self.service.fetch_booking_details(bid=bid)

        combined = {
            "login": login_result,
            "booking_details": details_result,
            "bid": bid,
        }

        if not details_result["success"]:
            return ToolResponseFormat(
                response_text=f"Login succeeded but failed to fetch details: {details_result.get('error')}",
                structured_content=combined,
                is_error=True,
            )

        rooms = details_result.get("rooms", [])
        room_lines = []
        for r in rooms:
            line = f"  - Room {r.get('room_no', 'N/A')}: {r.get('room_type', 'N/A')} (ID: {r.get('room_id')})"
            if r.get("cancellation_policy"):
                line += f" | Policy: {r['cancellation_policy']}"
            if r.get("amount"):
                line += f" | Amount: {r['amount']}"
            room_lines.append(line)

        text = (
            f"Booking authenticated. Found {len(rooms)} room(s):\n"
            + "\n".join(room_lines)
            + "\n\nWhich room would you like to cancel? Please also provide a reason."
        )

        whatsapp_response = None
        if is_whatsapp:
            from .hotel_cancellation_schema import (
                WhatsappCancellationFormat,
                WhatsappCancellationFinalResponse,
            )
            whatsapp_response = WhatsappCancellationFinalResponse(
                response_text=text,
                whatsapp_json=WhatsappCancellationFormat(
                    type="hotel_cancellation",
                    status="booking_details",
                    message=text,
                    booking_id=input_data.booking_id,
                    rooms=[
                        {
                            "room_id": r.get("room_id"),
                            "room_type": r.get("room_type"),
                            "room_no": r.get("room_no"),
                        }
                        for r in rooms
                    ],
                ),
            )

        return ToolResponseFormat(
            response_text=text,
            structured_content=combined,
            whatsapp_response=(
                whatsapp_response.model_dump() if whatsapp_response else None
            ),
        )
