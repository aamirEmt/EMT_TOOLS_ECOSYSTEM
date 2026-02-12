"""Cancellation Schemas - Unified input model for cancellation tool"""
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================
# Unified Input Schema
# ============================================================
class CancellationInput(BaseModel):
    """Unified input for cancellation tool"""
    action: str = Field(
        ...,
        description="Action to perform: 'start' (login + fetch details), 'verify_otp' (verify guest login OTP), 'send_otp' (send cancellation OTP), or 'confirm' (submit cancellation)",
    )
    booking_id: str = Field(
        ...,
        description="Booking reference ID (e.g., 'EMT1624718')",
    )
    email: str = Field(
        ...,
        description="Email address used during booking",
    )
    # Fields for action="confirm" (common + module-specific)
    otp: Optional[str] = Field(
        default=None,
        description="OTP received by the user (required for 'verify_otp' and 'confirm')",
    )
    room_id: Optional[str] = Field(
        default=None,
        description="Room ID to cancel (required for hotel 'confirm')",
    )
    transaction_id: Optional[str] = Field(
        default=None,
        description="Transaction ID (required for hotel 'confirm')",
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
    # Train-specific fields for action="confirm"
    pax_ids: Optional[List[str]] = Field(
        default=None,
        description="Selected passenger IDs for train cancellation (e.g., ['canidout(1)', 'canidout(2)'])",
    )
    reservation_id: Optional[str] = Field(
        default=None,
        description="Train reservation ID (required for train 'confirm')",
    )
    pnr_number: Optional[str] = Field(
        default=None,
        description="Train PNR number (required for train 'confirm')",
    )
    total_passenger: Optional[int] = Field(
        default=None,
        description="Total passengers to cancel (required for train 'confirm')",
    )


# ============================================================
# WhatsApp Response Models
# ============================================================
class WhatsappCancellationFormat(BaseModel):
    type: str = "cancellation"
    status: str
    message: str
    booking_id: Optional[str] = None
    rooms: Optional[list] = None
    passengers: Optional[list] = None
    transaction_type: Optional[str] = None


class WhatsappCancellationFinalResponse(BaseModel):
    response_text: str
    whatsapp_json: WhatsappCancellationFormat
