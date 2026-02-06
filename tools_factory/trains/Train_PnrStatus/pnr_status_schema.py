"""Pydantic schemas for PNR Status check tool."""

import re
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


class PnrStatusInput(BaseModel):
    """Schema for PNR status check input."""

    pnr_number: str = Field(
        ...,
        alias="pnrNumber",
        description="10-digit Indian Railways PNR number",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

    @field_validator("pnr_number")
    @classmethod
    def validate_pnr(cls, v: str) -> str:
        """Validate PNR is exactly 10 digits."""
        # Remove any spaces or hyphens
        cleaned = re.sub(r"[\s\-]", "", v)

        if not cleaned.isdigit():
            raise ValueError("PNR must contain only digits")

        if len(cleaned) != 10:
            raise ValueError("PNR must be exactly 10 digits")

        return cleaned


class PassengerInfo(BaseModel):
    """Individual passenger details from PNR status."""

    serial_number: int
    booking_status: str  # e.g., "CNF", "WL/10", "RAC/5", "NOSB"
    current_status: str  # e.g., "CNF", "WL/8", "CAN"
    coach: Optional[str] = None  # e.g., "S4"
    berth_number: Optional[str] = None  # e.g., "34"
    berth_type: Optional[str] = None  # e.g., "LB", "UB", "MB", "SL", "SU"


class PnrStatusInfo(BaseModel):
    """Complete PNR status response."""

    pnr_number: str
    train_number: str
    train_name: str
    date_of_journey: str
    source_station: str
    source_station_name: str
    destination_station: str
    destination_station_name: str
    boarding_point: Optional[str] = None
    boarding_point_name: Optional[str] = None
    reservation_upto: Optional[str] = None
    reservation_upto_name: Optional[str] = None
    journey_class: str  # e.g., "SL", "3A", "2A"
    class_name: Optional[str] = None  # e.g., "Sleeper Class"
    quota: str  # e.g., "GN", "TQ"
    quota_name: Optional[str] = None  # e.g., "General"
    booking_status: Optional[str] = None  # Overall booking status
    chart_status: str  # "Chart Not Prepared" or "Chart Prepared"
    booking_fare: Optional[str] = None
    ticket_fare: Optional[str] = None
    passengers: List[PassengerInfo]


class WhatsappPnrFormat(BaseModel):
    """WhatsApp-friendly format for PNR status."""

    type: str = "pnr_status"
    pnr_number: str
    train_info: str
    journey_date: str
    route: str
    journey_class: str
    chart_status: str
    passengers: List[dict]


class WhatsappPnrFinalResponse(BaseModel):
    """Final WhatsApp response for PNR status."""

    response_text: str
    whatsapp_json: WhatsappPnrFormat
