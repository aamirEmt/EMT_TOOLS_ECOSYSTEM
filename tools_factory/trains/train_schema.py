from typing import Optional, List, Dict, Any
from datetime import datetime
import re
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


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
    page: int = Field(
        default=1,
        ge=1,
        description="Page number for pagination. Default: 1",
    )
    travel_class: Optional[str] = Field(
        None,
        alias="travelClass",
        description="Preferred travel class. MUST use exact codes only: '1A' (First AC), '2A' (AC 2 Tier), '3A' (Third AC), 'SL' (Sleeper Class), '2S' (Second Seating), 'CC' (AC Chair Car), 'EC' (Executive Class), '3E' (AC 3 Tier Economy), 'FC' (First Class), 'EV' (Vistadome AC), 'VS' (Vistadome Non-AC), 'EA' (Anubhuti Class), 'VC' (Vistadome Chair Car). Do not use full names like 'Chair Car' or variations like '3AC' - use only the exact codes.",
    )
    departure_time_min: Optional[str] = Field(
        None,
        alias="departureTimeMin",
        description="Earliest departure time in HH:MM 24-hour format. Set this when the user wants to LEAVE AFTER a certain time. Examples: 'leave after 2pm'/'depart after 2'/'trains after 2pm' → '14:00', 'morning trains' → '06:00', 'evening trains' → '16:00', 'night trains' → '20:00', 'leave after 9am'/'go after 9' → '09:00'.",
    )
    departure_time_max: Optional[str] = Field(
        None,
        alias="departureTimeMax",
        description="Latest departure time in HH:MM 24-hour format. Set this when the user wants to LEAVE BY/BEFORE a certain time. Examples: 'leave by 10am'/'want to go by 10'/'depart before 10' → '10:00', 'leave by 6pm'/'go before 6pm' → '18:00', 'morning trains' → '12:00', 'evening trains' → '22:00', 'early trains' → '10:00'. Keywords: 'by', 'before', 'no later than', 'within'.",
    )
    arrival_time_min: Optional[str] = Field(
        None,
        alias="arrivalTimeMin",
        description="Earliest arrival time in HH:MM 24-hour format. Set this when the user wants to ARRIVE/REACH AFTER a certain time. Examples: 'arrive after 8am'/'reach after 8' → '08:00', 'don't want to arrive too early' → '06:00'.",
    )
    arrival_time_max: Optional[str] = Field(
        None,
        alias="arrivalTimeMax",
        description="Latest arrival time in HH:MM 24-hour format. Set this when the user wants to REACH BY/BEFORE a certain time. Examples: 'reach by 10pm'/'arrive before 10pm'/'want to be there by 10' → '22:00', 'reach by noon'/'arrive before 12' → '12:00', 'reach by morning' → '09:00'. Keywords: 'reach by', 'arrive before', 'be there by'.",
    )
    quota: Optional[str] = Field(
        "GN",
        alias="quota",
        description="Booking quota. Options: GN=General (default), TQ=Tatkal, SS=Senior Citizen, LD=Ladies.",
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

            # First Class variations
            "FC": "FC",
            "FIRST CLASS": "FC",
            "1ST CLASS": "FC",

            # Vistadome AC variations
            "EV": "EV",
            "VISTADOME AC": "EV",
            "VISTADOME": "EV",

            # Vistadome Non-AC variations
            "VS": "VS",
            "VISTADOME NON-AC": "VS",
            "VISTADOME NON AC": "VS",
            "VISTADOME NONAC": "VS",

            # Anubhuti Class variations
            "EA": "EA",
            "ANUBHUTI": "EA",
            "ANUBHUTI CLASS": "EA",

            # Vistadome Chair Car variations
            "VC": "VC",
            "VISTADOME CHAIR CAR": "VC",
            "VISTADOME CC": "VC",
        }

        # Try to find a match in the mapping
        matched_code = class_mapping.get(normalized)

        # If no match found, return None (gracefully handle invalid input)
        if matched_code is None:
            return None

        return matched_code

    @field_validator("departure_time_min", "departure_time_max", "arrival_time_min", "arrival_time_max")
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate time is in HH:MM 24-hour format."""
        if v is None:
            return v

        v = v.strip()

        # Validate format: HH:MM (00-23:00-59)
        if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError(
                "Time must be in HH:MM 24-hour format (e.g., '14:30', '09:00'). "
                "Hours: 00-23, Minutes: 00-59."
            )

        return v

    @field_validator("quota")
    @classmethod
    def validate_quota(cls, v: Optional[str]) -> str:
        """Validate and normalize quota code."""
        if v is None:
            return "GN"

        v = v.strip().upper()

        # Valid quota codes
        valid_quotas = ["GN", "TQ", "SS", "LD"]

        if v not in valid_quotas:
            # Default to GN for invalid codes
            return "GN"

        return v

    @model_validator(mode='after')
    def validate_time_ranges(self) -> 'TrainSearchInput':
        """Validate that min times are before or equal to max times."""
        # Validate departure time range
        if self.departure_time_min and self.departure_time_max:
            min_time = datetime.strptime(self.departure_time_min, "%H:%M").time()
            max_time = datetime.strptime(self.departure_time_max, "%H:%M").time()
            if min_time > max_time:
                raise ValueError(
                    f"departureTimeMin ({self.departure_time_min}) must be before or equal to "
                    f"departureTimeMax ({self.departure_time_max})"
                )

        # Validate arrival time range
        if self.arrival_time_min and self.arrival_time_max:
            min_time = datetime.strptime(self.arrival_time_min, "%H:%M").time()
            max_time = datetime.strptime(self.arrival_time_max, "%H:%M").time()
            if min_time > max_time:
                raise ValueError(
                    f"arrivalTimeMin ({self.arrival_time_min}) must be before or equal to "
                    f"arrivalTimeMax ({self.arrival_time_max})"
                )

        return self

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
    quota: Optional[str] = None
    quota_name: Optional[str] = None


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
    """WhatsApp response format - supports both class-mentioned and general search."""
    type: str = "train_collection"
    is_class_mentioned: bool = False
    search_context: Dict[str, Any] = {}  # source, destination, date, class, currency, search_id

    # Conditional fields (mutually exclusive based on is_class_mentioned)
    options: Optional[List[Dict[str, Any]]] = None  # When class NOT mentioned
    trains: Optional[List[Dict[str, Any]]] = None   # When class IS mentioned

    # Common fields
    journey_type: str = "train"
    currency: str = "INR"
    view_all_trains_url: str = ""

    @model_validator(mode='after')
    def validate_conditional_fields(self) -> 'WhatsappTrainFormat':
        """Ensure correct fields are populated based on is_class_mentioned."""
        if self.is_class_mentioned:
            if not self.trains:
                raise ValueError("trains list required when is_class_mentioned=True")
            if self.options:
                raise ValueError("options should not be set when is_class_mentioned=True")
        else:
            if not self.options:
                raise ValueError("options list required when is_class_mentioned=False")
            if self.trains:
                raise ValueError("trains should not be set when is_class_mentioned=False")
        return self


class WhatsappTrainFinalResponse(BaseModel):
    response_text: str
    whatsapp_json: WhatsappTrainFormat
