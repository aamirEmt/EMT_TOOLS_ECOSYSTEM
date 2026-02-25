"""Bus Bookings Renderer - HTML renderer for bus booking data."""
from typing import Dict, Any, List
from jinja2 import Environment, BaseLoader, select_autoescape

_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)

# =====================================================================
# BUS BOOKINGS TEMPLATE
# =====================================================================
BUS_BOOKINGS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

.bus-bookings {
  font-family: poppins, sans-serif;
  color: #202020;
  background: rgba(255, 255, 255, 0.92);
  max-width: 750px;
  margin: 0 auto;
  padding: 20px 0 30px;
}

.bus-bookings * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
}

.bus-bookings .bkng-header {
  margin-bottom: 16px;
}

.bus-bookings .bkng-title {
  font-size: 18px;
  font-weight: 600;
  color: #202020;
}

.bus-bookings .bkng-subtitle {
  font-size: 12px;
  color: #646d74;
  margin-top: 4px;
}

.bus-bookings .bkng-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
  margin-bottom: 16px;
  scrollbar-width: thin;
  scrollbar-color: #ccc transparent;
}

.bus-bookings .bkng-tabs::-webkit-scrollbar { height: 4px; }
.bus-bookings .bkng-tabs::-webkit-scrollbar-thumb { background: #ccc; border-radius: 4px; }

.bus-bookings .bkng-tab {
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

.bus-bookings .bkng-tab:hover {
  border-color: #ef6614;
  color: #ef6614;
}

.bus-bookings .bkng-tab.active {
  background: #ef6614;
  color: #fff;
  border-color: #ef6614;
}

.bus-bookings .tab-count {
  font-weight: 600;
  font-size: 12px;
}

.bus-bookings .bkng-cards {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.bus-bookings .bkng-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fff;
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}

.bus-bookings .bkng-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.bus-bookings .card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #f0f0f0;
}

.bus-bookings .card-top-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bus-bookings .status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.bus-bookings .status-badge.upcoming { background: #e3f2fd; color: #1565c0; }
.bus-bookings .status-badge.cancelled { background: #ffebee; color: #c62828; }
.bus-bookings .status-badge.completed { background: #e8f5e9; color: #2e7d32; }
.bus-bookings .status-badge.refunded { background: #fff3e0; color: #e65100; }
.bus-bookings .status-badge.cancel-request { background: #fff3e0; color: #e65100; }

.bus-bookings .booking-ref {
  font-size: 12px;
  font-weight: 600;
  color: #ef6614;
  font-family: inter, sans-serif;
}

.bus-bookings .card-body {
  padding: 16px;
}

.bus-bookings .operator-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.bus-bookings .operator-name {
  font-size: 15px;
  font-weight: 600;
  color: #202020;
}

.bus-bookings .bus-type-badge {
  font-size: 10px;
  font-weight: 500;
  padding: 2px 8px;
  background: #F2F9FF;
  border: 1px solid #B6D5F0;
  border-radius: 3px;
  color: #313131;
}

.bus-bookings .route-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 8px;
}

.bus-bookings .route-block {
  text-align: center;
  flex: 1;
}

.bus-bookings .route-time {
  font-size: 18px;
  font-weight: 700;
  color: #202020;
  font-family: inter, sans-serif;
}

.bus-bookings .route-city {
  font-size: 11px;
  color: #868686;
  margin-top: 2px;
}

.bus-bookings .duration-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 8px;
  min-width: 80px;
}

.bus-bookings .duration-text {
  font-size: 11px;
  color: #646d74;
  font-weight: 500;
  margin-bottom: 4px;
}

.bus-bookings .duration-line {
  width: 100%;
  height: 1px;
  background: #ccc;
  position: relative;
}

.bus-bookings .duration-line::before,
.bus-bookings .duration-line::after {
  content: '';
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ccc;
}

.bus-bookings .duration-line::before { left: 0; }
.bus-bookings .duration-line::after { right: 0; }

.bus-bookings .boarding-info {
  font-size: 11px;
  color: #646d74;
  padding: 4px 0;
}

.bus-bookings .boarding-label {
  font-weight: 500;
  color: #868686;
}

.bus-bookings .card-footer {
  padding: 10px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  flex-wrap: wrap;
  gap: 6px 16px;
  font-size: 11px;
  color: #646d74;
}

.bus-bookings .footer-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.bus-bookings .footer-label { font-weight: 500; color: #868686; }
.bus-bookings .footer-value { color: #202020; font-weight: 500; }

.bus-bookings .refund-row {
  padding: 6px 16px;
  background: #f1f8e9;
  font-size: 11px;
  color: #33691e;
  font-weight: 500;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bus-bookings .bkng-empty {
  text-align: center;
  color: #646d74;
  padding: 40px 20px;
  font-size: 14px;
}

.bus-bookings .show-more-btn {
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

.bus-bookings .show-more-btn:hover {
  background: #fff5ee;
  border-color: #ef6614;
}
</style>

<div class="bus-bookings" data-instance-id="bus-bookings-{{ instance_id }}">
  <div class="bkng-header">
    <div class="bkng-title">{{ title }}</div>
    <div class="bkng-subtitle">{{ subtitle }}</div>
  </div>

  {% if tabs %}
  <div class="bkng-tabs">
    {% for tab in tabs %}
    <button class="bkng-tab {% if tab.active %}active{% endif %}" data-status="{{ tab.key }}" onclick="var p=this.closest('.bus-bookings');p.querySelectorAll('.bkng-tab').forEach(function(t){t.classList.remove('active')});this.classList.add('active');var s=this.dataset.status,v=0,idx=0;p.querySelectorAll('.bkng-card').forEach(function(c){var match=c.dataset.status===s;if(match){c.style.display=idx<3?'':'none';if(idx<3)v++;idx++}else{c.style.display='none'}});p.querySelectorAll('.show-more-btn').forEach(function(b){if(b.dataset.forStatus===s){var t=parseInt(b.dataset.total);b.style.display=t>3?'':'none';b.dataset.expanded='false';b.textContent='Show '+(t-3)+' More'}else{b.style.display='none'}});var e=p.querySelector('.bkng-empty');if(e)e.style.display=v?'none':''">
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
        </div>
        <span class="booking-ref">{{ booking.booking_ref }}</span>
      </div>

      <div class="card-body">
        <div class="operator-row">
          <span class="operator-name">{{ booking.operator }}</span>
          {% if booking.bus_type %}
          <span class="bus-type-badge">{{ booking.bus_type }}</span>
          {% endif %}
        </div>

        <div class="route-row">
          <div class="route-block">
            <div class="route-time">{{ booking.departure_time }}</div>
            <div class="route-city">{{ booking.source }}</div>
          </div>
          <div class="duration-block">
            <div class="duration-text">{{ booking.duration }}</div>
            <div class="duration-line"></div>
          </div>
          <div class="route-block">
            <div class="route-time">{{ booking.arrival_time }}</div>
            <div class="route-city">{{ booking.destination }}</div>
          </div>
        </div>

        {% if booking.boarding_point %}
        <div class="boarding-info">
          <span class="boarding-label">Boarding:</span> {{ booking.boarding_point }}
        </div>
        {% endif %}
      </div>

      {% if booking.refund_amt %}
      <div class="refund-row"><span>Refund: {{ booking.refund_amt }}</span><span>{{ booking.refund_date }}</span></div>
      {% endif %}

      <div class="card-footer">
        <div class="footer-item">
          <span class="footer-label">Journey:</span>
          <span class="footer-value">{{ booking.journey_date }}</span>
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
    <button class="show-more-btn" data-for-status="{{ tab.key }}" data-total="{{ tab.count }}" data-expanded="false" {% if not tab.active %}style="display:none"{% endif %} onclick="var p=this.closest('.bus-bookings');var s=this.dataset.forStatus;var t=parseInt(this.dataset.total);if(this.dataset.expanded==='true'){var idx=0;p.querySelectorAll('.bkng-card').forEach(function(c){if(c.dataset.status===s){if(idx>=3)c.style.display='none';idx++}});this.dataset.expanded='false';this.textContent='Show '+(t-3)+' More'}else{p.querySelectorAll('.bkng-card').forEach(function(c){if(c.dataset.status===s)c.style.display=''});this.dataset.expanded='true';this.textContent='Show Less'}">
      Show {{ tab.count - 3 }} More
    </button>
    {% endif %}
    {% endfor %}

    <div class="bkng-empty" style="display:none">No bus bookings found for this category.</div>
  </div>
</div>

"""


# =====================================================================
# NORMALIZER
# =====================================================================
STATUS_KEYS = ["UpComing", "Cancelled", "Completed", "Refunded", "CancelRequest"]

STATUS_LABELS = {
    "UpComing": "Upcoming",
    "Cancelled": "Cancelled",
    "Completed": "Completed",
    "Refunded": "Refunded",
    "CancelRequest": "Cancel Requested",
}

STATUS_CSS = {
    "UpComing": "upcoming",
    "Cancelled": "cancelled",
    "Completed": "completed",
    "Refunded": "refunded",
    "CancelRequest": "cancel-request",
}


def _normalize_bus_booking(booking: Dict[str, Any], status_key: str, active_status: str) -> Dict[str, Any]:
    details = booking.get("Details") or {}

    departure_time = details.get("DepartureTime1") or details.get("DepartureTime") or details.get("BdTime") or ""
    arrival_time = details.get("ArrivalTime") or details.get("Droptime") or ""
    departure_date = details.get("DepartureDate") or ""
    source = details.get("Source") or ""
    destination = details.get("Destination") or ""
    operator = details.get("TravelsOperator") or ""
    bus_type = details.get("BusType") or ""
    duration = details.get("BusDuration") or ""
    boarding_point = details.get("BPLocation") or ""

    refund_amt = booking.get("RefundAmt")
    refund_date = booking.get("RefunUpdatedON") or booking.get("RefundTrandate") or ""
    refund_display = ""
    if refund_amt and refund_amt > 0:
        refund_display = f"INR {refund_amt}"

    return {
        "status_key": status_key,
        "status": booking.get("Status") or STATUS_LABELS.get(status_key, status_key),
        "status_class": STATUS_CSS.get(status_key, "upcoming"),
        "visible": status_key == active_status,
        "booking_ref": booking.get("BookingRefNo") or "",
        "trip_details": booking.get("TripDetails") or "",
        "journey_date": departure_date or booking.get("JourneyDate") or booking.get("DateOfJourney") or "",
        "booking_date": booking.get("BookingDate") or booking.get("BookedOn") or "",
        "travellers": booking.get("Travellers") or "",
        "operator": operator,
        "bus_type": bus_type.strip(),
        "source": source,
        "destination": destination,
        "departure_time": departure_time,
        "arrival_time": arrival_time,
        "duration": duration,
        "boarding_point": boarding_point.strip(),
        "refund_amt": refund_display,
        "refund_date": refund_date,
    }


# =====================================================================
# RENDER FUNCTION
# =====================================================================
def render_bus_bookings(raw_data: Dict[str, Any]) -> str:
    """
    Renders bus bookings HTML from raw API response.

    Args:
        raw_data: The BusDetails portion of the booking API response

    Returns:
        HTML string with rendered bus booking cards
    """
    if not raw_data or not isinstance(raw_data, dict):
        return '<div class="bus-bookings"><div class="bkng-empty">No bus bookings data available.</div></div>'

    # Determine active tab (first non-empty, defaulting to UpComing)
    active_status = None
    for key in STATUS_KEYS:
        items = raw_data.get(key)
        if items:
            if active_status is None:
                active_status = key
    if active_status is None:
        active_status = "UpComing"

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
        return '<div class="bus-bookings"><div class="bkng-empty">No bus bookings found.</div></div>'

    # Build bookings list with per-status index
    bookings = []
    status_counters = {}
    for key in STATUS_KEYS:
        for booking in raw_data.get(key) or []:
            normalized = _normalize_bus_booking(booking, key, active_status)
            idx = status_counters.get(key, 0)
            normalized["status_index"] = idx
            status_counters[key] = idx + 1
            bookings.append(normalized)

    total = sum(t["count"] for t in tabs)
    title = "Your Bus Bookings"
    subtitle = f"{total} booking{'s' if total != 1 else ''} found"

    import uuid
    instance_id = str(uuid.uuid4())[:8]

    template = _jinja_env.from_string(BUS_BOOKINGS_TEMPLATE)
    return template.render(
        title=title,
        subtitle=subtitle,
        tabs=tabs,
        bookings=bookings,
        instance_id=instance_id,
    )
