"""Booking schemas"""
from pydantic import BaseModel


class GetBookingsInput(BaseModel):
    """Schema for get bookings - no input needed"""
    pass
