from tools_factory.flights.flight_renderer import render_flight_results

# Sample flight data
sample_flights = {
    "outbound_flights": [
        {
            "origin": "DEL",
            "destination": "BOM",
            "total_stops": 1,
            "journey_time": "2h 15m",
            "fare_options": [{"total_fare": 4500}],
        },
        {
            "origin": "DEL",
            "destination": "BOM",
            "total_stops": 0,
            "journey_time": "2h 0m",
            "fare_options": [{"total_fare": 5000}],
        },
    ],
    "return_flights": [
        {
            "origin": "BOM",
            "destination": "DEL",
            "total_stops": 0,
            "journey_time": "2h 5m",
            "fare_options": [{"total_fare": 4700}],
        }
    ],
    "is_roundtrip": True,
}

# Render HTML
html_output = render_flight_results(sample_flights)

# Save to file to view in browser
with open("flight_ui_test.html", "w", encoding="utf-8") as f:
    f.write(html_output)

print("HTML generated in flight_ui_test.html! Open it in browser to see UI.")
