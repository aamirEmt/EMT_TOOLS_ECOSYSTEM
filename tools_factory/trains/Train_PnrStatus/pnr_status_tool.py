"""Train PNR Status Tool - Check PNR status for Indian Railways."""

from pydantic import ValidationError

from tools_factory.base import BaseTool, ToolMetadata
from tools_factory.base_schema import ToolResponseFormat

from .pnr_status_schema import PnrStatusInput
from .pnr_status_service import PnrStatusService, build_whatsapp_pnr_response
from .pnr_status_renderer import render_pnr_status


class TrainPnrStatusTool(BaseTool):
    """Tool for checking Indian Railways PNR status."""

    def __init__(self):
        super().__init__()
        self.service = PnrStatusService()

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="check_pnr_status",
            description="Check PNR status for Indian Railways train bookings. Requires a 10-digit PNR number.",
            input_schema=PnrStatusInput.model_json_schema(),
            output_template="ui://widget/pnr-status.html",
            category="travel",
            tags=["train", "railway", "pnr", "status", "booking"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        """Execute PNR status check."""

        # Extract runtime flags
        user_type = kwargs.pop("_user_type", "website")
        is_whatsapp = user_type.lower() == "whatsapp"

        # Validate input
        try:
            payload = PnrStatusInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid PNR number input",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        # Check PNR status
        result = await self.service.check_pnr_status(payload.pnr_number)

        has_error = bool(result.get("error"))

        if has_error:
            return ToolResponseFormat(
                response_text=f"Could not fetch PNR status: {result.get('message', 'Unknown error')}",
                structured_content=result,
                is_error=True,
            )

        pnr_info = result.get("pnr_info", {})

        # Build response text
        response_text = self._build_response_text(pnr_info)

        # Build WhatsApp response if needed
        whatsapp_response = None
        if is_whatsapp:
            whatsapp_response = build_whatsapp_pnr_response(pnr_info)

        # Render HTML for website users
        html_content = None
        if not is_whatsapp:
            html_content = render_pnr_status(pnr_info)

        return ToolResponseFormat(
            response_text=response_text,
            structured_content=None if is_whatsapp else result,
            html=html_content,
            whatsapp_response=whatsapp_response,
            is_error=False,
        )

    def _build_response_text(self, pnr_info: dict) -> str:
        """Build human-readable response text."""
        passengers = pnr_info.get("passengers", [])
        passenger_status = ", ".join(
            f"P{p['serial_number']}: {p['current_status']}" for p in passengers
        )

        return (
            f"PNR {pnr_info['pnr_number']} - "
            f"{pnr_info['train_name']} ({pnr_info['train_number']}) | "
            f"{pnr_info['source_station']} to {pnr_info['destination_station']} | "
            f"{pnr_info['date_of_journey']} | "
            f"Class: {pnr_info.get('class_name') or pnr_info['journey_class']} | "
            f"Status: {passenger_status} | "
            f"Chart: {pnr_info['chart_status']}"
        )
