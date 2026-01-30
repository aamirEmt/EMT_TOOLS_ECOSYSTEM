from typing import Dict, Any, List, Optional
from jinja2 import Environment, BaseLoader

_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=False,
)

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
  width: 90%;
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

.bus-carousel .view-all-card {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fff5f0 0%, #ffffff 100%);
  border: 2px dashed #ef6614;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.bus-carousel .view-all-card:hover {
  background: linear-gradient(135deg, #ffebe0 0%, #fff5f0 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 102, 20, 0.15);
}

.bus-carousel .view-all-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  text-align: center;
}

.bus-carousel .view-all-icon svg {
  width: 48px;
  height: 48px;
}

.bus-carousel .view-all-title {
  font-size: 16px;
  font-weight: 600;
  color: #ef6614;
}

.bus-carousel .view-all-subtitle {
  font-size: 12px;
  color: #868686;
}
"""

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
          <div class="buschdr">
            <div class="businfo">
              <div class="oprtname" title="{{ bus.operator_name }}">{{ bus.operator_name }}</div>
              <div class="bustype" title="{{ bus.bus_type }}">{{ bus.bus_type }}</div>
              <div class="bustags">
                {% if bus.is_ac %}<span class="bustag ac">AC</span>{% endif %}
                {% if bus.is_non_ac %}<span class="bustag nonac">Non-AC</span>{% endif %}
                {% if bus.is_volvo %}<span class="bustag volvo">Volvo</span>{% endif %}
                {% if bus.is_sleeper %}<span class="bustag sleeper">Sleeper</span>
                {% elif bus.is_seater %}<span class="bustag seater">Seater</span>{% endif %}
              </div>
            </div>
            <div class="busprcbx">
              <div class="sbttl">starts from</div>
              <div class="busprc">{{ bus.fare }}</div>
              {% if bus.seats_label %}<div class="seatsleft">{{ bus.seats_label }}</div>{% endif %}
            </div>
          </div>

          <div class="busbdy">
            <div class="bustme">{{ bus.departure_time }}</div>
            <div class="jrny">
              <div class="jrnttl">{{ bus.duration }}</div>
              <div class="j-br"></div>
            </div>
            <div class="bustme">{{ bus.arrival_time }}</div>
          </div>

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

          {% if bus.rating %}
          <div class="ratingrow">
            <span class="rtnvlu {{ bus.rating_class }}">★ {{ bus.rating }}</span>
          </div>
          {% endif %}

          {% if bus.amenities %}
          <ul class="busamnts">
            {% for amenity in bus.amenities[:4] %}<li>{{ amenity }}</li>{% endfor %}
            {% if bus.amenities|length > 4 %}<li>+{{ bus.amenities|length - 4 }} more</li>{% endif %}
          </ul>
          {% endif %}

          {% if bus.live_tracking or bus.m_ticket %}
          <div class="featuresrow">
            {% if bus.live_tracking %}<span class="featuretag">Live Tracking</span>{% endif %}
            {% if bus.m_ticket %}<span class="featuretag">M-Ticket</span>{% endif %}
          </div>
          {% endif %}

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
        
        {% if show_view_all_card and view_all_link %}
        <a href="{{ view_all_link }}" target="_blank" rel="noopener noreferrer" class="buscard item view-all-card">
          <div class="view-all-content">
            <div class="view-all-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ef6614" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 8v8M8 12h8"></path>
              </svg>
            </div>
            <div class="view-all-text">
              <div class="view-all-title">View All {{ total_bus_count }} Buses</div>
              <div class="view-all-subtitle">See more options for this route</div>
            </div>
          </div>
        </a>
        {% endif %}
      </div>
    </div>

    {% if not buses %}
    <div class="emt-empty">No buses found for this route</div>
    {% endif %}
  </main>
</div>
"""

