from typing import Dict, Any, Callable, Optional
from jinja2 import Environment, BaseLoader, select_autoescape

# -----------------------------------
# Jinja environment
# -----------------------------------
_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)

# =====================================================================
# 1️⃣ LEGACY SIMPLE UI (UNCHANGED – BACKWARD COMPATIBLE)
# =====================================================================
FLIGHT_RESULTS_TEMPLATE = """
<style>
.flight-results {
    font-family: Arial, sans-serif;
    background-color: #f8f8f8;
    padding: 15px;
    border-radius: 8px;
    max-width: 600px;
}
.flight-results h3 {
    color: #1a73e8;
}
.flight-results ul {
    list-style: none;
    padding: 0;
}
.flight-results li {
    background: #fff;
    padding: 10px;
    margin-bottom: 8px;
    border-radius: 6px;
}
.price {
    color: #0b8043;
    font-weight: bold;
}
.book-btn {
    display: inline-block;
    margin-top: 6px;
    background: #1a73e8;
    color: #fff;
    padding: 4px 10px;
    border-radius: 4px;
    text-decoration: none;
}
</style>

<div class="flight-results">
{% if outbound_flights %}
<h3>Outbound Flights</h3>
<ul>
{% for f in outbound_flights %}
<li>
<strong>{{ f.origin }} → {{ f.destination }}</strong><br/>
Stops: {{ f.total_stops }} | Duration: {{ f.journey_time }}<br/>
{% if f.fare_options %}
<span class="price">₹{{ f.fare_options[0].total_fare }}</span><br/>
{% endif %}
<a href="#" class="book-btn">Book</a>
</li>
{% endfor %}
</ul>
{% endif %}
</div>
"""

# =====================================================================
# 2️⃣ EASEMYTRIP REACT-PARITY UI (PRIMARY)
# =====================================================================
FLIGHT_CAROUSEL_TEMPLATE = """
<style>
.flight-carousel {
  font-family: Inter, Arial, sans-serif;
  background: #f4f6f9;
  padding: 12px;
}

.flight-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.flight-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.airline {
  font-size: 14px;
  font-weight: 600;
}

.route {
  font-size: 12px;
  color: #666;
}

.time {
  font-size: 16px;
  font-weight: 600;
}

.flight-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.meta {
  font-size: 12px;
  color: #666;
}

.price {
  font-size: 18px;
  font-weight: 700;
  color: #0b8043;
}

.book-btn {
  margin-top: 10px;
  display: inline-block;
  background: #ef6614;
  color: #fff;
  padding: 6px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
}
</style>

<div class="flight-carousel">
{% for f in flights %}
  <div class="flight-card">
    <div class="flight-top">
      <div>
        <div class="airline">{{ f.airline }} ({{ f.airlineCode }})</div>
        <div class="route">
          {{ f.origin }} → {{ f.destination }} • {{ f.stops }}
        </div>
      </div>
      <div class="time">
        {{ f.departureTime }} – {{ f.arrivalTime }}
      </div>
    </div>

    <div class="flight-bottom">
      <div class="meta">Duration: {{ f.duration }}</div>
      <div class="price">₹{{ f.price }}</div>
    </div>

    <a href="{{ f.bookUrl }}" class="book-btn">Book</a>
  </div>
{% endfor %}
</div>
"""

# =====================================================================
# 3️⃣ FINAL RENDERER (SAFE, COMPATIBLE, DETERMINISTIC)
# =====================================================================
def render_flight_results(
    flight_results: Dict[str, Any],
    extract_segments_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    build_deep_link_fn: Optional[Callable[[Dict[str, Any]], str]] = None,
) -> str:
    """
    Renders flight results.

    - If helpers are provided → React-parity EaseMyTrip UI
    - Else → legacy simple UI (unchanged)
    """

    # -------------------------------
    # React-style UI path
    # -------------------------------
    if extract_segments_fn and build_deep_link_fn:
        flights_ui = []

        for flight in flight_results.get("outbound_flights", []):
            seg = extract_segments_fn(flight)

            flights_ui.append({
                "airline": seg.get("airline", "Airline"),
                "airlineCode": seg.get("airline_code", ""),
                "origin": seg.get("origin"),
                "destination": seg.get("destination"),
                "departureTime": seg.get("departure_time"),
                "arrivalTime": seg.get("arrival_time"),
                "duration": seg.get("duration"),
                "stops": seg.get("stops"),
                "price": flight.get("fare_options", [{}])[0].get("total_fare"),
                "bookUrl": build_deep_link_fn(flight),
            })

        template = _jinja_env.from_string(FLIGHT_CAROUSEL_TEMPLATE)
        return template.render(flights=flights_ui)

    # -------------------------------
    # Legacy fallback UI
    # -------------------------------
    template = _jinja_env.from_string(FLIGHT_RESULTS_TEMPLATE)
    return template.render(
        outbound_flights=flight_results.get("outbound_flights", []),
        return_flights=flight_results.get("return_flights", []),
        is_roundtrip=flight_results.get("is_roundtrip", False),
    )
