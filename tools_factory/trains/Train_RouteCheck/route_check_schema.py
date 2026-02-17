"""Train Route Check Schemas - Input/Output models for checking train route/schedule."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class RouteCheckInput(BaseModel):
    """Schema for checking train route/schedule."""

    train_no: str = Field(
        ...,
        alias="trainNo",
        description="Train number (e.g., '12302', '12963').",
    )

    from_station_code: Optional[str] = Field(
        default=None,
        alias="fromStationCode",
        description="Origin station code (e.g., 'NDLS'). If not provided, fetched automatically from train details.",
    )

    to_station_code: Optional[str] = Field(
        default=None,
        alias="toStationCode",
        description="Destination station code (e.g., 'HWH'). If not provided, fetched automatically from train details.",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )


class StationStop(BaseModel):
    """Single station stop in the train route."""

    station_code: str = Field(..., description="Station code (e.g., 'NDLS')")
    station_name: str = Field(..., description="Station name (e.g., 'NEW DELHI')")
    arrival_time: str = Field(..., description="Arrival time (e.g., '21:30' or '--' for origin)")
    departure_time: str = Field(..., description="Departure time (e.g., '16:50' or '--' for destination)")
    halt_time: str = Field(..., description="Halt time (e.g., '05:00' or '--')")
    day_count: str = Field(..., description="Day number (e.g., '1', '2')")
    distance: str = Field(..., description="Distance from origin in km (e.g., '441')")
    route_number: str = Field(default="1", description="Route number")
    stn_serial_number: str = Field(..., description="Station serial number")


class TrainRouteInfo(BaseModel):
    """Complete train route response."""

    train_no: str
    train_name: str
    station_from: str
    station_to: str
    station_list: List[StationStop]
    running_days: List[str]


class WhatsappRouteFormat(BaseModel):
    """WhatsApp-friendly format for train route."""

    type: str = Field(default="train_route")
    response_text: str
    data: Dict[str, Any]


class WhatsappRouteFinalResponse(BaseModel):
    """Final WhatsApp response wrapper for train route."""

    response_text: str
    whatsapp_json: WhatsappRouteFormat