SEAT_LAYOUT_STYLES = """
.seat-layout {
  font-family: poppins, sans-serif;
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
}

.seat-layout * {
  box-sizing: border-box;
  margin: 0;
}

.seat-layout .layout-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.seat-layout .layout-title {
  font-size: 18px;
  font-weight: 600;
  color: #202020;
}

.seat-layout .layout-subtitle {
  font-size: 12px;
  color: #868686;
  margin-top: 4px;
}

.seat-layout .layout-info {
  display: flex;
  gap: 20px;
  margin-top: 10px;
  font-size: 12px;
}

.seat-layout .info-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.seat-layout .info-dot {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.seat-layout .info-dot.available { background: #4caf50; }
.seat-layout .info-dot.booked { background: #9e9e9e; }
.seat-layout .info-dot.ladies { background: #e91e63; }
.seat-layout .info-dot.selected { background: #ef6614; }

.seat-layout .deck-container {
  margin-bottom: 20px;
}

.seat-layout .deck-title {
  font-size: 14px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 10px;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 6px;
}

.seat-layout .deck-grid {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 15px;
  background: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.seat-layout .seat-row {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.seat-layout .seat {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.seat-layout .seat.sleeper { width: 72px; height: 36px; }
.seat-layout .seat.available { background: #e8f5e9; color: #2e7d32; border-color: #4caf50; }
.seat-layout .seat.available:hover { background: #c8e6c9; transform: scale(1.05); }
.seat-layout .seat.booked { background: #eeeeee; color: #9e9e9e; cursor: not-allowed; }
.seat-layout .seat.ladies { background: #fce4ec; color: #c2185b; border-color: #e91e63; }
.seat-layout .seat.selected { background: #fff3e0; color: #e65100; border-color: #ef6614; box-shadow: 0 2px 8px rgba(239, 102, 20, 0.3); }
.seat-layout .seat.blocked { background: #ffebee; color: #c62828; cursor: not-allowed; }
.seat-layout .seat.empty { visibility: hidden; }

.seat-layout .aisle { width: 20px; }

.seat-layout .driver-cabin {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 10px;
  margin-bottom: 10px;
}

.seat-layout .driver-icon {
  width: 40px;
  height: 40px;
  background: #424242;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.seat-layout .driver-icon svg { width: 24px; height: 24px; fill: #fff; }

.seat-layout .seat-summary {
  margin-top: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.seat-layout .summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 8px;
}

.seat-layout .summary-row:last-child {
  margin-bottom: 0;
  padding-top: 8px;
  border-top: 1px solid #e0e0e0;
  font-weight: 600;
}

.seat-layout .layout-empty {
  text-align: center;
  padding: 40px 20px;
  color: #868686;
}

.seat-layout .layout-note {
  font-size: 11px;
  color: #666;
  text-align: center;
  margin-top: 15px;
  padding: 10px;
  background: #fff8e1;
  border-radius: 6px;
  border: 1px solid #ffe082;
}
"""

SEAT_LAYOUT_TEMPLATE = """
<style>{{ styles }}</style>

<div class="seat-layout">
  <div class="layout-header">
    <div class="layout-title">{{ operator_name }} - Seat Layout</div>
    <div class="layout-subtitle">{{ bus_type }}</div>
    
    <div class="layout-info">
      <div class="info-item"><span class="info-dot available"></span><span>Available ({{ available_seats }})</span></div>
      <div class="info-item"><span class="info-dot booked"></span><span>Booked ({{ booked_seats }})</span></div>
      <div class="info-item"><span class="info-dot ladies"></span><span>Ladies</span></div>
    </div>
  </div>

  {% if lower_deck %}
  <div class="deck-container">
    <div class="deck-title">🚌 Lower Deck</div>
    <div class="driver-cabin">
      <div class="driver-icon">
        <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>
      </div>
    </div>
    <div class="deck-grid">
      {% for row in lower_deck.rows_data %}
      <div class="seat-row">
        {% for seat in row %}
          {% if seat.is_aisle %}<div class="aisle"></div>
          {% elif seat.is_empty %}<div class="seat empty"></div>
          {% else %}<div class="seat {{ seat.status_class }}{% if seat.is_sleeper %} sleeper{% endif %}" data-seat="{{ seat.seat_number }}" data-fare="{{ seat.fare }}" title="{{ seat.seat_name }} - ₹{{ seat.fare }}">{{ seat.seat_number }}</div>{% endif %}
        {% endfor %}
      </div>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  {% if upper_deck %}
  <div class="deck-container">
    <div class="deck-title">🛏️ Upper Deck</div>
    <div class="deck-grid">
      {% for row in upper_deck.rows_data %}
      <div class="seat-row">
        {% for seat in row %}
          {% if seat.is_aisle %}<div class="aisle"></div>
          {% elif seat.is_empty %}<div class="seat empty"></div>
          {% else %}<div class="seat {{ seat.status_class }}{% if seat.is_sleeper %} sleeper{% endif %}" data-seat="{{ seat.seat_number }}" data-fare="{{ seat.fare }}" title="{{ seat.seat_name }} - ₹{{ seat.fare }}">{{ seat.seat_number }}</div>{% endif %}
        {% endfor %}
      </div>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  {% if not lower_deck and not upper_deck %}
  <div class="layout-empty">
    <p>Seat layout not available for this bus.</p>
    <p class="layout-note">⚠️ Some bus operators do not provide seat layout data through the API. Please visit the EaseMyTrip website to select seats for this bus.</p>
  </div>
  {% endif %}

  <div class="seat-summary">
    <div class="summary-row"><span>Total Seats</span><span>{{ total_seats }}</span></div>
    <div class="summary-row"><span>Available</span><span>{{ available_seats }}</span></div>
    <div class="summary-row"><span>Boarding</span><span>{{ boarding_point }}</span></div>
    <div class="summary-row"><span>Dropping</span><span>{{ dropping_point }}</span></div>
  </div>
</div>
"""

