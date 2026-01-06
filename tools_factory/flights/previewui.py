"""
previewui.py
Standalone script to preview EaseMyTrip-style combined flight UI.
Generates 'flight_ui_preview.html' with full styling.
"""

from flight_renderer import render_flight_results

# ----------------------------
# Mock helper functions
# ----------------------------

def mock_extract_segments(flight):
    """
    Returns UI-ready flight segments for a single leg.
    """
    return {
        "airline": flight.get("airline", "IndiGo"),
        "origin": flight.get("origin", "DEL"),
        "destination": flight.get("destination", "BOM"),
        "departure_time": flight.get("departure_time", "06:30"),
        "arrival_time": flight.get("arrival_time", "08:45"),
        "duration": flight.get("journey_time", "2h 15m"),
        "stops": flight.get("total_stops", 0),
    }

def mock_build_deep_link(flight):
    """
    Returns a dummy flight booking URL.
    """
    return flight.get("book_url", "https://www.easemytrip.com/flight-booking/")

# ----------------------------
# Mock flight data (full round-trip)
# ----------------------------

# Each item is a **combined card**: outbound + return
flight_results = {
    "is_roundtrip": True,
    "outbound_flights": [
        {
            "origin": "DEL",
            "destination": "BOM",
            "departure_time": "06:30",
            "arrival_time": "08:45",
            "journey_time": "2h 15m",
            "total_stops": 0,
            "fare_options": [{"total_fare": 5249}],
            "airline": "IndiGo",
            "book_url": "https://www.easemytrip.com/flight-booking/1",
        },
    ],
    "return_flights": [
        {
            "origin": "BOM",
            "destination": "DEL",
            "departure_time": "17:00",
            "arrival_time": "19:15",
            "journey_time": "2h 15m",
            "total_stops": 0,
            "fare_options": [{"total_fare": 5249}],
            "airline": "IndiGo",
            "book_url": "https://www.easemytrip.com/flight-booking/1",
        },
    ],
}

# ----------------------------
# Combined UI generation
# ----------------------------

def combined_cards(flight_results):
    """
    Generate combined outbound + return cards for round-trip.
    """
    cards = []
    outbound = flight_results.get("outbound_flights", [])
    return_flights = flight_results.get("return_flights", [])

    # Pair outbound and return flights by index
    max_len = max(len(outbound), len(return_flights))
    for i in range(max_len):
        ob = outbound[i] if i < len(outbound) else None
        ret = return_flights[i] if i < len(return_flights) else None

        cards.append({
            "outbound": mock_extract_segments(ob) if ob else None,
            "return": mock_extract_segments(ret) if ret else None,
            "price": (ob.get("fare_options")[0]["total_fare"] if ob else 0) +
                     (ret.get("fare_options")[0]["total_fare"] if ret else 0),
            "book_url": mock_build_deep_link(ob or ret),
        })
    return cards

# ----------------------------
# Jinja template for combined card
# ----------------------------

from jinja2 import Environment, BaseLoader, select_autoescape

jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)

COMBINED_CARD_TEMPLATE = """
<style>
.flight-combined-carousel {
    font-family: Inter, Arial, sans-serif;
    background: #f4f6f9;
    padding: 12px;
    border-radius: 10px;
}
.flight-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.flight-leg {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
}
.airline {
    font-weight: 600;
    font-size: 14px;
}
.time {
    font-size: 16px;
    font-weight: 600;
}
.meta {
    font-size: 12px;
    color: #666;
}
.price {
    color: #0b8043;
    font-weight: 700;
    font-size: 16px;
}
.book {
    margin-top: 8px;
    display: inline-block;
    background: #ef6614;
    color: white;
    padding: 6px 14px;
    border-radius: 6px;
    text-decoration: none;
    font-size: 14px;
}
</style>

<div class="flight-combined-carousel">
  {% for card in cards %}
    <div class="flight-card">
      {% if card.outbound %}
      <div class="flight-leg">
        <div>
          <div class="airline">{{ card.outbound.airline }} (Outbound)</div>
          <div class="meta">{{ card.outbound.origin }} → {{ card.outbound.destination }} | {{ card.outbound.stops }} stop(s)</div>
        </div>
        <div class="time">{{ card.outbound.departure_time }} – {{ card.outbound.arrival_time }}</div>
      </div>
      {% endif %}

      {% if card.return %}
      <div class="flight-leg">
        <div>
          <div class="airline">{{ card.return.airline }} (Return)</div>
          <div class="meta">{{ card.return.origin }} → {{ card.return.destination }} | {{ card.return.stops }} stop(s)</div>
        </div>
        <div class="time">{{ card.return.departure_time }} – {{ card.return.arrival_time }}</div>
      </div>
      {% endif %}

      <div class="flight-leg" style="margin-top:6px;">
        <div class="meta">Total Duration: 
          {% if card.outbound %}{{ card.outbound.duration }}{% endif %} 
          {% if card.return %}+ {{ card.return.duration }}{% endif %}
        </div>
        <div class="price">₹{{ card.price }}</div>
      </div>

      <a href="{{ card.book_url }}" class="book">Book</a>
    </div>
  {% endfor %}
</div>
"""

# ----------------------------
# Render combined cards
# ----------------------------
cards = combined_cards(flight_results)
template = jinja_env.from_string(COMBINED_CARD_TEMPLATE)
html_content = template.render(cards=cards)

# ----------------------------
# Write HTML to file
# ----------------------------
output_file = "new_ui_preview.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Flight preview HTML generated: {output_file}")
print("Open this file in a browser to see the combined UI preview.")
