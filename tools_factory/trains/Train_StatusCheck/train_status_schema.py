"""Schema definitions for Train Status Check tool."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class TrainStatusInput(BaseModel):
    """Schema for train status tool input."""

    train_number: str = Field(
        ...,
        alias="trainNumber",
        description="Indian Railways train number (e.g., '12618' for Karnataka Express)",
    )
    journey_date: Optional[str] = Field(
        None,
        alias="journeyDate",
        description="Journey date in DD-MM-YYYY format. If not provided, will show available dates.",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

    @field_validator("train_number")
    @classmethod
    def validate_train_number(cls, v: str) -> str:
        """Validate train number is numeric and reasonable length."""
        v = v.strip()
        if not v.isdigit():
            raise ValueError("Train number must contain only digits")
        if len(v) < 4 or len(v) > 6:
            raise ValueError("Train number must be 4-6 digits")
        return v

    @field_validator("journey_date")
    @classmethod
    def validate_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format DD-MM-YYYY."""
        if v is None:
            return v
        try:
            datetime.strptime(v, "%d-%m-%Y")
        except ValueError:
            raise ValueError("Date must be in DD-MM-YYYY format")
        return v


class TrainDateInfo(BaseModel):
    """Available trackable date information."""

    date: str  # DD-MM-YYYY format
    day_name: str  # e.g., "Wednesday"
    formatted_date: str  # e.g., "29 Jan 2026"
    display_day: Optional[str] = None  # e.g., "Today", "Yesterday", "Tomorrow"


class StationSchedule(BaseModel):
    """Schedule information for a single station."""

    station_code: str
    station_name: str
    arrival_time: Optional[str] = None  # "HH:MM" or "--" for origin
    departure_time: Optional[str] = None  # "HH:MM" or "--" for destination
    halt_time: Optional[str] = None  # e.g., "2 min" or "--"
    day: int = 1  # Day number (1, 2, 3...)
    distance: Optional[str] = None  # Distance from origin in km
    platform: Optional[str] = None
    is_origin: bool = False
    is_destination: bool = False
    # Live tracking fields
    actual_arrival: Optional[str] = None  # Actual arrival time when live
    actual_departure: Optional[str] = None  # Actual departure time when live
    delay_arrival: Optional[str] = None  # e.g., "05M Late", "1H 20M Late"
    delay_departure: Optional[str] = None  # e.g., "53M Late"
    is_current_station: bool = False  # Train is currently at this station
    is_next_station: bool = False  # This is the next station


class TrainDetails(BaseModel):
    """Train details from API response."""

    train_number: str
    train_name: str
    train_type: Optional[str] = None
    total_halts: Optional[str] = None
    running_days: Optional[str] = None  # e.g., "0000010" for specific days


class TrainStatusResponse(BaseModel):
    """Complete train status response."""

    train_number: str
    train_name: str
    train_type: Optional[str] = None
    runs_on: List[str] = []  # ["Mon", "Tue", ...]
    origin_station: str
    origin_code: str
    destination_station: str
    destination_code: str
    departure_time: str
    arrival_time: str
    total_distance: Optional[str] = None
    journey_duration: Optional[str] = None
    journey_date: str
    formatted_date: str
    stations: List[StationSchedule]
    total_halts: int


class WhatsappStationInfo(BaseModel):
    """Simplified station info for WhatsApp response."""

    code: str
    name: str
    arrival: Optional[str] = None
    departure: Optional[str] = None
    day: int = 1


class WhatsappTrainStatusFormat(BaseModel):
    """WhatsApp formatted train status."""

    type: str = "train_status"
    train_number: str
    train_name: str
    journey_date: str
    origin: str
    origin_code: str
    destination: str
    destination_code: str
    departure_time: str
    arrival_time: str
    total_stations: int
    stations: List[WhatsappStationInfo]


class WhatsappTrainStatusFinalResponse(BaseModel):
    """Final WhatsApp response wrapper."""

    response_text: str
    whatsapp_json: WhatsappTrainStatusFormat
