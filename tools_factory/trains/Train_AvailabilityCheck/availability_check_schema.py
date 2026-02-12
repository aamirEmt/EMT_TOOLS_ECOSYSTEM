"""Train Availability Check Schemas - Input/Output models for checking train availability across multiple classes"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class AvailabilityCheckInput(BaseModel):
    """Schema for checking train availability across classes."""

    train_no: str = Field(
        ...,
        alias="trainNo",
        description="Train number (e.g., '12963', '12816').",
    )

    journey_date: str = Field(
        ...,
        alias="journeyDate",
        description="Journey date in DD-MM-YYYY format",
    )

    classes: List[str] = Field(
        ...,
        description="List of class codes to check availability for. MUST use exact codes only: '1A' (First AC), '2A' (AC 2 Tier), '3A' (Third AC), 'SL' (Sleeper Class), '2S' (Second Seating), 'CC' (AC Chair Car), 'EC' (Executive Class), '3E' (AC 3 Tier Economy), 'FC' (First Class), 'EV' (Vistadome AC), 'VS' (Vistadome Non-AC), 'EA' (Anubhuti Class), 'VC' (Vistadome Chair Car). Do not use full names like 'Chair Car' or variations like '3AC' - use only the exact codes.",
    )

    quota: str = Field(
        default="GN",
        description="Booking quota (GN=General, TQ=Tatkal, SS=Senior Citizen, LD=Ladies)",
    )

    from_station_code: Optional[str] = Field(
        default=None,
        alias="fromStationCode",
        description="Origin station code (e.g., 'NDLS', 'BCT'). If not provided, will be fetched from train route.",
    )

    to_station_code: Optional[str] = Field(
        default=None,
        alias="toStationCode",
        description="Destination station code (e.g., 'HWH', 'PUNE'). If not provided, will be fetched from train route.",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

    @field_validator("journey_date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate date is in DD-MM-YYYY format."""
        if v is None:
            return v
        try:
            datetime.strptime(v, "%d-%m-%Y")
        except ValueError:
            raise ValueError("Date must be in DD-MM-YYYY format")
        return v

    @field_validator("classes")
    @classmethod
    def validate_classes(cls, v: List[str]) -> List[str]:
        """Validate and normalize class codes."""
        if not v or len(v) == 0:
            raise ValueError("At least one class must be specified")

        # Valid class codes
        valid_classes = {
            "1A", "2A", "3A", "SL", "2S", "CC", "EC", "3E",
            "FC", "EV", "VS", "EA", "VC"
        }

        # Normalize to uppercase and strip whitespace
        normalized = [c.upper().strip() for c in v]

        # Check for invalid classes
        invalid = [c for c in normalized if c not in valid_classes]
        if invalid:
            raise ValueError(
                f"Invalid class codes: {invalid}. "
                f"Valid classes are: {', '.join(sorted(valid_classes))}"
            )

        return normalized


class ClassAvailabilityInfo(BaseModel):
    """Availability info for a single class."""

    class_code: str = Field(..., description="Class code (e.g., '3A', 'SL')")
    status: str = Field(..., description="Availability status (e.g., 'AVAILABLE 120', 'WL 25', 'RAC/5')")
    fare: Optional[int] = Field(None, description="Total fare in INR")
    fare_updated: Optional[str] = Field(None, description="Timestamp when fare was last updated")

    @property
    def normalized_status(self) -> str:
        """
        Normalize status to standard categories.
        Returns: AVAILABLE, WAITLIST, RAC, NOT_AVAILABLE, or UNKNOWN
        """
        status_upper = self.status.upper()

        if "AVAILABLE" in status_upper and "NOT" not in status_upper:
            return "AVAILABLE"
        elif "WL" in status_upper or "WAITLIST" in status_upper:
            return "WAITLIST"
        elif "RAC" in status_upper:
            return "RAC"
        elif any(x in status_upper for x in ["REGRET", "NOT AVAILABLE", "CANCELLED"]):
            return "NOT_AVAILABLE"
        elif "ERROR" in status_upper:
            return "ERROR"
        else:
            return "UNKNOWN"


class TrainAvailabilityInfo(BaseModel):
    """Complete train availability response."""

    train_no: str
    train_name: str
    from_station_code: str
    to_station_code: str
    from_station_name: Optional[str] = None
    to_station_name: Optional[str] = None
    journey_date: str
    quota: str
    classes: List[ClassAvailabilityInfo]


class WhatsappAvailabilityFormat(BaseModel):
    """WhatsApp-friendly format for availability check (matches requirements)."""

    type: str = Field(default="all_class_availability")
    status: str = Field(default="RESULT")
    response_text: str
    data: Dict[str, Any]  # Contains train info and classes list


class WhatsappAvailabilityFinalResponse(BaseModel):
    """Final WhatsApp response wrapper."""

    response_text: str
    whatsapp_json: WhatsappAvailabilityFormat
