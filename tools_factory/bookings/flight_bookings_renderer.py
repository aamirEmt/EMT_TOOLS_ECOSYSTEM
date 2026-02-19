"""Flight Bookings Renderer - HTML renderer for flight booking data."""
from typing import Dict, Any, List
from jinja2 import Environment, BaseLoader, select_autoescape

_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)

# =====================================================================
# FLIGHT BOOKINGS TEMPLATE
# =====================================================================
FLIGHT_BOOKINGS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

.flight-bookings {
  font-family: poppins, sans-serif;
  color: #202020;
  background: rgba(255, 255, 255, 0.92);
  max-width: 750px;
  margin: 0 auto;
  padding: 20px 0 30px;
}

.flight-bookings * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
}

.flight-bookings .bkng-header {
  margin-bottom: 16px;
}

.flight-bookings .bkng-title {
  font-size: 18px;
  font-weight: 600;
  color: #202020;
}

.flight-bookings .bkng-subtitle {
  font-size: 12px;
  color: #646d74;
  margin-top: 4px;
}

.flight-bookings .bkng-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
  margin-bottom: 16px;
  scrollbar-width: thin;
  scrollbar-color: #ccc transparent;
}

.flight-bookings .bkng-tabs::-webkit-scrollbar {
  height: 4px;
}

.flight-bookings .bkng-tabs::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}

.flight-bookings .bkng-tab {
  padding: 8px 18px;
  border-radius: 20px;
  border: 1px solid #e0e0e0;
  background: #fff;
  color: #646d74;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
  font-family: poppins, sans-serif;
}

.flight-bookings .bkng-tab:hover {
  border-color: #ef6614;
  color: #ef6614;
}

.flight-bookings .bkng-tab.active {
  background: #ef6614;
  color: #fff;
  border-color: #ef6614;
}

.flight-bookings .tab-count {
  font-weight: 600;
  font-size: 12px;
}

.flight-bookings .bkng-cards {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.flight-bookings .bkng-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fff;
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}

.flight-bookings .bkng-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.flight-bookings .card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #f0f0f0;
}

.flight-bookings .card-top-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.flight-bookings .status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.flight-bookings .status-badge.upcoming {
  background: #e3f2fd;
  color: #1565c0;
}

.flight-bookings .status-badge.cancelled {
  background: #ffebee;
  color: #c62828;
}

.flight-bookings .status-badge.completed {
  background: #e8f5e9;
  color: #2e7d32;
}

.flight-bookings .status-badge.locked {
  background: #f5f5f5;
  color: #757575;
}

.flight-bookings .status-badge.rejected {
  background: #fce4ec;
  color: #c62828;
}

.flight-bookings .trip-type-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
  background: #f3e5f5;
  color: #7b1fa2;
}

.flight-bookings .booking-ref {
  font-size: 12px;
  font-weight: 600;
  color: #ef6614;
  font-family: inter, sans-serif;
}

.flight-bookings .card-body {
  padding: 16px;
}

.flight-bookings .segment {
  margin-bottom: 12px;
}

.flight-bookings .segment:last-child {
  margin-bottom: 0;
}

.flight-bookings .airline-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.flight-bookings .airline-name {
  font-size: 14px;
  font-weight: 600;
  color: #202020;
}

.flight-bookings .flight-num {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 6px;
  background: #F2F9FF;
  border: 1px solid #B6D5F0;
  border-radius: 3px;
  color: #313131;
}

.flight-bookings .class-info {
  font-size: 11px;
  color: #868686;
  margin-left: auto;
}

.flight-bookings .timing-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 8px;
}

.flight-bookings .time-block {
  text-align: center;
  flex: 1;
}

.flight-bookings .time-value {
  font-size: 18px;
  font-weight: 700;
  color: #202020;
  font-family: inter, sans-serif;
}

.flight-bookings .city-code {
  font-size: 10px;
  color: #868686;
  text-transform: uppercase;
  margin-top: 2px;
}

.flight-bookings .city-name {
  font-size: 10px;
  color: #868686;
  margin-top: 1px;
}

.flight-bookings .terminal {
  font-size: 9px;
  color: #aaa;
  margin-top: 1px;
}

.flight-bookings .duration-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 8px;
  min-width: 90px;
}

.flight-bookings .duration-text {
  font-size: 11px;
  color: #646d74;
  font-weight: 500;
  margin-bottom: 4px;
}

.flight-bookings .duration-line {
  width: 100%;
  height: 1px;
  background: #ccc;
  position: relative;
}

.flight-bookings .duration-line::before,
.flight-bookings .duration-line::after {
  content: '';
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ccc;
}

