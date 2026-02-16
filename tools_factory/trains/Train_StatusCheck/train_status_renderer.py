"""Train Status HTML Renderer.

This module renders train status data into HTML using Jinja2 templates.
"""

from typing import Dict, Any
from jinja2 import Environment, BaseLoader, select_autoescape


_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)


TRAIN_STATUS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');

.tst-card {
  font-family: 'Poppins', sans-serif;
  color: #202020;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  width: 320px;
  min-width: 280px;
  overflow: hidden;
}

.tst-card * {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Header */
.tst-header {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.tst-train-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.tst-train-name {
  font-size: 14px;
  font-weight: 600;
  color: #202020;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 8px;
}

.tst-train-number {
  background: #F2F9FF;
  border: 1px solid #B6D5F0;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  color: #1976d2;
  flex-shrink: 0;
}

/* Timing Block */
.tst-timing {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.tst-time-block {
  text-align: center;
  min-width: 50px;
}

.tst-time {
  font-size: 18px;
  font-weight: 600;
  color: #202020;
  font-family: 'Inter', sans-serif;
}

.tst-station-code {
  font-size: 11px;
  color: #868686;
  margin-top: 2px;
}

.tst-duration-block {
  flex: 1;
  text-align: center;
  position: relative;
}

.tst-duration {
  font-size: 11px;
  color: #646d74;
  margin-bottom: 4px;
}

.tst-duration-line {
  height: 1px;
  background: #ccc;
  position: relative;
  margin: 0 10px;
}

.tst-duration-line::before,
.tst-duration-line::after {
  content: '';
  position: absolute;
  width: 6px;
  height: 6px;
  background: #ccc;
  border-radius: 50%;
  top: 50%;
  transform: translateY(-50%);
}

.tst-duration-line::before { left: -3px; }
.tst-duration-line::after { right: -3px; }

.tst-date {
  font-size: 10px;
  color: #868686;
  margin-top: 4px;
}

/* Live Status Section */
.tst-live-section {
  padding: 12px;
  background: #f8fafe;
}

.tst-progress-row {
  margin-bottom: 10px;
}

.tst-progress-bar {
  width: 100%;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: visible;
  position: relative;
}

.tst-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #8bc34a);
  border-radius: 3px;
  position: relative;
}

.tst-progress-train {
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  background: #2093ef;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.tst-progress-train img {
  width: 14px;
  height: 14px;
}

/* Current Station */
.tst-current-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e8f4fd;
}

.tst-current-icon {
  width: 32px;
  height: 32px;
  background: #2093ef;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tst-current-icon img {
  width: 18px;
  height: 18px;
}

.tst-current-info {
  flex: 1;
  min-width: 0;
}

.tst-current-label {
  font-size: 9px;
  text-transform: uppercase;
  color: #868686;
  letter-spacing: 0.5px;
}

.tst-current-station {
  font-size: 13px;
  font-weight: 600;
  color: #202020;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tst-current-time {
  font-size: 11px;
  color: #646d74;
  margin-top: 2px;
}

.tst-delay-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  white-space: nowrap;
}

.tst-delay-badge.late {
  background: #fff3e0;
  color: #e65100;
}

.tst-delay-badge.severe {
  background: #ffebee;
  color: #c62828;
}

.tst-delay-badge.ontime {
  background: #e8f5e9;
  color: #2e7d32;
}

/* Schedule Mode */
.tst-schedule-section {
  padding: 10px 12px;
  background: #fafafa;
}

.tst-schedule-row {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #646d74;
}

/* Dropdown Section */
.tst-dropdown {
  border-top: 1px solid #e8e8e8;
}

.tst-dropdown-btn {
  width: 100%;
  padding: 10px 12px;
  background: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-family: 'Poppins', sans-serif;
  font-size: 12px;
  font-weight: 500;
  color: #2093ef;
}

.tst-dropdown-btn:hover {
  background: #f8f9fa;
}

.tst-dropdown-icon {
  transition: transform 0.2s ease;
  font-size: 10px;
}

.tst-dropdown-btn.open .tst-dropdown-icon {
  transform: rotate(180deg);
}

.tst-stations-list {
  display: none;
  max-height: 250px;
  overflow-y: auto;
  background: #fafafa;
  border-top: 1px solid #e8e8e8;
}

.tst-stations-list.open {
  display: block;
}

