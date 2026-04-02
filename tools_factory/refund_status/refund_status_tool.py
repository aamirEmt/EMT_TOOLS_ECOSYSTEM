"""Refund Status Tool"""
import logging

from pydantic import ValidationError

from ..base import BaseTool, ToolMetadata
from .refund_status_schema import RefundStatusInput
from .refund_status_service import RefundStatusService, build_whatsapp_refund_status_response
from .refund_status_renderer import render_refund_status
from tools_factory.base_schema import ToolResponseFormat

logger = logging.getLogger(__name__)


class GetRefundStatusTool(BaseTool):
    """Tool for checking refund status by booking ID and email."""

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="get_refund_status_by_booking_id",
            description=(
                "Check the refund status of a booking using a booking/transaction ID and the "
                "email address associated with the booking. Use this when the user asks about "
                "refunds, e.g. 'what is the refund status of my booking', 'has my refund been "
                "processed', 'did I get a refund', 'when will I get my refund'. "
                "Requires both the booking ID and registered email."
            ),
            input_schema=RefundStatusInput.model_json_schema(),
            category="bookings",
            tags=["refund", "status", "booking", "trip"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        """Execute refund status check."""

        # Extract runtime flags
        kwargs.pop("_session_id", None)
        kwargs.pop("_limit", None)
        user_type = kwargs.pop("_user_type", "website")
        is_whatsapp = user_type.lower() == "whatsapp"

        try:
            payload = RefundStatusInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid input. Please provide a valid email and booking ID.",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        service = RefundStatusService(payload.email, payload.booking_id)
        result = await service.get_refund_status()

        if not result.get("success"):
            error = result.get("error", "")
            if error == "INVALID_CREDENTIALS":
                return ToolResponseFormat(
                    response_text=(
                        "The email or booking ID you provided doesn't match our records. "
                        "Please check and try again."
                    ),
                    is_error=True,
                )
            return ToolResponseFormat(
                response_text="Unable to fetch refund status. Please try again later.",
                is_error=True,
            )

        product_type = result["product_type"]
        trip_status = result["trip_status"]
        refund_status = result["refund_status"]
        booking_id = payload.booking_id

        response_text = (
            f"Booking ID: {booking_id}\n"
            f"Product Type: {product_type}\n"
            f"Current Status: {trip_status}\n"
            f"Refund Status: {refund_status}"
        )

        html_content = None
        if not is_whatsapp:
            html_content = render_refund_status(booking_id, product_type, trip_status, refund_status)

        whatsapp_response = None
        if is_whatsapp:
            whatsapp_response = build_whatsapp_refund_status_response(
                booking_id, product_type, trip_status, refund_status
            ).model_dump()

        return ToolResponseFormat(
            response_text=response_text,
            structured_content=None if is_whatsapp else {
                "booking_id": booking_id,
                "product_type": product_type,
                "trip_status": trip_status,
                "refund_status": refund_status,
            },
            html=html_content,
            whatsapp_response=whatsapp_response,
            is_error=False,
        )