def _format_currency(value: Any) -> str:
    if not value:
        return "₹0"
    try:
        amount = float(value)
        return f"₹{int(amount):,}"
    except (ValueError, TypeError):
        return f"₹{value}"


def _format_time(time_value: Any) -> str:
    if not time_value:
        return "--:--"
    time_str = str(time_value)
    if ":" in time_str and len(time_str) >= 4:
        return time_str[:5]
    digits = ''.join(filter(str.isdigit, time_str))
    if len(digits) >= 4:
        return f"{digits[:2]}:{digits[2:4]}"
    return time_str


def _format_date(date_value: Any) -> str:
    if not date_value:
        return "--"
    try:
        from datetime import datetime
        if isinstance(date_value, str):
            dt = datetime.strptime(date_value, "%Y-%m-%d")
        else:
            dt = date_value
        return dt.strftime("%d %b %Y")
    except (ValueError, TypeError):
        return str(date_value)


def _truncate_text(text: str, max_length: int = 25) -> str:
    if not text:
        return ""
    text_str = str(text)
    if len(text_str) <= max_length:
        return text_str
    return text_str[:max_length] + "..."


def _normalize_rating_for_display(rating_value: Any) -> Optional[str]:

    if rating_value is None or rating_value == "" or rating_value == 0:
        return None
    try:
        rating_float = float(rating_value)
        if rating_float > 5:
            rating_float = rating_float / 10
        if rating_float < 0 or rating_float > 5:
            return None
        if rating_float == 0:
            return None
        if rating_float == int(rating_float):
            return str(int(rating_float))
        return f"{rating_float:.1f}"
    except (ValueError, TypeError):
        return None


def _get_rating_class(rating: Any) -> str:
    if not rating:
        return ""
    try:
        rating_str = _normalize_rating_for_display(rating)
        if not rating_str:
            return ""
        rating_val = float(rating_str)
        if rating_val < 3:
            return "poor"
        elif rating_val < 4:
            return "low"
        return ""
    except (ValueError, TypeError):
        return ""


def _get_first_boarding_point(boarding_points: List[Dict[str, Any]]) -> str:
    if not boarding_points:
        return "N/A"
    first = boarding_points[0] if isinstance(boarding_points, list) else {}
    name = (first.get("bd_long_name") or first.get("bdLongName") or 
            first.get("bd_point") or first.get("bdPoint") or "N/A")
    return _truncate_text(name, 20)


def _get_first_dropping_point(dropping_points: List[Dict[str, Any]]) -> str:
    if not dropping_points:
        return "N/A"
    first = dropping_points[0] if isinstance(dropping_points, list) else {}
    name = first.get("dp_name") or first.get("dpName") or "N/A"
    return _truncate_text(name, 20)