.tst-station-row {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 12px;
}

.tst-station-row:last-child {
  border-bottom: none;
}

.tst-station-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #e0e0e0;
  margin-right: 10px;
  flex-shrink: 0;
}

.tst-station-dot.origin { background: #2e7d32; }
.tst-station-dot.destination { background: #d32f2f; }
.tst-station-dot.current { background: #2093ef; }
.tst-station-dot.passed { background: #4caf50; }

.tst-station-name {
  flex: 1;
  color: #202020;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tst-station-name .code {
  color: #868686;
  font-size: 10px;
}

.tst-station-time {
  color: #646d74;
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  margin-left: 8px;
}

.tst-station-delay {
  color: #e65100;
  font-size: 10px;
  margin-left: 6px;
}

/* Footer */
.tst-footer {
  padding: 8px 12px;
  background: #f5f5f5;
  border-top: 1px solid #e8e8e8;
  font-size: 9px;
  color: #868686;
  text-align: center;
}

.tst-footer.live {
  background: #e3f2fd;
  color: #1565c0;
}

</style>

<div class="tst-card" data-train-no="{{ train_number }}" data-journey-date="{{ journey_date }}">
  <!-- Header -->
  <div class="tst-header">
    <div class="tst-train-row">
      <div class="tst-train-name">{{ train_name }}</div>
      <div class="tst-train-number">{{ train_number }}</div>
    </div>

    <div class="tst-timing">
      <div class="tst-time-block">
        <div class="tst-time">{{ departure_time }}</div>
        <div class="tst-station-code">{{ origin_code }}</div>
      </div>

      <div class="tst-duration-block">
        {% if journey_duration %}
        <div class="tst-duration">{{ journey_duration }}</div>
        {% endif %}
        <div class="tst-duration-line"></div>
        <div class="tst-date">{{ formatted_date }}</div>
      </div>

      <div class="tst-time-block">
        <div class="tst-time">{{ arrival_time }}</div>
        <div class="tst-station-code">{{ destination_code }}</div>
      </div>
    </div>
  </div>

  {% if is_live and distance_percentage %}
  <!-- Live Status -->
  <div class="tst-live-section">
    <div class="tst-progress-row">
      <div class="tst-progress-bar">
        <div class="tst-progress-fill" style="width: {{ distance_percentage }};">
          <div class="tst-progress-train">
            <img src="https://railways.easemytrip.com/Content/Train/img/train.svg" alt="Train">
          </div>
        </div>
      </div>
    </div>

    {% if current_station_index is not none and stations[current_station_index] %}
    {% set current = stations[current_station_index] %}
    <div class="tst-current-row">
      <div class="tst-current-icon">
        <img src="https://railways.easemytrip.com/Content/Train/img/train.svg" alt="Train">
      </div>
      <div class="tst-current-info">
        <div class="tst-current-label">Last at</div>
        <div class="tst-current-station">{{ current.station_name }}</div>
        {% if current.actual_departure %}
        <div class="tst-current-time">Dep: {{ current.actual_departure }}</div>
        {% endif %}
      </div>
      {% if current.delay_departure and current.delay_departure != '0' %}
      <div class="tst-delay-badge {% if 'H' in current.delay_departure %}severe{% else %}late{% endif %}">
        {{ current.delay_departure }}
      </div>
      {% else %}
      <div class="tst-delay-badge ontime">On Time</div>
      {% endif %}
    </div>
    {% endif %}
  </div>
  {% else %}
  <!-- Schedule Only -->
  <div class="tst-schedule-section">
    <div class="tst-schedule-row">
      <span>🚉 {{ total_halts }} stops</span>
      {% if total_distance %}
      <span>📍 {{ total_distance }} km</span>
      {% endif %}
    </div>
  </div>
  {% endif %}

  <!-- Stations Dropdown -->
  <div class="tst-dropdown">
    <button class="tst-dropdown-btn" onclick="this.classList.toggle('open'); this.nextElementSibling.classList.toggle('open');">
      <span>View all {{ stations|length }} stations</span>
      <span class="tst-dropdown-icon">▼</span>
    </button>
    <div class="tst-stations-list">
      {% for station in stations %}
      {% set is_passed = is_live and station.actual_departure %}
      {% set is_current = station.is_current_station or (current_station_index is not none and loop.index0 == current_station_index) %}
      <div class="tst-station-row">
        <div class="tst-station-dot {% if station.is_origin %}origin{% elif station.is_destination %}destination{% elif is_current %}current{% elif is_passed %}passed{% endif %}"></div>
        <div class="tst-station-name">
          {{ station.station_name }}
          <span class="code">({{ station.station_code }})</span>
        </div>
        <div class="tst-station-time">
          {% if station.is_origin %}{{ station.departure_time or '--' }}{% elif station.is_destination %}{{ station.arrival_time or '--' }}{% else %}{{ station.arrival_time or '--' }}{% endif %}
        </div>
        {% if is_live and station.actual_departure and not station.is_destination %}
        {% if station.delay_departure and station.delay_departure != '0' %}
        <div class="tst-station-delay">{{ station.delay_departure }}</div>
        {% else %}
        <div class="tst-station-delay" style="color: #2e7d32;">On Time</div>
        {% endif %}
        {% endif %}
      </div>
      {% endfor %}
    </div>
  </div>

  <div class="tst-footer {% if is_live %}live{% endif %}">
    {% if is_live %}Live · {{ distance_travelled }} km done · {{ remain_distance }} km left{% else %}Schedule only{% endif %}
  </div>
</div>
"""


TRAIN_DATES_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

.train-dates-widget {
  font-family: 'Poppins', sans-serif;
  color: #202020;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
}

.train-dates-widget * {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.tdt-header {
  margin-bottom: 16px;
}

.tdt-title {
  font-size: 16px;
  font-weight: 600;
  color: #202020;
}

.tdt-subtitle {
  font-size: 12px;
  color: #646d74;
  margin-top: 4px;
}

.tdt-dates {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tdt-date-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.tdt-date-item:hover {
  border-color: #2093ef;
  background: #f0f7ff;
}

.tdt-date-info {
  display: flex;
  flex-direction: column;
}

.tdt-date-main {
  font-size: 14px;
  font-weight: 500;
  color: #202020;
}

.tdt-date-day {
  font-size: 12px;
  color: #646d74;
}

.tdt-date-display {
  font-size: 12px;
  font-weight: 500;
  color: #2093ef;
  background: #e3f2fd;
  padding: 4px 8px;
  border-radius: 4px;
}
</style>

<div class="train-dates-widget">
  <div class="tdt-header">
    <div class="tdt-title">Train {{ train_number }}</div>
    <div class="tdt-subtitle">Select a date to check status</div>
  </div>

  <div class="tdt-dates">
    {% for date in available_dates %}
    <div class="tdt-date-item">
      <div class="tdt-date-info">
        <span class="tdt-date-main">{{ date.formatted_date }}</span>
        <span class="tdt-date-day">{{ date.day_name }}</span>
      </div>
      {% if date.display_day %}
      <span class="tdt-date-display">{{ date.display_day }}</span>
      {% endif %}
    </div>
    {% endfor %}
  </div>
</div>
"""


def render_train_status_results(status_result: Dict[str, Any]) -> str:
    """
    Renders train status into HTML.

    Args:
        status_result: Train status data from service

    Returns:
        HTML string with rendered train status
    """
    if status_result.get("error"):
        error_msg = status_result.get("message", "Unknown error")
        return f"""
        <div class="tst-card" style="padding: 30px 20px; text-align: center;">
          <div style="font-size: 32px; margin-bottom: 12px;">🚂</div>
          <div style="font-size: 13px; font-weight: 500; color: #202020;">Unable to fetch train status</div>
          <div style="font-size: 11px; color: #868686; margin-top: 6px;">{error_msg}</div>
        </div>
        """

    template = _jinja_env.from_string(TRAIN_STATUS_TEMPLATE)
    return template.render(**status_result)


def render_train_dates(dates_result: Dict[str, Any]) -> str:
    """
    Renders available dates selection into HTML.

    Args:
        dates_result: Available dates data from service

    Returns:
        HTML string with date selection UI
    """
    if dates_result.get("error"):
        error_msg = dates_result.get("message", "Unknown error")
        return f"""
        <div class="train-dates-widget">
          <div style="padding: 20px; text-align: center; color: #646d74;">
            <div style="font-size: 14px;">{error_msg}</div>
          </div>
        </div>
        """

    template = _jinja_env.from_string(TRAIN_DATES_TEMPLATE)
    return template.render(**dates_result)
