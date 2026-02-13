"""Train Route Check HTML Renderer - Vertical timeline UI for train route/schedule."""

from typing import Dict, Any, List
from jinja2 import Environment, BaseLoader, select_autoescape


# Initialize Jinja2 environment
_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)


ROUTE_CHECK_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,100..900&family=Poppins:wght@300;400;500;600;700&display=swap');

.train-route {
  font-family: Poppins, sans-serif;
  color: #202020;
  background: #fff;
  max-width: 400px;
  margin: 0 auto;
}

.train-route * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.train-route .route-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}

/* Header */
.train-route .route-header {
  padding: 14px 16px;
  border-bottom: 1px solid #e0e0e0;
}

.train-route .route-header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.train-route .route-train-name {
  font-size: 15px;
  font-weight: 600;
  color: #202020;
  line-height: 1.3;
}

.train-route .route-train-no {
  font-weight: 500;
  font-size: 13px;
  padding: 3px 6px;
  color: #313131;
  background: #F2F9FF;
  border: 1px solid #B6D5F0;
  border-radius: 3px;
  white-space: nowrap;
}

.train-route .route-running-days {
  display: flex;
  gap: 4px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.train-route .day-chip {
  font-size: 10px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
  background: #f5f5f5;
  color: #888;
  border: 1px solid #e0e0e0;
}

.train-route .day-chip.active {
  background: #e8f5e9;
  color: #2e7d32;
  border-color: #a5d6a7;
  font-weight: 600;
}

/* Timeline */
.train-route .route-timeline {
  padding: 16px;
}

.train-route .timeline-stop {
  display: flex;
  gap: 12px;
  position: relative;
}

/* Timeline line connecting dots */
.train-route .timeline-track {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20px;
  flex-shrink: 0;
}

.train-route .timeline-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #fff;
  border: 3px solid #1976d2;
  z-index: 1;
  flex-shrink: 0;
}

.train-route .timeline-dot.first {
  background: #1976d2;
  border-color: #1976d2;
}

.train-route .timeline-dot.last {
  background: #1976d2;
  border-color: #1976d2;
}

.train-route .timeline-line {
  width: 2px;
  flex: 1;
  background: #bbdefb;
  min-height: 20px;
}

/* Station info */
.train-route .stop-info {
  flex: 1;
  padding-bottom: 18px;
  min-width: 0;
}

.train-route .timeline-stop:last-child .stop-info {
  padding-bottom: 0;
}

