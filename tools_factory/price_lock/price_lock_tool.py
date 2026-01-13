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
                lock_period_hours=payload.lock_period_hours,
            )
        except Exception as exc:  # noqa: BLE001
            return {
                "text": f"Failed to lock price: {exc}",
                "is_error": True,
            }

        checkout_url = result.get("checkoutUrl")
        price_lock_id = result.get("priceLockId")
        is_error = price_lock_id is None

        # Only return the checkout URL (safepay) or a concise error message.
        if not is_error and checkout_url:
            return {
                "text": checkout_url,
                "is_error": False,
            }

        # Fallback error text if checkout URL is missing.
        return {
            "text": "Price lock did not return a checkout URL.",
            "is_error": True,
        }
