"""Hotel Cancellation Schemas - Input/Output models for all cancellation flow steps"""
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================
# Step 1: Guest Login
# ============================================================
class GuestLoginInput(BaseModel):
    """Input for guest login (Step 1)"""
    booking_id: str = Field(
        ...,
        description="Hotel booking reference ID (e.g., 'EMT1624718')",
    )
    email: str = Field(
        ...,
        description="Email address used during booking",
    )


class GuestLoginIds(BaseModel):
    """Response data from guest login"""
    transaction_id: Optional[str] = None
    transaction_screen_id: Optional[str] = None
    transaction_type: Optional[str] = None
    bid: str
    is_otp_send: Optional[str] = None
    message: Optional[str] = None


# ============================================================
# Step 2: Fetch Booking Details
# ============================================================
class FetchBookingDetailsInput(BaseModel):
    """Input for fetching booking details (Step 2)"""
    bid: str = Field(
        ...,
        description="Token returned from guest login (Ids.bid)",
    )


class RoomDetail(BaseModel):
    """Individual room from booking details"""
    room_id: Optional[str] = None
    room_type: Optional[str] = None
    room_no: Optional[str] = None
    transaction_id: Optional[str] = None
    cancellation_policy: Optional[str] = None
    is_pay_at_hotel: bool = False
    guest_name: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    hotel_name: Optional[str] = None
    amount: Optional[str] = None


class BookingDetailsResponse(BaseModel):
    """Structured booking details"""
    rooms: List[RoomDetail] = []
    payment_url: Optional[str] = None


# ============================================================
# Step 3: Send Cancellation OTP
# ============================================================
class SendCancellationOtpInput(BaseModel):
    """Input for sending cancellation OTP (Step 3)"""
    booking_id: str = Field(
        ...,
        description="Booking ID for session refresh (e.g., 'EMT1624718')",
    )
    email: str = Field(
        ...,
        description="Email for session refresh",
    )


# ============================================================
# Step 4: Request Cancellation
# ============================================================
class RequestCancellationInput(BaseModel):
    """Input for final cancellation request (Step 4)"""
    booking_id: str = Field(
        ...,
        description="Booking ID for session refresh (e.g., 'EMT1624718')",
    )
    email: str = Field(
        ...,
        description="Email for session refresh",
    )
    otp: str = Field(
        ...,
        description="OTP received by the user",
    )
    room_id: str = Field(
        ...,
        description="Room ID to cancel (from booking details)",
    )
    transaction_id: str = Field(
        ...,
        description="Transaction ID (from booking details)",
    )
    is_pay_at_hotel: bool = Field(
        default=False,
        description="Whether booking was pay-at-hotel",
    )
    payment_url: Optional[str] = Field(
        default="",
        description="Payment URL from booking details (Links.PaymentURL)",
    )
    reason: str = Field(
        default="Change of plans",
        description="Cancellation reason",
    )
    remark: str = Field(
        default="",
        description="Additional remarks for cancellation",
    )


# ============================================================
# Orchestrator Tool Input (standalone HTML mode)
# ============================================================
class HotelCancellationFlowInput(BaseModel):
    """Input for the standalone cancellation flow"""
    booking_id: str = Field(
        ...,
        description="Hotel booking reference ID",
    )
    email: str = Field(
        ...,
        description="Email address used during booking",
    )


# ============================================================
# WhatsApp Response Models
# ============================================================
class WhatsappCancellationFormat(BaseModel):
    type: str = "hotel_cancellation"
    status: str
    message: str
    booking_id: Optional[str] = None
    rooms: Optional[list] = None


class WhatsappCancellationFinalResponse(BaseModel):
    response_text: str
    whatsapp_json: WhatsappCancellationFormat