.train-route .stop-station {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.train-route .stop-station-name {
  font-size: 13px;
  font-weight: 600;
  color: #202020;
}

.train-route .stop-station-code {
  font-size: 11px;
  font-weight: 500;
  color: #1976d2;
  background: #e3f2fd;
  padding: 1px 5px;
  border-radius: 3px;
}

.train-route .stop-details {
  display: flex;
  gap: 6px;
  margin-top: 4px;
  flex-wrap: wrap;
  align-items: center;
}

.train-route .stop-detail {
  font-size: 11px;
  color: #646d74;
}

.train-route .stop-detail strong {
  color: #202020;
  font-weight: 600;
}

.train-route .stop-detail-sep {
  color: #ccc;
  font-size: 10px;
}

.train-route .halt-badge {
  font-size: 10px;
  font-weight: 500;
  padding: 1px 5px;
  border-radius: 3px;
  background: #fff3e0;
  color: #f57c00;
}

.train-route .distance-badge {
  font-size: 10px;
  font-weight: 500;
  padding: 1px 5px;
  border-radius: 3px;
  background: #f5f5f5;
  color: #666;
}

/* Show more button */
.train-route .show-more-wrapper {
  padding: 0 16px 16px;
  text-align: center;
}

.train-route .show-more-btn {
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

.train-route .show-more-btn:hover {
  background: #e3f2fd;
  border-color: #1976d2;
}

/* Route summary footer */
.train-route .route-footer {
  padding: 10px 16px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #646d74;
}

.train-route .route-footer strong {
  color: #202020;
}

/* Hidden stops */
.train-route .hidden-stops {
  display: none;
}

.train-route .hidden-stops.visible {
  display: block;
}
</style>

<div class="train-route" id="route-{{ instance_id }}">
  <div class="route-card">
    <div class="route-header">
      <div class="route-header-top">
        <div class="route-train-name">{{ train_name }}</div>
        <div class="route-train-no">{{ train_no }}</div>
      </div>
      <div class="route-running-days">
        {% for day in all_days %}
        <span class="day-chip {{ 'active' if day in running_days else '' }}">{{ day }}</span>
        {% endfor %}
      </div>
    </div>

    <div class="route-timeline">
      {# First 5 stops (always visible) #}
      {% for stop in visible_stops %}
      <div class="timeline-stop">
        <div class="timeline-track">
          <div class="timeline-dot {{ 'first' if loop.first else ('last' if loop.last and hidden_stops|length == 0 else '') }}"></div>
          {% if not (loop.last and hidden_stops|length == 0) %}
          <div class="timeline-line"></div>
          {% endif %}
        </div>
        <div class="stop-info">
          <div class="stop-station">
            <span class="stop-station-name">{{ stop.station_name }}</span>
            <span class="stop-station-code">{{ stop.station_code }}</span>
          </div>
          <div class="stop-details">
            {% if stop.arrival_time != '--' %}
            <span class="stop-detail">Arr: <strong>{{ stop.arrival_time }}</strong></span>
            <span class="stop-detail-sep">|</span>
            {% endif %}
            {% if stop.departure_time != '--' %}
            <span class="stop-detail">Dep: <strong>{{ stop.departure_time }}</strong></span>
            <span class="stop-detail-sep">|</span>
            {% endif %}
            {% if stop.halt_time != '--' %}
            <span class="halt-badge">Halt: {{ format_halt(stop.halt_time) }}</span>
            <span class="stop-detail-sep">|</span>
            {% endif %}
            <span class="stop-detail">Day {{ stop.day_count }}</span>
            <span class="stop-detail-sep">|</span>
            <span class="distance-badge">{{ stop.distance }} km</span>
          </div>
        </div>
      </div>
      {% endfor %}

      {# Hidden stops (shown on click) #}
      {% if hidden_stops|length > 0 %}
      <div class="hidden-stops" id="hidden-stops-{{ instance_id }}">
        {% for stop in hidden_stops %}
        <div class="timeline-stop">
          <div class="timeline-track">
            <div class="timeline-dot {{ 'last' if loop.last else '' }}"></div>
            {% if not loop.last %}
            <div class="timeline-line"></div>
            {% endif %}
          </div>
          <div class="stop-info">
            <div class="stop-station">
              <span class="stop-station-name">{{ stop.station_name }}</span>
              <span class="stop-station-code">{{ stop.station_code }}</span>
            </div>
            <div class="stop-details">
              {% if stop.arrival_time != '--' %}
              <span class="stop-detail">Arr: <strong>{{ stop.arrival_time }}</strong></span>
              <span class="stop-detail-sep">|</span>
              {% endif %}
              {% if stop.departure_time != '--' %}
              <span class="stop-detail">Dep: <strong>{{ stop.departure_time }}</strong></span>
              <span class="stop-detail-sep">|</span>
              {% endif %}
              {% if stop.halt_time != '--' %}
              <span class="halt-badge">Halt: {{ format_halt(stop.halt_time) }}</span>
              <span class="stop-detail-sep">|</span>
              {% endif %}
              <span class="stop-detail">Day {{ stop.day_count }}</span>
              <span class="stop-detail-sep">|</span>
              <span class="distance-badge">{{ stop.distance }} km</span>
            </div>
          </div>
        </div>
        {% endfor %}
      </div>
      {% endif %}
    </div>

    {% if hidden_stops|length > 0 %}
    <div class="show-more-wrapper">
      <button class="show-more-btn" id="show-more-btn-{{ instance_id }}" onclick="toggleStops_{{ instance_id }}()">
        Show All {{ total_stops }} Stops
      </button>
    </div>
    {% endif %}

    <div class="route-footer">
      <span>Total Stops: <strong>{{ total_stops }}</strong></span>
      {% if total_distance %}
      <span>Distance: <strong>{{ total_distance }} km</strong></span>
      {% endif %}
    </div>
  </div>
</div>

<script>
(function() {
  var expanded = false;
  window['toggleStops_{{ instance_id }}'] = function() {
    var hiddenEl = document.getElementById('hidden-stops-{{ instance_id }}');
    var btnEl = document.getElementById('show-more-btn-{{ instance_id }}');
    if (!hiddenEl || !btnEl) return;

    expanded = !expanded;
    if (expanded) {
      hiddenEl.classList.add('visible');
      btnEl.textContent = 'Show Less';
    } else {
      hiddenEl.classList.remove('visible');
      btnEl.textContent = 'Show All {{ total_stops }} Stops';
    }
  };
})();
</script>
"""


def _format_halt_time(halt_str: str) -> str:
    """Convert halt time from MM:SS format to readable format (e.g., '05:00' -> '5 min')."""
    if not halt_str or halt_str == "--":
        return halt_str
    try:
        parts = halt_str.split(":")
        minutes = int(parts[0])
        return f"{minutes} min"
    except (ValueError, IndexError):
        return halt_str


_jinja_env.globals["format_halt"] = _format_halt_time


def render_route_check(
    train_info: Dict[str, Any],
    station_list: List[Dict[str, Any]],
    running_days: List[str],
) -> str:
    """
    Render train route as HTML vertical timeline.

    Args:
        train_info: Dictionary containing train_no and train_name
        station_list: List of station stop dictionaries
        running_days: List of running day strings (e.g., ["Mon", "Tue", ...])

    Returns:
        HTML string with rendered route timeline
    """
    import uuid

    instance_id = uuid.uuid4().hex[:8]

    all_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Split into visible (first 5) and hidden (rest)
    visible_stops = station_list[:5]
    hidden_stops = station_list[5:]

    # Get total distance from last station
    total_distance = ""
    if station_list:
        last_station = station_list[-1]
        total_distance = last_station.get("distance", "")

    template = _jinja_env.from_string(ROUTE_CHECK_TEMPLATE)

    return template.render(
        instance_id=instance_id,
        train_name=train_info.get("train_name", "Unknown Train"),
        train_no=train_info.get("train_no", ""),
        all_days=all_days,
        running_days=running_days,
        visible_stops=visible_stops,
        hidden_stops=hidden_stops,
        total_stops=len(station_list),
        total_distance=total_distance,
    )
