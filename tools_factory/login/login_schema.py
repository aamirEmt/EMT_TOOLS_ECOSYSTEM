"""Login Input Schema"""
from typing import Optional
from pydantic import BaseModel, Field


class LoginInput(BaseModel):
    
    phone_number: str = Field(
        ...,
        description="User phone number or email address"
    )
    
    ip_address: Optional[str] = Field(
        "49.249.40.58",
        description="USER IP Address But its not mandatory"
    )
