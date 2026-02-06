"""PNR Status Service - Business logic for checking PNR status."""

import base64
import re
from typing import Any, Dict, List

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from emt_client.clients.train_client import TrainApiClient
from .pnr_status_schema import PassengerInfo, PnrStatusInfo


# AES-128 CBC encryption constants
PNR_ENCRYPTION_KEY = b"8080808080808080"  # 16 bytes
PNR_ENCRYPTION_IV = b"8080808080808080"  # 16 bytes


def encrypt_pnr(pnr_number: str) -> str:
    """
    Encrypt PNR number using AES-128 CBC with PKCS7 padding.

    Args:
        pnr_number: 10-digit PNR number

    Returns:
        Base64 encoded encrypted string
    """
    pnr_number = re.sub(r"[\s\-]", "", pnr_number)
    cipher = AES.new(PNR_ENCRYPTION_KEY, AES.MODE_CBC, PNR_ENCRYPTION_IV)
    padded_data = pad(pnr_number.encode("utf-8"), AES.block_size)
    encrypted = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted).decode("utf-8")


class PnrStatusService:
    """Service for checking PNR status."""

    def __init__(self):
        self.client = TrainApiClient()

    async def check_pnr_status(self, pnr_number: str) -> Dict[str, Any]:
        """
        Check PNR status via EaseMyTrip Railways API.

        Args:
            pnr_number: 10-digit PNR number

        Returns:
            Dict containing processed PNR status or error
        """
        try:
            encrypted_pnr = encrypt_pnr(pnr_number)
            response = await self.client.check_pnr_status(encrypted_pnr)

            # Check for error in response
            if response.get("errorMessage"):
                error_msg = response.get("errorMessage")
                error_type = "API_ERROR"

                # Categorize specific error types
                if "Invalid PNR" in error_msg or "Flushed PNR" in error_msg or "PNR not yet generated" in error_msg:
                    error_type = "INVALID_PNR"

                return {
                    "error": error_type,
                    "message": error_msg,
                    "pnr_number": pnr_number,
                }

            # Check if response has required data
            if not response.get("pnrNumber"):
                return {
                    "error": "INVALID_PNR",
                    "message": "Invalid PNR or PNR not found",
                }

            return self._process_pnr_response(pnr_number, response)

        except Exception as e:
            return {
                "error": "REQUEST_ERROR",
                "message": str(e),
            }

    def _process_pnr_response(
        self,
        pnr_number: str,
        response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Process raw API response into structured format."""

        # Extract passenger list
        passengers: List[PassengerInfo] = []
        passenger_list = response.get("passengerList", [])

        for p in passenger_list:
            serial = p.get("passengerSerialNumber", "")
            try:
                serial_num = int(serial) if serial else len(passengers) + 1
            except ValueError:
                serial_num = len(passengers) + 1

            passengers.append(
                PassengerInfo(
                    serial_number=serial_num,
                    booking_status=p.get("bookingStatus", "N/A"),
                    current_status=p.get("currentStatus", "N/A"),
                    coach=p.get("bookingCoachId") or p.get("currentCoachId"),
                    berth_number=p.get("bookingBerthNo") or p.get("currentBerthNo"),
                    berth_type=p.get("bookingBerthCode"),
                )
            )

        pnr_info = PnrStatusInfo(
            pnr_number=response.get("pnrNumber", pnr_number),
            train_number=response.get("trainNumber", ""),
            train_name=response.get("trainName", ""),
            date_of_journey=response.get("dateOfJourney", ""),
            source_station=response.get("sourceStation", ""),
            source_station_name=response.get("SrcStnName", ""),
            destination_station=response.get("destinationStation", ""),
            destination_station_name=response.get("DestStnName", ""),
            boarding_point=response.get("boardingPoint"),
            boarding_point_name=response.get("BrdPointName"),
            reservation_upto=response.get("reservationUpto"),
            reservation_upto_name=response.get("reservationUptoName"),
            journey_class=response.get("journeyClass", ""),
            class_name=response.get("className"),
            quota=response.get("quota", "GN"),
            quota_name=response.get("quotaName"),
            booking_status=response.get("bookingStatus") or None,
            chart_status=response.get("chartStatus", "Chart Not Prepared"),
            booking_fare=response.get("bookingFare"),
            ticket_fare=response.get("ticketFare"),
            passengers=passengers,
        )

        return {
            "success": True,
            "pnr_info": pnr_info.model_dump(),
        }


def build_whatsapp_pnr_response(pnr_info: Dict[str, Any]) -> Dict[str, Any]:
    """Build WhatsApp-formatted response for PNR status."""
    passengers = []
    for p in pnr_info.get("passengers", []):
        berth_info = None
        if p.get("coach") and p.get("berth_number"):
            berth_info = f"{p['coach']}/{p['berth_number']}"
            if p.get("berth_type"):
                berth_info += f" ({p['berth_type']})"

        passengers.append(
            {
                "serial": p["serial_number"],
                "booking": p["booking_status"],
                "current": p["current_status"],
                "berth": berth_info,
            }
        )

    return {
        "type": "pnr_status",
        "pnr_number": pnr_info["pnr_number"],
        "train_info": f"{pnr_info['train_name']} ({pnr_info['train_number']})",
        "journey_date": pnr_info["date_of_journey"],
        "route": f"{pnr_info['source_station_name']} ({pnr_info['source_station']}) → {pnr_info['destination_station_name']} ({pnr_info['destination_station']})",
        "journey_class": pnr_info.get("class_name") or pnr_info["journey_class"],
        "quota": pnr_info.get("quota_name") or pnr_info["quota"],
        "chart_status": pnr_info["chart_status"],
        "passengers": passengers,
    }
