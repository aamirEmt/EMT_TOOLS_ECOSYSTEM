"""Train Status Check Tool for EaseMyTrip Railways.

This tool allows users to check the live running status and schedule
of Indian Railway trains with station-wise arrival/departure times.
"""

from tools_factory.base import BaseTool, ToolMetadata
from pydantic import ValidationError

from .train_status_schema import TrainStatusInput
from .train_status_service import (
    get_train_trackable_dates,
    get_train_live_status,
    validate_date_against_available,
    build_whatsapp_train_status_response,
)
from .train_status_renderer import render_train_status_results, render_train_dates
from tools_factory.base_schema import ToolResponseFormat


class TrainStatusTool(BaseTool):
    """Train status check tool for EaseMyTrip Railways."""

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="check_train_status",
            description="Check running status and schedule of Indian Railway trains with station-wise arrival/departure times",
            input_schema=TrainStatusInput.model_json_schema(),
            output_template="ui://widget/train-status.html",
            category="travel",
            tags=["train", "railway", "status", "schedule", "tracking"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        """Execute train status check with provided parameters."""

        # Extract runtime flags
        user_type = kwargs.pop("_user_type", "website")
        is_whatsapp = user_type.lower() == "whatsapp"

        # Validate input
        try:
            payload = TrainStatusInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid train status input",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        # Step 1: Fetch available dates for the train
        dates_result = await get_train_trackable_dates(payload.train_number)

        if dates_result.get("error"):
            return ToolResponseFormat(
                response_text=f"Could not find train {payload.train_number}. {dates_result.get('message', '')}",
                structured_content=dates_result,
                is_error=True,
            )

        available_dates = dates_result.get("available_dates", [])

        # Step 2: If no date provided, return available dates for selection
        if not payload.journey_date:
            if not available_dates:
                return ToolResponseFormat(
                    response_text=f"No trackable dates available for train {payload.train_number}",
                    structured_content=dates_result,
                    is_error=True,
                )

            # Build response with available dates
            date_suggestions = []
            for d in available_dates[:5]:
                display = d.get("display_day", "")
                formatted = d.get("formatted_date", d.get("date", ""))
                if display:
                    date_suggestions.append(f"{formatted} ({display})")
                else:
                    date_suggestions.append(formatted)

            text = (
                f"Train {payload.train_number}: Please provide a date to check status. "
                f"Available dates: {', '.join(date_suggestions)}"
            )

            # Render date selection HTML for website
            html_content = None
            if not is_whatsapp:
                html_content = render_train_dates(dates_result)

            return ToolResponseFormat(
                response_text=text,
                structured_content=dates_result,
                html=html_content,
                is_error=False,
            )

        # Step 3: Validate the requested date against available dates
        is_valid, validation_msg = validate_date_against_available(
            payload.journey_date,
            available_dates,
        )

        if not is_valid:
            return ToolResponseFormat(
                response_text=validation_msg,
                structured_content={
                    "error": "INVALID_DATE",
                    "message": validation_msg,
                    "train_number": payload.train_number,
                    "requested_date": payload.journey_date,
                    "available_dates": available_dates,
                },
                is_error=True,
            )

        # Step 4: Fetch train status for the valid date
        status_result = await get_train_live_status(
            train_number=payload.train_number,
            journey_date=payload.journey_date,
        )

        has_error = bool(status_result.get("error"))

        # Build response text
        if has_error:
            text = f"Unable to fetch status for train {payload.train_number}. {status_result.get('message', '')}"
        else:
            station_count = len(status_result.get("stations", []))
            text = (
                f"Train {status_result.get('train_number')} - {status_result.get('train_name')}: "
                f"{status_result.get('origin_station')} to {status_result.get('destination_station')} "
                f"({station_count} stations)"
            )

        # Build WhatsApp response if needed
        whatsapp_response = None
        if is_whatsapp and not has_error:
            whatsapp_response = build_whatsapp_train_status_response(payload, status_result)

        # Render HTML for website users
        html_content = None
        if not is_whatsapp and not has_error:
            html_content = render_train_status_results(status_result)

        return ToolResponseFormat(
            response_text=text,
            structured_content=None if is_whatsapp else status_result,
            html=html_content,
            whatsapp_response=(
                whatsapp_response.model_dump() if whatsapp_response else None
            ),
            is_error=has_error,
        )