.flight-bookings .duration-line::before { left: 0; }
.flight-bookings .duration-line::after { right: 0; }

.flight-bookings .stops-text {
  font-size: 9px;
  color: #868686;
  margin-top: 4px;
}

.flight-bookings .card-footer {
  padding: 10px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  flex-wrap: wrap;
  gap: 6px 16px;
  font-size: 11px;
  color: #646d74;
}

.flight-bookings .footer-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.flight-bookings .footer-label {
  font-weight: 500;
  color: #868686;
}

.flight-bookings .footer-value {
  color: #202020;
  font-weight: 500;
}

.flight-bookings .pax-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 16px;
  padding: 8px 16px;
  border-top: 1px dashed #e0e0e0;
  font-size: 11px;
}

.flight-bookings .pax-name {
  font-weight: 600;
  color: #202020;
}

.flight-bookings .pax-status {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
}

.flight-bookings .pax-status.confirmed {
  background: #e8f5e9;
  color: #2e7d32;
}

.flight-bookings .pax-status.cancel-requested {
  background: #fff3e0;
  color: #e65100;
}

.flight-bookings .pax-status.cancelled {
  background: #ffebee;
  color: #c62828;
}

.flight-bookings .pax-amount {
  margin-left: auto;
  font-weight: 600;
  color: #202020;
  font-family: inter, sans-serif;
}

.flight-bookings .cancel-strip {
  padding: 6px 16px;
  background: #fff3e0;
  font-size: 11px;
  color: #e65100;
  font-weight: 500;
}

.flight-bookings .bkng-empty {
  text-align: center;
  color: #646d74;
  padding: 40px 20px;
  font-size: 14px;
}

.flight-bookings .baggage-info {
  display: flex;
  gap: 12px;
  font-size: 10px;
  color: #868686;
  padding: 4px 16px 8px;
}

.flight-bookings .show-more-btn {
  width: 100%;
  padding: 8px 16px;
  background: #fff;
  color: #ef6614;
  border: 1px solid #f0c8a8;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  font-family: poppins, sans-serif;
  transition: all 0.2s ease;
}

.flight-bookings .show-more-btn:hover {
  background: #fff5ee;
  border-color: #ef6614;
}
</style>

