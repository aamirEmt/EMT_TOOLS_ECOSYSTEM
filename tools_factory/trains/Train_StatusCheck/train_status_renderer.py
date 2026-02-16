"""Train Status HTML Renderer.

This module renders train status data into HTML using Jinja2 templates.
Uses vertical timeline UI consistent with the route check renderer.
"""

from typing import Dict, Any
from jinja2 import Environment, BaseLoader, select_autoescape


_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)


TRAIN_STATUS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,100..900&family=Poppins:wght@300;400;500;600;700&display=swap');

.train-status {
  font-family: Poppins, sans-serif;
  color: #202020;
  background: #fff;
  max-width: 400px;
  margin: 0 auto;
}

.train-status * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.train-status .status-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}

/* Header */
.train-status .status-header {
  padding: 14px 16px;
  border-bottom: 1px solid #e0e0e0;
}

.train-status .status-header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.train-status .status-train-name {
  font-size: 15px;
  font-weight: 600;
  color: #202020;
  line-height: 1.3;
}

.train-status .status-train-no {
  font-weight: 500;
  font-size: 13px;
  padding: 3px 6px;
  color: #313131;
  background: #F2F9FF;
  border: 1px solid #B6D5F0;
  border-radius: 3px;
  white-space: nowrap;
}

.train-status .status-running-days {
  display: flex;
  gap: 4px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.train-status .day-chip {
  font-size: 10px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
  background: #f5f5f5;
  color: #888;
  border: 1px solid #e0e0e0;
}

.train-status .day-chip.active {
  background: #e8f5e9;
  color: #2e7d32;
  border-color: #a5d6a7;
  font-weight: 600;
}

/* Timing row */
.train-status .status-timing {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 12px;
}

.train-status .status-time-block {
  text-align: center;
  min-width: 50px;
}

.train-status .status-time {
  font-size: 18px;
  font-weight: 600;
  color: #202020;
  font-family: 'Inter', sans-serif;
}

.train-status .status-stn-code {
  font-size: 11px;
  color: #868686;
  margin-top: 2px;
}

.train-status .status-duration-block {
  flex: 1;
  text-align: center;
  position: relative;
}

.train-status .status-duration {
  font-size: 11px;
  color: #646d74;
  margin-bottom: 4px;
}

.train-status .status-duration-line {
  height: 1px;
  background: #ccc;
  position: relative;
  margin: 0 10px;
}

.train-status .status-duration-line::before,
.train-status .status-duration-line::after {
  content: '';
  position: absolute;
  width: 6px;
  height: 6px;
  background: #ccc;
  border-radius: 50%;
  top: 50%;
  transform: translateY(-50%);
}

.train-status .status-duration-line::before { left: -3px; }
.train-status .status-duration-line::after { right: -3px; }

.train-status .status-date {
  font-size: 10px;
  color: #868686;
  margin-top: 4px;
}

/* Live progress bar */
.train-status .live-progress {
  padding: 12px 16px;
  background: #f8fafe;
  border-bottom: 1px solid #e0e0e0;
}

.train-status .progress-bar {
  width: 100%;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: visible;
  position: relative;
  margin-bottom: 10px;
}

.train-status .progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #8bc34a);
  border-radius: 3px;
  position: relative;
}

.train-status .progress-train-icon {
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

.train-status .progress-train-icon img {
  width: 14px;
  height: 14px;
}

.train-status .current-station-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e8f4fd;
}

.train-status .current-stn-icon {
  width: 32px;
  height: 32px;
  background: #2093ef;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.train-status .current-stn-icon img {
  width: 18px;
  height: 18px;
}

.train-status .current-stn-info {
  flex: 1;
  min-width: 0;
}

.train-status .current-stn-label {
  font-size: 9px;
  text-transform: uppercase;
  color: #868686;
  letter-spacing: 0.5px;
}

.train-status .current-stn-name {
  font-size: 13px;
  font-weight: 600;
  color: #202020;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.train-status .current-stn-time {
  font-size: 11px;
  color: #646d74;
  margin-top: 2px;
}

.train-status .delay-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  white-space: nowrap;
}

.train-status .delay-badge.late {
  background: #fff3e0;
  color: #e65100;
}

.train-status .delay-badge.severe {
  background: #ffebee;
  color: #c62828;
}

.train-status .delay-badge.ontime {
  background: #e8f5e9;
  color: #2e7d32;
}

/* Timeline */
.train-status .status-timeline {
  padding: 16px;
}

.train-status .timeline-stop {
  display: flex;
  gap: 12px;
  position: relative;
}

.train-status .timeline-track {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20px;
  flex-shrink: 0;
}