def _extract_amenities(amenities: Any) -> List[str]:
    if not amenities:
        return []
    if isinstance(amenities, list):
        if amenities and isinstance(amenities[0], str):
            return amenities
        return [a.get("name") for a in amenities if isinstance(a, dict) and a.get("name")]
    return []


def _get_seats_label(seats: Any) -> str:
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
    if not bus:
        return None
    
    price = bus.get("price")
    fares = bus.get("fares", [])
    if not price and fares:
        price = fares[0] if isinstance(fares, list) and fares else "0"
    
    boarding_points = bus.get("boarding_points", []) or bus.get("bdPoints", [])
    dropping_points = bus.get("dropping_points", []) or bus.get("dpPoints", [])
    amenities = bus.get("amenities", []) or bus.get("lstamenities", [])
    
    # Get raw rating and normalize it
    raw_rating = bus.get("rating") or bus.get("rt")
    normalized_rating = _normalize_rating_for_display(raw_rating)
    
    m_ticket_raw = bus.get("m_ticket_enabled") or bus.get("mTicketEnabled") or ""
    m_ticket = str(m_ticket_raw).lower() == "true"
    
    live_tracking = bus.get("live_tracking_available") or bus.get("liveTrackingAvailable", False)
    is_cancellable = bus.get("is_cancellable") or bus.get("isCancellable", False)
    
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
        "rating": normalized_rating,
        "rating_class": _get_rating_class(raw_rating),
        "boarding_point": _get_first_boarding_point(boarding_points),
        "dropping_point": _get_first_dropping_point(dropping_points),
        "amenities": _extract_amenities(amenities),
        "live_tracking": live_tracking,
        "m_ticket": m_ticket,
        "is_cancellable": is_cancellable,
        "booking_link": booking_link,
    }


def render_bus_results(bus_results: Dict[str, Any]) -> str:
    """Render bus search results as HTML carousel."""
    if "structured_content" in bus_results:
        bus_results = bus_results["structured_content"]
    
    buses = bus_results.get("buses", [])
    
    if not buses:
        return "<div class='bus-carousel'><main><div class='emt-empty'>No buses found for this route</div></main></div>"
    
    buses_ui = [_normalize_bus_for_ui(bus) for bus in buses]
    buses_ui = [b for b in buses_ui if b]
    
    if not buses_ui:
        return "<div class='bus-carousel'><main><div class='emt-empty'>No buses found for this route</div></main></div>"
    
    source_city = bus_results.get("source_name") or bus_results.get("source_id", "")
    destination_city = bus_results.get("destination_name") or bus_results.get("destination_id", "")
    journey_date = _format_date(bus_results.get("journey_date"))
    ac_count = bus_results.get("ac_count", 0)
    non_ac_count = bus_results.get("non_ac_count", 0)
    bus_count = bus_results.get("total_count") or len(buses_ui)
    
    template = _jinja_env.from_string(BUS_CAROUSEL_TEMPLATE)
    return template.render(
        styles=BUS_CAROUSEL_STYLES,
        source_city=source_city,
        destination_city=destination_city,
        journey_date=journey_date,
        bus_count=bus_count,
        ac_count=ac_count,
        non_ac_count=non_ac_count,
        buses=buses_ui,
        view_all_link=bus_results.get("view_all_link"),
        show_view_all_card=False,
        total_bus_count=bus_count,
    )


