from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class TrainSearchInput(BaseModel):
    """Schema for train search tool input."""

    from_station: str = Field(
        ...,
        alias="fromStation",
        description="Origin station name with code (e.g., 'Delhi All Stations (NDLS)', 'Mumbai Central (MMCT)')",
    )
    to_station: str = Field(
        ...,
        alias="toStation",
        description="Destination station name with code (e.g., 'Vaishno Devi Katra (SVDK)', 'Chennai Central (MAS)')",
    )
    journey_date: str = Field(
        ...,
        alias="journeyDate",
        description="Journey date in YYYY-MM-DD format",
    )
    travel_class: Optional[str] = Field(
        None,
        alias="travelClass",
        description="Preferred travel class (e.g., '1A', '2A', '3A', 'SL', '2S', 'CC')",
    )
    quota: Optional[str] = Field(
        "GN",
        description="Booking quota (GN=General, TQ=Tatkal, SS=Senior Citizen, LD=Ladies)",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

    @field_validator("journey_date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class TrainClassAvailability(BaseModel):
    """Availability info for a specific class."""
    class_code: str
    class_name: str
    fare: str
    availability_status: str
    fare_updated: Optional[str] = None
    book_now: Optional[str] = None


class TrainInfo(BaseModel):
    """Processed train information."""
    train_number: str
    train_name: str
    from_station_code: str
    from_station_name: str
    to_station_code: str
    to_station_name: str
    departure_time: str
    arrival_time: str
    duration: str
    distance: str
    departure_date: str
    arrival_date: str
    running_days: List[str]
    classes: List[TrainClassAvailability]


class WhatsappTrainFormat(BaseModel):
    type: str = "train_collection"
    options: list
    journey_type: str = "train"
    currency: str = "INR"
    view_all_trains_url: str = ""


class WhatsappTrainFinalResponse(BaseModel):
    response_text: str
    whatsapp_json: WhatsappTrainFormat
