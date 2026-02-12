"""Train Availability Check HTML Renderer - Jinja2 template for displaying availability across classes."""

from typing import Dict, Any, List
from jinja2 import Environment, BaseLoader, select_autoescape
from datetime import datetime


# Initialize Jinja2 environment
_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)


AVAILABILITY_CHECK_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

.train-availability {
  font-family: poppins, sans-serif;
  color: #202020;
  background: rgba(255, 255, 255, 0.92);
  position: relative;
}

.train-availability * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
}

.train-availability main {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px 0 30px;
}

.train-availability .avl-header {
  margin-bottom: 12px;
}

.train-availability .avl-title {
  font-size: 18px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 4px;
}

.train-availability .avl-subtitle {
  font-size: 12px;
  color: #646d74;
  margin-top: 4px;
}

.train-availability .avl-card {
  width: 80%;
  max-width: 294px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fff;
  padding: 14px;
  display: flex;
  flex-direction: column;
}

.train-availability .trn-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
  margin-bottom: 14px;
  gap: 10px;
}

.train-availability .trn-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.train-availability .trn-details {
  flex: 1;
}

.train-availability .trn-name {
  font-size: 15px;
  font-weight: 600;
  color: #202020;
  line-height: 1.3;
}

.train-availability .trn-route {
  font-size: 11px;
  color: #646d74;
  margin-top: 4px;
}

.train-availability .trn-number {
  font-weight: 500;
  font-size: 14px;
  width: auto;
  padding: 3px 5px;
  color: #313131;
  background: #F2F9FF;
  border: 1px solid #B6D5F0;
  border-radius: 3px;
}

.train-availability .journey-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #646d74;
  margin-bottom: 14px;
}

.train-availability .journey-date {
  font-weight: 600;
  color: #202020;
}

.train-availability .quota-badge {
  padding: 2px 8px;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 4px;
  font-weight: 600;
  font-size: 10px;
}

.train-availability .class-carousel-wrapper {
  margin-top: auto;
}

.train-availability .class-carousel {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: thin;
  scrollbar-color: #ccc transparent;
}

.train-availability .class-carousel::-webkit-scrollbar {
  height: 4px;
}

.train-availability .class-carousel::-webkit-scrollbar-track {
  background: transparent;
}

.train-availability .class-carousel::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}

.train-availability .class-card {
  min-width: 110px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  background: #fff;
  transition: all 0.2s ease;
  position: relative;
}

.train-availability .class-card:hover {
  border-color: #ef6614;
  box-shadow: 0 2px 8px rgba(239, 102, 20, 0.15);
}

.train-availability .class-code {
  font-size: 13px;
  font-weight: 700;
  color: #202020;
}

.train-availability .class-fare {
  font-size: 14px;
  font-weight: 700;
  color: #202020;
  font-family: inter, sans-serif;
  margin-top: 6px;
}

.train-availability .class-fare-updated {
  font-size: 8px;
  color: #868686;
  margin-top: 2px;
}

.train-availability .class-availability {
  font-size: 9px;
  margin-top: auto;
  padding-top: 4px;
  font-weight: 500;
}

.train-availability .class-availability.available {
  color: #2e7d32;
}

.train-availability .class-availability.waitlist {
  color: #f57c00;
}

.train-availability .class-availability.rac {
  color: #1976d2;
}

.train-availability .class-availability.unavailable {
  color: #d32f2f;
}

.train-availability .class-book-btn {
  margin-top: 8px;
  padding: 6px 8px;
  background: #ef6614;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  display: block;
  transition: background 0.2s ease;
}

.train-availability .class-book-btn:hover {
  background: #e75806;
}

.train-availability .class-book-btn.disabled {
  background: #ccc;
  color: #888;
  cursor: not-allowed;
  pointer-events: none;
  opacity: 0.6;
}

.train-availability .empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #646d74;
  font-size: 14px;
}
</style>

