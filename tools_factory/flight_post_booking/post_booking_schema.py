"""Input schema for flight post-booking workflow."""
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr


class FlightPostBookingInput(BaseModel):
    """Validate inputs for sending and verifying OTP for post-booking actions."""

    action: Literal["start", "verify_otp"] = Field(
        ...,
        description="Workflow step to perform. Use 'start' to send OTP and 'verify_otp' to validate it.",
    )
    booking_id: str = Field(
        ...,
        description="Flight booking reference or PNR.",
        min_length=3,
    )
    email: str = Field(
        ...,
        description="Email address used for the booking.",
    )
    otp: Optional[str] = Field(
        None,
        description="One-time password received by the user (required when action='verify_otp').",
        min_length=4,
        max_length=10,
    )
    download: Optional[bool] = Field(
        False,
        description="Necessary set this to True if user wants to or intends Download ticket after OTP verification. or ",
    )