.train-status .timeline-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #fff;
  border: 3px solid #e0e0e0;
  z-index: 1;
  flex-shrink: 0;
}

.train-status .timeline-dot.origin {
  background: #2e7d32;
  border-color: #2e7d32;
}

.train-status .timeline-dot.destination {
  background: #d32f2f;
  border-color: #d32f2f;
}

.train-status .timeline-dot.passed {
  background: #4caf50;
  border-color: #4caf50;
}

.train-status .timeline-dot.current {
  background: #fff;
  border: 3px solid #2093ef;
  box-shadow: 0 0 0 3px rgba(32, 147, 239, 0.2);
}

.train-status .timeline-dot.upcoming {
  background: #fff;
  border: 3px solid #e0e0e0;
}

.train-status .timeline-line {
  width: 2px;
  flex: 1;
  background: #e0e0e0;
  min-height: 20px;
}

.train-status .timeline-line.passed {
  background: #4caf50;
}

/* Stop info */
.train-status .stop-info {
  flex: 1;
  padding-bottom: 18px;
  min-width: 0;
}

.train-status .timeline-stop:last-child .stop-info {
  padding-bottom: 0;
}

.train-status .stop-station {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.train-status .stop-station-name {
  font-size: 13px;
  font-weight: 600;
  color: #202020;
}

.train-status .stop-station-code {
  font-size: 11px;
  font-weight: 500;
  color: #1976d2;
  background: #e3f2fd;
  padding: 1px 5px;
  border-radius: 3px;
}

.train-status .stop-platform {
  font-size: 10px;
  font-weight: 500;
  padding: 1px 5px;
  border-radius: 3px;
  background: #f3e5f5;
  color: #7b1fa2;
}

.train-status .stop-details {
  display: flex;
  gap: 6px;
  margin-top: 4px;
  flex-wrap: wrap;
  align-items: center;
}

.train-status .stop-detail {
  font-size: 11px;
  color: #646d74;
}

.train-status .stop-detail strong {
  color: #202020;
  font-weight: 600;
}

.train-status .stop-detail-sep {
  color: #ccc;
  font-size: 10px;
}

.train-status .halt-badge {
  font-size: 10px;
  font-weight: 500;
  padding: 1px 5px;
  border-radius: 3px;
  background: #fff3e0;
  color: #f57c00;
}

.train-status .distance-badge {
  font-size: 10px;
  font-weight: 500;
  padding: 1px 5px;
  border-radius: 3px;
  background: #f5f5f5;
  color: #666;
}

/* Live detail row (actual time + delay) */
.train-status .stop-live-row {
  display: flex;
  gap: 6px;
  margin-top: 3px;
  align-items: center;
  flex-wrap: wrap;
}

.train-status .stop-actual {
  font-size: 10px;
  color: #1976d2;
  font-weight: 500;
}

.train-status .stop-delay {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 5px;
  border-radius: 3px;
}

.train-status .stop-delay.late {
  background: #fff3e0;
  color: #e65100;
}

.train-status .stop-delay.ontime {
  background: #e8f5e9;
  color: #2e7d32;
}

/* Show more button */
.train-status .show-more-wrapper {
  padding: 0 16px 16px;
  text-align: center;
}

.train-status .show-more-btn {
  width: 100%;
  padding: 8px 16px;
  background: #fff;
  color: #1976d2;
  border: 1px solid #bbdefb;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  font-family: Poppins, sans-serif;
  transition: all 0.2s ease;
}

.train-status .show-more-btn:hover {
  background: #e3f2fd;
  border-color: #1976d2;
}

/* Hidden stops */
.train-status .hidden-stops {
  display: none;
}

.train-status .hidden-stops.visible {
  display: block;
}

/* Footer */
.train-status .status-footer {
  padding: 10px 16px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #646d74;
}

.train-status .status-footer strong {
  color: #202020;
}

.train-status .status-footer .live-tag {
  font-size: 10px;
  font-weight: 600;
  color: #1565c0;
  background: #e3f2fd;
  padding: 2px 8px;
  border-radius: 4px;
}

</style>

<div class="train-status" id="status-{{ instance_id }}">
  <div class="status-card">
    <!-- Header -->
    <div class="status-header">
      <div class="status-header-top">
        <div class="status-train-name">{{ train_name }}</div>
        <div class="status-train-no">{{ train_number }}</div>
      </div>
      {% if runs_on %}
      <div class="status-running-days">
        {% for day in all_days %}
        <span class="day-chip {{ 'active' if day in runs_on else '' }}">{{ day }}</span>
        {% endfor %}
      </div>
      {% endif %}

      <div class="status-timing">
        <div class="status-time-block">
          <div class="status-time">{{ departure_time }}</div>
          <div class="status-stn-code">{{ origin_code }}</div>
        </div>
        <div class="status-duration-block">
          {% if journey_duration %}
          <div class="status-duration">{{ journey_duration }}</div>
          {% endif %}
          <div class="status-duration-line"></div>
          <div class="status-date">{{ formatted_date }}</div>
        </div>
        <div class="status-time-block">
          <div class="status-time">{{ arrival_time }}</div>
          <div class="status-stn-code">{{ destination_code }}</div>
        </div>
      </div>
    </div>

    {% if is_live and distance_percentage %}
    <!-- Live Progress -->
    <div class="live-progress">
      <div class="progress-bar">
        <div class="progress-fill" style="width: {{ distance_percentage }};">
          <div class="progress-train-icon">
            <img src="https://railways.easemytrip.com/Content/Train/img/train.svg" alt="Train">
          </div>
        </div>
      </div>

      {% if current_station_index is not none and stations[current_station_index] %}
      {% set current = stations[current_station_index] %}
      <div class="current-station-row">
        <div class="current-stn-icon">
          <img src="https://railways.easemytrip.com/Content/Train/img/train.svg" alt="Train">
        </div>
        <div class="current-stn-info">
          <div class="current-stn-label">Last at</div>
          <div class="current-stn-name">{{ current.station_name }}</div>
          {% if current.actual_departure %}
          <div class="current-stn-time">Dep: {{ current.actual_departure }}</div>
          {% endif %}
        </div>
        {% if current.delay_departure and current.delay_departure != '0' %}
        <div class="delay-badge {% if 'H' in current.delay_departure %}severe{% else %}late{% endif %}">
          {{ current.delay_departure }}
        </div>
        {% else %}
        <div class="delay-badge ontime">On Time</div>
        {% endif %}
      </div>
      {% endif %}
    </div>
    {% endif %}

    <!-- Timeline: Visible stops (first 5) -->
    <div class="status-timeline">
      {% for station in visible_stops %}
      {% set is_passed = is_live and station.actual_departure %}
      {% set is_current = station.is_current_station or (current_station_index is not none and loop.index0 == current_station_index_visible) %}
      {% set is_last_visible = loop.last and hidden_stops|length == 0 %}
      <div class="timeline-stop">
        <div class="timeline-track">
          <div class="timeline-dot {% if station.is_origin %}origin{% elif station.is_destination %}destination{% elif is_current %}current{% elif is_passed %}passed{% else %}upcoming{% endif %}"></div>
          {% if not is_last_visible %}
          <div class="timeline-line {% if is_passed %}passed{% endif %}"></div>
          {% endif %}
        </div>
        <div class="stop-info">
          <div class="stop-station">
            <span class="stop-station-name">{{ station.station_name }}</span>
            <span class="stop-station-code">{{ station.station_code }}</span>
            {% if station.platform %}
            <span class="stop-platform">PF {{ station.platform }}</span>
            {% endif %}
          </div>
          <div class="stop-details">
            {% if station.arrival_time and station.arrival_time != '--' %}
            <span class="stop-detail">Arr: <strong>{{ station.arrival_time }}</strong></span>
            <span class="stop-detail-sep">|</span>
            {% endif %}
            {% if station.departure_time and station.departure_time != '--' %}
            <span class="stop-detail">Dep: <strong>{{ station.departure_time }}</strong></span>
            <span class="stop-detail-sep">|</span>
            {% endif %}
            {% if station.halt_time %}
            <span class="halt-badge">{{ station.halt_time }}</span>
            <span class="stop-detail-sep">|</span>
            {% endif %}
            <span class="stop-detail">Day {{ station.day }}</span>
            {% if station.distance %}
            <span class="stop-detail-sep">|</span>
            <span class="distance-badge">{{ station.distance }} km</span>
            {% endif %}
          </div>
          {% if is_live %}
          <div class="stop-live-row">
            {% if station.actual_arrival %}
            <span class="stop-actual">Act Arr: {{ station.actual_arrival }}</span>
            {% endif %}
            {% if station.actual_departure %}
            <span class="stop-actual">Act Dep: {{ station.actual_departure }}</span>
            {% endif %}
            {% if station.delay_departure and station.delay_departure != '0' %}
            <span class="stop-delay late">{{ station.delay_departure }}</span>
            {% elif is_passed %}
            <span class="stop-delay ontime">On Time</span>
            {% endif %}
          </div>
          {% endif %}
        </div>
      </div>
      {% endfor %}

      {# Hidden stops (shown on click) #}
      {% if hidden_stops|length > 0 %}
      <div class="hidden-stops" id="hidden-stops-{{ instance_id }}">
        {% for station in hidden_stops %}
        {% set is_passed = is_live and station.actual_departure %}
        {% set is_current = station.is_current_station or (current_station_index is not none and (loop.index0 + visible_count) == current_station_index) %}
        {% set is_last = loop.last %}
        <div class="timeline-stop">
          <div class="timeline-track">
            <div class="timeline-dot {% if station.is_destination %}destination{% elif is_current %}current{% elif is_passed %}passed{% else %}upcoming{% endif %}"></div>
            {% if not is_last %}
            <div class="timeline-line {% if is_passed %}passed{% endif %}"></div>
            {% endif %}
          </div>
          <div class="stop-info">
            <div class="stop-station">
              <span class="stop-station-name">{{ station.station_name }}</span>
              <span class="stop-station-code">{{ station.station_code }}</span>
              {% if station.platform %}
              <span class="stop-platform">PF {{ station.platform }}</span>
              {% endif %}
            </div>
            <div class="stop-details">
              {% if station.arrival_time and station.arrival_time != '--' %}
              <span class="stop-detail">Arr: <strong>{{ station.arrival_time }}</strong></span>
              <span class="stop-detail-sep">|</span>
              {% endif %}
              {% if station.departure_time and station.departure_time != '--' %}
              <span class="stop-detail">Dep: <strong>{{ station.departure_time }}</strong></span>
              <span class="stop-detail-sep">|</span>
              {% endif %}
              {% if station.halt_time %}
              <span class="halt-badge">{{ station.halt_time }}</span>
              <span class="stop-detail-sep">|</span>
              {% endif %}
              <span class="stop-detail">Day {{ station.day }}</span>
              {% if station.distance %}
              <span class="stop-detail-sep">|</span>
              <span class="distance-badge">{{ station.distance }} km</span>
              {% endif %}
            </div>
            {% if is_live %}
            <div class="stop-live-row">
              {% if station.actual_arrival %}
              <span class="stop-actual">Act Arr: {{ station.actual_arrival }}</span>
              {% endif %}
              {% if station.actual_departure %}
              <span class="stop-actual">Act Dep: {{ station.actual_departure }}</span>
              {% endif %}
              {% if station.delay_departure and station.delay_departure != '0' %}
              <span class="stop-delay late">{{ station.delay_departure }}</span>
              {% elif is_passed %}
              <span class="stop-delay ontime">On Time</span>
              {% endif %}
            </div>
            {% endif %}
          </div>
        </div>
        {% endfor %}
      </div>
      {% endif %}
    </div>

    {% if hidden_stops|length > 0 %}
    <div class="show-more-wrapper">
      <button class="show-more-btn" onclick="var h=document.getElementById('hidden-stops-{{ instance_id }}');if(h.classList.contains('visible')){h.classList.remove('visible');this.textContent='Show All {{ total_stations }} Stations';}else{h.classList.add('visible');this.textContent='Show Less';}">
        Show All {{ total_stations }} Stations
      </button>
    </div>
    {% endif %}

    <div class="status-footer">
      <span>{{ total_stations }} stations {% if total_distance %} &middot; {{ total_distance }} km{% endif %}</span>
      {% if is_live %}
      <span class="live-tag">Live</span>
      {% else %}
      <span>Schedule only</span>
      {% endif %}
    </div>
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
    Renders train status into HTML with vertical timeline UI.

    Args:
        status_result: Train status data from service

    Returns:
        HTML string with rendered train status
    """
    import uuid

    if status_result.get("error"):
        error_msg = status_result.get("message", "Unknown error")
        return f"""
        <div style="font-family: Poppins, sans-serif; max-width: 400px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 12px; padding: 30px 20px; text-align: center; background: #fff;">
          <div style="font-size: 13px; font-weight: 500; color: #202020;">Unable to fetch train status</div>
          <div style="font-size: 11px; color: #868686; margin-top: 6px;">{error_msg}</div>
        </div>
        """

    instance_id = uuid.uuid4().hex[:8]
    all_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    stations = status_result.get("stations", [])

    # All stations behind "Show All" button
    visible_stops = []
    hidden_stops = stations

    current_station_index_visible = None

    template = _jinja_env.from_string(TRAIN_STATUS_TEMPLATE)
    return template.render(
        instance_id=instance_id,
        all_days=all_days,
        visible_stops=visible_stops,
        hidden_stops=hidden_stops,
        visible_count=len(visible_stops),
        total_stations=len(stations),
        current_station_index_visible=current_station_index_visible,
        **status_result,
    )


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
