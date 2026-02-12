"""Train Availability Check Tool - Check real-time train availability across multiple classes."""

from pydantic import ValidationError

from tools_factory.base import BaseTool, ToolMetadata
from tools_factory.base_schema import ToolResponseFormat

from .availability_check_schema import AvailabilityCheckInput
from .availability_check_service import (
    AvailabilityCheckService,
    build_whatsapp_availability_response,
)
from .availability_check_renderer import render_availability_check


class TrainAvailabilityCheckTool(BaseTool):
    """Tool for checking train availability across multiple classes."""

    def __init__(self):
        super().__init__()
        self.service = AvailabilityCheckService()

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="check_train_availability",
            description="Check real-time train availability across multiple classes for a specific train and date. Shows seat availability and fares for different travel classes.",
            input_schema=AvailabilityCheckInput.model_json_schema(),
            output_template="ui://widget/train-availability.html",
            category="travel",
            tags=["train", "railway", "availability", "booking", "seat"],
        )

    async def execute(self, **kwargs) -> ToolResponseFormat:
        """Execute availability check."""

        # Extract runtime flags
        user_type = kwargs.pop("_user_type", "website")
        is_whatsapp = user_type.lower() == "whatsapp"
        _ = kwargs.pop("_limit", None)  # Extract but not used

        # Validate input
        try:
            payload = AvailabilityCheckInput.model_validate(kwargs)
        except ValidationError as exc:
            return ToolResponseFormat(
                response_text="Invalid availability check input",
                structured_content={
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                is_error=True,
            )

        # Check availability across multiple classes (route is fetched if not provided)
        result = await self.service.check_availability_multiple_classes(
            train_no=payload.train_no,
            classes=payload.classes,
            journey_date=payload.journey_date,
            quota=payload.quota,
            from_station_code=payload.from_station_code,
            to_station_code=payload.to_station_code,
        )

        has_error = not result.get("success")

        if has_error:
            return ToolResponseFormat(
                response_text="Could not check availability",
                structured_content=result,
                is_error=True,
            )

        train_info = result.get("train_info", {})
        classes = result.get("classes", [])

        # Check if ALL classes have error messages (quota/tatkal errors)
        if classes:
            error_keywords = [
                "quota", "not valid", "tatkal", "advance reservation period",
                "error", "regret", "not available", "does not exist",
                "class does not exist", "invalid", "failed"
            ]
            all_errors = all(
                any(keyword in cls.get("status", "").lower() for keyword in error_keywords)
                for cls in classes
            )

            if all_errors:
                # All classes have errors - return error response without UI
                error_status = classes[0].get("status", "Availability check failed")
                return ToolResponseFormat(
                    response_text=error_status,
                    structured_content=result,
                    is_error=True,
                )

        # Get route information from result
        route_info = result.get("route_info", {})
        from_station = route_info.get("from_station_name", route_info.get("from_station_code", ""))
        to_station = route_info.get("to_station_name", route_info.get("to_station_code", ""))

        # Build response text
        response_text = self._build_response_text(train_info, classes, payload.journey_date)

        # Build WhatsApp response if needed
        whatsapp_response = None
        if is_whatsapp:
            whatsapp_response = build_whatsapp_availability_response(
                train_info=train_info,
                classes=classes,
                journey_date=payload.journey_date,
                route_info=route_info,
                quota=payload.quota,
            )

        # Render HTML for website users
        html_content = None
        if not is_whatsapp:
            html_content = render_availability_check(
                train_info=train_info,
                classes=classes,
                journey_date=payload.journey_date,
                from_station=from_station,
                to_station=to_station,
                quota=payload.quota,
                from_station_code=route_info.get("from_station_code", ""),
                to_station_code=route_info.get("to_station_code", ""),
            )

        return ToolResponseFormat(
            response_text=response_text,
            structured_content=None if is_whatsapp else result,
            html=html_content,
            whatsapp_response=whatsapp_response,
            is_error=False,
        )

    def _build_response_text(self, train_info: dict, classes: list, journey_date: str) -> str:
        """Build human-readable response text."""
        train_name = train_info.get("train_name", "Unknown Train")
        train_no = train_info.get("train_no", "")

        # Count available seats
        available_count = 0
        waitlist_count = 0
        rac_count = 0

        for cls in classes:
            status = cls.get("status", "").upper()
            if "AVAILABLE" in status and "NOT" not in status:
                available_count += 1
            elif "WL" in status or "WAITLIST" in status:
                waitlist_count += 1
            elif "RAC" in status:
                rac_count += 1

        # Build summary
        summary_parts = []
        if available_count > 0:
            summary_parts.append(f"{available_count} available")
        if waitlist_count > 0:
            summary_parts.append(f"{waitlist_count} waitlist")
        if rac_count > 0:
            summary_parts.append(f"{rac_count} RAC")

        summary = ", ".join(summary_parts) if summary_parts else "No seats available"

        return (
            f"Availability for {train_name} ({train_no}) on {journey_date}: "
            f"{summary}. Classes checked: {', '.join(c['class_code'] for c in classes)}"
        )
