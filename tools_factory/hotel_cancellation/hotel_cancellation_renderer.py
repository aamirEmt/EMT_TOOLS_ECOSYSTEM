"""Hotel Cancellation Booking Details Renderer (Display-Only)"""
from typing import Dict, Any
from jinja2 import Environment, BaseLoader, select_autoescape


def _truncate_text(text: str, max_length: int = 30) -> str:
    """Truncate text to max_length characters and add ellipsis if truncated"""
    if not text:
        return text
    text_str = str(text)
    if len(text_str) <= max_length:
        return text_str
    return text_str[:max_length] + "..."


_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)
_jinja_env.filters['truncate_text'] = _truncate_text


# =====================================================================
# 🏨 BOOKING DETAILS DISPLAY TEMPLATE (DISPLAY-ONLY, NO FORMS)
# =====================================================================
BOOKING_DETAILS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

.booking-details-carousel {
  font-family: poppins, sans-serif;
  color: #202020;
  background: rgba(255, 255, 255, 0.92);
  position: relative;
}

.booking-details-carousel * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
}

.booking-details-carousel main {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px 0 30px;
}

.booking-details-carousel .bkhd {
  margin-bottom: 16px;
}

.booking-details-carousel .bkttl {
  font-size: 18px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 4px;
}

.booking-details-carousel .bksub {
  font-size: 12px;
  color: #646d74;
  margin-top: 4px;
}

.booking-details-carousel .hotel-info {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 16px;
  border: 1px solid #e0e0e0;
}

.booking-details-carousel .hotel-name {
  font-size: 16px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 6px;
}

.booking-details-carousel .hotel-address {
  font-size: 12px;
  color: #646d74;
  margin-bottom: 8px;
}

.booking-details-carousel .hotel-dates {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #202020;
  margin-top: 8px;
}

.booking-details-carousel .date-item {
  display: flex;
  flex-direction: column;
}

.booking-details-carousel .date-label {
  font-size: 10px;
  color: #868686;
  text-transform: uppercase;
  margin-bottom: 2px;
}

.booking-details-carousel .date-value {
  font-weight: 600;
}

.booking-details-carousel .rooms-title {
  font-size: 14px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 12px;
}

.booking-details-carousel .slider-shell {
  position: relative;
}

.booking-details-carousel .rsltcvr {
  width: 90%;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  cursor: grab;
}

.booking-details-carousel .rsltcvr:active {
  cursor: grabbing;
}

.booking-details-carousel .embla__container {
  display: flex;
  gap: 16px;
}

.booking-details-carousel .room-card {
  width: 280px;
  min-width: 280px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fff;
  padding: 14px;
  display: flex;
  flex-direction: column;
}

.booking-details-carousel .room-header {
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
  margin-bottom: 10px;
}

.booking-details-carousel .room-type {
  font-size: 15px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 4px;
}

.booking-details-carousel .room-number {
  font-size: 12px;
  color: #646d74;
  margin-bottom: 8px;
}

.booking-details-carousel .room-id {
  font-size: 10px;
  color: #868686;
  font-family: monospace;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
}

.booking-details-carousel .room-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.booking-details-carousel .detail-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  font-size: 12px;
}

.booking-details-carousel .detail-label {
  color: #646d74;
  font-weight: 500;
}

.booking-details-carousel .detail-value {
  color: #202020;
  font-weight: 600;
  text-align: right;
  max-width: 60%;
}

.booking-details-carousel .amount-highlight {
  font-size: 16px;
  font-family: inter, sans-serif;
  color: #ef6614;
}

.booking-details-carousel .policy-text {
  font-size: 11px;
  color: #646d74;
  background: #fff8e1;
  padding: 8px;
  border-radius: 6px;
  border-left: 3px solid #ffc107;
  margin-top: 8px;
  line-height: 1.4;
}

.booking-details-carousel .refundable {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #2e7d32;
  background: #e8f5e9;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 600;
  margin-top: 8px;
}

.booking-details-carousel .refundable::before {
  content: '✓';
  font-weight: bold;
}

.booking-details-carousel .non-refundable {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #d32f2f;
  background: #ffebee;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 600;
  margin-top: 8px;
}

.booking-details-carousel .non-refundable::before {
  content: '✗';
  font-weight: bold;
}

.booking-details-carousel .empty-state {
  text-align: center;
  color: #646d74;
  padding: 60px 20px;
  font-size: 14px;
}

/* Dark mode support */
.booking-details-carousel.dark {
  background: #000;
  color: #fff;
}

.booking-details-carousel.dark .room-card,
.booking-details-carousel.dark .hotel-info {
  background: #000;
  border-color: #373737;
}

.booking-details-carousel.dark .room-header {
  border-color: #373737;
}

.booking-details-carousel.dark .bkttl,
.booking-details-carousel.dark .hotel-name,
.booking-details-carousel.dark .room-type,
.booking-details-carousel.dark .date-value,
.booking-details-carousel.dark .detail-value {
  color: #fff;
}

.booking-details-carousel.dark .bksub,
.booking-details-carousel.dark .hotel-address,
.booking-details-carousel.dark .room-number,
.booking-details-carousel.dark .date-label,
.booking-details-carousel.dark .detail-label {
  color: #bcbcbc;
}

.booking-details-carousel.dark .room-id {
  background: #1a1a1a;
  color: #bcbcbc;
}
</style>

