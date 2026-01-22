from typing import Optional, Any
from pydantic import BaseModel

class ToolResponseFormat(BaseModel):
    response_text: str
    structured_content: dict | None = None
    html: Optional[str] = None
    whatsapp_response: Optional[dict] = None
    is_error: bool = False



