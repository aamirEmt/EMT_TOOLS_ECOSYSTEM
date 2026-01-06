from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


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
    """
    Base class for all tools.

    Tools are free to directly use kwargs.pop("_limit"), kwargs.pop("_html")
    """

    CONTROL_PREFIX = "_"  # internal execution-only params

    def __init__(self):
        self.metadata = self.get_metadata()

    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool logic.

        kwargs may include internal control params like:
        - _limit
        - _html

        Tools decide how and when to pop/use them.
        """
        pass

    # HELPERS

    def pop_control_args(
        self,
        kwargs: Dict[str, Any],
        *,
        limit_default: Optional[int] = None,
        html_default: bool = False,
    ) -> Tuple[Optional[int], bool]:
        """
        Pop common internal execution flags from kwargs.

        This follows the SAME pattern tools already use:
            limit = kwargs.pop("_limit", None)
            render_html = kwargs.pop("_html", False)

        Usage (optional):
            limit, render_html = self.pop_control_args(kwargs)
        """
        limit = kwargs.pop("_limit", limit_default)
        render_html = kwargs.pop("_html", html_default)
        return limit, render_html

    def split_control_kwargs(
        self, kwargs: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        OPTIONAL utility to split kwargs into:
        - tool_args    -> safe for schema validation
        - control_args -> internal execution params

        This does NOT mutate kwargs
        This does NOT affect existing tools
        """
        tool_args: Dict[str, Any] = {}
        control_args: Dict[str, Any] = {}

        for key, value in kwargs.items():
            if key.startswith(self.CONTROL_PREFIX):
                control_args[key] = value
            else:
                tool_args[key] = value

        return tool_args, control_args
