"""Login Input Schema"""
from pydantic import BaseModel, Field


class LoginInput(BaseModel):
    """Schema matching main.py login tool"""
    
    phone_number: str = Field(
        ...,
        description="User phone number"
    )
    
    ip_address: str = Field(
        ...,
        description="User IP address"
    )
