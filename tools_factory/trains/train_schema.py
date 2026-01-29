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
        description="Journey date in DD-MM-YYYY format",
    )
    travel_class: Optional[str] = Field(
        None,
        alias="travelClass",
        description="Preferred travel class. MUST use exact codes only: '1A' (First AC), '2A' (AC 2 Tier), '3A' (Third AC), 'SL' (Sleeper Class), '2S' (Second Seating), 'CC' (AC Chair Car), 'EC' (Executive Class), '3E' (AC 3 Tier Economy). Do not use full names like 'Chair Car' or variations like '3AC' - use only the exact codes.",
    )
    # quota: Optional[str] = Field(
    #     "GN",
    #     description="Booking quota (GN=General, TQ=Tatkal, SS=Senior Citizen, LD=Ladies)",
    # )

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
            raise ValueError("Date must be in DD-MM-YYYY format")
        return v

    @field_validator("travel_class")
    @classmethod
    def validate_travel_class(cls, v: Optional[str]) -> Optional[str]:
        """
        Normalize travel class input to valid codes.
        Returns None if input is None, 'NONE', or doesn't match any valid class.
        """
        if v is None or v.upper().strip() == "NONE":
            return None

        # Normalize input: uppercase and strip whitespace
        normalized = v.upper().strip()

        # Mapping of variations to standard codes
        class_mapping = {
            # First AC variations
            "1A": "1A",
            "FIRST AC": "1A",
            "1ST AC": "1A",
            "FIRST CLASS AC": "1A",

            # Second AC (AC 2 Tier) variations
            "2A": "2A",
            "SECOND AC": "2A",
            "2ND AC": "2A",
            "AC 2 TIER": "2A",
            "2 TIER AC": "2A",

            # Third AC variations
            "3A": "3A",
            "THIRD AC": "3A",
            "3RD AC": "3A",
            "3AC": "3A",
            "AC 3 TIER": "3A",
            "3 TIER AC": "3A",

            # Sleeper variations
            "SL": "SL",
            "SLEEPER": "SL",
            "SLEEPER CLASS": "SL",

            # Second Seating variations
            "2S": "2S",
            "SECOND SEATING": "2S",
            "2ND SEATING": "2S",
            "25": "2S",  # User mentioned "25" - likely a typo for "2S"

            # AC Chair Car variations
            "CC": "CC",
            "CHAIR CAR": "CC",
            "CHAIRCAR": "CC",
            "AC CHAIR CAR": "CC",

            # Executive Class variations
            "EC": "EC",
            "EXECUTIVE": "EC",
            "EXECUTIVE CLASS": "EC",
            "EXEC": "EC",

            # AC 3 Tier Economy variations
            "3E": "3E",
            "AC 3 TIER ECONOMY": "3E",
            "3 TIER ECONOMY": "3E",
            "3E ECONOMY": "3E",
        }

        # Try to find a match in the mapping
        matched_code = class_mapping.get(normalized)

        # If no match found, return None (gracefully handle invalid input)
        if matched_code is None:
            return None

        return matched_code

    # @field_validator("quota")
    # @classmethod
    # def validate_quota(cls, v: Optional[str]) -> str:
    #     """Convert 'NONE' string to default 'GN'"""
    #     if v is None or v.upper() == "NONE":
    #         return "GN"
    #     return v


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
