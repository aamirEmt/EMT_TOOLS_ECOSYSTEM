"""Refund Status Schema"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RefundStatusInput(BaseModel):
    """Schema for refund status tool input."""

    email: str = Field(
        ...,
        description="User's registered email address associated with the booking",
    )
    booking_id: str = Field(
        ...,
        alias="bookingId",
        description="The booking/transaction ID to check refund status for",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )


class WhatsappRefundStatusFormat(BaseModel):
    """WhatsApp response format for refund status."""

    type: str = "refund_status"
    booking_id: str
    product_type: str
    trip_status: str
    refund_status: str
