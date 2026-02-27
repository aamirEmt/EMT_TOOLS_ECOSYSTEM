from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

class BusSearchInput(BaseModel):

    source_name: Optional[str] = Field(
        None,
        alias="sourceName",
        description="PREFERRED: Source city name (e.g., 'Delhi', 'Mumbai', 'Bangalore'). Will be auto-resolved to city ID. Use this instead of source_id.",
    )
    destination_name: Optional[str] = Field(
        None,
        alias="destinationName",
        description="PREFERRED: Destination city name (e.g., 'Manali', 'Pune', 'Ranchi'). Will be auto-resolved to city ID. Use this instead of destination_id.",
    )
    
    source_id: Optional[str] = Field(
        None,
        alias="sourceId",
        description="Source city ID (only if known). Prefer using source_name instead.",
    )
    destination_id: Optional[str] = Field(
        None,
        alias="destinationId",
        description="Destination city ID (only if known). Prefer using destination_name instead.",
    )
    
    journey_date: str = Field(
        ...,
        alias="journeyDate",
        description="Journey date in dd-mm-yyyy format (e.g., '30-01-2026')",
    )
    is_volvo: Optional[bool] = Field(
        None,
        alias="isVolvo",
        description="Filter for Volvo buses only",
    )
    is_ac: Optional[bool] = Field(
        None,
        alias="isAC",
        description="Filter for AC buses only. Set True for AC, False for Non-AC, None for all.",
    )
    is_seater: Optional[bool] = Field(
        None,
        alias="isSeater",
        description="Filter for Seater buses only. Set True for Seater, False for Sleeper, None for all.",
    )
    is_sleeper: Optional[bool] = Field(
        None,
        alias="isSleeper",
        description="Filter for Sleeper buses only. Set True for Sleeper, False for Seater, None for all.",
    )
    departure_time_from: Optional[str] = Field(
        None,
        alias="departureTimeFrom",
        description="Filter buses departing after this time (HH:MM format, 24-hour). E.g., '06:00' for 6 AM, '18:00' for 6 PM.",
    )
    departure_time_to: Optional[str] = Field(
        None,
        alias="departureTimeTo",
        description="Filter buses departing before this time (HH:MM format, 24-hour). E.g., '12:00' for 12 PM, '18:00' for 6 PM.",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number for pagination. Default: 1",
    )
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        json_schema_extra={
            "additionalProperties": False,
        }
    )
    
    @classmethod
    def model_json_schema(cls, **kwargs):
        schema = super().model_json_schema(**kwargs)
        if "required" in schema:
            schema["required"] = [f for f in schema.get("required", []) 
                                  if f not in ["min_price", "max_price", "minPrice", "maxPrice"]]
        return schema
    
    @field_validator("journey_date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        if v is None:
            return v
        try:
            datetime.strptime(v, "%d-%m-%Y")
        except ValueError:
            raise ValueError("Date must be in dd-MM-yyyy format (e.g., '30-01-2026')")
        return v

class BoardingPoint(BaseModel):
    
    bd_id: str = Field(..., alias="bdid")
    bd_long_name: str = Field("", alias="bdLongName")
    bd_location: Optional[str] = Field(None, alias="bdlocation")
    bd_point: Optional[str] = Field(None, alias="bdPoint")
    landmark: Optional[str] = None
    time: Optional[str] = None
    contact_number: Optional[str] = Field(None, alias="contactNumber")
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    bording_date: Optional[str] = Field(None, alias="bordingDate")

    model_config = ConfigDict(populate_by_name=True)


class DroppingPoint(BaseModel):
    
    dp_id: str = Field(..., alias="dpId")
    dp_name: str = Field("", alias="dpName")
    location: Optional[str] = Field(None, alias="locatoin")  
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
    operator_id: str
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
    engine_id: int
    trace_id: Optional[str] = None
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
    source_name: Optional[str] = Field(
        None,
        alias="sourceName",
        description="Source city name",
    )
    destination_name: Optional[str] = Field(
        None,
        alias="destinationName",
        description="Destination city name",
    )
    journey_date: str = Field(
        ...,
        alias="journeyDate",
        description="Journey date in dd-MM-yyyy format (e.g., '30-01-2026')",
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
        description="Engine ID from search results (e.g., 2, 4, 7)",
    )
    operator_id: Optional[str] = Field(
        None,
        alias="operatorId",
        description="Operator ID from search results",
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

    bus_type: Optional[str] = Field(
        None,
        alias="busType",
        description="Bus type string",
    )
    operator_name: Optional[str] = Field(
        None,
        alias="operatorName",
        description="Operator/Travel name",
    )
    departure_time: Optional[str] = Field(
        None,
        alias="departureTime",
        description="Departure time",
    )
    arrival_time: Optional[str] = Field(
        None,
        alias="arrivalTime",
        description="Arrival time",
    )
    duration: Optional[str] = Field(
        None,
        alias="duration",
        description="Journey duration",
    )
    trace_id: Optional[str] = Field(
        None,
        alias="traceId",
        description="Trace ID from search results",
    )
    is_seater: Optional[bool] = Field(
        True,
        alias="isSeater",
        description="Has seater seats",
    )
    is_sleeper: Optional[bool] = Field(
        True,
        alias="isSleeper",
        description="Has sleeper seats",
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
            datetime.strptime(v, "%d-%m-%Y")
        except ValueError:
            raise ValueError("Date must be in dd-MM-yyyy format (e.g., '30-01-2026')")
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
    gender: Optional[str] = None
    encrypted_seat: Optional[str] = None


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


class SeatSelectionInput(BaseModel):
    
    source_id: str = Field(..., alias="sourceId", description="Source city ID")
    destination_id: str = Field(..., alias="destinationId", description="Destination city ID")
    source_name: Optional[str] = Field(None, alias="sourceName", description="Source city name")
    destination_name: Optional[str] = Field(None, alias="destinationName", description="Destination city name")
    journey_date: str = Field(..., alias="journeyDate", description="Journey date in dd-MM-yyyy format")
    bus_id: str = Field(..., alias="busId", description="Bus ID from search results")
    route_id: str = Field(..., alias="routeId", description="Route ID from search results")
    engine_id: int = Field(..., alias="engineId", description="Engine ID from search results")
    operator_id: str = Field(..., alias="operatorId", description="Operator ID")
    operator_name: str = Field(..., alias="operatorName", description="Operator/Travel name")
    bus_type: str = Field(..., alias="busType", description="Bus type string")
    departure_time: str = Field(..., alias="departureTime", description="Departure time")
    arrival_time: str = Field(..., alias="arrivalTime", description="Arrival time")
    duration: str = Field(..., alias="duration", description="Journey duration")
    is_seater: bool = Field(True, alias="isSeater", description="Has seater seats")
    is_sleeper: bool = Field(True, alias="isSleeper", description="Has sleeper seats")
    session_id: Optional[str] = Field(None, alias="sessionId", description="Session ID from search")
    visitor_id: Optional[str] = Field(None, alias="visitorId", description="Visitor ID from search")
    trace_id: Optional[str] = Field(None, alias="traceId", description="Trace ID from search")
    
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class SelectedSeat(BaseModel):
    
    seat_no: str = Field(..., alias="seatNo", description="Seat number/name")
    seat_type: str = Field(..., alias="seatType", description="Seat type (ST/SL)")
    fare: float = Field(..., description="Seat fare")
    seat_id: Optional[str] = Field(None, alias="seatId", description="Seat ID")
    actual_fare: float = Field(..., alias="actualfare", description="Actual fare")
    gender: str = Field("M", description="Gender (M/F)")
    base_fare: float = Field(..., alias="baseFare", description="Base fare")
    encrypted_seat: str = Field(..., alias="EncriSeat", description="Encrypted seat data")
    
    model_config = ConfigDict(populate_by_name=True)


class ConfirmSeatsInput(BaseModel):
    
    available_trip_id: str = Field(..., alias="availableTripId", description="Bus trip ID")
    engine_id: int = Field(..., alias="engineId", description="Engine ID")
    route_id: str = Field(..., alias="routeId", description="Route ID")
    operator_id: str = Field(..., alias="operator_id", description="Operator ID")
    
    source: str = Field(..., description="Source city name")
    destination: str = Field(..., description="Destination city name")
    bus_operator: str = Field(..., alias="busOperator", description="Bus operator name")
    bus_type: str = Field(..., alias="busType", description="Bus type")
    departure_time: str = Field(..., alias="DepTime", description="Departure time")
    arrival_date: str = Field(..., alias="arrivalDate", description="Arrival time")
    
    seats: List[SelectedSeat] = Field(..., description="List of selected seats")
    
    boarding_id: str = Field(..., alias="boardingId", description="Boarding point ID")
    boarding_name: str = Field("", alias="boardingName", description="Boarding point name")
    boarding_point: Dict[str, Any] = Field(..., alias="boardingPoint", description="Full boarding point details")
    
    drop_id: str = Field(..., alias="dropId", description="Dropping point ID")
    dropping_point: Dict[str, Any] = Field(..., alias="DropingPoint", description="Full dropping point details")
    
    session_id: Optional[str] = Field(None, alias="sessionId", description="Session ID")
    sid: str = Field(..., alias="Sid", description="Session ID")
    vid: str = Field(..., alias="Vid", description="Visitor ID")
    trace_id: str = Field(..., alias="TraceId", description="Trace ID")
    
    total_fare: float = Field(0, alias="totalFare", description="Total fare")
    discount: float = Field(0, alias="Discount", description="Discount amount")
    cash_back: float = Field(0, alias="CashBack", description="Cashback amount")
    service_fee: float = Field(0, alias="serviceFee", description="Service fee")
    stf: float = Field(0, alias="STF", description="STF")
    tds: float = Field(0, alias="TDS", description="TDS")
    
    coupon_code: str = Field("", alias="cpnCode", description="Coupon code")
    agent_code: str = Field("", alias="agentCode", description="Agent code")
    agent_type: str = Field("", alias="agentType", description="Agent type")
    agent_markup: float = Field(0, alias="agentMarkUp", description="Agent markup")
    agent_ac_balance: float = Field(0, alias="agentACBalance", description="Agent AC balance")
    departure_date: Optional[str] = Field(None, alias="departureDate", description="Departure date")
    cancel_policy_list: List[Dict[str, Any]] = Field([], alias="cancelPolicyList", description="Cancellation policy")
    
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