<div class="train-availability">
  <main>
    <div class="avl-header">
      <div class="avl-title">Train Availability Check</div>
      <div class="avl-subtitle">{{ formatted_date }}</div>
    </div>

    {% if classes and classes|length > 0 %}
    <div class="avl-card">
      <div class="trn-header">
        <div class="trn-info">
          <div class="trn-details">
            <div class="trn-name">{{ train_name }}</div>
            <div class="trn-route">{{ from_station }} → {{ to_station }}</div>
          </div>
          <div class="trn-number">{{ train_no }}</div>
        </div>
      </div>

      <div class="journey-info">
        <span>Journey Date:</span>
        <span class="journey-date">{{ journey_date }}</span>
        <span>•</span>
        <span class="quota-badge">{{ quota_name }}</span>
      </div>

      <div class="class-carousel-wrapper">
        <div class="class-carousel">
          {% for cls in classes %}
          {% set is_regret = 'REGRET' in cls.status or 'NOT AVAILABLE' in cls.status or 'TRAIN CANCELLED' in cls.status or 'ERROR' in cls.status %}
          {% set is_bookable = 'AVAILABLE' in cls.status or 'WL' in cls.status or 'RAC' in cls.status %}
          <div class="class-card">
            <div class="class-code">{{ cls.class_code }}</div>
            {% if cls.fare %}
            <div class="class-fare">Rs.{{ cls.fare }}</div>
            {% endif %}
            <div class="class-availability {% if is_regret %}unavailable{% elif 'WL' in cls.status %}waitlist{% elif 'RAC' in cls.status %}rac{% elif 'AVAILABLE' in cls.status %}available{% else %}unavailable{% endif %}">
              {{ cls.status[:15] }}{% if cls.status|length > 15 %}...{% endif %}
            </div>
            {% if cls.fare_updated %}
            <div class="class-fare-updated">{{ cls.fare_updated }}</div>
            {% endif %}
            {% if is_bookable %}
            <a href="{{ build_book_url(train_no, cls.class_code, from_station_code, to_station_code, quota, journey_date_api, from_station, to_station) }}"
               target="_blank"
               rel="noopener noreferrer"
               class="class-book-btn">{% if quota == 'TQ' %}Book Tatkal{% else %}Book Now{% endif %}</a>
            {% elif is_regret %}
            <a href="javascript:void(0)" class="class-book-btn disabled">Not Available</a>
            {% endif %}
          </div>
          {% endfor %}
        </div>
      </div>
    </div>
    {% else %}
    <div class="empty-state">No availability information available.</div>
    {% endif %}
  </main>
</div>
"""


def _get_quota_name(quota: str) -> str:
    """
    Get full quota name from quota code.

    Args:
        quota: Quota code (e.g., "GN", "TQ")

    Returns:
        Full quota name
    """
    quota_names = {
        "GN": "General",
        "TQ": "Tatkal",
        "SS": "Senior Citizen",
        "LD": "Ladies",
        "PT": "Premium Tatkal",
        "HO": "Head On Generation",
        "PH": "Physically Handicapped",
    }
    return quota_names.get(quota.upper(), quota)


def _format_date_display(date_str: str) -> str:
    """
    Format date for display.

    Args:
        date_str: Date in DD-MM-YYYY format

    Returns:
        Date formatted as "DD Mon YYYY" (e.g., "25 Feb 2026")
    """
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        return date_obj.strftime("%d %b %Y")
    except Exception:
        return date_str


def _build_book_url(
    train_no: str,
    class_code: str,
    from_code: str,
    to_code: str,
    quota: str,
    journey_date: str,
    from_display: str,
    to_display: str,
) -> str:
    """
    Build booking URL for EaseMyTrip railways.

    Args:
        train_no: Train number
        class_code: Class code
        from_code: Origin station code
        to_code: Destination station code
        quota: Quota code
        journey_date: Journey date in DD/MM/YYYY format
        from_display: Full from station display
        to_display: Full to station display

    Returns:
        Booking URL
    """
    # Convert date format: DD/MM/YYYY -> D-M-YYYY
    date_parts = journey_date.split("/")
    date_formatted = f"{int(date_parts[0])}-{int(date_parts[1])}-{date_parts[2]}"

    # Extract station names and convert to URL format
    from_name = from_display.split("(")[0].strip().replace(" ", "-")
    to_name = to_display.split("(")[0].strip().replace(" ", "-")

    return f"https://railways.easemytrip.com/TrainInfo/{from_name}-to-{to_name}/{class_code}/{train_no}/{from_code}/{to_code}/{quota}/{date_formatted}"


def render_availability_check(
    train_info: Dict[str, Any],
    classes: List[Dict[str, Any]],
    journey_date: str,
    from_station: str,
    to_station: str,
    quota: str,
    from_station_code: str = "",
    to_station_code: str = "",
) -> str:
    """
    Render train availability check results as HTML.

    Args:
        train_info: Dictionary containing train_no and train_name
        classes: List of class availability dictionaries
        journey_date: Journey date string in DD-MM-YYYY format
        from_station: Origin station name/code
        to_station: Destination station name/code
        quota: Quota code
        from_station_code: Origin station code (optional, extracted if not provided)
        to_station_code: Destination station code (optional, extracted if not provided)

    Returns:
        HTML string with rendered availability check results
    """
    # Extract station codes if not provided
    if not from_station_code and "(" in from_station:
        from_station_code = from_station.split("(")[1].replace(")", "").strip()
    if not to_station_code and "(" in to_station:
        to_station_code = to_station.split("(")[1].replace(")", "").strip()

    # Convert journey date to API format (DD/MM/YYYY)
    journey_date_api = journey_date.replace("-", "/")

    # Format date for display
    formatted_date = _format_date_display(journey_date)

    # Add helper function to Jinja2 environment
    _jinja_env.globals["build_book_url"] = _build_book_url

    template = _jinja_env.from_string(AVAILABILITY_CHECK_TEMPLATE)

    return template.render(
        train_name=train_info.get("train_name", "Unknown Train"),
        train_no=train_info.get("train_no", ""),
        from_station=from_station,
        to_station=to_station,
        from_station_code=from_station_code,
        to_station_code=to_station_code,
        journey_date=journey_date,
        formatted_date=formatted_date,
        journey_date_api=journey_date_api,
        classes=classes,
        quota=quota,
        quota_name=_get_quota_name(quota),
    )