def render_bus_results_with_limit(
    bus_results: Dict[str, Any],
    display_limit: int = 5,
    show_view_all: bool = True,
) -> str:
    if "structured_content" in bus_results:
        bus_results = bus_results["structured_content"]
    
    buses = bus_results.get("buses", [])
    
    if not buses:
        return "<div class='bus-carousel'><main><div class='emt-empty'>No buses found for this route</div></main></div>"
    
    total_buses = len(buses)
    display_buses = buses[:display_limit]
    
    buses_ui = [_normalize_bus_for_ui(bus) for bus in display_buses]
    buses_ui = [b for b in buses_ui if b]
    
    if not buses_ui:
        return "<div class='bus-carousel'><main><div class='emt-empty'>No buses found for this route</div></main></div>"
    
    source_city = bus_results.get("source_name") or bus_results.get("source_id", "")
    destination_city = bus_results.get("destination_name") or bus_results.get("destination_id", "")
    journey_date = _format_date(bus_results.get("journey_date"))
    ac_count = bus_results.get("ac_count", 0)
    non_ac_count = bus_results.get("non_ac_count", 0)
    view_all_link = bus_results.get("view_all_link", "")
    
    should_show_view_all = show_view_all and total_buses > display_limit and view_all_link
    
    template = _jinja_env.from_string(BUS_CAROUSEL_TEMPLATE)
    return template.render(
        styles=BUS_CAROUSEL_STYLES,
        source_city=source_city,
        destination_city=destination_city,
        journey_date=journey_date,
        bus_count=total_buses,
        ac_count=ac_count,
        non_ac_count=non_ac_count,
        buses=buses_ui,
        view_all_link=view_all_link,
        show_view_all_card=should_show_view_all,
        total_bus_count=total_buses,
    )


def _get_seat_status_class(seat: Dict[str, Any]) -> str:
    if seat.get("is_booked"):
        return "booked"
    if seat.get("is_blocked"):
        return "blocked"
    if seat.get("is_ladies"):
        return "ladies"
    if seat.get("is_available"):
        return "available"
    return "booked"


def _build_deck_rows(deck: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
    if not deck or not deck.get("seats"):
        return []
    
    seats = deck["seats"]
    rows = deck.get("rows", 10)
    columns = deck.get("columns", 5)
    
    grid = [[{"is_empty": True} for _ in range(columns)] for _ in range(rows)]
    
    for seat in seats:
        row = seat.get("row", 0)
        col = seat.get("column", 0)
        
        if 0 <= row < rows and 0 <= col < columns:
            grid[row][col] = {
                "is_empty": False,
                "is_aisle": False,
                "seat_number": seat.get("seat_number", ""),
                "seat_name": seat.get("seat_name", ""),
                "fare": seat.get("fare", "0"),
                "status_class": _get_seat_status_class(seat),
                "is_sleeper": seat.get("seat_type", "").upper() in ["SL", "SLEEPER"],
            }
    
    return grid


def _normalize_deck_for_ui(deck: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not deck:
        return None
    
    rows_data = _build_deck_rows(deck)
    
    return {
        "deck_name": deck.get("deck_name", ""),
        "rows": deck.get("rows", 0),
        "columns": deck.get("columns", 0),
        "rows_data": rows_data,
    }


def render_seat_layout(seat_layout_response: Dict[str, Any]) -> str:
    """Render seat layout as HTML."""
    if not seat_layout_response.get("success"):
        message = seat_layout_response.get('message', 'Failed to load seat layout')
        return f"""
<style>{SEAT_LAYOUT_STYLES}</style>
<div class='seat-layout'>
  <div class='layout-empty'>
    <p>{message}</p>
    <p class="layout-note">⚠️ Some bus operators do not provide seat layout data through the API. Please visit the EaseMyTrip website to select seats for this bus.</p>
  </div>
</div>
"""
    
    layout = seat_layout_response.get("layout")
    if not layout:
        return f"""
<style>{SEAT_LAYOUT_STYLES}</style>
<div class='seat-layout'>
  <div class='layout-empty'>
    <p>Seat layout not available</p>
    <p class="layout-note">⚠️ Some bus operators do not provide seat layout data through the API. Please visit the EaseMyTrip website to select seats for this bus.</p>
  </div>
</div>
"""
    
    lower_deck = _normalize_deck_for_ui(layout.get("lower_deck"))
    upper_deck = _normalize_deck_for_ui(layout.get("upper_deck"))
    
    template = _jinja_env.from_string(SEAT_LAYOUT_TEMPLATE)
    return template.render(
        styles=SEAT_LAYOUT_STYLES,
        operator_name=layout.get("operator_name", "Bus"),
        bus_type=layout.get("bus_type", ""),
        total_seats=layout.get("total_seats", 0),
        available_seats=layout.get("available_seats", 0),
        booked_seats=layout.get("booked_seats", 0),
        lower_deck=lower_deck,
        upper_deck=upper_deck,
        boarding_point=layout.get("boarding_point", ""),
        dropping_point=layout.get("dropping_point", ""),
    )