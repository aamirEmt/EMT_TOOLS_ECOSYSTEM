"""PNR Status HTML Renderer - Jinja2 template for PNR status display."""

from typing import Dict, Any
from jinja2 import Environment, BaseLoader, select_autoescape


PNR_STATUS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');

.pnr-status-card {
  font-family: Poppins, sans-serif;
  color: #202020;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  margin: 0 auto;
  overflow: hidden;
}

.pnr-status-card * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.pnr-header {
  background: #ffffff;
  color: #202020;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;  
}


.pnr-number {
  font-size: 18px;
  font-weight: 700;
  color: #202020;
  display: flex;
  align-items: center;
  gap: 10px;
}

.pnr-logo {
  width: 50px;
  height: 32px;
  object-fit: contain;
}

.chart-badge {
  font-size: 11px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 12px;
  text-transform: uppercase;
}

.chart-badge.prepared {
  background: #2e7d32;
  color: #ffffff;
}

.chart-badge.not-prepared {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
}

.pnr-body {
  padding: 20px;
}

.train-route-container {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.train-info {
  min-width: 0;
}

.train-name {
  font-size: 16px;
  font-weight: 600;
  color: #202020;
}

.train-number {
  font-size: 13px;
  color: #666;
  margin-top: 2px;
}

.journey-date {
  font-size: 12px;
  color: #665;
  font-weight: 500;
}

.route-line {
  font-size: 14px;
  font-weight: 600;
  color: #202020;
  text-align: right;
  line-height: 1.3;
}

.route-line .route-arrow {
  margin: 0 6px;
  color: #ef6614;
  font-weight: 700;
}

.route-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  flex: 1;
  min-width: 0;
}

.station {
  flex: 1;
}

.station.destination {
  text-align: right;
}

.station-code {
  font-size: 16px;
  font-weight: 600;
  color: #202020;
}

.station-name {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

.route-arrow {
  color: #ef6614;
  font-size: 20px;
  font-weight: bold;
}

.journey-details {
  justify-content: center;
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.info-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f1f3f5;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 13px;
  border: 1px solid #e5e7eb;;
}

.info-chip .label {
  color: #666;
}

.info-chip .value {
  font-weight: 600;
  color: #202020;
}

.passenger-section {
  margin-top: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 12px;
}

.passenger-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.passenger-table th {
  background: #f8f9fa;
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  color: #666;
  border-bottom: 2px solid #eee;
}

.passenger-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
  vertical-align: middle;
}

.passenger-table tr:last-child td {
  border-bottom: none;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.status-confirmed {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-waitlist {
  background: #fff3e0;
  color: #f57c00;
}

.status-rac {
  background: #e3f2fd;
  color: #1976d2;
}

.status-cancelled {
  background: #ffebee;
  color: #d32f2f;
}

.status-nosb {
  background: #f5f5f5;
  color: #757575;
}

.berth-info {
  font-family: monospace;
  font-size: 12px;
  color: #333;
}

.fare-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fare-label {
  font-size: 13px;
  color: #666;
}

.fare-amount {
  font-size: 18px;
  font-weight: 600;
  color: #2e7d32;
}

.fare-amount::before {
  content: "\\20B9";
  margin-right: 2px;
}
</style>

<div class="pnr-status-card">
  <div class="pnr-header">
    <div class="pnr-number">
      <img src="https://railways.easemytrip.com/Content/img/Group%20118.svg" alt="PNR" class="pnr-logo">
      <span>{{ pnr_number }}</span>
    </div>
    <span class="chart-badge {{ 'prepared' if 'prepared' in chart_status.lower() else 'not-prepared' }}">
      {{ chart_status }}
    </span>
  </div>

  <div class="pnr-body">
    <div class="train-route-container">
      <div class="train-info">
        <div class="train-name">{{ train_name }}</div>
        <div class="train-number">Train No: {{ train_number }}</div>
      </div>

      <div class="route-info">
        <div class="route-line">
          {{ source_station_name }} ({{ source_station }})
          <span class="route-arrow">&#8594;</span>
          {{ destination_station_name }} ({{ destination_station }})
        </div>
        <div class="journey-date">Journey Date: {{ date_of_journey }}</div>
      </div>
    </div>

    <div class="journey-details">
      <div class="info-chip">
        <span class="label">Class:</span>
        <span class="value">{{ class_name or journey_class }}</span>
      </div>
      <div class="info-chip">
        <span class="label">Quota:</span>
        <span class="value">{{ quota_name or quota }}</span>
      </div>
      {% if boarding_point %}
      <div class="info-chip">
        <span class="label">Boarding:</span>
        <span class="value">{{ boarding_point }}</span>
      </div>
      {% endif %}
    </div>

    <div class="passenger-section">
      <div class="section-title">Passenger Details</div>
      <table class="passenger-table">
        <thead>
          <tr>
            <th>S.No</th>
            <th>Booking Status</th>
            <th>Current Status</th>
            <th>Coach/Berth</th>
          </tr>
        </thead>
        <tbody>
          {% for passenger in passengers %}
          <tr>
            <td>{{ passenger.serial_number }}</td>
            <td>
              <span class="status-badge {{ get_status_class(passenger.booking_status) }}">
                {{ passenger.booking_status }}
              </span>
            </td>
            <td>
              <span class="status-badge {{ get_status_class(passenger.current_status) }}">
                {{ passenger.current_status }}
              </span>
            </td>
            <td class="berth-info">
              {% if passenger.coach and passenger.berth_number %}
                {{ passenger.coach }}/{{ passenger.berth_number }}{% if passenger.berth_type %} ({{ passenger.berth_type }}){% endif %}
              {% else %}
                -
              {% endif %}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>

    {% if booking_fare or ticket_fare %}
    <div class="fare-section">
      <span class="fare-label">Ticket Fare</span>
      <span class="fare-amount">{{ ticket_fare or booking_fare }}</span>
    </div>
    {% endif %}
  </div>
</div>
"""


def _get_status_class(status: str) -> str:
    """Get CSS class based on booking/current status."""
    if not status:
        return ""

    status_upper = status.upper()

    if "CNF" in status_upper or "CONFIRMED" in status_upper:
        return "status-confirmed"
    if "WL" in status_upper or "WAITLIST" in status_upper:
        return "status-waitlist"
    if "RAC" in status_upper:
        return "status-rac"
    if "CAN" in status_upper:
        return "status-cancelled"
    if "NOSB" in status_upper or "NRSB" in status_upper:
        return "status-nosb"

    return ""


# Create Jinja2 environment
_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)
_jinja_env.globals["get_status_class"] = _get_status_class


def render_pnr_status(pnr_info: Dict[str, Any]) -> str:
    """
    Render PNR status as HTML.

    Args:
        pnr_info: Dictionary containing PNR status information

    Returns:
        HTML string for PNR status display
    """
    template = _jinja_env.from_string(PNR_STATUS_TEMPLATE)
    return template.render(**pnr_info)