<div class="flight-bookings" data-instance-id="flight-bookings-{{ instance_id }}">
  <div class="bkng-header">
    <div class="bkng-title">{{ title }}</div>
    <div class="bkng-subtitle">{{ subtitle }}</div>
  </div>

  {% if tabs %}
  <div class="bkng-tabs">
    {% for tab in tabs %}
    <button class="bkng-tab {% if tab.active %}active{% endif %}" data-status="{{ tab.key }}" onclick="var p=this.closest('.flight-bookings');p.querySelectorAll('.bkng-tab').forEach(function(t){t.classList.remove('active')});this.classList.add('active');var s=this.dataset.status,v=0,idx=0;p.querySelectorAll('.bkng-card').forEach(function(c){var match=c.dataset.status===s;if(match){c.style.display=idx<3?'':'none';if(idx<3)v++;idx++}else{c.style.display='none'}});p.querySelectorAll('.show-more-btn').forEach(function(b){if(b.dataset.forStatus===s){var t=parseInt(b.dataset.total);b.style.display=t>3?'':'none';b.textContent='Show '+(t-3)+' More'}else{b.style.display='none'}});var e=p.querySelector('.bkng-empty');if(e)e.style.display=v?'none':''">
      {{ tab.label }} <span class="tab-count">({{ tab.count }})</span>
    </button>
    {% endfor %}
  </div>
  {% endif %}

  <div class="bkng-cards">
    {% for booking in bookings %}
    <div class="bkng-card" data-status="{{ booking.status_key }}" {% if not booking.visible or booking.status_index >= 3 %}style="display:none"{% endif %}>
      <div class="card-top">
        <div class="card-top-left">
          <span class="status-badge {{ booking.status_class }}">{{ booking.status }}</span>
          {% if booking.trip_type %}
          <span class="trip-type-badge">{{ booking.trip_type }}</span>
          {% endif %}
        </div>
        <span class="booking-ref">{{ booking.booking_ref }}</span>
      </div>

      <div class="card-body">
        {% for seg in booking.segments %}
        <div class="segment">
          <div class="airline-row">
            <span class="airline-name">{{ seg.airline }}</span>
            <span class="flight-num">{{ seg.airline_code }}-{{ seg.flight_number }}</span>
            <span class="class-info">{{ seg.class_type }}{% if seg.brand_fare %} | {{ seg.brand_fare }}{% endif %}</span>
          </div>
          <div class="timing-row">
            <div class="time-block">
              <div class="time-value">{{ seg.departure_time }}</div>
              <div class="city-code">{{ seg.departure_code }}</div>
              <div class="city-name">{{ seg.departure_city }}</div>
              {% if seg.source_terminal %}<div class="terminal">{{ seg.source_terminal }}</div>{% endif %}
            </div>
            <div class="duration-block">
              <div class="duration-text">{{ seg.duration }}</div>
              <div class="duration-line"></div>
              <div class="stops-text">{{ seg.stops_text }}</div>
            </div>
            <div class="time-block">
              <div class="time-value">{{ seg.arrival_time }}</div>
              <div class="city-code">{{ seg.arrival_code }}</div>
              <div class="city-name">{{ seg.arrival_city }}</div>
              {% if seg.dest_terminal %}<div class="terminal">{{ seg.dest_terminal }}</div>{% endif %}
            </div>
          </div>
          {% if seg.baggage or seg.cabin_baggage %}
          <div class="baggage-info">
            {% if seg.baggage %}<span>Check-in: {{ seg.baggage }}</span>{% endif %}
            {% if seg.cabin_baggage %}<span>Cabin: {{ seg.cabin_baggage }}</span>{% endif %}
          </div>
          {% endif %}
        </div>
        {% endfor %}
      </div>

      {% for pax in booking.passengers %}
      <div class="pax-row">
        <span class="pax-name">{{ pax.name }}</span>
        <span class="pax-status {{ pax.status_class }}">{{ pax.status }}</span>
        {% if pax.pnr %}<span class="footer-item"><span class="footer-label">PNR:</span> <span class="footer-value">{{ pax.pnr }}</span></span>{% endif %}
        {% if pax.booking_amt %}<span class="pax-amount">{{ booking.currency }} {{ pax.booking_amt }}</span>{% endif %}
      </div>
      {% endfor %}

      {% if booking.cancel_strip %}
      <div class="cancel-strip">{{ booking.cancel_strip }}</div>
      {% endif %}

      <div class="card-footer">
        <div class="footer-item">
          <span class="footer-label">Travel:</span>
          <span class="footer-value">{{ booking.travel_date }}</span>
        </div>
        <div class="footer-item">
          <span class="footer-label">Booked:</span>
          <span class="footer-value">{{ booking.booking_date }}</span>
        </div>
        <div class="footer-item">
          <span class="footer-label">Travellers:</span>
          <span class="footer-value">{{ booking.travellers }}</span>
        </div>
      </div>
    </div>
    {% endfor %}

    {% for tab in tabs %}
    {% if tab.count > 3 %}
    <button class="show-more-btn" data-for-status="{{ tab.key }}" data-total="{{ tab.count }}" {% if not tab.active %}style="display:none"{% endif %} onclick="var p=this.closest('.flight-bookings');p.querySelectorAll('.bkng-card[data-status=\''+this.dataset.forStatus+'\']').forEach(function(c){c.style.display=''});this.style.display='none'">
      Show {{ tab.count - 3 }} More
    </button>
    {% endif %}
    {% endfor %}

    <div class="bkng-empty" style="display:none">No flight bookings found for this category.</div>
  </div>
</div>

