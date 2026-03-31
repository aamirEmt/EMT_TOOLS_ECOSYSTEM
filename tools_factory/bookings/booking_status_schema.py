"""Booking Status Schema"""
from pydantic import BaseModel, Field, ConfigDict


class BookingStatusInput(BaseModel):
    """Schema for booking status tool input."""

    email: str = Field(
        ...,
        description="User's registered email address associated with the booking",
    )
    booking_id: str = Field(
        ...,
        alias="bookingId",
        description="The booking/transaction ID to check status for",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )


class WhatsappBookingStatusFormat(BaseModel):
    """WhatsApp response format for booking status."""

    type: str = "booking_status"
    booking_id: str
    product_type: str
    trip_status: str
