from typing import Any, Dict, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PriceLockInput(BaseModel):
    """Schema for flight price lock tool input."""

    login_key: str = Field(
        ...,
        alias="loginKey",
        description="LoginKey (CookC) returned by the login tool.",
    )
    flight_index: int = Field(
        ...,
        ge=0,
        alias="flightIndex",
        description="Zero-based index of the flight to lock from the search results.",
    )
    search_response: Dict[str, Any] = Field(
        ...,
        alias="searchResponse",
        description="Full flight search response (structured data that includes the raw response).",
    )
    fare_index: int = Field(
        0,
        ge=0,
        alias="fareIndex",
        description="Fare option index to lock for the selected flight (defaults to the first fare).",
    )
    direction: Literal["outbound", "return"] = Field(
        "outbound",
        description="Which direction list to pick the flight from. Defaults to outbound flights.",
    )

    lock_period_hours: Literal[4, 8, 12, 24, 48] = Field(
        8,
        alias="lockPeriodHours",
        description="Number of hours to lock the fare (4, 8, 12, 24, or 48).",
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    @field_validator("login_key")
    @classmethod
    def _validate_login_key(cls, value: str) -> str:
        if not value or not str(value).strip():
            raise ValueError("login_key is required")
        return str(value).strip()

    @field_validator("search_response")
    @classmethod
    def _validate_search_response(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("search_response must be an object")
        return value
