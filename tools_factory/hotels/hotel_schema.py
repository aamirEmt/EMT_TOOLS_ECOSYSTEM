from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, timedelta
from enum import Enum


class SortType(str, Enum):
    """Hotel search sort options"""
    PRICE_LOW_TO_HIGH = "price|ASC"   # Sort by price: cheapest first
    PRICE_HIGH_TO_LOW = "price|DESC"  # Sort by price: expensive first
    POPULARITY = "Popular|DSC"         # Sort by popularity (default)

    @classmethod
    def from_user_input(cls, value: str) -> "SortType":
        """
        Map user input to SortType enum.
        Works with both LLM-provided enum names and direct user strings.
        """
        if value is None:
            return cls.POPULARITY

        value_lower = value.lower().strip()

        # Map common user inputs to enum values
        low_to_high_keywords = {"low to high", "low", "cheapest", "lowest", "ascending", "asc", "price_low_to_high"}
        high_to_low_keywords = {"high to low", "high", "expensive", "highest", "descending", "desc", "price_high_to_low"}
        popularity_keywords = {"popular", "popularity", "default", "recommended"}

        if value_lower in low_to_high_keywords:
            return cls.PRICE_LOW_TO_HIGH
        if value_lower in high_to_low_keywords:
            return cls.PRICE_HIGH_TO_LOW
        if value_lower in popularity_keywords:
            return cls.POPULARITY

        # Check if it's already a valid API value (e.g., "price|ASC")
        for member in cls:
            if value == member.value:
                return member

        # Default to popularity
        return cls.POPULARITY


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
    sort_type: str = Field(
        default="Popular|DSC",
        description="""Sort order for hotels. Pass one of these values:
        - 'price|ASC' : when user wants cheap/budget/low to high/lowest price first
        - 'price|DESC' : when user wants expensive/luxury/high to low/highest price first
        - 'Popular|DSC' : default, when user wants popular/recommended hotels or doesn't specify sorting"""
    )
    rating: Optional[List[str]] = Field(default=None, description="Star ratings (e.g., ['3','4','5'])")
    amenities: Optional[List[str]] = Field(
        default=None,
        description="""Hotel amenities filter. Valid values: 'Free Cancellation', '24 Hour Front Desk', 'AC', 'Bar', 'Wi-Fi', 'Breakfast', 'Spa Service', 'Swimming Pool', 'Parking', 'Restaurant'. Example: ['Wi-Fi', 'Parking']"""
    )
    user_rating: Optional[List[str]] = Field(
        default=None,
        description="""Guest/User rating filter (based on reviews). Pass list of values:
        - '5' : Excellent (4.2+) - when user wants top/best/excellent/highly rated hotels
        - '4' : Very Good (3.5+) - when user wants very good/great rated hotels
        - '3' : Good (3+) - when user wants good/decent rated hotels
        Multiple selections allowed. Example: ['5', '4'] for excellent and very good hotels"""
    )
    
    @field_validator("sort_type", mode="before")
    @classmethod
    def validate_sort_type(cls, v) -> str:
        """Convert user input to API payload value"""
        return SortType.from_user_input(v).value

    @field_validator("user_rating", mode="before")
    @classmethod
    def validate_user_rating(cls, v) -> Optional[List[str]]:
        """Convert user input to valid rating values ('3', '4', '5')"""
        if v is None:
            return None

        # Mapping for non-LLM user inputs
        rating_map = {
            # Excellent (4.2+)
            "5": "5", "excellent": "5", "best": "5", "top rated": "5", "highly rated": "5",
            # Very Good (3.5+)
            "4": "4", "very good": "4", "great": "4",
            # Good (3+)
            "3": "3", "good": "3", "decent": "3",
        }

        def map_rating(val: str) -> Optional[str]:
            return rating_map.get(str(val).lower().strip())

        # Handle single value
        if isinstance(v, str):
            mapped = map_rating(v)
            return [mapped] if mapped else None

        # Handle list
        if isinstance(v, list):
            result = []
            for r in v:
                mapped = map_rating(r)
                if mapped and mapped not in result:
                    result.append(mapped)
            return result if result else None

        return None

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