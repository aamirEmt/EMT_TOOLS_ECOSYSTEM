"""Bus Results Renderer.

This module renders bus search results into HTML carousel format.

POST http://busapi.easemytrip.com/v1/api/detail/List/

"""

from typing import Dict, Any, List, Optional
from jinja2 import Environment, BaseLoader


_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=False,
)


# =====================================================================
# 🚌 BUS RESULTS CAROUSEL STYLES
# =====================================================================

BUS_CAROUSEL_STYLES = """
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

.bus-carousel {
  font-family: poppins, sans-serif;
}

.bus-carousel * {
  font-family: poppins, sans-serif;
  box-sizing: border-box;
  margin: 0;
}

.bus-carousel main {
  max-width: 700px;
  margin: auto;
  padding: 20px 0;
}

.bus-carousel .rslt-heading {
  margin-bottom: 12px;
}

.bus-carousel .rslttp {
  padding: 0 0 8px;
}

.bus-carousel .busctl {
  font-size: 15px;
  font-weight: 600;
  color: #202020;
  display: flex;
  gap: 5px;
  align-items: center;
}

.bus-carousel .bussbt {
  font-size: 11px;
  color: #868686;
  font-weight: 500;
  margin-top: 2px;
}

.bus-carousel .buscardbx {
  width: 100%;
  padding: 8px 6px;
}

.bus-carousel .rsltcvr {
  max-width: 100%;
  overflow-x: auto;
  display: flex;
  gap: 20px;
  cursor: grab;
}

.bus-carousel .rsltcvr::-webkit-scrollbar {
  height: 7px;
}

.bus-carousel .rsltcvr::-webkit-scrollbar-track {
  background: #fff;
}

.bus-carousel .rsltcvr::-webkit-scrollbar-thumb {
  background: #373737;
  border-radius: 5px;
}

.bus-carousel .rsltcvr:active {
  cursor: grabbing;
}

.bus-carousel .buscard {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  min-width: 300px;
  width: 300px;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.bus-carousel .buschdr {
  padding: 0 0 10px;
  display: flex;
  gap: 10px;
  align-items: flex-start;
  border-bottom: 1px solid #e0e0e0;
}

.bus-carousel .businfo {
  flex: 1;
  min-width: 0;
}

.bus-carousel .oprtname {
  font-size: 14px;
  font-weight: 600;
  color: #202020;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bus-carousel .bustype {
  font-size: 11px;
  color: #868686;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bus-carousel .bustags {
  display: flex;
  gap: 4px;
  margin-top: 6px;
  flex-wrap: wrap;
}

.bus-carousel .bustag {
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.bus-carousel .bustag.ac {
  background: #e3f2fd;
  color: #1565c0;
}

.bus-carousel .bustag.nonac {
  background: #fff3e0;
  color: #e65100;
}

.bus-carousel .bustag.sleeper {
  background: #f3e5f5;
  color: #7b1fa2;
}

.bus-carousel .bustag.seater {
  background: #e8f5e9;
  color: #2e7d32;
}

.bus-carousel .bustag.volvo {
  background: #fce4ec;
  color: #c2185b;
}

.bus-carousel .busprcbx {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  text-align: right;
}

.bus-carousel .sbttl {
  font-size: 9px;
  color: #868686;
}

.bus-carousel .busprc {
  font-size: 18px;
  font-weight: 700;
  color: #202020;
}

.bus-carousel .seatsleft {
  font-size: 10px;
  color: #d32f2f;
  font-weight: 500;
  margin-top: 2px;
}

.bus-carousel .busbdy {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.bus-carousel .bustme {
  font-size: 17px;
  font-weight: 600;
  color: #202020;
}

.bus-carousel .jrny {
  text-align: center;
}

.bus-carousel .jrnttl {
  font-size: 11px;
  color: #868686;
}

.bus-carousel .j-br {
  width: 55px;
  border-bottom: 1px solid #9e9da1;
  position: relative;
  margin: 4px 0;
}

.bus-carousel .pointsrow {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.bus-carousel .pointbox {
  flex: 1;
  min-width: 0;
}

.bus-carousel .pointlbl {
  font-size: 9px;
  color: #868686;
  text-transform: uppercase;
  margin-bottom: 2px;
}

.bus-carousel .pointval {
  font-size: 11px;
  color: #4b4b4b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bus-carousel .ratingrow {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
}

.bus-carousel .rtnvlu {
  background: #00a664;
  color: #fff;
  padding: 3px 8px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 11px;
}

.bus-carousel .rtnvlu.low {
  background: #ff9800;
}

.bus-carousel .rtnvlu.poor {
  background: #f44336;
}

.bus-carousel .busamnts {
  list-style: none;
  margin: 0;
  padding: 8px 0;
  font-size: 10px;
  color: #4b4b4b;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.bus-carousel .busamnts li {
  background: #f5f5f5;
  padding: 3px 8px;
  border-radius: 10px;
}

.bus-carousel .featuresrow {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding: 6px 0;
}

.bus-carousel .featuretag {
  font-size: 10px;
  color: #04a77a;
  display: flex;
  align-items: center;
  gap: 4px;
}

.bus-carousel .featuretag::before {
  content: '✓';
  font-weight: bold;
}

.bus-carousel .busftr {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 10px;
  margin-top: auto;
}

.bus-carousel .bkbtn {
  border-radius: 40px;
  background: #ef6614;
  color: #fff;
  text-align: center;
  font-size: 12px;
  padding: 10px 15px;
  width: 100%;
  border: 0;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s ease;
  font-weight: 600;
}

.bus-carousel .bkbtn:hover {
  background: #e75806;
}

.bus-carousel .cancelpolicy {
  font-size: 10px;
  color: #646d74;
  text-align: center;
}

.bus-carousel .cancelpolicy.cancellable {
  color: #04a77a;
}

.bus-carousel .emt-empty {
  padding: 60px 20px;
  text-align: center;
  color: #646d74;
  font-size: 14px;
  font-weight: 500;
}

.bus-carousel .emt-inline-arrow {
  width: 14px;
  height: auto;
  object-fit: contain;
  vertical-align: baseline;
}

.bus-carousel .view-all-link {
  margin-left: 12px;
  padding: 6px 14px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  color: #2093ef;
  text-decoration: none;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.bus-carousel .view-all-link:hover {
  background: #2093ef;
  color: #fff;
  border-color: #2093ef;
}
"""


