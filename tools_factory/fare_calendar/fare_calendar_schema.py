from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class FareCalendarInput(BaseModel):
    """Input schema for fare calendar lookups."""

    date: str = Field(
        ...,
        description="Travel date in DD/MM/YYYY format (used as-is for the API payload)",
    )
    departure_code: str = Field(
        ...,
        alias="departureCode",
        description="Origin airport IATA code (e.g., DEL)",
    )
    arrival_code: str = Field(
        ...,
        alias="arrivalCode",
        description="Destination airport IATA code (e.g., BOM)",
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    @field_validator("departure_code", "arrival_code")
    @classmethod
    def normalize_airport_code(cls, value: str) -> str:
        code = value.strip().upper()
        if len(code) != 3:
            raise ValueError("Airport code must be a 3-letter IATA code")
        return code

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, value: str) -> str:
        value = value.strip()
        try:
            datetime.strptime(value, "%d/%m/%Y")
        except ValueError:
            raise ValueError("Date must be in DD/MM/YYYY format")
        return value
