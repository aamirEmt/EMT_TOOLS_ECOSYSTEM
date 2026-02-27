"""Hotel Bookings Renderer - HTML renderer for hotel booking data."""
from typing import Dict, Any, List
from jinja2 import Environment, BaseLoader, select_autoescape

_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)

# =====================================================================
# HOTEL BOOKINGS TEMPLATE
# =====================================================================
HOTEL_BOOKINGS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

.hotel-bookings {
  font-family: poppins, sans-serif;
  color: #202020;
  background: rgba(255, 255, 255, 0.92);
  max-width: 750px;
  margin: 0 auto;
  padding: 20px 0 30px;
}

.hotel-bookings * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
}

.hotel-bookings .bkng-header {
  margin-bottom: 16px;
}

.hotel-bookings .bkng-title {
  font-size: 18px;
  font-weight: 600;
  color: #202020;
}

.hotel-bookings .bkng-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
  margin-bottom: 16px;
  scrollbar-width: thin;
  scrollbar-color: #ccc transparent;
}

.hotel-bookings .bkng-tabs::-webkit-scrollbar { height: 4px; }
.hotel-bookings .bkng-tabs::-webkit-scrollbar-thumb { background: #ccc; border-radius: 4px; }

.hotel-bookings .bkng-tab {
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

.hotel-bookings .bkng-tab:hover {
  border-color: #ef6614;
  color: #ef6614;
}

.hotel-bookings .bkng-tab.active {
  background: #ef6614;
  color: #fff;
  border-color: #ef6614;
}

.hotel-bookings .tab-count {
  font-weight: 600;
  font-size: 12px;
}

.hotel-bookings .bkng-cards {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.hotel-bookings .bkng-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fff;
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}

.hotel-bookings .bkng-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.hotel-bookings .card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #f0f0f0;
}

.hotel-bookings .card-top-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.hotel-bookings .status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.hotel-bookings .status-badge.upcoming { background: #e3f2fd; color: #1565c0; }
.hotel-bookings .status-badge.cancelled { background: #ffebee; color: #c62828; }
.hotel-bookings .status-badge.completed { background: #e8f5e9; color: #2e7d32; }
.hotel-bookings .status-badge.pending { background: #fff8e1; color: #f57f17; }
.hotel-bookings .status-badge.refunded { background: #fff3e0; color: #e65100; }

.hotel-bookings .booking-ref {
  font-size: 12px;
  font-weight: 600;
  color: #ef6614;
  font-family: inter, sans-serif;
}

.hotel-bookings .card-body {
  padding: 16px;
}

.hotel-bookings .hotel-name {
  font-size: 16px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 4px;
}

.hotel-bookings .hotel-address {
  font-size: 11px;
  color: #868686;
  margin-bottom: 12px;
}

.hotel-bookings .stay-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 8px;
}

.hotel-bookings .stay-block {
  text-align: center;
  flex: 1;
}

.hotel-bookings .stay-label {
  font-size: 10px;
  color: #868686;
  text-transform: uppercase;
  font-weight: 500;
  margin-bottom: 4px;
}

.hotel-bookings .stay-date {
  font-size: 14px;
  font-weight: 700;
  color: #202020;
  font-family: inter, sans-serif;
}

.hotel-bookings .stay-separator {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 8px;
  min-width: 80px;
}

.hotel-bookings .nights-text {
  font-size: 11px;
  color: #646d74;
  font-weight: 500;
  margin-bottom: 4px;
}

.hotel-bookings .stay-line {
  width: 100%;
  height: 1px;
  background: #ccc;
  position: relative;
}

.hotel-bookings .stay-line::before,
.hotel-bookings .stay-line::after {
  content: '';
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ccc;
}

.hotel-bookings .stay-line::before { left: 0; }
.hotel-bookings .stay-line::after { right: 0; }

.hotel-bookings .room-info {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #646d74;
  padding: 8px 0;
}

.hotel-bookings .room-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.hotel-bookings .room-label { font-weight: 500; color: #868686; }
.hotel-bookings .room-value { color: #202020; font-weight: 600; }

.hotel-bookings .card-footer {
  padding: 10px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  flex-wrap: wrap;
  gap: 6px 16px;
  font-size: 11px;
  color: #646d74;
}

.hotel-bookings .footer-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.hotel-bookings .footer-item.location-item {
  flex-basis: 100%;
  display: inline;
}

.hotel-bookings .footer-label { font-weight: 500; color: #868686; }
.hotel-bookings .footer-value { color: #202020; font-weight: 500; }

.hotel-bookings .bkng-empty {
  text-align: center;
  color: #646d74;
  padding: 40px 20px;
  font-size: 14px;
}

.hotel-bookings .show-more-btn {
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

.hotel-bookings .show-more-btn:hover {
  background: #fff5ee;
  border-color: #ef6614;
}
</style>

<div class="hotel-bookings" data-instance-id="hotel-bookings-{{ instance_id }}">
  <div class="bkng-header">
    <div class="bkng-title">{{ title }}</div>
  </div>

  {% if tabs %}
  <div class="bkng-tabs">
    {% for tab in tabs %}
    <button class="bkng-tab {% if tab.active %}active{% endif %}" data-status="{{ tab.key }}" onclick="var p=this.closest('.hotel-bookings');p.querySelectorAll('.bkng-tab').forEach(function(t){t.classList.remove('active')});this.classList.add('active');var s=this.dataset.status,v=0,idx=0;p.querySelectorAll('.bkng-card').forEach(function(c){var match=c.dataset.status===s;if(match){c.style.display=idx<3?'':'none';if(idx<3)v++;idx++}else{c.style.display='none'}});p.querySelectorAll('.show-more-btn').forEach(function(b){if(b.dataset.forStatus===s){var t=parseInt(b.dataset.total);b.style.display=t>3?'':'none';b.dataset.expanded='false';b.textContent='Show '+(t-3)+' More'}else{b.style.display='none'}});var e=p.querySelector('.bkng-empty');if(e)e.style.display=v?'none':''">
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
        <div class="hotel-name">{{ booking.hotel_name }}</div>
        {% if booking.address %}
        <div class="hotel-address">{{ booking.address }}</div>
        {% endif %}

        <div class="stay-row">
          <div class="stay-block">
            <div class="stay-label">Check-in</div>
            <div class="stay-date">{{ booking.checkin }}</div>
          </div>
          <div class="stay-separator">
            {% if booking.nights %}
            <div class="nights-text">{{ booking.nights }} Night{{ 's' if booking.nights != '1' else '' }}</div>
            {% endif %}
            <div class="stay-line"></div>
          </div>
          <div class="stay-block">
            <div class="stay-label">Check-out</div>
            <div class="stay-date">{{ booking.checkout }}</div>
          </div>
        </div>

        <div class="room-info">
          {% if booking.rooms %}
          <div class="room-item">
            <span class="room-label">Rooms:</span>
            <span class="room-value">{{ booking.rooms }}</span>
          </div>
          {% endif %}
          {% if booking.guests %}
          <div class="room-item">
            <span class="room-label">Guests:</span>
            <span class="room-value">{{ booking.guests }}</span>
          </div>
          {% endif %}
          {% if booking.room_type %}
          <div class="room-item">
            <span class="room-label">Type:</span>
            <span class="room-value">{{ booking.room_type }}</span>
          </div>
          {% endif %}
        </div>
      </div>

      <div class="card-footer">
        {% if booking.trip_details %}
        <div class="footer-item location-item">
          <span class="footer-label">Location:</span> <span class="footer-value">{{ booking.trip_details }}</span>
        </div>
        {% endif %}
        <div class="footer-item">
          <span class="footer-label">Booked:</span>
          <span class="footer-value">{{ booking.booking_date }}</span>
        </div>
        {% if booking.travellers %}
        <div class="footer-item">
          <span class="footer-label">Travellers:</span>
          <span class="footer-value">{{ booking.travellers }}</span>
        </div>
        {% endif %}
      </div>
    </div>
    {% endfor %}

    {% for tab in tabs %}
    {% if tab.count > 3 %}
    <button class="show-more-btn" data-for-status="{{ tab.key }}" data-total="{{ tab.count }}" data-expanded="false" {% if not tab.active %}style="display:none"{% endif %} onclick="var p=this.closest('.hotel-bookings');var s=this.dataset.forStatus;var t=parseInt(this.dataset.total);if(this.dataset.expanded==='true'){var idx=0;p.querySelectorAll('.bkng-card').forEach(function(c){if(c.dataset.status===s){if(idx>=3)c.style.display='none';idx++}});this.dataset.expanded='false';this.textContent='Show '+(t-3)+' More'}else{p.querySelectorAll('.bkng-card').forEach(function(c){if(c.dataset.status===s)c.style.display=''});this.dataset.expanded='true';this.textContent='Show Less'}">
      Show {{ tab.count - 3 }} More
    </button>
    {% endif %}
    {% endfor %}

    <div class="bkng-empty" style="display:none">No hotel bookings found for this category.</div>
  </div>
</div>

"""


# =====================================================================
# NORMALIZER
# =====================================================================
STATUS_KEYS = ["Upcoming", "Completed", "Cancelled", "Pending", "Refunded"]

STATUS_LABELS = {
    "Upcoming": "Upcoming",
    "Completed": "Completed",
    "Cancelled": "Cancelled",
    "Pending": "Pending",
    "Refunded": "Refunded",
}

STATUS_CSS = {
    "Upcoming": "upcoming",
    "Completed": "completed",
    "Cancelled": "cancelled",
    "Pending": "pending",
    "Refunded": "refunded",
}


def _normalize_hotel_booking(booking: Dict[str, Any], status_key: str, active_status: str) -> Dict[str, Any]:
    return {
        "status_key": status_key,
        "status": booking.get("TripStatus") or booking.get("Status") or STATUS_LABELS.get(status_key, status_key),
        "status_class": STATUS_CSS.get(status_key, "upcoming"),
        "visible": status_key == active_status,
        "booking_ref": booking.get("BookingRefNo") or "",
        "hotel_name": booking.get("HotelName") or "",
        "address": booking.get("Address_Description") or "",
        "checkin": booking.get("CheckInDate") or booking.get("CheckIn") or "",
        "checkout": booking.get("CheckOutDate") or booking.get("checkOut") or "",
        "rooms": str(booking.get("NoOfRooms") or booking.get("NumberOfRoomsBooked") or ""),
        "guests": str(booking.get("NoOfGuests") or ""),
        "nights": str(booking.get("Night") or ""),
        "room_type": booking.get("RoomType") or "",
        "trip_details": booking.get("TripDetails") or "",
        "booking_date": booking.get("BookingDate") or "",
        "travellers": str(booking.get("Travellers") or ""),
    }


# =====================================================================
# RENDER FUNCTION
# =====================================================================
def render_hotel_bookings(raw_data: Dict[str, Any]) -> str:
    """
    Renders hotel bookings HTML from raw API response.

    Args:
        raw_data: The HotelDetails portion of the booking API response

    Returns:
        HTML string with rendered hotel booking cards
    """
    if not raw_data or not isinstance(raw_data, dict):
        return '<div class="hotel-bookings"><div class="bkng-empty">No hotel bookings data available.</div></div>'

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

    if not tabs:
        return '<div class="hotel-bookings"><div class="bkng-empty">No hotel bookings found.</div></div>'

    # Build bookings list with per-status index
    bookings = []
    status_counters = {}
    for key in STATUS_KEYS:
        for booking in raw_data.get(key) or []:
            normalized = _normalize_hotel_booking(booking, key, active_status)
            idx = status_counters.get(key, 0)
            normalized["status_index"] = idx
            status_counters[key] = idx + 1
            bookings.append(normalized)

    total = sum(t["count"] for t in tabs)
    title = "Your Hotel Bookings"
    subtitle = f"{total} booking{'s' if total != 1 else ''} found"

    import uuid
    instance_id = str(uuid.uuid4())[:8]

    template = _jinja_env.from_string(HOTEL_BOOKINGS_TEMPLATE)
    return template.render(
        title=title,
        subtitle=subtitle,
        tabs=tabs,
        bookings=bookings,
        instance_id=instance_id,
    )