# =====================================================================
# 🚌 BUS RESULTS CAROUSEL TEMPLATE
# =====================================================================

BUS_CAROUSEL_TEMPLATE = """
<style>
{{ styles }}
</style>

<div class="bus-carousel">
  <main>
    <div class="rslttp rslt-heading">
      <div class="busctl">
        <span>{{ source_city }}</span>
        <img
          class="emt-inline-arrow"
          src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='15.728' height='8.101' viewBox='0 0 15.728 8.101'%3E%3Cpath d='M16.536,135.588h0l-3.414-3.4a.653.653,0,0,0-.922.926l2.292,2.281H1.653a.653.653,0,1,0,0,1.307H14.492L12.2,138.985a.653.653,0,0,0,.922.926l3.414-3.4h0A.654.654,0,0,0,16.536,135.588Z' transform='translate(-1 -132)' fill='%23202020'/%3E%3C/svg%3E"
          alt="→"
        />
        <span>{{ destination_city }}</span>
        {% if view_all_link %}
        <a href="{{ view_all_link }}" target="_blank" rel="noopener noreferrer" class="view-all-link">View All</a>
        {% endif %}
      </div>
      <div class="bussbt">
        <span>{{ journey_date }}</span> •
        <span>{{ bus_count }} bus{{ 's' if bus_count != 1 else '' }} found</span>
        {% if ac_count %} • <span>{{ ac_count }} AC</span>{% endif %}
        {% if non_ac_count %} • <span>{{ non_ac_count }} Non-AC</span>{% endif %}
      </div>
    </div>

    <div class="buscardbx">
      <div class="rsltcvr">
        {% for bus in buses %}
        <div class="buscard item">
          <!-- Header: Operator, Type, Tags, Price -->
          <div class="buschdr">
            <div class="businfo">
              <div class="oprtname" title="{{ bus.operator_name }}">{{ bus.operator_name }}</div>
              <div class="bustype" title="{{ bus.bus_type }}">{{ bus.bus_type }}</div>
              <div class="bustags">
                {% if bus.is_ac %}
                <span class="bustag ac">AC</span>
                {% endif %}
                {% if bus.is_non_ac %}
                <span class="bustag nonac">Non-AC</span>
                {% endif %}
                {% if bus.is_volvo %}
                <span class="bustag volvo">Volvo</span>
                {% endif %}
                {% if bus.is_sleeper %}
                <span class="bustag sleeper">Sleeper</span>
                {% elif bus.is_seater %}
                <span class="bustag seater">Seater</span>
                {% endif %}
              </div>
            </div>
            <div class="busprcbx">
              <div class="sbttl">starts from</div>
              <div class="busprc">{{ bus.fare }}</div>
              {% if bus.seats_label %}
              <div class="seatsleft">{{ bus.seats_label }}</div>
              {% endif %}
            </div>
          </div>

          <!-- Body: Timing -->
          <div class="busbdy">
            <div class="bustme">{{ bus.departure_time }}</div>
            <div class="jrny">
              <div class="jrnttl">{{ bus.duration }}</div>
              <div class="j-br"></div>
            </div>
            <div class="bustme">{{ bus.arrival_time }}</div>
          </div>

          <!-- Boarding/Dropping Points (from  bdPoints, dpPoints) -->
          <div class="pointsrow">
            <div class="pointbox">
              <div class="pointlbl">Boarding</div>
              <div class="pointval" title="{{ bus.boarding_point }}">{{ bus.boarding_point }}</div>
            </div>
            <div class="pointbox">
              <div class="pointlbl">Dropping</div>
              <div class="pointval" title="{{ bus.dropping_point }}">{{ bus.dropping_point }}</div>
            </div>
          </div>

          <!-- Rating (from  rt) -->
          {% if bus.rating %}
          <div class="ratingrow">
            <span class="rtnvlu {{ bus.rating_class }}">★ {{ bus.rating }}</span>
          </div>
          {% endif %}

          <!-- Amenities (from  lstamenities) -->
          {% if bus.amenities %}
          <ul class="busamnts">
            {% for amenity in bus.amenities[:4] %}
            <li>{{ amenity }}</li>
            {% endfor %}
            {% if bus.amenities|length > 4 %}
            <li>+{{ bus.amenities|length - 4 }} more</li>
            {% endif %}
          </ul>
          {% endif %}

          <!-- Features (from  liveTrackingAvailable, mTicketEnabled) -->
          {% if bus.live_tracking or bus.m_ticket %}
          <div class="featuresrow">
            {% if bus.live_tracking %}
            <span class="featuretag">Live Tracking</span>
            {% endif %}
            {% if bus.m_ticket %}
            <span class="featuretag">M-Ticket</span>
            {% endif %}
          </div>
          {% endif %}


          <!-- Footer: Book Button, Cancellation -->
          <div class="busftr">
            <a href="{{ bus.booking_link }}" target="_blank" rel="noopener noreferrer" class="bkbtn">Book Now</a>


            {% if bus.is_cancellable %}
            <div class="cancelpolicy cancellable">Cancellation Available</div>
            {% else %}
            <div class="cancelpolicy">Non-refundable</div>
            {% endif %}
          </div>
        </div>
        {% endfor %}
      </div>
    </div>

    {% if not buses %}
    <div class="emt-empty">No buses found for this route</div>
    {% endif %}
  </main>
</div>
"""


# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def _format_currency(value: Any) -> str:
    """Format price in Indian Rupees."""
    if not value:
        return "₹0"
    try:
        amount = float(value)
        return f"₹{int(amount):,}"
    except (ValueError, TypeError):
        return f"₹{value}"


def _format_time(time_value: Any) -> str:
    """Format time to HH:MM format."""
    if not time_value:
        return "--:--"
    
    time_str = str(time_value)
    
    # Already in HH:MM format
    if ":" in time_str and len(time_str) >= 4:
        return time_str[:5]
    
    # HHMM format
    digits = ''.join(filter(str.isdigit, time_str))
    if len(digits) >= 4:
        return f"{digits[:2]}:{digits[2:4]}"
    
    return time_str


def _format_date(date_value: Any) -> str:
    """Format date as DD Mon YYYY."""
    if not date_value:
        return "--"
    
    try:
        from datetime import datetime
        
        if isinstance(date_value, str):
            # Try YYYY-MM-DD format
            dt = datetime.strptime(date_value, "%Y-%m-%d")
        else:
            dt = date_value
        
        return dt.strftime("%d %b %Y")
    except (ValueError, TypeError):
        return str(date_value)


def _truncate_text(text: str, max_length: int = 25) -> str:
    """Truncate text with ellipsis."""
    if not text:
        return ""
    text_str = str(text)
    if len(text_str) <= max_length:
        return text_str
    return text_str[:max_length] + "..."


