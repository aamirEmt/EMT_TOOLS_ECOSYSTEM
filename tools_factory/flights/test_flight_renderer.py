from flight_renderer import render_flight_results  # import your renderer

# --------------------------
# Mock flight data (sample)
# --------------------------
flight_results = {
    "outbound_flights": [
        {
            "origin": "DEL",
            "destination": "BOM",
            "total_stops": 1,
            "journey_time": "2h 30m",
            "fare_options": [{"total_fare": 4500}],
        },
        {
            "origin": "DEL",
            "destination": "BOM",
            "total_stops": 0,
            "journey_time": "2h 15m",
            "fare_options": [{"total_fare": 5200}],
        },
    ],
    "return_flights": [
        {
            "origin": "BOM",
            "destination": "DEL",
            "total_stops": 1,
            "journey_time": "2h 35m",
            "fare_options": [{"total_fare": 4800}],
        }
    ],
    "is_roundtrip": True,
}

# --------------------------
# Render HTML
# --------------------------
html_output = render_flight_results(flight_results)

# --------------------------
# Save to file
# --------------------------
with open("flight_results_test.html", "w", encoding="utf-8") as f:
    f.write(html_output)

print("✅ HTML file generated: flight_results_test.html")
print("Open this file in your browser to see the UI.")
