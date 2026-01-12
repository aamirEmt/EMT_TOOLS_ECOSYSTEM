from typing import Any, Dict

from pydantic import ValidationError

from tools_factory.base import BaseTool, ToolMetadata
from .price_lock_schema import PriceLockInput
from .price_lock_service import PriceLockService


class PriceLockTool(BaseTool):
    """Tool that reprices a selected flight and creates a price lock order."""

    def __init__(self) -> None:
        super().__init__()
        self.service = PriceLockService()

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="lock_flight_price",
            description=(
                "Lock a flight fare using an existing search response. "
                "Provide the login key, flight index, fare index (optional), "
                "and the full search response returned by the flight search tool."
            ),
            input_schema=PriceLockInput.model_json_schema(),
            category="travel",
            tags=["flight", "lock", "reprice", "booking"],
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            payload = PriceLockInput.model_validate(kwargs)
        except ValidationError as exc:
            return {
                "text": "Invalid price lock input",
                "structured_content": {
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                "html": None,
                "is_error": True,
            }

        try:
            result = await self.service.lock_price(
                login_key=payload.login_key,
                flight_index=payload.flight_index,
                fare_index=payload.fare_index,
                search_response=payload.search_response,
                direction=payload.direction,
            )
        except Exception as exc:  # noqa: BLE001
            return {
                "text": f"Failed to lock price: {exc}",
                "structured_content": {
                    "error": "LOCK_FAILED",
                    "message": str(exc),
                },
                "html": None,
                "is_error": True,
            }

        checkout_url = result.get("checkoutUrl")
        price_lock_id = result.get("priceLockId")
        is_error = price_lock_id is None

        text_parts = []
        if price_lock_id:
            text_parts.append(
                f"Locked flight #{payload.flight_index + 1} ({payload.direction})."
            )
            if checkout_url:
                text_parts.append(f"Checkout URL: {checkout_url}")
        else:
            text_parts.append(
                f"Price lock did not return an ID for flight #{payload.flight_index + 1}."
            )
            text_parts.append("Check lockResponse for API details.")

        return {
            "text": " ".join(text_parts),
            "structured_content": result,
            "html": None,
            "is_error": is_error,
        }
