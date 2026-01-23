from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class BusSearchInput(BaseModel):
    """Schema for bus search tool input.

    - sourceId: Source city ID
    - destinationId: Destination city ID  
    - date: Search date in dd-MM-yyyy format
    """

    source_id: str = Field(
        ...,
        alias="sourceId",
        description="Source city ID (e.g., '733' for Delhi)",
    )
    destination_id: str = Field(
        ...,
        alias="destinationId",
        description="Destination city ID (e.g., '757' for Manali)",
    )
    journey_date: str = Field(
        ...,
        alias="journeyDate",
        description="Journey date in YYYY-MM-DD format (will be converted to dd-MM-yyyy for API)",
    )
    is_volvo: Optional[bool] = Field(
        False,
        alias="isVolvo",
        description="Filter for Volvo buses only",
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


class BoardingPoint(BaseModel):
    """Boarding point information from bdPoints in API response."""

    bd_id: str = Field(..., alias="bdid")
    bd_long_name: str = Field(..., alias="bdLongName")
    bd_location: Optional[str] = Field(None, alias="bdlocation")
    landmark: Optional[str] = None
    time: Optional[str] = None
    contact_number: Optional[str] = Field(None, alias="contactNumber")
    latitude: Optional[str] = None
    longitude: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class DroppingPoint(BaseModel):
    """Dropping point information from dpPoints in API response."""

    dp_id: str = Field(..., alias="dpId")
    dp_name: str = Field(..., alias="dpName")
    location: Optional[str] = Field(None, alias="locatoin")  # Note: API has typo "locatoin"
    dp_time: Optional[str] = Field(None, alias="dpTime")
    contact_number: Optional[str] = Field(None, alias="contactNumber")
    landmark: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class CancellationPolicy(BaseModel):
    """Cancellation policy from cancelPolicyList in API response."""

    time_from: int = Field(..., alias="timeFrom")
    time_to: int = Field(..., alias="timeTo")
    percentage_charge: float = Field(..., alias="percentageCharge")
    flat_charge: int = Field(0, alias="flatCharge")
    is_flat: bool = Field(False, alias="isFlat")

    model_config = ConfigDict(populate_by_name=True)


class Amenity(BaseModel):
    """Bus amenity from lstamenities in API response."""

    id: int
    name: str


class BusInfo(BaseModel):
    """Processed bus information from AvailableTrips in API response.
    
    All fields are mapped from the AvailableTrips array in response.
    """

    bus_id: str  # "id" in API
    operator_name: str  # "Travels" in API
    bus_type: str  # "busType" in API
    departure_time: str  # "departureTime" in API
    arrival_time: str  # "ArrivalTime" in API
    duration: str  # "duration" in API
    available_seats: str  # "AvailableSeats" in API
    price: str  # "price" in API
    fares: List[str]  # "fares" array in API
    is_ac: bool  # "AC" in API
    is_non_ac: bool  # "nonAC" in API
    is_volvo: bool  # "isVolvo" in API
    is_seater: bool  # "seater" in API
    is_sleeper: bool  # "sleeper" in API
    is_semi_sleeper: bool  # "isSemiSleeper" in API
    rating: Optional[str] = None  # "rt" in API
    live_tracking_available: bool  # "liveTrackingAvailable" in API
    is_cancellable: bool  # "isCancellable" in API
    m_ticket_enabled: str  # "mTicketEnabled" in API
    departure_date: str  # "departureDate" in API
    arrival_date: str  # "arrivalDate" in API
    route_id: str  # "routeId" in API
    operator_id: str  # "operatorid" in API
    engine_id: int  # "engineId" in API
    boarding_points: List[BoardingPoint]  # "bdPoints" in API
    dropping_points: List[DroppingPoint]  # "dpPoints" in API
    amenities: List[str]  # extracted names from "lstamenities" in API
    cancellation_policy: List[CancellationPolicy]  # "cancelPolicyList" in API
    book_now: Optional[str] = None


class WhatsappBusFormat(BaseModel):
    """WhatsApp formatted response for bus search."""

    type: str = "bus_collection"
    options: list
    journey_type: str = "bus"
    currency: str = "INR"
    view_all_buses_url: str = ""


class WhatsappBusFinalResponse(BaseModel):
    """Final WhatsApp response wrapper."""

    response_text: str
    whatsapp_json: WhatsappBusFormat