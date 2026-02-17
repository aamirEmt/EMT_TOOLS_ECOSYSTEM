"""Train Bookings Renderer - HTML renderer for train booking data."""
from typing import Dict, Any, List
from jinja2 import Environment, BaseLoader, select_autoescape

_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)

# =====================================================================
# TRAIN BOOKINGS TEMPLATE
# =====================================================================
TRAIN_BOOKINGS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

.train-bookings {
  font-family: poppins, sans-serif;
  color: #202020;
  background: rgba(255, 255, 255, 0.92);
  max-width: 750px;
  margin: 0 auto;
  padding: 20px 0 30px;
}

.train-bookings * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
}

.train-bookings .bkng-header {
  margin-bottom: 16px;
}

.train-bookings .bkng-title {
  font-size: 18px;
  font-weight: 600;
  color: #202020;
}

.train-bookings .bkng-subtitle {
  font-size: 12px;
  color: #646d74;
  margin-top: 4px;
}

.train-bookings .bkng-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
  margin-bottom: 16px;
  scrollbar-width: thin;
  scrollbar-color: #ccc transparent;
}

.train-bookings .bkng-tabs::-webkit-scrollbar { height: 4px; }
.train-bookings .bkng-tabs::-webkit-scrollbar-thumb { background: #ccc; border-radius: 4px; }

.train-bookings .bkng-tab {
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

.train-bookings .bkng-tab:hover {
  border-color: #ef6614;
  color: #ef6614;
}

.train-bookings .bkng-tab.active {
  background: #ef6614;
  color: #fff;
  border-color: #ef6614;
}

.train-bookings .tab-count {
  font-weight: 600;
  font-size: 12px;
}

.train-bookings .bkng-cards {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.train-bookings .bkng-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fff;
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}

.train-bookings .bkng-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.train-bookings .card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #f0f0f0;
}

.train-bookings .card-top-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.train-bookings .status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.train-bookings .status-badge.upcoming { background: #e3f2fd; color: #1565c0; }
.train-bookings .status-badge.cancelled { background: #ffebee; color: #c62828; }
.train-bookings .status-badge.completed { background: #e8f5e9; color: #2e7d32; }
.train-bookings .status-badge.refunded { background: #fff3e0; color: #e65100; }
.train-bookings .status-badge.pending { background: #fff8e1; color: #f57f17; }
.train-bookings .status-badge.cancel-requested { background: #fff3e0; color: #e65100; }
.train-bookings .status-badge.rejected { background: #fce4ec; color: #c62828; }
.train-bookings .status-badge.partially-refunded { background: #fce4ec; color: #ad1457; }

.train-bookings .booking-ref {
  font-size: 12px;
  font-weight: 600;
  color: #ef6614;
  font-family: inter, sans-serif;
}

.train-bookings .card-body {
  padding: 16px;
}

.train-bookings .train-info-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.train-bookings .train-name {
  font-size: 15px;
  font-weight: 600;
  color: #202020;
}

.train-bookings .train-number {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 6px;
  background: #F2F9FF;
  border: 1px solid #B6D5F0;
  border-radius: 3px;
  color: #313131;
}

.train-bookings .class-quota {
  font-size: 11px;
  color: #868686;
  margin-left: auto;
}

.train-bookings .timing-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 8px;
}

.train-bookings .time-block {
  text-align: center;
  flex: 1;
}

.train-bookings .time-value {
  font-size: 18px;
  font-weight: 700;
  color: #202020;
  font-family: inter, sans-serif;
}

.train-bookings .station-code {
  font-size: 10px;
  color: #868686;
  text-transform: uppercase;
  margin-top: 2px;
}

.train-bookings .station-name {
  font-size: 10px;
  color: #868686;
  margin-top: 1px;
}

.train-bookings .duration-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 8px;
  min-width: 80px;
}

.train-bookings .duration-text {
  font-size: 11px;
  color: #646d74;
  font-weight: 500;
  margin-bottom: 4px;
}

.train-bookings .duration-line {
  width: 100%;
  height: 1px;
  background: #ccc;
  position: relative;
}

.train-bookings .duration-line::before,
.train-bookings .duration-line::after {
  content: '';
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ccc;
}

.train-bookings .duration-line::before { left: 0; }
.train-bookings .duration-line::after { right: 0; }

.train-bookings .boarding-info {
  font-size: 11px;
  color: #646d74;
  padding: 4px 0;
}

.train-bookings .boarding-label {
  font-weight: 500;
  color: #868686;
}

.train-bookings .refund-row {
  padding: 6px 16px;
  background: #f1f8e9;
  font-size: 11px;
  color: #33691e;
  font-weight: 500;
  border-top: 1px solid #f0f0f0;
}

.train-bookings .card-footer {
  padding: 10px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  flex-wrap: wrap;
  gap: 6px 16px;
  font-size: 11px;
  color: #646d74;
}

.train-bookings .footer-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.train-bookings .footer-label { font-weight: 500; color: #868686; }
.train-bookings .footer-value { color: #202020; font-weight: 500; }

.train-bookings .bkng-empty {
  text-align: center;
  color: #646d74;
  padding: 40px 20px;
  font-size: 14px;
}
</style>

<div class="train-bookings" data-instance-id="train-bookings-{{ instance_id }}">
  <div class="bkng-header">
    <div class="bkng-title">{{ title }}</div>
    <div class="bkng-subtitle">{{ subtitle }}</div>
  </div>

  {% if tabs %}
  <div class="bkng-tabs">
    {% for tab in tabs %}
    <button class="bkng-tab {% if tab.active %}active{% endif %}" data-status="{{ tab.key }}" onclick="var p=this.closest('.train-bookings');p.querySelectorAll('.bkng-tab').forEach(function(t){t.classList.remove('active')});this.classList.add('active');var s=this.dataset.status,v=0;p.querySelectorAll('.bkng-card').forEach(function(c){var show=s==='all'||c.dataset.status===s;c.style.display=show?'':'none';if(show)v++});var e=p.querySelector('.bkng-empty');if(e)e.style.display=v?'none':''">
      {{ tab.label }} <span class="tab-count">({{ tab.count }})</span>
    </button>
    {% endfor %}
  </div>
  {% endif %}

  <div class="bkng-cards">
    {% for booking in bookings %}
    <div class="bkng-card" data-status="{{ booking.status_key }}" {% if not booking.visible %}style="display:none"{% endif %}>
      <div class="card-top">
        <div class="card-top-left">
          <span class="status-badge {{ booking.status_class }}">{{ booking.status }}</span>
        </div>
        <span class="booking-ref">{{ booking.booking_ref }}</span>
      </div>

      <div class="card-body">
        <div class="train-info-row">
          <span class="train-name">{{ booking.train_name }}</span>
          <span class="train-number">{{ booking.train_no }}</span>
          <span class="class-quota">{{ booking.travel_class }}{% if booking.quota %} | {{ booking.quota }}{% endif %}</span>
        </div>

        <div class="timing-row">
          <div class="time-block">
            <div class="time-value">{{ booking.departure_time }}</div>
            <div class="station-code">{{ booking.from_stn_code }}</div>
            <div class="station-name">{{ booking.from_stn }}</div>
          </div>
          <div class="duration-block">
            <div class="duration-text">{{ booking.duration }}</div>
            <div class="duration-line"></div>
          </div>
          <div class="time-block">
            <div class="time-value">{{ booking.arrival_time }}</div>
            <div class="station-code">{{ booking.to_stn_code }}</div>
            <div class="station-name">{{ booking.to_stn }}</div>
          </div>
        </div>

        {% if booking.boarding_station and booking.boarding_station != booking.from_stn_code %}
        <div class="boarding-info">
          <span class="boarding-label">Boarding:</span> {{ booking.boarding_station }} at {{ booking.boarding_time }}
        </div>
        {% endif %}
      </div>

      {% if booking.refund_amt %}
      <div class="refund-row">Refund: INR {{ booking.refund_amt }} | {{ booking.refund_date }}</div>
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

    <div class="bkng-empty" style="display:none">No train bookings found for this category.</div>
  </div>
</div>

"""


# =====================================================================
# NORMALIZER
# =====================================================================
STATUS_KEYS = ["Upcoming", "Completed", "Cancelled", "Refunded", "PartiallyRefunded", "Pending", "CancelRequested", "Rejected"]

STATUS_LABELS = {
    "Upcoming": "Upcoming",
    "Completed": "Completed",
    "Cancelled": "Cancelled",
    "Refunded": "Refunded",
    "PartiallyRefunded": "Partially Refunded",
    "Pending": "Pending",
    "CancelRequested": "Cancel Requested",
    "Rejected": "Rejected",
}

STATUS_CSS = {
    "Upcoming": "upcoming",
    "Completed": "completed",
    "Cancelled": "cancelled",
    "Refunded": "refunded",
    "PartiallyRefunded": "partially-refunded",
    "Pending": "pending",
    "CancelRequested": "cancel-requested",
    "Rejected": "rejected",
}


def _normalize_train_booking(booking: Dict[str, Any], status_key: str, active_status: str) -> Dict[str, Any]:
    trip_details = booking.get("TripDetails") or ""
    from_stn_code = ""
    to_stn_code = ""
    if "-" in trip_details:
        parts = trip_details.split("-", 1)
        from_stn_code = parts[0].strip()
        to_stn_code = parts[1].strip()

    refund_amt = booking.get("RefundAmt")
    refund_display = refund_amt if refund_amt and refund_amt > 0 else ""
    refund_date = booking.get("RefundDate") or ""

    return {
        "status_key": status_key,
        "status": booking.get("TripStatus") or STATUS_LABELS.get(status_key, status_key),
        "status_class": STATUS_CSS.get(status_key, "upcoming"),
        "visible": status_key == active_status,
        "booking_ref": booking.get("BookingRefNo") or "",
        "train_name": booking.get("TrainName") or "",
        "train_no": booking.get("TrainNo") or "",
        "from_stn": booking.get("FromStn") or "",
        "to_stn": booking.get("ToStn") or "",
        "from_stn_code": from_stn_code or booking.get("BoardingStation") or "",
        "to_stn_code": to_stn_code,
        "departure_time": booking.get("DepartureTime") or "",
        "arrival_time": booking.get("ArrivalTime") or "",
        "duration": booking.get("TrainDuration") or "",
        "travel_class": booking.get("Class") or "",
        "quota": booking.get("Quota") or "",
        "boarding_station": booking.get("BoardingStation") or "",
        "boarding_time": booking.get("BoardingTime") or "",
        "travel_date": booking.get("TravelDate") or "",
        "booking_date": booking.get("BookingDate") or "",
        "travellers": booking.get("Travellers") or "",
        "refund_amt": refund_display,
        "refund_date": refund_date,
    }


# =====================================================================
# RENDER FUNCTION
# =====================================================================
def render_train_bookings(raw_data: Dict[str, Any]) -> str:
    """
    Renders train bookings HTML from raw API response.

    Args:
        raw_data: The TrainDetails portion of the booking API response

    Returns:
        HTML string with rendered train booking cards
    """
    if not raw_data or not isinstance(raw_data, dict):
        return '<div class="train-bookings"><div class="bkng-empty">No train bookings data available.</div></div>'

    # Determine active tab (first non-empty, defaulting to Upcoming)
    active_status = None
    for key in STATUS_KEYS:
        items = raw_data.get(key)
        if items:
            if active_status is None:
                active_status = key
    if active_status is None:
        active_status = "Upcoming"

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

    # If no categorized data, try trainJourneyDetails (flat list)
    if not tabs:
        all_trains = raw_data.get("trainJourneyDetails") or []
        if all_trains:
            # Group by TripStatus
            grouped = {}
            for t in all_trains:
                status = t.get("TripStatus") or "Unknown"
                # Map TripStatus to our status keys
                mapped = _map_trip_status(status)
                if mapped not in grouped:
                    grouped[mapped] = []
                grouped[mapped].append(t)

            for key in STATUS_KEYS:
                if key in grouped:
                    raw_data[key] = grouped[key]
                    if active_status is None or active_status == "Upcoming":
                        active_status = key
                    tabs.append({
                        "key": key,
                        "label": STATUS_LABELS.get(key, key),
                        "count": len(grouped[key]),
                        "active": key == active_status,
                    })

            # Fix active flags
            if tabs:
                active_status = tabs[0]["key"]
                for tab in tabs:
                    tab["active"] = tab["key"] == active_status

    if not tabs:
        return '<div class="train-bookings"><div class="bkng-empty">No train bookings found.</div></div>'

    # Build bookings list
    bookings = []
    for key in STATUS_KEYS:
        for booking in raw_data.get(key) or []:
            bookings.append(_normalize_train_booking(booking, key, active_status))

    total = sum(t["count"] for t in tabs)
    title = "Your Train Bookings"
    subtitle = f"{total} booking{'s' if total != 1 else ''} found"

    import uuid
    instance_id = str(uuid.uuid4())[:8]

    template = _jinja_env.from_string(TRAIN_BOOKINGS_TEMPLATE)
    return template.render(
        title=title,
        subtitle=subtitle,
        tabs=tabs,
        bookings=bookings,
        instance_id=instance_id,
    )


def _map_trip_status(status: str) -> str:
    """Map TripStatus from API to our normalized status keys."""
    s = status.lower()
    if "upcoming" in s or "confirmed" in s:
        return "Upcoming"
    if "refunded" in s:
        return "Refunded"
    if "partially" in s:
        return "PartiallyRefunded"
    if "cancel requested" in s or "cancel request" in s:
        return "CancelRequested"
    if "cancelled" in s or "canceled" in s:
        return "Cancelled"
    if "completed" in s:
        return "Completed"
    if "pending" in s:
        return "Pending"
    if "rejected" in s:
        return "Rejected"
    return "Upcoming"
