from typing import Dict, Any
from tools_factory.base import BaseTool, ToolMetadata
from pydantic import ValidationError

from emt_client.utils import generate_short_link
from .flight_scehma import FlightSearchInput,FlightResponseFormat,WhatsappFlightFinalResponse,WhatsappFlightFormat
from .flight_search_service import search_flights
from .flight_renderer import render_flight_results


def extract_segment_summary(segment: dict) -> dict:
    """
    Extract normalized flight data from a real EMT flight segment.
    Works for single-leg and multi-leg journeys.
    """
    legs = segment.get("legs") or []

    if not legs:
        return {
            "airline": None,
            "flight_number": None,
            "departure_time": None,
            "arrival_time": None,
            "duration": segment.get("journey_time"),
            "stops": segment.get("total_stops", 0),
        }

    first_leg = legs[0]
    last_leg = legs[-1]

    return {
        "airline": first_leg.get("airline_name"),
        "flight_number": " / ".join(
            f"{leg.get('airline_code')}{leg.get('flight_number')}"
            for leg in legs
            if leg.get("flight_number")
        ),
        "departure_time": first_leg.get("departure_time"),
        "arrival_time": last_leg.get("arrival_time"),
        "duration": segment.get("journey_time"),
        "stops": segment.get("total_stops", 0),
    }