"""


# =====================================================================
# NORMALIZER
# =====================================================================
STATUS_KEYS = ["Upcoming", "Cancelled", "Completed", "Locked", "Rejected"]

STATUS_LABELS = {
    "Upcoming": "Upcoming",
    "Cancelled": "Cancelled",
    "Completed": "Completed",
    "Locked": "Locked",
    "Rejected": "Rejected",
}

STATUS_CSS = {
    "Upcoming": "upcoming",
    "Cancelled": "cancelled",
    "Completed": "completed",
    "Locked": "locked",
    "Rejected": "rejected",
}


def _get_pax_status_class(status: str) -> str:
    if not status:
        return ""
    s = status.lower()
    if "confirmed" in s:
        return "confirmed"
    if "cancel" in s:
        return "cancel-requested"
    return ""


def _normalize_flight_booking(booking: Dict[str, Any], status_key: str, active_status: str) -> Dict[str, Any]:
    segments = []
    for seg in booking.get("FlightDetailUI") or []:
        stops = seg.get("FlightStops", "0")
        stops_text = "non-Stop" if stops == "0" else f"{stops} Stop{'s' if int(stops or 0) > 1 else ''}"

        segments.append({
            "airline": seg.get("FullAirLineName") or seg.get("AirLineName") or "",
            "airline_code": seg.get("AirLineName") or "",
            "flight_number": (seg.get("FlightNumber") or "").strip(),
            "departure_city": seg.get("DepartureCity") or "",
            "arrival_city": seg.get("ArrivalCity") or "",
            "departure_code": seg.get("DepartureCityCode") or "",
            "arrival_code": seg.get("ArrivalCityCode") or "",
            "departure_time": seg.get("DepartureTime") or "",
            "arrival_time": seg.get("ArrivalTime") or "",
            "duration": seg.get("FlightDuration") or "",
            "stops": stops,
            "stops_text": stops_text,
            "class_type": seg.get("ClassType") or "",
            "brand_fare": seg.get("BrandFareName") or "",
            "source_terminal": seg.get("SourceTerminal") or "",
            "dest_terminal": seg.get("DestinationalTerminal") or "",
            "baggage": seg.get("BaggageWeight") or "",
            "cabin_baggage": seg.get("CabinBaggageWeight") or "",
        })

    passengers = []
    flt_details = booking.get("fltDetails") or {}
    for pax in flt_details.get("passengerDetails") or []:
        name_parts = [pax.get("title") or "", pax.get("firstName") or "", pax.get("lastName") or ""]
        name = " ".join(p for p in name_parts if p).strip()
        passengers.append({
            "name": name,
            "status": pax.get("status") or "",
            "status_class": _get_pax_status_class(pax.get("status") or ""),
            "pnr": pax.get("airLinePnr") or pax.get("GDSPnr") or "",
            "booking_amt": pax.get("bookingAmt"),
        })

    trip_type_raw = booking.get("TripType") or ""
    trip_type_map = {"OneWay": "One Way", "RoundTrip": "Round Trip", "MultiCity": "Multi City"}
    trip_type = trip_type_map.get(trip_type_raw, trip_type_raw)

    return {
        "status_key": status_key,
        "status": booking.get("Status") or booking.get("TripStatus") or status_key,
        "status_class": STATUS_CSS.get(status_key, "upcoming"),
        "visible": status_key == active_status,
        "booking_ref": booking.get("BookingRefNo") or "",
        "trip_details": booking.get("TripDetails") or "",
        "travel_date": booking.get("TravelDate") or "",
        "booking_date": booking.get("BookingDate") or "",
        "trip_type": trip_type,
        "travellers": booking.get("Travellers") or "",
        "currency": booking.get("Currency") or "INR",
        "cancel_strip": booking.get("CancelListStrip") or "",
        "segments": segments,
        "passengers": passengers,
    }


# =====================================================================
# RENDER FUNCTION
# =====================================================================
def render_flight_bookings(raw_data: Dict[str, Any]) -> str:
    """
    Renders flight bookings HTML from raw API response.

    Args:
        raw_data: The FlightDetails portion of the booking API response

    Returns:
        HTML string with rendered flight booking cards
    """
    if not raw_data or not isinstance(raw_data, dict):
        return '<div class="flight-bookings"><div class="bkng-empty">No flight bookings data available.</div></div>'

    # Determine active tab (first non-empty status, defaulting to Upcoming)
    active_status = "Upcoming"
    for key in STATUS_KEYS:
        items = raw_data.get(key)
        if items:
            active_status = key
            break

    # Build tabs
    tabs = []
    for key in STATUS_KEYS:
        items = raw_data.get(key) or []
        count = len(items)
        if count > 0:
            tabs.append({
                "key": key,
                "label": STATUS_LABELS.get(key, key),
                "count": count,
                "active": key == active_status,
            })

    if not tabs:
        return '<div class="flight-bookings"><div class="bkng-empty">No flight bookings found.</div></div>'

    # Build bookings list with per-status index
    bookings = []
    status_counters = {}
    for key in STATUS_KEYS:
        for booking in raw_data.get(key) or []:
            normalized = _normalize_flight_booking(booking, key, active_status)
            idx = status_counters.get(key, 0)
            normalized["status_index"] = idx
            status_counters[key] = idx + 1
            bookings.append(normalized)

    # Build title/subtitle
    total = sum(t["count"] for t in tabs)
    title = "Your Flight Bookings"
    subtitle = f"{total} booking{'s' if total != 1 else ''} found"

    import uuid
    instance_id = str(uuid.uuid4())[:8]

    template = _jinja_env.from_string(FLIGHT_BOOKINGS_TEMPLATE)
    return template.render(
        title=title,
        subtitle=subtitle,
        tabs=tabs,
        bookings=bookings,
        instance_id=instance_id,
    )
