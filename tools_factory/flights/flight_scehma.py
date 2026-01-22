from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class MultiCitySegment(BaseModel):
    """Single leg definition for a multi-city search."""

    origin: str = Field(
        ...,
        alias="org",
        description="Origin airport code for this leg (e.g., 'DEL')",
    )
    destination: str = Field(
        ...,
        alias="dept",
        description="Destination airport code for this leg (e.g., 'BOM')",
    )
    departure_date: str = Field(
        ...,
        alias="deptDT",
        description="Departure date for this leg in YYYY-MM-DD format",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

    @field_validator("origin", "destination")
    @classmethod
    def normalize_airport_code(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 3:
            raise ValueError("Airport code must be a 3-letter IATA code")
        return v

    @field_validator("departure_date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class FlightSearchInput(BaseModel):
    """Schema for flight search tool input."""

    origin: str = Field(
        ...,
        description="Origin airport code (e.g., 'DEL' for Delhi, 'BOM' for Mumbai)",
    )
    destination: str = Field(
        ...,
        description="Destination airport code (e.g., 'BOM' for Mumbai, 'DEL' for Delhi)",
    )
    outbound_date: str = Field(
        ...,
        alias="outboundDate",
        description="Outbound flight date in YYYY-MM-DD format",
    )
    return_date: Optional[str] = Field(
        None,
        alias="returnDate",
        description="Return flight date in YYYY-MM-DD format (optional for one-way)",
    )
    cabin: Optional[str] = Field(
        None,
        description="Cabin preference like economy, premium economy, business, or first"
    )
    is_multicity: bool = Field(
        False,
        description="Indicates if the trip is multi-city (True/False)",
    )
    multi_city_segments: Optional[List[MultiCitySegment]] = Field(
        None,
        alias="multiCitySegments",
        max_length=6,
        description=(
            "For multi-city searches, provide up to 6 legs as objects with org, dept, and deptDT"
        ),
    )
    
    adults: int = Field(1, ge=1, le=9)
    children: int = Field(0, ge=0, le=8)
    infants: int = Field(0, ge=0, le=8)

    model_config = ConfigDict(
        populate_by_name=True,  # accept both outbound_date & outboundDate
        extra="forbid",         # block unknown fields (VERY important for tools)
    )

    @field_validator("origin", "destination")
    @classmethod
    def normalize_airport_code(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 3:
            raise ValueError("Airport code must be a 3-letter IATA code")
        return v

    @field_validator("outbound_date", "return_date")
    @classmethod
    def validate_date(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v
    
    @field_validator("multi_city_segments")
    @classmethod
    def validate_multi_city_segments(cls, v: Optional[List[MultiCitySegment]]) -> Optional[List[MultiCitySegment]]:
        if v is None:
            return v

        if len(v) == 0:
            raise ValueError("Multi-city segments must include at least one item")

        if len(v) > 6:
            raise ValueError("Multi-city segments cannot exceed 6 legs")

        return v
    

class WhatsappFlightFormat(BaseModel):
        type: str = "flight_collection"
        options: list
        trip_type: str
        journey_type: str
        currency: str
        view_all_flights_url: str

class WhatsappFlightFinalResponse(BaseModel):
    response_text: str
    whatsapp_json: WhatsappFlightFormat