class FlightSearchTool(BaseTool):
    """Flight search tool for EaseMyTrip"""

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="search_flights",
            description="Search for flights on EaseMyTrip with origin, destination, dates, and passengers",
            input_schema=FlightSearchInput.model_json_schema(),
            output_template="ui://widget/flight-carousel.html",
            category="travel",
            tags=["flight", "booking", "travel", "search"],
        )

    async def execute(self, **kwargs) -> FlightResponseFormat:
        """
        Execute flight search with provided parameters.
        """

        # --------------------------------------------------
        # Runtime flags (internal)
        # --------------------------------------------------
        # limit = kwargs.pop("_limit", None)
        # render_html = kwargs.pop("_html", False)
        # is_coming_from_whatsapp = kwargs.pop("_is_coming_from_whatsapp", False)

        # --------------------------
        # Extract runtime flags (with backward compatibility)
        # --------------------------
        limit = kwargs.pop("_limit", None)

        # Handle legacy flags for backward compatibility
        if "_user_type" not in kwargs:
            if kwargs.pop("_is_coming_from_whatsapp", False):
                kwargs["_user_type"] = "whatsapp"
            elif kwargs.pop("_html", False):
                kwargs["_user_type"] = "web"

        # Unified user type handling
        user_type = kwargs.pop("_user_type", "web")
        render_html = user_type.lower() != "whatsapp"
        is_coming_from_whatsapp = user_type.lower() == "whatsapp"


        try:
            payload = FlightSearchInput.model_validate(kwargs)
        except ValidationError as exc:
            return {
                "text": "Invalid flight search input",
                "structured_content": {
                    "error": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
                "html": None,
                "is_error": True,
            }

        # --------------------------------------------------
        # Search flights
        # --------------------------------------------------
        flight_results = await search_flights(
            origin=payload.origin,
            destination=payload.destination,
            outbound_date=payload.outbound_date,
            return_date=payload.return_date,
            adults=payload.adults,
            children=payload.children,
            infants=payload.infants,
            cabin=payload.cabin,
        )

        # --------------------------------------------------
        # Passenger context (required for deeplinks)
        # --------------------------------------------------
        flight_results["passengers"] = {
            "adults": payload.adults,
            "children": payload.children,
            "infants": payload.infants,
        }

        # --------------------------------------------------
        # Apply limit (explicit or WhatsApp default = 3)
        # --------------------------------------------------
        applied_limit = limit if limit is not None else (3 if is_coming_from_whatsapp else None)

        if applied_limit is not None:
            if "outbound_flights" in flight_results:
                flight_results["outbound_flights"] = flight_results["outbound_flights"][:applied_limit]
            if "return_flights" in flight_results:
                flight_results["return_flights"] = flight_results["return_flights"][:applied_limit]
            if "international_combos" in flight_results:
                flight_results["international_combos"] = flight_results["international_combos"][:applied_limit]

        # --------------------------------------------------
        # Normalize & short-link results
        # --------------------------------------------------
        outbound_count = 0
        return_count = 0
        combo_count = 0

        is_roundtrip = flight_results.get("is_roundtrip")
        is_international = flight_results.get("is_international")

        international_combos = flight_results.get("international_combos") or []

        if is_international and international_combos:
            combo_count = len(international_combos)
            flight_results["international_combos"] = generate_short_link(
                international_combos,
                product_type="flight",
            )
            flight_results["outbound_flights"] = []
            flight_results["return_flights"] = []

        else:
            outbound_flights = flight_results.get("outbound_flights") or []
            outbound_count = len(outbound_flights)
            flight_results["outbound_flights"] = generate_short_link(
                outbound_flights,
                product_type="flight",
            )

            if is_roundtrip:
                return_flights = flight_results.get("return_flights") or []
                return_count = len(return_flights)
                flight_results["return_flights"] = generate_short_link(
                    return_flights,
                    product_type="flight",
                )

        # --------------------------------------------------
        # WhatsApp FINAL JSON (Hotels-style, 4 combos)
        # --------------------------------------------------
        if is_coming_from_whatsapp and not flight_results.get("error"):
            options = []

            # ---------- ONEWAY (Domestic + International) ----------
            if not is_roundtrip:
                for idx, flight in enumerate(flight_results.get("outbound_flights", []), start=1):
                    summary = extract_segment_summary(flight)
                    fare = (flight.get("fare_options") or [{}])[0]

                    options.append({
                        "option_id": idx,
                        "outbound_flight": {
                            "airline": summary["airline"],
                            "flight_number": summary["flight_number"],
                            "origin": payload.origin,
                            "destination": payload.destination,
                            "departure_time": summary["departure_time"],
                            "arrival_time": summary["arrival_time"],
                            "duration": summary["duration"],
                            "stops": summary["stops"],
                            "date": payload.outbound_date,
                        },
                        "price": fare.get("total_fare"),
                        "booking_url": flight.get("booking_url"),
                    })

                trip_type = "oneway"

            # ---------- ROUNDTRIP DOMESTIC ----------
            elif is_roundtrip and not is_international:
                for idx, (out_f, ret_f) in enumerate(
                    zip(
                        flight_results.get("outbound_flights", []),
                        flight_results.get("return_flights", []),
                    ),
                    start=1,
                ):
                    out_summary = extract_segment_summary(out_f)
                    ret_summary = extract_segment_summary(ret_f)

                    out_fare = (out_f.get("fare_options") or [{}])[0]
                    ret_fare = (ret_f.get("fare_options") or [{}])[0]

                    total_price = (out_fare.get("total_fare") or 0) + (ret_fare.get("total_fare") or 0)

                    options.append({
                        "option_id": idx,
                        "outbound_flight": out_summary,
                        "inbound_flight": ret_summary,
                        "total_price": total_price,
                        "booking_url": out_f.get("booking_url"),
                    })

                trip_type = "roundtrip"

            # ---------- ROUNDTRIP INTERNATIONAL ----------
            else:
                for idx, combo in enumerate(flight_results.get("international_combos", []), start=1):
                    onward = combo.get("onward_flight", {})
                    return_f = combo.get("return_flight", {})

                    options.append({
                        "option_id": idx,
                        "outbound_flight": extract_segment_summary(onward),
                        "inbound_flight": extract_segment_summary(return_f),
                        "total_price": combo.get("combo_fare"),
                        "booking_url": combo.get("deepLink"),
                    })

                trip_type = "roundtrip"
            whatsapp_json: WhatsappFlightFormat = WhatsappFlightFormat(
                options=options,
                trip_type=trip_type,
                journey_type="international" if is_international else "domestic",
                currency=flight_results.get("currency", "INR"),
                view_all_flights_url=flight_results.get("view_all_flights_url", ""),
            )
            whatsapp_response: WhatsappFlightFinalResponse =WhatsappFlightFinalResponse(
                response_text =  f"Here are the best flight options from {payload.origin} to {payload.destination}",
                whatsapp_json=whatsapp_json
            )

        # --------------------------------------------------
        # Human-readable text (existing behavior)
        # --------------------------------------------------
        if flight_results.get("error"):
            text = f"No flights found. {flight_results.get('message', '')}"
        elif is_international and is_roundtrip:
            text = f"Found {combo_count} international round-trip combinations!"
        elif is_roundtrip:
            text = f"Found {outbound_count} outbound and {return_count} return flights!"
        else:
            text = f"Found {outbound_count} flights!"

        # --------------------------------------------------
        # Default response (existing behavior)
        # --------------------------------------------------
        # if render_html and not flight_results.get("error"):
        #     response["html"] = render_flight_results(flight_results)
        response: FlightResponseFormat = FlightResponseFormat(
            response_text=text,
            structured_content=flight_results if not is_coming_from_whatsapp else {},
            html= render_flight_results(flight_results) if render_html and not flight_results.get("error") else None,
            whatsapp_response=whatsapp_response if is_coming_from_whatsapp and not flight_results.get("error") else None,
            is_error=flight_results.get("error") is not None,
        )

        # --------------------------------------------------
        # Render HTML (if requested)
        # --------------------------------------------------
       

        return response
