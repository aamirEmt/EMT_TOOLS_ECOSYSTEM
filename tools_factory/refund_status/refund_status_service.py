"""Refund Status Service"""
from typing import Dict, Any
import logging

from emt_client.clients.mybookings_client import MyBookingsApiClient
from .refund_status_schema import WhatsappRefundStatusFormat

logger = logging.getLogger(__name__)


class RefundStatusService:
    """Service for fetching refund status by booking ID and email."""

    def __init__(self, email: str, booking_id: str):
        self.email = email
        self.booking_id = booking_id

    async def get_refund_status(self) -> Dict[str, Any]:
        """Fetch booking status from EMT API and derive refund status."""
        try:
            async with MyBookingsApiClient() as client:
                data = await client.fetch_booking_status(self.booking_id, self.email)

            if not data.get("IsSucess"):
                return {"success": False, "error": "INVALID_CREDENTIALS"}

            trip_status = data.get("TripStatus", "")
            refund_status = "Refunded" if "refunded" in trip_status.lower() else "Refund status not available"

            return {
                "success": True,
                "product_type": data.get("ProductType", ""),
                "trip_status": trip_status,
                "refund_status": refund_status,
            }

        except Exception as e:
            logger.error(f"Error fetching refund status: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}


def build_whatsapp_refund_status_response(
    booking_id: str, product_type: str, trip_status: str, refund_status: str
) -> WhatsappRefundStatusFormat:
    """Build WhatsApp-formatted response for refund status."""
    return WhatsappRefundStatusFormat(
        booking_id=booking_id,
        product_type=product_type,
        trip_status=trip_status,
        refund_status=refund_status,
    )
