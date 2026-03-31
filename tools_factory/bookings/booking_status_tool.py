"""Booking Status Tool"""
import logging

from pydantic import ValidationError

from ..base import BaseTool, ToolMetadata
from .booking_status_schema import BookingStatusInput
from .booking_status_service import BookingStatusService, build_whatsapp_booking_status_response
from .booking_status_renderer import render_booking_status
from tools_factory.base_schema import ToolResponseFormat

logger = logging.getLogger(__name__)


class GetBookingStatusTool(BaseTool):
    """Tool for checking booking status by booking ID and email."""

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="get_booking_status",
            description=(
                "Check the status of a booking using a booking/transaction ID and the email "
                "address associated with the booking. Use this when the user asks about the "
                "status of a specific booking, e.g. 'what is the status of booking ABC123', "
                "'check my booking', 'is my trip confirmed'. "
                "Requires both the booking ID and registered email."
            ),
            input_schema=BookingStatusInput.model_json_schema(),
            category="bookings",
            tags=["booking", "status", "check", "trip"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        """Execute booking status check."""

        # Extract runtime flags
        kwargs.pop("_session_id", None)
        kwargs.pop("_limit", None)
        user_type = kwargs.pop("_user_type", "website")
        is_whatsapp = user_type.lower() == "whatsapp"

        try:
            payload = BookingStatusInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid input. Please provide a valid email and booking ID.",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        service = BookingStatusService(payload.email, payload.booking_id)
        result = await service.get_booking_status()

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
                response_text=f"Unable to fetch booking status. Please try again later.",
                is_error=True,
            )

        product_type = result["product_type"]
        trip_status = result["trip_status"]
        booking_id = payload.booking_id

        response_text = (
            f"Booking ID: {booking_id}\n"
            f"Product Type: {product_type}\n"
            f"Trip Status: {trip_status}"
        )

        html_content = None
        if not is_whatsapp:
            html_content = render_booking_status(booking_id, product_type, trip_status)

        whatsapp_response = None
        if is_whatsapp:
            whatsapp_response = build_whatsapp_booking_status_response(
                booking_id, product_type, trip_status
            ).model_dump()

        return ToolResponseFormat(
            response_text=response_text,
            structured_content=None if is_whatsapp else {
                "booking_id": booking_id,
                "product_type": product_type,
                "trip_status": trip_status,
            },
            html=html_content,
            whatsapp_response=whatsapp_response,
            is_error=False,
        )
