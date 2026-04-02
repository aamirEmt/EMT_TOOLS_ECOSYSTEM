"""Booking schemas"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class GetBookingsInput(BaseModel):
    """Schema for get bookings"""
    status: Optional[str] = Field(
        None,
        description="Filter bookings by status. MUST be one of: 'Upcoming', 'Completed', 'Cancelled'. Any other value is invalid. If not provided, all bookings are returned.",
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip().capitalize()
        valid_statuses = ["Upcoming", "Completed", "Cancelled"]
        if v not in valid_statuses:
            return None
        return v
