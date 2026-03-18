from tools_factory.base import BaseTool, ToolMetadata
from tools_factory.base_schema import ToolResponseFormat


class HandoffToCustomerAgentTool(BaseTool):
    """Tool to hand off the conversation to a customer support agent."""

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="handoff_to_customer_agent",
            description=(
                "Use this tool when the user wants to speak to a human customer support agent. "
                "Triggers include requests like 'talk to an agent', 'connect me to support', "
                "'I want to speak to a person', 'transfer me', 'customer care', etc. "
                "This tool requires no inputs."
            ),
            input_schema={"type": "object", "properties": {}},
            category="support",
            tags=["handoff", "customer", "agent", "support", "human"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        # Pop runtime parameters injected by the caller
        kwargs.pop("_session_id", None)
        kwargs.pop("_user_type", None)
        kwargs.pop("_limit", None)

        return ToolResponseFormat(
            response_text="Transferring you to a customer support agent.",
            handoffToCustomerAgent=True,
        )
