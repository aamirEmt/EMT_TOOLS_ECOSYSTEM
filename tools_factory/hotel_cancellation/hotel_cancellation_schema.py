"""Hotel Cancellation Schemas - Unified input model for cancellation tool"""
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================
# Unified Input Schema
# ============================================================
class HotelCancellationInput(BaseModel):
    """Unified input for hotel cancellation tool"""
    action: str = Field(
        ...,
        description="Action to perform: 'start' (login + fetch details), 'send_otp', or 'confirm' (submit cancellation)",
    )
    booking_id: str = Field(
        ...,
        description="Hotel booking reference ID (e.g., 'EMT1624718')",
    )
    email: str = Field(
        ...,
        description="Email address used during booking",
    )
    # Fields required only for action="confirm"
    otp: Optional[str] = Field(
        default=None,
        description="OTP received by the user (required for 'confirm')",
    )
    room_id: Optional[str] = Field(
        default=None,
        description="Room ID to cancel (required for 'confirm')",
    )
    transaction_id: Optional[str] = Field(
        default=None,
        description="Transaction ID (required for 'confirm')",
    )
    is_pay_at_hotel: bool = Field(
        default=False,
        description="Whether booking was pay-at-hotel",
    )
    payment_url: Optional[str] = Field(
        default="",
        description="Payment URL from booking details",
    )
    reason: str = Field(
        default="Change of plans",
        description="Cancellation reason",
    )
    remark: str = Field(
        default="",
        description="Additional remarks",
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