def _get_rating_class(rating: Any) -> str:
    """Get CSS class for rating badge based on value ( rt field)."""
    if not rating:
        return ""
    try:
        rating_val = float(rating)
        if rating_val < 3:
            return "poor"
        elif rating_val < 4:
            return "low"
        return ""
    except (ValueError, TypeError):
        return ""


def _get_first_boarding_point(boarding_points: List[Dict[str, Any]]) -> str:
    """Extract first boarding point name ( bdPoints → bdLongName)."""
    if not boarding_points:
        return "N/A"
    
    first = boarding_points[0] if isinstance(boarding_points, list) else {}
    name = (
        first.get("bd_long_name") or 
        first.get("bdLongName") or 
        first.get("bdPoint") or 
        "N/A"
    )
    return _truncate_text(name, 20)


def _get_first_dropping_point(dropping_points: List[Dict[str, Any]]) -> str:
    """Extract first dropping point name ( dpPoints → dpName)."""
    if not dropping_points:
        return "N/A"
    
    first = dropping_points[0] if isinstance(dropping_points, list) else {}
    name = (
        first.get("dp_name") or 
        first.get("dpName") or 
        "N/A"
    )
    return _truncate_text(name, 20)


def _extract_amenities(amenities: Any) -> List[str]:
    """Extract amenity names ( lstamenities → [{name, id}])."""
    if not amenities:
        return []
    
    if isinstance(amenities, list):
        # If already list of strings (processed)
        if amenities and isinstance(amenities[0], str):
            return amenities
        # If list of dicts (raw from API)
        return [a.get("name") for a in amenities if isinstance(a, dict) and a.get("name")]
    
    return []


def _get_seats_label(seats: Any) -> str:
    """Get seats left label ( AvailableSeats)."""
    if not seats:
        return ""
    
    try:
        seats_num = int(seats)
        if seats_num <= 0:
            return ""
        if seats_num <= 5:
            return f"{seats_num} seats left"
        return f"{seats_num} seats"
    except (ValueError, TypeError):
        return ""


