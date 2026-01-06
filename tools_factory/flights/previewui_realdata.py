import json
from flight_renderer import render_flight_results

# --------------------------
# Load your EMT flight search JSON
# --------------------------
with open("result.json", "r", encoding="utf-8") as f:
    flight_results = json.load(f)

# --------------------------
# Ensure outbound and return lists exist
# --------------------------
flight_results.setdefault("outbound_flights", [])
flight_results.setdefault("return_flights", [])

# Limit to 10 flights each if you want
flight_results["outbound_flights"] = flight_results["outbound_flights"][:10]
flight_results["return_flights"] = flight_results["return_flights"][:10]

# --------------------------
# Render HTML
# --------------------------
html_output = render_flight_results(flight_results)

# --------------------------
# Save to file for preview
# --------------------------
with open("preview_flights.html", "w", encoding="utf-8") as f:
    f.write(html_output)

print("✅ Preview HTML generated: preview_flights.html")
print(f"Outbound flights: {len(flight_results['outbound_flights'])}")
print(f"Return flights: {len(flight_results['return_flights'])}")
