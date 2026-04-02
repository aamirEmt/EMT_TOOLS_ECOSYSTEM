"""Booking Status HTML Renderer"""
from jinja2 import Environment, BaseLoader, select_autoescape

_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)

BOOKING_STATUS_TEMPLATE = """
<style>
.booking-status-card {
  font-family: Poppins, sans-serif;
  width: 360px;
  margin: 0 auto;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.booking-status-card * {
  box-sizing: border-box;
  margin: 0;
}

.bsc-header {
  background: linear-gradient(135deg, #0057b8, #0099cc);
  padding: 18px 24px;
  color: #ffffff;
}

.bsc-header h2 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 2px;
}

.bsc-header span {
  font-size: 12px;
  opacity: 0.85;
}

.bsc-body {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.bsc-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 12px;
}

.bsc-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.bsc-label {
  font-size: 12px;
  color: #888888;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.bsc-value {
  font-size: 14px;
  font-weight: 600;
  color: #202020;
}

.bsc-status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: #e8f5e9;
  color: #2e7d32;
}
</style>

<div class="booking-status-card">
  <div class="bsc-header">
    <h2>Booking Status</h2>
    <span>ID: {{ booking_id }}</span>
  </div>
  <div class="bsc-body">
    <div class="bsc-row">
      <span class="bsc-label">Booking Type</span>
      <span class="bsc-value">{{ product_type }}</span>
    </div>
    <div class="bsc-row">
      <span class="bsc-label">Trip Status</span>
      <span class="bsc-status-badge">{{ trip_status }}</span>
    </div>
  </div>
</div>
"""


def render_booking_status(booking_id: str, product_type: str, trip_status: str) -> str:
    """Render booking status as a styled HTML card."""
    template = _jinja_env.from_string(BOOKING_STATUS_TEMPLATE)
    return template.render(
        booking_id=booking_id,
        product_type=product_type,
        trip_status=trip_status,
    )
