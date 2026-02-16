"""Train Status HTML Renderer.

This module renders train status data into HTML using Jinja2 templates.
Uses vertical timeline UI consistent with the route check renderer.
"""

from typing import Dict, Any
from jinja2 import Environment, BaseLoader, select_autoescape
import uuid

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
  background: linear-gradient(90deg, #2093ef, #42b4ff);
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
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #fff;
  border: 2px solid #e0e0e0;
  z-index: 1;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.train-status .timeline-dot img {
  width: 12px;
  height: 12px;
}

.train-status .timeline-dot.origin {
  background: #2093ef;
  border-color: #2093ef;
}

.train-status .timeline-dot.destination {
  background: #d32f2f;
  border-color: #d32f2f;
}

.train-status .timeline-dot.passed {
  background: #2093ef;
  border-color: #2093ef;
}

.train-status .timeline-dot.current {
  background: #2093ef;
  border-color: #2093ef;
  box-shadow: 0 0 0 3px rgba(32, 147, 239, 0.2);
}

.train-status .timeline-dot.upcoming {
  background: #fff;
  border: 2px solid #e0e0e0;
}

.train-status .timeline-line {
  width: 2px;
  flex: 1;
  background: #e0e0e0;
  min-height: 20px;
}

.train-status .timeline-line.passed {
  background: #2093ef;
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

/* Not started banner */
.train-status .not-started-banner {
  padding: 10px 16px;
  background: #fff8e1;
  border-bottom: 1px solid #ffe082;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 500;
  color: #f57f17;
}

.train-status .not-started-banner .not-started-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ffa000;
  flex-shrink: 0;
}

</style>

<div class="train-status round-trip-selector" id="status-{{ instance_id }}">
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

    {% if not is_live or (is_live and current_station_index is none) %}
    <div class="not-started-banner">
      <span class="not-started-dot"></span>
      Train has not started yet
    </div>
    {% endif %}

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
          <div class="timeline-dot {% if station.is_origin %}origin{% elif station.is_destination %}destination{% elif is_current %}current{% elif is_passed %}passed{% else %}upcoming{% endif %}">
            {% if is_passed or (station.is_origin and is_live) %}
            <img src="https://railways.easemytrip.com/Content/Train/img/tick.svg" alt="">
            {% elif is_current %}
            <img src="https://railways.easemytrip.com/Content/Train/img/train.svg" alt="">
            {% endif %}
          </div>
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
            <div class="timeline-dot {% if station.is_destination %}destination{% elif is_current %}current{% elif is_passed %}passed{% else %}upcoming{% endif %}">
              {% if is_passed or (station.is_origin and is_live) %}
              <img src="https://railways.easemytrip.com/Content/Train/img/tick.svg" alt="">
              {% elif is_current %}
              <img src="https://railways.easemytrip.com/Content/Train/img/train.svg" alt="">
              {% endif %}
            </div>
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
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,100..900&family=Poppins:wght@300;400;500;600;700&display=swap');

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
  cursor: pointer;
  transition: all 0.2s ease;
}

.tdt-date-item:hover {
  border-color: #2093ef;
  background: #f0f7ff;
}