<div class="booking-details-carousel">
  <main>
    <div class="bkhd">
      <div class="bkttl">{{ title }}</div>
      <div class="bksub">{{ subtitle }}</div>
    </div>

    {% if hotel_info %}
    <div class="hotel-info">
      <div class="hotel-name">{{ hotel_info.name }}</div>
      {% if hotel_info.address %}
      <div class="hotel-address">{{ hotel_info.address }}</div>
      {% endif %}
      <div class="hotel-dates">
        {% if hotel_info.check_in %}
        <div class="date-item">
          <div class="date-label">Check-in</div>
          <div class="date-value">{{ hotel_info.check_in }}</div>
        </div>
        {% endif %}
        {% if hotel_info.check_out %}
        <div class="date-item">
          <div class="date-label">Check-out</div>
          <div class="date-value">{{ hotel_info.check_out }}</div>
        </div>
        {% endif %}
      </div>
    </div>
    {% endif %}

    {% if rooms %}
    <div class="rooms-title">Rooms in this booking</div>
    <div class="slider-shell">
      <div class="rsltcvr">
        <div class="embla__container">
        {% for room in rooms %}
          <div class="room-card">
            <div class="room-header">
              <div class="room-type">{{ room.room_type }}</div>
              {% if room.room_no %}
              <div class="room-number">Room {{ room.room_no }}</div>
              {% endif %}
              {% if room.room_id %}
              <div class="room-id">ID: {{ room.room_id }}</div>
              {% endif %}
            </div>

            <div class="room-details">
              {% if room.amount %}
              <div class="detail-row">
                <span class="detail-label">Amount</span>
                <span class="detail-value amount-highlight">₹{{ room.amount }}</span>
              </div>
              {% endif %}

              {% if room.is_pay_at_hotel is not none %}
              <div class="detail-row">
                <span class="detail-label">Payment</span>
                <span class="detail-value">{% if room.is_pay_at_hotel %}Pay at Hotel{% else %}Prepaid{% endif %}</span>
              </div>
              {% endif %}

              {% if room.cancellation_policy %}
              <div class="policy-text">{{ room.cancellation_policy }}</div>
              {% endif %}

              {% if room.is_refundable %}
              <div class="refundable">Refundable</div>
              {% elif room.is_refundable is not none %}
              <div class="non-refundable">Non-Refundable</div>
              {% endif %}
            </div>
          </div>
        {% endfor %}
        </div>
      </div>
    </div>
    {% else %}
    <div class="empty-state">No room information available</div>
    {% endif %}
  </main>
</div>
"""


# =====================================================================
# 🎨 RENDERER FUNCTION
# =====================================================================
def render_cancellation_flow(booking_id: str, email: str) -> str:
    """
    Render booking details as display-only HTML (no forms, no API calls).

    This is a PLACEHOLDER that returns a message. The actual booking details
    should be fetched and rendered by the tool itself using render_booking_details().

    Args:
        booking_id: Booking ID
        email: User email

    Returns:
        HTML string with message
    """
    template = _jinja_env.from_string("""
    <div class="booking-details-carousel">
      <main style="max-width: 700px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; color: #646d74; padding: 40px 20px;">
          <p style="font-size: 14px; margin-bottom: 10px;">Loading booking details for <strong>{{ booking_id }}</strong>...</p>
          <p style="font-size: 12px; color: #868686;">Please use chatbot mode for hotel cancellation.</p>
        </div>
      </main>
    </div>
    """)
    return template.render(booking_id=booking_id)


def render_booking_details(booking_details: Dict[str, Any]) -> str:
    """
    Render booking details as display-only HTML carousel.

    Args:
        booking_details: Booking details from API including hotel info and rooms

    Returns:
        HTML string with rendered booking details
    """
    # Extract hotel information
    hotel_info = None
    if booking_details.get("hotel_name"):
        hotel_info = {
            "name": booking_details.get("hotel_name", "Hotel"),
            "address": booking_details.get("hotel_address", ""),
            "check_in": _format_date(booking_details.get("check_in")),
            "check_out": _format_date(booking_details.get("check_out")),
        }

    # Extract rooms
    rooms = booking_details.get("rooms", [])

    if not rooms:
        return """
        <div class="booking-details-carousel">
          <main style="max-width: 700px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; color: #646d74; padding: 40px 20px;">
              <p style="font-size: 14px;">No rooms found in this booking.</p>
            </div>
          </main>
        </div>
        """

    # Normalize rooms for display
    rooms_ui = []
    for room in rooms:
        rooms_ui.append({
            "room_type": room.get("room_type", "Standard Room"),
            "room_no": room.get("room_no"),
            "room_id": room.get("room_id"),
            "amount": room.get("amount"),
            "is_pay_at_hotel": room.get("is_pay_at_hotel"),
            "cancellation_policy": room.get("cancellation_policy"),
            "is_refundable": room.get("is_refundable"),
        })

    # Build title and subtitle
    booking_id = booking_details.get("booking_id", "")
    title = f"Booking Details - {booking_id}" if booking_id else "Booking Details"

    subtitle_parts = []
    if hotel_info and hotel_info["check_in"] and hotel_info["check_out"]:
        subtitle_parts.append(f"{hotel_info['check_in']} to {hotel_info['check_out']}")
    subtitle_parts.append(f"{len(rooms)} room{'s' if len(rooms) > 1 else ''}")
    subtitle = " • ".join(subtitle_parts)

    # Render template
    template = _jinja_env.from_string(BOOKING_DETAILS_TEMPLATE)
    return template.render(
        title=title,
        subtitle=subtitle,
        hotel_info=hotel_info,
        rooms=rooms_ui,
    )


def _format_date(date_str: str) -> str:
    """Format date string for display"""
    if not date_str:
        return None

    try:
        from datetime import datetime
        # Try parsing various date formats
        for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"]:
            try:
                date = datetime.strptime(date_str.split("T")[0], fmt)
                return date.strftime("%d %b %Y")
            except ValueError:
                continue
        return date_str
    except Exception:
        return date_str
