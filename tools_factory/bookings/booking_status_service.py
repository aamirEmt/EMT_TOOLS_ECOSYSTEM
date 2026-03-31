"""Booking Status Service"""
from typing import Dict, Any
import logging

from emt_client.clients.mybookings_client import MyBookingsApiClient
from .booking_status_schema import WhatsappBookingStatusFormat

logger = logging.getLogger(__name__)


class BookingStatusService:
    """Service for fetching booking status by booking ID and email."""

    def __init__(self, email: str, booking_id: str):
        self.email = email
        self.booking_id = booking_id

    async def get_booking_status(self) -> Dict[str, Any]:
        """Fetch booking status from EMT API."""
        try:
            async with MyBookingsApiClient() as client:
                data = await client.fetch_booking_status(self.booking_id, self.email)

            if not data.get("IsSucess"):
                return {"success": False, "error": "INVALID_CREDENTIALS"}

            return {
                "success": True,
                "product_type": data.get("ProductType", ""),
                "trip_status": data.get("TripStatus", ""),
            }

        except Exception as e:
            logger.error(f"Error fetching booking status: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}


def build_whatsapp_booking_status_response(
    booking_id: str, product_type: str, trip_status: str
) -> WhatsappBookingStatusFormat:
    """Build WhatsApp-formatted response for booking status."""
    return WhatsappBookingStatusFormat(
        booking_id=booking_id,
        product_type=product_type,
        trip_status=trip_status,
    )
