from typing import Dict, Any, List
from jinja2 import Environment, BaseLoader, select_autoescape


_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)

# =====================================================================
# 1️⃣ LEGACY SIMPLE UI (BACKWARD COMPATIBLE – DO NOT BREAK)
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
{% else %}
<p>No flights available.</p>
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
          {{ f.origin }} → {{ f.destination }} • {{ f.stops }} stop{{ 's' if f.stops != 1 else '' }}
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

    {% if f.bookUrl %}
      <a href="{{ f.bookUrl }}" class="book-btn">Book</a>
    {% endif %}
  </div>
{% endfor %}
</div>
"""

# =====================================================================
# 3️⃣ NORMALIZER — REAL EMT JSON → UI MODEL
# =====================================================================
def _normalize_flight_for_ui(flight: Dict[str, Any]) -> Dict[str, Any]:
    legs: List[Dict[str, Any]] = flight.get("legs", [])
    if not legs:
        return {}

    first_leg = legs[0]
    last_leg = legs[-1]

    fare_options = flight.get("fare_options", [])
    lowest_fare = min(
        fare_options,
        key=lambda x: x.get("total_fare", float("inf")),
        default={}
    )

    return {
        "airline": first_leg.get("airline_name", "Airline"),
        "airlineCode": first_leg.get("airline_code", ""),
        "origin": first_leg.get("origin"),
        "destination": last_leg.get("destination"),
        "departureTime": first_leg.get("departure_time"),
        "arrivalTime": last_leg.get("arrival_time"),
        "duration": flight.get("journey_time"),
        "stops": flight.get("total_stops", 0),
        "price": lowest_fare.get("total_fare"),
        "bookUrl": flight.get("deepLink"),
    }

# =====================================================================
# 4️⃣ FINAL RENDERER (PURE, SAFE, COMPATIBLE)
# =====================================================================
def render_flight_results(flight_results: Dict[str, Any]) -> str:
    """
    Renders flight results into HTML.

    Priority:
    1. Real EMT JSON → EaseMyTrip React-parity UI
    2. Old structure → Legacy simple UI
    """

    # -------------------------------------------------
    # 🔥 CRITICAL FIX: unwrap real EMT response
    # -------------------------------------------------
    if "structured_content" in flight_results:
        flight_results = flight_results["structured_content"]

    outbound_flights = flight_results.get("outbound_flights", [])

    # -------------------------------------------------
    # React-parity path (real EMT data)
    # -------------------------------------------------
    flights_ui = [
        _normalize_flight_for_ui(f)
        for f in outbound_flights
        if f.get("legs")
    ]

    # Remove empty normalizations (safety)
    flights_ui = [f for f in flights_ui if f]

    if flights_ui:
        template = _jinja_env.from_string(FLIGHT_CAROUSEL_TEMPLATE)
        return template.render(flights=flights_ui)

    # -------------------------------------------------
    # Legacy fallback (DO NOT TOUCH)
    # -------------------------------------------------
    template = _jinja_env.from_string(FLIGHT_RESULTS_TEMPLATE)
    return template.render(
        outbound_flights=outbound_flights,
        return_flights=flight_results.get("return_flights", []),
        is_roundtrip=flight_results.get("is_roundtrip", False),
    )
