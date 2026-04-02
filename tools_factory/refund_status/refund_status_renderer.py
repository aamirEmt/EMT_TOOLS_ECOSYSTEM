"""Refund Status HTML Renderer"""
from jinja2 import Environment, BaseLoader, select_autoescape

_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)

REFUND_STATUS_TEMPLATE = """
<style>
.refund-status-card {
  font-family: Poppins, sans-serif;
  max-width: 480px;
  margin: 0 auto;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.refund-status-card * {
  box-sizing: border-box;
  margin: 0;
}

.rsc-header {
  background: linear-gradient(135deg, #0057b8, #0099cc);
  padding: 18px 24px;
  color: #ffffff;
}

.rsc-header h2 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 2px;
}

.rsc-header span {
  font-size: 12px;
  opacity: 0.85;
}

.rsc-body {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.rsc-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 12px;
}

.rsc-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.rsc-label {
  font-size: 12px;
  color: #888888;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.rsc-value {
  font-size: 14px;
  font-weight: 600;
  color: #202020;
}

.rsc-badge-refunded {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: #e8f5e9;
  color: #2e7d32;
}

.rsc-badge-unavailable {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: #fff3e0;
  color: #e65100;
}

.rsc-refund-note {
  font-size: 12px;
  color: #888888;
  margin-top: 6px;
  line-height: 1.5;
}
</style>

<div class="refund-status-card">
  <div class="rsc-header">
    <h2>Refund Status</h2>
    <span>ID: {{ booking_id }}</span>
  </div>
  <div class="rsc-body">
    <div class="rsc-row">
      <span class="rsc-label">Booking Type</span>
      <span class="rsc-value">{{ product_type }}</span>
    </div>
    <div class="rsc-row">
      <span class="rsc-label">Current Status</span>
      {% if is_refunded %}
        <span class="rsc-badge-refunded">{{ trip_status }}</span>
      {% else %}
        <span class="rsc-badge-unavailable">{{ trip_status }}</span>
      {% endif %}
    </div>
    <div class="rsc-row" style="flex-direction: column; align-items: flex-start; gap: 6px;">
      {% if not is_refunded %}
        <p class="rsc-refund-note">Your booking is currently <strong>{{ trip_status }}</strong>. No refund status is available for this booking.</p>
      {% endif %}
    </div>
  </div>
</div>
"""


def render_refund_status(booking_id: str, product_type: str, trip_status: str, refund_status: str) -> str:
    """Render refund status as a styled HTML card."""
    template = _jinja_env.from_string(REFUND_STATUS_TEMPLATE)
    return template.render(
        booking_id=booking_id,
        product_type=product_type,
        trip_status=trip_status,
        refund_status=refund_status,
        is_refunded=refund_status == "Refunded",
    )