def _normalize_bus_for_ui(bus: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Normalize a single bus for UI rendering.
    
    Maps AvailableTrips fields to UI format:
        - Travels → operator_name
        - busType → bus_type
        - departureTime → departure_time
        - ArrivalTime → arrival_time
        - duration → duration
        - price/fares → fare
        - AvailableSeats → seats_label
        - AC → is_ac
        - nonAC → is_non_ac
        - isVolvo → is_volvo
        - seater → is_seater
        - sleeper → is_sleeper
        - rt → rating
        - bdPoints → boarding_point
        - dpPoints → dropping_point
        - lstamenities → amenities
        - liveTrackingAvailable → live_tracking
        - mTicketEnabled → m_ticket
        - isCancellable → is_cancellable
    """
    if not bus:
        return None
    
    # Get price ( price or fares array)
    price = bus.get("price")
    fares = bus.get("fares", [])
    if not price and fares:
        price = fares[0] if isinstance(fares, list) and fares else "0"
    
    # Get boarding/dropping points
    boarding_points = bus.get("boarding_points", []) or bus.get("bdPoints", [])
    dropping_points = bus.get("dropping_points", []) or bus.get("dpPoints", [])
    
    # Get amenities ( lstamenities)
    amenities = bus.get("amenities", []) or bus.get("lstamenities", [])
    
    # Get rating ( rt)
    rating = bus.get("rating") or bus.get("rt")
    
    # Get M-ticket (can be string "True" or bool)
    m_ticket_raw = bus.get("m_ticket_enabled") or bus.get("mTicketEnabled") or ""
    m_ticket = str(m_ticket_raw).lower() == "true"
    
    # Get live tracking ( liveTrackingAvailable)
    live_tracking = bus.get("live_tracking_available") or bus.get("liveTrackingAvailable", False)
    
    # Get cancellable ( isCancellable)
    is_cancellable = bus.get("is_cancellable") or bus.get("isCancellable", False)
    
    # Get booking link
    booking_link = bus.get("book_now") or bus.get("deepLink") or bus.get("booking_link") or "#"
    if isinstance(booking_link, str):
        booking_link = booking_link.strip()

    return {
        "operator_name": _truncate_text(bus.get("operator_name") or bus.get("Travels") or "Unknown", 22),
        "bus_type": _truncate_text(bus.get("bus_type") or bus.get("busType") or "Bus", 30),
        "departure_time": _format_time(bus.get("departure_time") or bus.get("departureTime")),
        "arrival_time": _format_time(bus.get("arrival_time") or bus.get("ArrivalTime")),
        "duration": bus.get("duration") or "--",
        "fare": _format_currency(price),
        "seats_label": _get_seats_label(bus.get("available_seats") or bus.get("AvailableSeats")),
        "is_ac": bus.get("is_ac") or bus.get("AC", False),
        "is_non_ac": bus.get("is_non_ac") or bus.get("nonAC", False),
        "is_volvo": bus.get("is_volvo") or bus.get("isVolvo", False),
        "is_seater": bus.get("is_seater") or bus.get("seater", False),
        "is_sleeper": bus.get("is_sleeper") or bus.get("sleeper", False),
        "rating": rating,
        "rating_class": _get_rating_class(rating),
        "boarding_point": _get_first_boarding_point(boarding_points),
        "dropping_point": _get_first_dropping_point(dropping_points),
        "amenities": _extract_amenities(amenities),
        "live_tracking": live_tracking,
        "m_ticket": m_ticket,
        "is_cancellable": is_cancellable,
        "booking_link": booking_link,
    }


# =====================================================================
# MAIN RENDER FUNCTION
# =====================================================================

def render_bus_results(bus_results: Dict[str, Any]) -> str:
    """
    Render bus search results carousel.
    
    Args:
        bus_results: Dictionary containing bus search results from search_buses()
            Expected keys:
            - buses: List of processed AvailableTrips
            - total_count: Number of buses
            - ac_count: AcCount from API
            - non_ac_count: NonAcCount from API
            - source_id: Source city ID
            - destination_id: Destination city ID
            - journey_date: Journey date (YYYY-MM-DD)
    
    Returns:
        HTML string for the bus carousel
    """
    # Unwrap structured_content if present
    if "structured_content" in bus_results:
        bus_results = bus_results["structured_content"]
    
    buses = bus_results.get("buses", [])
    
    if not buses:
        return "<div class='bus-carousel'><main><div class='emt-empty'>No buses found for this route</div></main></div>"
    
    # Normalize buses for UI
    buses_ui = [_normalize_bus_for_ui(bus) for bus in buses]
    buses_ui = [b for b in buses_ui if b]
    
    if not buses_ui:
        return "<div class='bus-carousel'><main><div class='emt-empty'>No buses found for this route</div></main></div>"
    
    # Get route info
    source_id = bus_results.get("source_id", "")
    destination_id = bus_results.get("destination_id", "")
    
    # Format journey date
    journey_date = _format_date(bus_results.get("journey_date"))
    
    # Get counts (from  AcCount, NonAcCount)
    ac_count = bus_results.get("ac_count", 0)
    non_ac_count = bus_results.get("non_ac_count", 0)
    bus_count = bus_results.get("total_count") or len(buses_ui)
    
    # Render template
    template = _jinja_env.from_string(BUS_CAROUSEL_TEMPLATE)
    return template.render(
        styles=BUS_CAROUSEL_STYLES,
        source_city=source_id,
        destination_city=destination_id,
        journey_date=journey_date,
        bus_count=bus_count,
        ac_count=ac_count,
        non_ac_count=non_ac_count,
        buses=buses_ui,
        view_all_link=bus_results.get("view_all_link"),
    )