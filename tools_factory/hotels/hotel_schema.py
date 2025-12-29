from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, timedelta

class HotelSearchInput(BaseModel):
    """Schema for hotel search input validation"""
    
    # Required fields
    city_name: str = Field(
        description="City or area name (e.g., 'Pune', 'Viman Nagar, Pune')"
    )
    check_in_date: str = Field(
        description="Check-in date in YYYY-MM-DD format"
    )
    check_out_date: str = Field(
        description="Check-out date in YYYY-MM-DD format"
    )
    
    # Room configuration
    num_rooms: int = Field(default=1, ge=1, le=10, description="Number of rooms")
    num_adults: int = Field(default=2, ge=1, le=20, description="Number of adults")
    num_children: int = Field(default=0, ge=0, le=10, description="Number of children")
    
    # Pagination
    page_no: int = Field(default=1, ge=1, description="Page number for results")
    hotel_count: int = Field(default=30, ge=1, le=50, description="Max hotels per page")
    
    # Filters
    min_price: Optional[int] = Field(default=None, ge=1, description="Minimum price filter")
    max_price: int = Field(default=10_000_000, ge=1, description="Maximum price filter")
    sort_type: str = Field(default="Popular|DESC", description="Sort criteria")
    rating: Optional[List[str]] = Field(default=None, description="Star ratings (e.g., ['3','4','5'])")
    amenities: Optional[List[str]] = Field(default=None, description="Amenities filter")
    
    @field_validator("check_in_date", "check_out_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Ensure dates are in YYYY-MM-DD format"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError(f"Date must be in YYYY-MM-DD format, got: {v}")
    
    @field_validator("check_out_date")
    @classmethod
    def validate_checkout_after_checkin(cls, v: str, info) -> str:
        """Ensure check-out is after check-in"""
        check_in = info.data.get("check_in_date")
        if check_in:
            check_in_dt = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_dt = datetime.strptime(v, "%Y-%m-%d")
            if check_out_dt <= check_in_dt:
                raise ValueError("Check-out date must be after check-in date")
        return v