from typing import Callable, Dict, Any, Optional, List
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from .base_schema import ToolResponseFormat

@dataclass
class ToolMetadata:
    """Metadata for a tool"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_template: Optional[str] = None  # For OpenAI Apps
    category: str = "general"
    tags: List[str] = field(default_factory=list)

class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self):
        self.metadata = self.get_metadata()
    
    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResponseFormat:
        """Execute the tool logic"""
        pass