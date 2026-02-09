"""PNR Status HTML Renderer - Jinja2 template for PNR status display."""

from typing import Dict, Any
from jinja2 import Environment, BaseLoader, select_autoescape


PNR_ERROR_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');

.pnr-error-card {
  font-family: Poppins, sans-serif;
  color: #202020;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-width: 394px;
  width: 100%;
  margin: 0 auto;
  overflow: hidden;
}

.pnr-error-header {
  background: #ffebee;
  color: #c62828;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ffcdd2;
}

.pnr-error-title {
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pnr-error-icon {
  font-size: 20px;
}

.pnr-error-body {
  padding: 24px 16px;
  text-align: center;
}

.pnr-error-message {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
}

.pnr-error-details {
  font-size: 12px;
  color: #999;
  font-style: italic;
}

.pnr-number-display {
  font-size: 18px;
  font-weight: 600;
  color: #c62828;
  margin: 12px 0;
  font-family: monospace;
}
</style>

<div class="pnr-error-card">
  <div class="pnr-error-header">
    <div class="pnr-error-title">
      <span class="pnr-error-icon">⚠️</span>
      <span>Invalid PNR</span>
    </div>
  </div>

  <div class="pnr-error-body">
    <div class="pnr-number-display">{{ pnr_number }}</div>
    <div class="pnr-error-message">
      {{ error_message }}
    </div>
    <div class="pnr-error-details">
      Please verify your PNR number and try again.
    </div>
  </div>
</div>
"""


PNR_STATUS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');

.pnr-status-card {
  font-family: Poppins, sans-serif;
  color: #202020;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-width: 394px;
  width: 100%;
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
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
}


.pnr-number {
  font-size: 16px;
  font-weight: 700;
  color: #202020;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pnr-logo {
  width: 40px;
  height: 26px;
  object-fit: contain;
}

.chart-badge {
  font-size: 10px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 10px;
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
  padding: 16px;
}

.train-route-container {
  display: flex;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.train-info {
  min-width: 0;
}

.train-name {
  font-size: 14px;
  font-weight: 600;
  color: #202020;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: help;
}

.train-number {
  font-size: 11px;
  color: #666;
  margin-top: 2px;
}

.journey-date {
  font-size: 12px;
  color: #665;
  font-weight: 500;
}

.route-line {
  font-size: 16px;
  font-weight: 600;
  color: #202020;
  text-align: center;
  margin-bottom: 12px;
  line-height: 1.4;
  background: #d4e9ff;
  padding: 10px 16px;
  border-radius: 6px;
  border: 1px solid #8ec3ff;
}

.route-line .route-arrow {
  margin: 0 6px;
  color: #4a90e2;
  font-weight: 700;
  font-size: 16px;
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
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.info-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f1f3f5;
  padding: 5px 8px;
  border-radius: 8px;
  font-size: 10px;
  border: 1px solid #e5e7eb;
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
  font-size: 13px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 10px;
}

.passenger-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.passenger-table th {
  background: #f8f9fa;
  padding: 8px 6px;
  text-align: left;
  font-weight: 600;
  color: #666;
  border-bottom: 2px solid #eee;
  font-size: 10px;
}

.passenger-table td {
  padding: 8px 6px;
  border-bottom: 1px solid #eee;
  vertical-align: middle;
}

.passenger-table tr:last-child td {
  border-bottom: none;
}

.status-badge {
  display: inline-block;
  padding: 3px 6px;
  border-radius: 4px;
  font-size: 10px;
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
  font-size: 10px;
  color: #333;
}

.fare-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fare-label {
  font-size: 12px;
  color: #666;
}

.fare-amount {
  font-size: 16px;
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
        <div class="train-name" title="{{ train_name }}">{{ train_name }}</div>
        <div class="train-number">Train No: {{ train_number }}</div>
      </div>

      <div class="route-info">
        <div class="journey-date">Journey Date: {{ date_of_journey }}</div>
      </div>
    </div>

    <div class="route-line">
      {{ source_station_name }} ({{ source_station }})
      <span class="route-arrow">&#8594;</span>
      {{ destination_station_name }} ({{ destination_station }})
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

    {% set fare_value = ticket_fare or booking_fare %}
    {% if is_valid_fare(fare_value) and not has_cancelled_passenger(passengers) %}
    <div class="fare-section">
      <span class="fare-label">Ticket Fare</span>
      <span class="fare-amount">{{ fare_value }}</span>
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


def _has_cancelled_passenger(passengers: list) -> bool:
    """Check if any passenger has cancelled status."""
    if not passengers:
        return False

    for passenger in passengers:
        current_status = passenger.get("current_status", "")
        if current_status and "CAN" in current_status.upper():
            return True

    return False


def _is_valid_fare(fare: str) -> bool:
    """Check if fare value is valid and should be displayed."""
    if not fare:
        return False

    fare_str = str(fare).strip().upper()

    # Check for invalid values
    if fare_str in ["0", "N/A", "NA", "NULL", "NONE", ""]:
        return False

    # Try to convert to number and check if it's greater than 0
    try:
        fare_num = float(fare_str)
        return fare_num > 0
    except (ValueError, TypeError):
        return False


# Create Jinja2 environment
_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)
_jinja_env.globals["get_status_class"] = _get_status_class
_jinja_env.globals["has_cancelled_passenger"] = _has_cancelled_passenger
_jinja_env.globals["is_valid_fare"] = _is_valid_fare


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


def render_pnr_error(pnr_number: str, error_message: str) -> str:
    """
    Render PNR error as simple HTML.

    Args:
        pnr_number: The PNR number that failed
        error_message: Error message to display

    Returns:
        HTML string for error display
    """
    template = _jinja_env.from_string(PNR_ERROR_TEMPLATE)
    return template.render(pnr_number=pnr_number, error_message=error_message)
