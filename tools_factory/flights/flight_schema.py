from typing import Optional
from datetime import datetime
import re
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
    stops: Optional[int] = Field(
        None,
        description="Flight stop preference only if specified: 0(for non-stop), 1(stop), or 2(stops)"
    )
    fastest: Optional[bool] = Field(
        None,
        description="If true (or 1), sort results by fastest journey time first"
    )
    departure_time_window: Optional[str] = Field(
        "00:00-24:00",
        alias="departureTimeWindow",
        description=(
            "Preferred departure time window in 24-hour format 'HH:MM-HH:MM'. "
            "Accepts natural phrases (morning/afternoon/evening/night/early morning) or loose inputs like '6am-11am'. "
            "Defaults to '00:00-24:00' (no restriction)."
        ),
    )
    arrival_time_window: Optional[str] = Field(
        "00:00-24:00",
        alias="arrivalTimeWindow",
        description=(
            "Preferred arrival time window in 24-hour format 'HH:MM-HH:MM'. "
            "Accepts natural phrases (morning/afternoon/evening/night/early morning) or loose inputs like '5pm-9:30pm'. "
            "Defaults to '00:00-24:00' (no restriction)."
        ),
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
    
    @field_validator("fastest", mode="before")
    @classmethod
    def coerce_fastest(cls, v):
        if v is None:
            return v
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(int(v))
        if isinstance(v, str):
            text = v.strip().lower()
            if text in {"1", "true", "yes", "y"}:
                return True
            if text in {"0", "false", "no", "n"}:
                return False
        raise ValueError("fastest must be a boolean-like value (true/false or 1/0)")
    
    @staticmethod
    def _normalize_time_str(raw: str) -> Optional[tuple[int, int]]:
        """Parse times like '6am', '18:30', '1830', '06:00' into (hh, mm)."""
        if not raw:
            return None

        text = raw.strip().lower()
        meridian = None
        if text.endswith("am") or text.endswith("pm"):
            meridian = text[-2:]
            text = text[:-2].strip()

        text = text.replace(".", ":")
        digits = re.sub(r"\D", "", text)

        hour = minute = None
        if ":" in text:
            parts = text.split(":", 1)
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                hour = int(parts[0])
                minute = int(parts[1].ljust(2, "0")[:2])
        elif len(digits) in (3, 4):
            hour = int(digits[:-2])
            minute = int(digits[-2:])
        elif digits.isdigit():
            hour = int(digits)
            minute = 0

        if hour is None or minute is None or minute > 59 or hour > 24:
            return None
        if hour == 24 and minute > 0:
            return None

        if meridian:
            if meridian == "pm" and hour != 12:
                hour += 12
            if meridian == "am" and hour == 12:
                hour = 0

        if hour == 24:
            hour = 24
            minute = 0

        return (hour, minute)

    @classmethod
    def _format_minutes(cls, hh: int, mm: int) -> str:
        if hh == 24 and mm == 0:
            return "24:00"
        return f"{hh:02d}:{mm:02d}"

    @classmethod
    def _normalize_window(cls, value: Optional[str]) -> str:
        """Convert various inputs to strict HH:MM-HH:MM, with NL shortcuts."""
        default = "00:00-24:00"
        if value is None:
            return default

        text = str(value).strip().lower()
        if not text:
            return default

        presets = {
            "early morning": "03:00-06:00",
            "morning": "06:00-12:00",
            "afternoon": "12:00-17:00",
            "evening": "17:00-21:00",
            "night": "21:00-03:00",
        }
        if text in presets:
            return presets[text]

        if "-" not in text and "to" not in text:
            return default if text not in presets else presets[text]

        separator = "-" if "-" in text else "to"
        parts = [p.strip() for p in text.split(separator, 1)]
        if len(parts) != 2:
            return default

        start = cls._normalize_time_str(parts[0])
        end = cls._normalize_time_str(parts[1])
        if start is None or end is None:
            raise ValueError("Time window must be in HH:MM-HH:MM or a known period like 'morning'")

        start_str = cls._format_minutes(*start)
        end_str = cls._format_minutes(*end)
        return f"{start_str}-{end_str}"

    @field_validator("departure_time_window", "arrival_time_window", mode="before")
    @classmethod
    def ensure_time_window(cls, v: Optional[str]) -> str:
        return cls._normalize_window(v)
    

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