.tdt-date-item.loading {
  opacity: 0.6;
  pointer-events: none;
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

.tdt-loading-text {
  font-size: 12px;
  font-weight: 500;
  color: #2093ef;
}

.tdt-error {
  padding: 16px;
  text-align: center;
  color: #d32f2f;
  font-size: 13px;
}
</style>

<div class="train-dates-widget round-trip-selector" data-train-number="{{ train_number }}" id="train-dates-{{ instance_id }}">
  <div class="tdt-header">
    <div class="tdt-title">Train {{ train_number }}</div>
    <div class="tdt-subtitle">Select a date to check status</div>
  </div>

  <div class="tdt-dates">
    {% for date in available_dates %}
    <div class="tdt-date-item" data-date="{{ date.date }}">
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

<script>
(function() {
  var AUTOSUGGEST_URL = 'https://autosuggest.easemytrip.com/api/auto/train_name?useby=popularu&key=jNUYK0Yj5ibO6ZVIkfTiFA==';
  var LIVE_STATUS_URL = 'https://railways.easemytrip.com/TrainService/TrainLiveStatus';

  function parseRunningDays(str) {
    if (!str || str.length !== 7) return [];
    var days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
    var result = [];
    for (var i = 0; i < 7; i++) {
      if (str[i] === '1') result.push(days[i]);
    }
    return result;
  }

  function calcDuration(depTime, arrTime, depDay, arrDay) {
    if (!depTime || !arrTime || depTime === '--' || arrTime === '--') return '';
    try {
      var dp = depTime.split(':'), ap = arrTime.split(':');
      var depMin = parseInt(dp[0]) * 60 + parseInt(dp[1]);
      var arrMin = parseInt(ap[0]) * 60 + parseInt(ap[1]);
      var total = arrMin - depMin + (arrDay - depDay) * 1440;
      if (total < 0) total += 1440;
      var h = Math.floor(total / 60), m = total % 60;
      if (h >= 24) { var d = Math.floor(h / 24); h = h % 24; return d + 'd ' + h + 'h ' + m + 'm'; }
      return h + 'h ' + m + 'm';
    } catch(e) { return ''; }
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
      var p = dateStr.split('-');
      var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      var dayNames = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
      var dt = new Date(parseInt(p[2]), parseInt(p[1]) - 1, parseInt(p[0]));
      return p[0] + ' ' + months[parseInt(p[1]) - 1] + ' ' + p[2] + ', ' + dayNames[dt.getDay()];
    } catch(e) { return dateStr; }
  }

  function isValidTime(v) {
    if (!v || v.indexOf(':') === -1) return false;
    var p = v.split(':');
    if (p.length !== 2) return false;
    var h = parseInt(p[0]), m = parseInt(p[1]);
    return !isNaN(h) && !isNaN(m) && h >= 0 && h <= 23 && m >= 0 && m <= 59;
  }

  function processLiveStations(stations) {
    var result = [];
    var total = stations.length;
    for (var i = 0; i < total; i++) {
      var s = stations[i];
      var schArr = s.schArrTime || '';
      var schDep = s.schDepTime || '';
      var actArr = s.actArr || '';
      var actDep = s.actDep || '';
      var delayArr = s.delayArr || '';
      var delayDep = s.delayDep || '';
      var isOrigin = i === 0;
      var isDest = i === total - 1;
      var arrTime = (isOrigin || schArr === 'Source' || schArr === '00:00') ? '--' : schArr;
      var depTime = (isDest || schDep === '00:00') ? '--' : schDep;
      var halt = s.Halt || '--';
      result.push({
        station_code: s.stnCode || '',
        station_name: s.StationName || '',
        arrival_time: arrTime,
        departure_time: depTime,
        halt_time: (halt && halt !== '--') ? halt : null,
        day: parseInt(s.dayCnt || '1') || 1,
        distance: s.distance || '',
        platform: s.pfNo || null,
        is_origin: isOrigin,
        is_destination: isDest,
        actual_arrival: isValidTime(actArr) ? actArr : null,
        actual_departure: isValidTime(actDep) ? actDep : null,
        delay_arrival: delayArr || null,
        delay_departure: delayDep || null,
        is_current_station: !!s.isCurrentStation,
        is_next_station: !!s.isNextStation
      });
    }
    return result;
  }

  function processScheduleStations(stations) {
    var result = [];
    var total = stations.length;
    for (var i = 0; i < total; i++) {
      var s = stations[i];
      var isOrigin = i === 0;
      var isDest = i === total - 1;
      var arr = s.arrivalTime || '';
      var dep = s.departureTime || '';
      if (isOrigin || arr === '00:00') arr = '--';
      if (isDest || dep === '00:00') dep = '--';
      var halt = s.haltTime || '--';
      result.push({
        station_code: s.stationCode || '',
        station_name: s.stationName || '',
        arrival_time: arr,
        departure_time: dep,
        halt_time: (halt && halt !== '--') ? halt : null,
        day: parseInt(s.dayCount || '1') || 1,
        distance: s.distance || '',
        platform: s.plateform || null,
        is_origin: isOrigin,
        is_destination: isDest,
        actual_arrival: null,
        actual_departure: null,
        delay_arrival: null,
        delay_departure: null,
        is_current_station: false,
        is_next_station: false
      });
    }
    return result;
  }

  function buildStationHtml(station, isLive, isPassed, isCurrent, isLast) {
    var dotClass = 'upcoming';
    if (station.is_origin) dotClass = 'origin';
    else if (station.is_destination) dotClass = 'destination';
    else if (isCurrent) dotClass = 'current';
    else if (isPassed) dotClass = 'passed';

    var dotIcon = '';
    if (isPassed || (station.is_origin && isLive)) {
      dotIcon = '<img src="https://railways.easemytrip.com/Content/Train/img/tick.svg" alt="">';
    } else if (isCurrent) {
      dotIcon = '<img src="https://railways.easemytrip.com/Content/Train/img/train.svg" alt="">';
    }

    var lineClass = isPassed ? 'passed' : '';
    var linePart = isLast ? '' : '<div class="timeline-line ' + lineClass + '"></div>';

    var details = '';
    if (station.arrival_time && station.arrival_time !== '--') {
      details += '<span class="stop-detail">Arr: <strong>' + station.arrival_time + '</strong></span><span class="stop-detail-sep">|</span>';
    }
    if (station.departure_time && station.departure_time !== '--') {
      details += '<span class="stop-detail">Dep: <strong>' + station.departure_time + '</strong></span><span class="stop-detail-sep">|</span>';
    }
    if (station.halt_time) {
      details += '<span class="halt-badge">' + station.halt_time + '</span><span class="stop-detail-sep">|</span>';
    }
    details += '<span class="stop-detail">Day ' + station.day + '</span>';
    if (station.distance) {
      details += '<span class="stop-detail-sep">|</span><span class="distance-badge">' + station.distance + ' km</span>';
    }

    var platformHtml = station.platform ? '<span class="stop-platform">PF ' + station.platform + '</span>' : '';

    var liveRow = '';
    if (isLive) {
      var liveParts = '';
      if (station.actual_arrival) liveParts += '<span class="stop-actual">Act Arr: ' + station.actual_arrival + '</span>';
      if (station.actual_departure) liveParts += '<span class="stop-actual">Act Dep: ' + station.actual_departure + '</span>';
      if (station.delay_departure && station.delay_departure !== '0') {
        liveParts += '<span class="stop-delay late">' + station.delay_departure + '</span>';
      } else if (isPassed) {
        liveParts += '<span class="stop-delay ontime">On Time</span>';
      }
      if (liveParts) liveRow = '<div class="stop-live-row">' + liveParts + '</div>';
    }

    return '<div class="timeline-stop">' +
      '<div class="timeline-track">' +
        '<div class="timeline-dot ' + dotClass + '">' + dotIcon + '</div>' +
        linePart +
      '</div>' +
      '<div class="stop-info">' +
        '<div class="stop-station">' +
          '<span class="stop-station-name">' + station.station_name + '</span>' +
          '<span class="stop-station-code">' + station.station_code + '</span>' +
          platformHtml +
        '</div>' +
        '<div class="stop-details">' + details + '</div>' +
        liveRow +
      '</div>' +
    '</div>';
  }

  function buildStatusHtml(data) {
    var id = 'ts-' + Math.random().toString(36).substr(2, 8);
    var allDays = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
    var runsOn = data.runs_on || [];
    var stations = data.stations || [];
    var isLive = data.is_live;
    var currentIdx = data.current_station_index;
    var totalStations = stations.length;
    var lastStation = stations[totalStations - 1];
    var totalDistance = lastStation ? lastStation.distance : '';

    var daysHtml = '';
    if (runsOn.length > 0) {
      daysHtml = '<div class="status-running-days">';
      for (var i = 0; i < allDays.length; i++) {
        var active = runsOn.indexOf(allDays[i]) !== -1 ? ' active' : '';
        daysHtml += '<span class="day-chip' + active + '">' + allDays[i] + '</span>';
      }
      daysHtml += '</div>';
    }

    var progressHtml = '';
    if (isLive && data.distance_percentage) {
      var currentInfo = '';
      if (currentIdx !== null && currentIdx !== undefined && stations[currentIdx]) {
        var cur = stations[currentIdx];
        var delayBadge = '';
        if (cur.delay_departure && cur.delay_departure !== '0') {
          var severeClass = cur.delay_departure.indexOf('H') !== -1 ? 'severe' : 'late';
          delayBadge = '<div class="delay-badge ' + severeClass + '">' + cur.delay_departure + '</div>';
        } else {
          delayBadge = '<div class="delay-badge ontime">On Time</div>';
        }
        var curDepTime = cur.actual_departure ? '<div class="current-stn-time">Dep: ' + cur.actual_departure + '</div>' : '';
        currentInfo = '<div class="current-station-row">' +
          '<div class="current-stn-icon"><img src="https://railways.easemytrip.com/Content/Train/img/train.svg" alt="Train"></div>' +
          '<div class="current-stn-info">' +
            '<div class="current-stn-label">Last at</div>' +
            '<div class="current-stn-name">' + cur.station_name + '</div>' +
            curDepTime +
          '</div>' +
          delayBadge +
        '</div>';
      }
      progressHtml = '<div class="live-progress">' +
        '<div class="progress-bar"><div class="progress-fill" style="width:' + data.distance_percentage + ';">' +
          '<div class="progress-train-icon"><img src="https://railways.easemytrip.com/Content/Train/img/train.svg" alt="Train"></div>' +
        '</div></div>' +
        currentInfo +
      '</div>';
    }

    var timelineHtml = '';
    for (var j = 0; j < totalStations; j++) {
      var st = stations[j];
      var isPassed = isLive && !!st.actual_departure;
      var isCurrent = st.is_current_station || (currentIdx !== null && currentIdx !== undefined && j === currentIdx);
      var isLast = j === totalStations - 1;
      timelineHtml += buildStationHtml(st, isLive, isPassed, isCurrent, isLast);
    }

    var showBtnHtml = totalStations > 0 ?
      '<div class="show-more-wrapper">' +
        '<button class="show-more-btn" onclick="var h=document.getElementById(\\'' + id + '-hidden\\');if(h.classList.contains(\\'visible\\')){h.classList.remove(\\'visible\\');this.textContent=\\'Show All ' + totalStations + ' Stations\\';}else{h.classList.add(\\'visible\\');this.textContent=\\'Show Less\\';}">Show All ' + totalStations + ' Stations</button>' +
      '</div>' : '';

    var footerLive = isLive ? '<span class="live-tag">Live</span>' : '<span>Schedule only</span>';

    var html = '<style>' +
      '@import url(\\'https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,100..900&family=Poppins:wght@300;400;500;600;700&display=swap\\');' +
      '.train-status{font-family:Poppins,sans-serif;color:#202020;background:#fff;max-width:400px;margin:0 auto}' +
      '.train-status *{font-family:inherit;box-sizing:border-box;margin:0;padding:0}' +
      '.train-status .status-card{border:1px solid #e0e0e0;border-radius:12px;overflow:hidden;background:#fff}' +
      '.train-status .status-header{padding:14px 16px;border-bottom:1px solid #e0e0e0}' +
      '.train-status .status-header-top{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}' +
      '.train-status .status-train-name{font-size:15px;font-weight:600;color:#202020;line-height:1.3}' +
      '.train-status .status-train-no{font-weight:500;font-size:13px;padding:3px 6px;color:#313131;background:#F2F9FF;border:1px solid #B6D5F0;border-radius:3px;white-space:nowrap}' +
      '.train-status .status-running-days{display:flex;gap:4px;margin-top:10px;flex-wrap:wrap}' +
      '.train-status .day-chip{font-size:10px;font-weight:500;padding:2px 6px;border-radius:4px;background:#f5f5f5;color:#888;border:1px solid #e0e0e0}' +
      '.train-status .day-chip.active{background:#e8f5e9;color:#2e7d32;border-color:#a5d6a7;font-weight:600}' +
      '.train-status .status-timing{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:12px}' +
      '.train-status .status-time-block{text-align:center;min-width:50px}' +
      '.train-status .status-time{font-size:18px;font-weight:600;color:#202020;font-family:Inter,sans-serif}' +
      '.train-status .status-stn-code{font-size:11px;color:#868686;margin-top:2px}' +
      '.train-status .status-duration-block{flex:1;text-align:center;position:relative}' +
      '.train-status .status-duration{font-size:11px;color:#646d74;margin-bottom:4px}' +
      '.train-status .status-duration-line{height:1px;background:#ccc;position:relative;margin:0 10px}' +
      '.train-status .status-duration-line::before,.train-status .status-duration-line::after{content:\\'\\';position:absolute;width:6px;height:6px;background:#ccc;border-radius:50%;top:50%;transform:translateY(-50%)}' +
      '.train-status .status-duration-line::before{left:-3px}' +
      '.train-status .status-duration-line::after{right:-3px}' +
      '.train-status .status-date{font-size:10px;color:#868686;margin-top:4px}' +
      '.train-status .live-progress{padding:12px 16px;background:#f8fafe;border-bottom:1px solid #e0e0e0}' +
      '.train-status .progress-bar{width:100%;height:6px;background:#e0e0e0;border-radius:3px;overflow:visible;position:relative;margin-bottom:10px}' +
      '.train-status .progress-fill{height:100%;background:linear-gradient(90deg,#2093ef,#42b4ff);border-radius:3px;position:relative}' +
      '.train-status .progress-train-icon{position:absolute;right:-12px;top:50%;transform:translateY(-50%);width:24px;height:24px;background:#2093ef;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 4px rgba(0,0,0,0.2)}' +
      '.train-status .progress-train-icon img{width:14px;height:14px}' +
      '.train-status .current-station-row{display:flex;align-items:center;gap:8px;padding:10px;background:#fff;border-radius:8px;border:1px solid #e8f4fd}' +
      '.train-status .current-stn-icon{width:32px;height:32px;background:#2093ef;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0}' +
      '.train-status .current-stn-icon img{width:18px;height:18px}' +
      '.train-status .current-stn-info{flex:1;min-width:0}' +
      '.train-status .current-stn-label{font-size:9px;text-transform:uppercase;color:#868686;letter-spacing:0.5px}' +
      '.train-status .current-stn-name{font-size:13px;font-weight:600;color:#202020;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}' +
      '.train-status .current-stn-time{font-size:11px;color:#646d74;margin-top:2px}' +
      '.train-status .delay-badge{padding:4px 8px;border-radius:4px;font-size:10px;font-weight:600;white-space:nowrap}' +
      '.train-status .delay-badge.late{background:#fff3e0;color:#e65100}' +
      '.train-status .delay-badge.severe{background:#ffebee;color:#c62828}' +
      '.train-status .delay-badge.ontime{background:#e8f5e9;color:#2e7d32}' +
      '.train-status .status-timeline{padding:16px}' +
      '.train-status .timeline-stop{display:flex;gap:12px;position:relative}' +
      '.train-status .timeline-track{display:flex;flex-direction:column;align-items:center;width:20px;flex-shrink:0}' +
      '.train-status .timeline-dot{width:20px;height:20px;border-radius:50%;background:#fff;border:2px solid #e0e0e0;z-index:1;flex-shrink:0;display:flex;align-items:center;justify-content:center}' +
      '.train-status .timeline-dot img{width:12px;height:12px}' +
      '.train-status .timeline-dot.origin{background:#2093ef;border-color:#2093ef}' +
      '.train-status .timeline-dot.destination{background:#d32f2f;border-color:#d32f2f}' +
      '.train-status .timeline-dot.passed{background:#2093ef;border-color:#2093ef}' +
      '.train-status .timeline-dot.current{background:#2093ef;border-color:#2093ef;box-shadow:0 0 0 3px rgba(32,147,239,0.2)}' +
      '.train-status .timeline-dot.upcoming{background:#fff;border:2px solid #e0e0e0}' +
      '.train-status .timeline-line{width:2px;flex:1;background:#e0e0e0;min-height:20px}' +
      '.train-status .timeline-line.passed{background:#2093ef}' +
      '.train-status .stop-info{flex:1;padding-bottom:18px;min-width:0}' +
      '.train-status .timeline-stop:last-child .stop-info{padding-bottom:0}' +
      '.train-status .stop-station{display:flex;align-items:center;gap:6px;flex-wrap:wrap}' +
      '.train-status .stop-station-name{font-size:13px;font-weight:600;color:#202020}' +
      '.train-status .stop-station-code{font-size:11px;font-weight:500;color:#1976d2;background:#e3f2fd;padding:1px 5px;border-radius:3px}' +
      '.train-status .stop-platform{font-size:10px;font-weight:500;padding:1px 5px;border-radius:3px;background:#f3e5f5;color:#7b1fa2}' +
      '.train-status .stop-details{display:flex;gap:6px;margin-top:4px;flex-wrap:wrap;align-items:center}' +
      '.train-status .stop-detail{font-size:11px;color:#646d74}' +
      '.train-status .stop-detail strong{color:#202020;font-weight:600}' +
      '.train-status .stop-detail-sep{color:#ccc;font-size:10px}' +
      '.train-status .halt-badge{font-size:10px;font-weight:500;padding:1px 5px;border-radius:3px;background:#fff3e0;color:#f57c00}' +
      '.train-status .distance-badge{font-size:10px;font-weight:500;padding:1px 5px;border-radius:3px;background:#f5f5f5;color:#666}' +
      '.train-status .stop-live-row{display:flex;gap:6px;margin-top:3px;align-items:center;flex-wrap:wrap}' +
      '.train-status .stop-actual{font-size:10px;color:#1976d2;font-weight:500}' +
      '.train-status .stop-delay{font-size:10px;font-weight:600;padding:1px 5px;border-radius:3px}' +
      '.train-status .stop-delay.late{background:#fff3e0;color:#e65100}' +
      '.train-status .stop-delay.ontime{background:#e8f5e9;color:#2e7d32}' +
      '.train-status .show-more-wrapper{padding:0 16px 16px;text-align:center}' +
      '.train-status .show-more-btn{width:100%;padding:8px 16px;background:#fff;color:#1976d2;border:1px solid #bbdefb;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;font-family:Poppins,sans-serif;transition:all 0.2s ease}' +
      '.train-status .show-more-btn:hover{background:#e3f2fd;border-color:#1976d2}' +
      '.train-status .hidden-stops{display:none}' +
      '.train-status .hidden-stops.visible{display:block}' +
      '.train-status .status-footer{padding:10px 16px;border-top:1px solid #e0e0e0;display:flex;justify-content:space-between;align-items:center;font-size:11px;color:#646d74}' +
      '.train-status .status-footer strong{color:#202020}' +
      '.train-status .status-footer .live-tag{font-size:10px;font-weight:600;color:#1565c0;background:#e3f2fd;padding:2px 8px;border-radius:4px}' +
      '.train-status .not-started-banner{padding:10px 16px;background:#fff8e1;border-bottom:1px solid #ffe082;display:flex;align-items:center;gap:8px;font-size:12px;font-weight:500;color:#f57f17}' +
      '.train-status .not-started-banner .not-started-dot{width:8px;height:8px;border-radius:50%;background:#ffa000;flex-shrink:0}' +
    '</style>' +
    '<div class="train-status" id="status-' + id + '">' +
      '<div class="status-card">' +
        '<div class="status-header">' +
          '<div class="status-header-top">' +
            '<div class="status-train-name">' + data.train_name + '</div>' +
            '<div class="status-train-no">' + data.train_number + '</div>' +
          '</div>' +
          daysHtml +
          '<div class="status-timing">' +
            '<div class="status-time-block">' +
              '<div class="status-time">' + data.departure_time + '</div>' +
              '<div class="status-stn-code">' + data.origin_code + '</div>' +
            '</div>' +
            '<div class="status-duration-block">' +
              (data.journey_duration ? '<div class="status-duration">' + data.journey_duration + '</div>' : '') +
              '<div class="status-duration-line"></div>' +
              '<div class="status-date">' + data.formatted_date + '</div>' +
            '</div>' +
            '<div class="status-time-block">' +
              '<div class="status-time">' + data.arrival_time + '</div>' +
              '<div class="status-stn-code">' + data.destination_code + '</div>' +
            '</div>' +
          '</div>' +
        '</div>' +
        (!isLive || (isLive && currentIdx === null) ? '<div class="not-started-banner"><span class="not-started-dot"></span>Train has not started yet</div>' : '') +
        progressHtml +
        '<div class="status-timeline">' +
          '<div class="hidden-stops visible" id="' + id + '-hidden">' + timelineHtml + '</div>' +
        '</div>' +
        showBtnHtml +
        '<div class="status-footer">' +
          '<span>' + totalStations + ' stations' + (totalDistance ? ' &middot; ' + totalDistance + ' km' : '') + '</span>' +
          footerLive +
        '</div>' +
      '</div>' +
    '</div>';

    return html;
  }

  async function fetchTrainStatus(el) {
    var widget = el.closest('.train-dates-widget');
    var trainNumber = widget.dataset.trainNumber;
    var dateStr = el.dataset.date;

    el.classList.add('loading');
    var displayEl = el.querySelector('.tdt-date-display');
    var prevDisplay = displayEl ? displayEl.textContent : '';
    if (displayEl) {
      displayEl.textContent = 'Loading...';
      displayEl.style.display = 'inline-block';
    } else {
      var loadEl = document.createElement('span');
      loadEl.className = 'tdt-loading-text';
      loadEl.textContent = 'Loading...';
      el.appendChild(loadEl);
    }

    try {
      var apiDate = dateStr.replace(/-/g, '/');

      var autoRes = await fetch(AUTOSUGGEST_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request: trainNumber })
      });
      var autoData = await autoRes.json();

      var trainName = '', trainNo = trainNumber, srcCode = '', destCode = '';
      if (autoData && autoData.length > 0) {
        trainName = autoData[0].TrainName || '';
        trainNo = autoData[0].TrainNo || trainNumber;
        srcCode = autoData[0].SrcStnCode || '';
        destCode = autoData[0].DestStnCode || '';
      }

      var trainIdentifier = trainNo + (trainName ? '-' + trainName : '');

      var statusRes = await fetch(LIVE_STATUS_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          TrainNo: trainIdentifier,
          selectedDate: apiDate,
          Srchtype: '',
          fromSrc: srcCode,
          DestStnCode: destCode
        })
      });
      var statusData = await statusRes.json();

      if (statusData.ErrorMessage) {
        widget.innerHTML = '<div class="tdt-error">' + statusData.ErrorMessage + '</div>';
        return;
      }

      var trainDetails = statusData._TrainDetails || {};
      var isLive = false;
      var stations = [];

      var liveStations = statusData.LiveStationList || [];
      if (liveStations.length > 0) {
        stations = processLiveStations(liveStations);
        isLive = true;
      } else {
        var scheduleList = statusData.trainScheduleList || {};
        var stationList = scheduleList.stationList || [];
        stations = processScheduleStations(stationList);
      }

      if (stations.length === 0) {
        widget.innerHTML = '<div class="tdt-error">No station information available</div>';
        return;
      }

      var origin = stations[0];
      var destination = stations[stations.length - 1];
      var runsOn = parseRunningDays(trainDetails.Running_Days || '');
      var duration = calcDuration(origin.departure_time, destination.arrival_time, origin.day, destination.day);
      var formattedDate = formatDate(dateStr);

      var currentIdx = null;
      var lastDepartedIdx = null;
      for (var k = 0; k < stations.length; k++) {
        if (stations[k].is_current_station) currentIdx = k;
        if (stations[k].actual_departure) lastDepartedIdx = k;
      }
      if (currentIdx === null && lastDepartedIdx !== null) currentIdx = lastDepartedIdx;

      var data = {
        train_number: trainDetails.TrainNo || trainNo,
        train_name: trainDetails.TrainName || trainName || (origin.station_name + ' - ' + destination.station_name + ' Express'),
        runs_on: runsOn,
        origin_code: origin.station_code,
        destination_code: destination.station_code,
        departure_time: origin.departure_time || '--',
        arrival_time: destination.arrival_time || '--',
        journey_duration: duration,
        formatted_date: formattedDate,
        stations: stations,
        is_live: isLive,
        distance_percentage: statusData.distancePercentage || '',
        current_station_index: currentIdx
      };

      widget.outerHTML = buildStatusHtml(data);

    } catch (error) {
      console.error('Error fetching train status:', error);
      el.classList.remove('loading');
      if (displayEl) {
        displayEl.textContent = prevDisplay || '';
        if (!prevDisplay) displayEl.style.display = '';
      } else {
        var loadingEl = el.querySelector('.tdt-loading-text');
        if (loadingEl) loadingEl.remove();
      }
      var errDiv = widget.querySelector('.tdt-error');
      if (!errDiv) {
        errDiv = document.createElement('div');
        errDiv.className = 'tdt-error';
        widget.appendChild(errDiv);
      }
      errDiv.textContent = 'Failed to fetch status. Please try again.';
    }
  }

  document.querySelectorAll('.tdt-date-item').forEach(function(item) {
    item.addEventListener('click', function() {
      fetchTrainStatus(this);
    });
  });
})();
</script>
"""


def render_train_status_results(status_result: Dict[str, Any]) -> str:
    """
    Renders train status into HTML with vertical timeline UI.

    Args:
        status_result: Train status data from service

    Returns:
        HTML string with rendered train status
    """
    

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
    
    instance_id = uuid.uuid4().hex[:8]
    template = _jinja_env.from_string(TRAIN_DATES_TEMPLATE)
    return template.render( instance_id=instance_id,**dates_result)
