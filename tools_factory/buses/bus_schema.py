from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

class BusSearchInput(BaseModel):
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
    time_from: int = Field(..., alias="timeFrom")
    time_to: int = Field(..., alias="timeTo")
    percentage_charge: float = Field(..., alias="percentageCharge")
    flat_charge: int = Field(0, alias="flatCharge")
    is_flat: bool = Field(False, alias="isFlat")

    model_config = ConfigDict(populate_by_name=True)

class Amenity(BaseModel):
    id: int
    name: str

class BusInfo(BaseModel):
    bus_id: str 
    operator_name: str  
    bus_type: str 
    departure_time: str  
    arrival_time: str  
    duration: str  
    available_seats: str 
    price: str  
    fares: List[str]  
    is_ac: bool 
    is_non_ac: bool 
    is_volvo: bool  
    is_seater: bool  
    is_sleeper: bool 
    is_semi_sleeper: bool  
    rating: Optional[str] = None 
    live_tracking_available: bool 
    is_cancellable: bool  
    m_ticket_enabled: str  
    departure_date: str  
    arrival_date: str  
    route_id: str
    operator_id: str  
    engine_id: int  
    boarding_points: List[BoardingPoint]  
    dropping_points: List[DroppingPoint]  
    amenities: List[str]  
    cancellation_policy: List[CancellationPolicy] 
    book_now: Optional[str] = None

class WhatsappBusFormat(BaseModel):
    type: str = "bus_collection"
    options: list
    journey_type: str = "bus"
    currency: str = "INR"
    view_all_buses_url: str = ""

class WhatsappBusFinalResponse(BaseModel):
    response_text: str
    whatsapp_json: WhatsappBusFormat

class SeatBindInput(BaseModel):
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
        description="Journey date in YYYY-MM-DD format",
    )
    bus_id: str = Field(
        ...,
        alias="busId",
        description="Bus ID from search results",
    )
    route_id: str = Field(
        ...,
        alias="routeId",
        description="Route ID from search results",
    )
    engine_id: int = Field(
        ...,
        alias="engineId",
        description="Engine ID from search results (e.g., 4 for RedBus, 7 for VRL)",
    )
    boarding_point_id: str = Field(
        ...,
        alias="boardingPointId",
        description="Selected boarding point ID from bdPoints",
    )
    dropping_point_id: str = Field(
        ...,
        alias="droppingPointId",
        description="Selected dropping point ID from dpPoints",
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

class SeatInfo(BaseModel):
    seat_number: str  
    seat_name: str  
    seat_type: str 
    seat_status: str  
    is_available: bool  
    is_ladies: bool  
    fare: str  
    row: int  
    column: int  
    deck: str  
    width: int = 1  
    length: int = 1  
    is_booked: bool = False
    is_blocked: bool = False

class DeckLayout(BaseModel):   
    deck_name: str  
    rows: int 
    columns: int  
    seats: List[SeatInfo] 

class SeatLayoutInfo(BaseModel):    
    bus_id: str
    bus_type: str
    operator_name: str
    total_seats: int
    available_seats: int
    booked_seats: int
    lower_deck: Optional[DeckLayout] = None
    upper_deck: Optional[DeckLayout] = None
    boarding_point: str
    dropping_point: str
    boarding_time: str
    dropping_time: str
    fare_details: List[Dict[str, Any]] = []

class SeatLayoutResponse(BaseModel):    
    success: bool
    message: str
    layout: Optional[SeatLayoutInfo] = None
    raw_response: Optional[Dict[str, Any]] = None  