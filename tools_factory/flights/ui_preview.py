from flight_renderer import render_flight_results

# ---- mock data (matches your real structure) ----
mock_flight_results = {
    "is_roundtrip": False,
    "outbound_flights": [
        {
            "origin": "DEL",
            "destination": "BOM",
            "total_stops": 0,
            "journey_time": "2h 15m",
            "fare_options": [{"total_fare": 5499}],
        },
        {
            "origin": "DEL",
            "destination": "BLR",
            "total_stops": 1,
            "journey_time": "3h 40m",
            "fare_options": [{"total_fare": 6899}],
        },
    ],
    "return_flights": [],
}

html = render_flight_results(mock_flight_results)

with open("flight_ui_preview.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Preview generated: flight_ui_preview.html")
