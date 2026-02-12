from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


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
    stops: int = Field(
        None,
        description="Flight stop preference only if specified: 0(for non-stop), 1(stop), or 2(stops)"
    )
    
    adults: int = Field(1, ge=1, le=9, description="Number of adults (1-9). Cannot be null or None, defaults to 1.")
    children: int = Field(0, ge=0, le=8, description="Number of children (0-8). Cannot be null or None, defaults to 0.")
    infants: int = Field(0, ge=0, le=8, description="Number of infants (0-8). Cannot be null or None, defaults to 0.")

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
