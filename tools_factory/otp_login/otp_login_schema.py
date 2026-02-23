"""OTP Login Input Schema"""
from typing import Optional
from pydantic import BaseModel, Field


class OtpLoginInput(BaseModel):

    action: str = Field(
        ...,
        description="Action to perform: 'send_otp' to send OTP to phone/email, or 'verify_otp' to verify the received OTP"
    )
    phone_or_email: Optional[str] = Field(
        None,
        description="User phone number or email address (required for send_otp action)"
    )
    otp_code: Optional[str] = Field(
        None,
        description="The OTP code received by the user (required for verify_otp action)"
    )
