from typing import Dict, Any, List
from jinja2 import Environment, BaseLoader, select_autoescape


def _truncate_text(text: str, max_length: int = 20) -> str:
    """Truncate text to max_length characters and add ellipsis if truncated"""
    if not text:
        return text
    text_str = str(text)
    if len(text_str) <= max_length:
        return text_str
    return text_str[:max_length] + "..."

_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)
_jinja_env.filters['truncate_text'] = _truncate_text

# =====================================================================
# 🏨 HOTEL RESULTS CAROUSEL TEMPLATE (EASEMYTRIP REACT-PARITY)
# =====================================================================
HOTEL_CAROUSEL_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

.hotel-carousel {
  font-family: poppins, sans-serif;
  color: #202020;
  background: rgba(255, 255, 255, 0.92);
  position: relative;
}

.hotel-carousel * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
}

.hotel-carousel main {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px 0 30px;
}

.hotel-carousel .htlhd {
  margin-bottom: 12px;
}

.hotel-carousel .htlttl {
  font-size: 18px;
  font-weight: 600;
  color: #202020;
}

.hotel-carousel .htlsub {
  font-size: 12px;
  color: #646d74;
  margin-top: 4px;
}

.hotel-carousel .htlcnt {
  font-size: 11px;
  color: #868686;
  margin-top: 2px;
}

.hotel-carousel .dtldte {
  font-size: 12px;
  color: #646d74;
  margin-bottom: 10px;
}

.hotel-carousel .slider-shell {
  position: relative;
}

.hotel-carousel .rsltcvr {
  width: 90%;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  cursor: grab;
}

.hotel-carousel .rsltcvr:active {
  cursor: grabbing;
}

.hotel-carousel .embla__container {
  display: flex;
  gap: 20px;
}

.hotel-carousel .htlcard {
  width: 300px;
  min-width: 300px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fff;
  padding: 10px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.hotel-carousel .img-top {
  width: 100%;
  height: 165px;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 10px;
}

.hotel-carousel .img-top img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.hotel-carousel .htlcrdbdy {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.hotel-carousel .nmeorc {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 8px;
}

.hotel-carousel .htlinfo {
  max-width: calc(100% - 90px);
}

.hotel-carousel .rntgs {
  display: flex;
  gap: 3px;
}

.hotel-carousel .rntgs img {
  width: 14px;
  height: 14px;
  object-fit: contain;
}

.hotel-carousel .htlnme {
  font-size: 15px;
  font-weight: 600;
  margin-top: 4px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hotel-carousel .htllcn {
  font-size: 11px;
  color: #868686;
  margin-top: 2px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hotel-carousel .htlprcbx {
  min-width: max-content;
  text-align: end;
}

.hotel-carousel .sbttl {
  font-size: 9px;
  color: #868686;
}

.hotel-carousel .htlprc {
  font-size: 18px;
  font-family: inter, sans-serif;
  font-weight: 700;
}

.hotel-carousel .htlrevbx {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
}

.hotel-carousel .rtnvlu {
  background: #00a664;
  color: #fff;
  padding: 3px 8px;
  border-radius: 6px;
  font-weight: 600;
}

.hotel-carousel .rtnabb {
  font-weight: 600;
}

.hotel-carousel .revnmb {
  color: #646d74;
}

.hotel-carousel .htlamnts {
  list-style: disc;
  margin-left: 18px;
  padding: 0;
  font-size: 11px;
  color: #4b4b4b;
  display: flex;
  flex-wrap: wrap;
  gap: 5px 16px;
}

.hotel-carousel .htlamnts li {
  min-width: 110px;
}

.hotel-carousel .htlusp {
  color: #04a77a;
  font-size: 11px;
  display: flex;
  gap: 10px;
}

.hotel-carousel .htlusp span {
  position: relative;
  padding-left: 12px;
}

.hotel-carousel .htlusp span::before {
  content: '';
  position: absolute;
  left: 0;
  top: 2px;
  width: 4px;
  height: 8px;
  border-bottom: 2px solid #04a77a;
  border-right: 2px solid #04a77a;
  transform: rotate(45deg);
}

.hotel-carousel .bkbtn {
  border-radius: 40px;
  background: #ef6614;
  color: #fff;
  text-align: center;
  font-size: 12px;
  padding: 9px 15px;
  width: 100%;
  border: 0;
  transition: all 0.2s ease;
  cursor: pointer;
}

.hotel-carousel .bkbtn-link {
  display: block;
  margin-top: auto;
  text-decoration: none;
}

.hotel-carousel .bkbtn:hover {
  background: #e75806;
}

.hotel-carousel .vwrms {
  font-size: 11px;
  color: #ef6614;
  margin-top: 8px;
  text-align: center;
  cursor: pointer;
}

.hotel-carousel .hotel-carousel__empty {
  text-align: center;
  color: #646d74;
  padding: 60px 20px;
  font-size: 14px;
}

.hotel-carousel .view-all-link {
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
  display: inline-block;
  vertical-align: middle;
}

.hotel-carousel .view-all-link:hover {
  background: #2093ef;
  color: #fff;
  border-color: #2093ef;
}

.hotel-carousel.dark {
  background: #000;
  color: #fff;
}

.hotel-carousel.dark .htlcard {
  background: #000;
  border-color: #373737;
}

.hotel-carousel.dark .nmeorc,
.hotel-carousel.dark .htlcard,
.hotel-carousel.dark .dtldte {
  border-color: #373737;
  color: #fff;
}

.hotel-carousel.dark .htllcn,
.hotel-carousel.dark .sbttl,
.hotel-carousel.dark .revnmb,
.hotel-carousel.dark .htlcnt,
.hotel-carousel.dark .htlsub,
.hotel-carousel.dark .dtldte,
.hotel-carousel.dark .htlamnts li {
  color: #bcbcbc;
}

/* View All Card Styles */
.hotel-carousel .view-all-card {
  width: 300px;
  min-width: 300px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  position: relative;
  overflow: visible;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  color: inherit;
}

.hotel-carousel .view-all-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #2093ef;
}

/* Layered edge effect (book pages) */
.hotel-carousel .view-all-card::before,
.hotel-carousel .view-all-card::after {
  content: '';
  position: absolute;
  right: -6px;
  width: 100%;
  height: 100%;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  background: linear-gradient(135deg, #f0f1f3 0%, #d8dce0 100%);
  z-index: -1;
}

.hotel-carousel .view-all-card::before {
  right: -3px;
  height: 98%;
  top: 1%;
  opacity: 0.7;
}

.hotel-carousel .view-all-card::after {
  right: -6px;
  height: 96%;
  top: 2%;
  opacity: 0.5;
}

.hotel-carousel .view-all-card:hover::before {
  right: -4px;
}

.hotel-carousel .view-all-card:hover::after {
  right: -8px;
}

.hotel-carousel .view-all-card-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2093ef 0%, #1976d2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(32, 147, 239, 0.3);
}

.hotel-carousel .view-all-card-icon svg {
  width: 28px;
  height: 28px;
  color: #fff;
}

.hotel-carousel .view-all-card-title {
  font-size: 18px;
  font-weight: 700;
  color: #202020;
  margin-bottom: 8px;
  text-align: center;
}

.hotel-carousel .view-all-card-subtitle {
  font-size: 13px;
  color: #646d74;
  text-align: center;
  font-weight: 500;
  line-height: 1.4;
}

.dtldte {
  font-size: 13px;
  color: #666;
  margin-bottom: 10px;
  padding: 6px 10px;
  background: #fff8e1;
  border-radius: 4px;
  border-left: 3px solid #ffc107;
}

.htlamnts {
  list-style: none;
  padding: 0;
  margin: 12px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.htlamnts li {
  font-size: 12px;
  color: #444;
  padding: 4px 10px;
  background: #e8f5e9;
  border-radius: 12px;
  border: 1px solid #c8e6c9;
}

.htlusp {
  margin: 10px 0;
  padding: 6px 10px;
  background: #e3f2fd;
  border-radius: 4px;
  border-left: 3px solid #2196f3;
}

.htlusp span {
  font-size: 13px;
  font-weight: 600;
  color: #1565c0;
}

.bkbtn-link {
  display: block;
  text-decoration: none;
  margin-top: 12px;
}

.bkbtn {
  width: 100%;
  padding: 12px;
  background: #ef6614;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.bkbtn:hover {
  background: #d95a0f;
}

.vwrms {
  text-align: center;
  font-size: 13px;
  color: #1a73e8;
  margin-top: 8px;
  cursor: pointer;
}

/* Star icons as Unicode */
.star-filled::before {
  content: '★';
  color: #ffc107;
}

.star-empty::before {
  content: '☆';
  color: #ccc;
}
</style>

<div class="hotel-carousel">
  <main>
    <div class="htlhd">
      <div class="htlttl">
        {{ title }}
        {% if view_all_link %}
        <a href="{{ view_all_link }}" target="_blank" rel="noopener noreferrer" class="view-all-link">View All</a>
        {% endif %}
      </div>
      <div class="htlsub">{{ subtitle }}</div>
    </div>

    {% if hotels %}
    <div class="slider-shell">
      <div class="rsltcvr">
        <div class="embla__container">
        {% for hotel in hotels %}
          <div class="htlcard">
            <div class="img-top">
              <img src="{{ hotel.image }}" alt="{{ hotel.name }}">
            </div>
            <div class="htlcrdbdy">
              <div class="nmeorc">
                <div class="htlinfo">
                  <div class="rntgs" {% if hotel.rating %}aria-label="Rated {{ hotel.rating }} of 5"{% endif %}>
                    {% for i in range(5) %}
                      <img src="{% if hotel.rating and i < hotel.rating|round %}data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23FFC107'%3E%3Cpath d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'/%3E%3C/svg%3E{% else %}data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23BDBDBD'%3E%3Cpath d='M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z'/%3E%3C/svg%3E{% endif %}" alt="rating star">
                    {% endfor %}
                  </div>
                  <div class="htlnme" title="{{ hotel.name }}">{{ hotel.name | truncate_text(20) }}</div>
                  <div class="htllcn" title="{{ hotel.location }}">{{ hotel.location }}</div>
                </div>
                <div class="htlprcbx">
                  <div class="sbttl">{{ hotel.pricePrefix }}</div>
                  <div class="htlprc">{{ hotel.priceLabel }}</div>
                  <div class="sbttl">{{ hotel.nightlySubtitle }}</div>
                </div>
              </div>

              {% if hotel.usp %}
              <div class="htlusp">
                <span>{{ hotel.usp }}</span>
              </div>
              {% endif %}

              <a class="bkbtn-link" href="{{ hotel.deepLink }}" target="_blank" rel="noopener noreferrer">
                <button class="bkbtn" type="button">Book Now</button>
              </a>
            </div>
          </div>
        {% endfor %}

        {% if view_all_link %}
        <a href="{{ view_all_link }}" target="_blank" rel="noopener noreferrer" class="view-all-card">
          <div class="view-all-card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
            </svg>
          </div>
          <div class="view-all-card-title">View All</div>
          <div class="view-all-card-subtitle">Explore more hotel options</div>
        </a>
        {% endif %}
        </div>
      </div>
    </div>
    {% else %}
    <div class="hotel-carousel__empty">No hotels found for the selected dates.</div>
    {% endif %}
  </main>
</div>
"""

# =====================================================================
# 🔧 NORMALIZER — REAL EMT JSON → UI MODEL
# =====================================================================
def _parse_highlights(highlights) -> List[str]:
    """Parse highlights into a list of strings"""
    if not highlights:
        return []
    
    if isinstance(highlights, list):
        return [h for h in highlights if h]
    
    if isinstance(highlights, str):
        items = []
        for entry in highlights.replace('|', '\n').replace('•', '\n').split('\n'):
            cleaned = entry.strip()
            if cleaned:
                items.append(cleaned)
        return items[:5]
    
    return []


def _format_price(price) -> str:
    """Format price with currency"""
    if not price:
        return None
    
    if isinstance(price, dict):
        amount = price.get('amount')
        currency = price.get('currency', 'INR')
    else:
        amount = price
        currency = 'INR'
    
    if amount is None:
        return None
    
    try:
        amount_num = float(amount)
        if currency == 'INR':
            return f"₹{amount_num:,.0f}"
        return f"{currency} {amount_num:,.0f}"
    except (ValueError, TypeError):
        return str(amount)


def _get_discount_value(discount) -> float:
    """Extract numeric discount value"""
    if discount is None:
        return 0
    if isinstance(discount, (int, float)):
        return float(discount)
    if isinstance(discount, str):
        # Remove non-numeric characters and parse
        import re
        match = re.search(r'[\d.]+', discount)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return 0
    if isinstance(discount, dict) and 'amount' in discount:
        try:
            return float(discount['amount'])
        except (ValueError, TypeError):
            return 0
    return 0


def _resolve_location(hotel: Dict[str, Any]) -> str:
    """Resolve hotel location from various fields"""
    if hotel.get('location'):
        return hotel['location']
    
    segments = []
    for key in ['city', 'region', 'country']:
        if hotel.get(key):
            segments.append(hotel[key])
    
    return ', '.join(segments) if segments else 'Location unavailable'


def _get_rating_value(hotel: Dict[str, Any]) -> float:
    """Extract numeric rating from hotel data"""
    for key in ['rating', 'starRating', 'category', 'reviewScore', 'popularity']:
        value = hotel.get(key)
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                continue
    return None


def _get_review_label(rating: float) -> str:
    """Generate review label from rating"""
    if not rating:
        return None
    if rating >= 4.5:
        return "Excellent"
    if rating >= 4.0:
        return "Very Good"
    if rating >= 3.0:
        return "Good"
    return "Average"


def _build_amenities(hotel: Dict[str, Any], highlights: List[str]) -> List[str]:
    """Build amenities list from hotel data"""
    if isinstance(hotel.get('amenities'), list):
        return [a for a in hotel['amenities'] if a]
    return highlights


def _build_usp(hotel: Dict[str, Any]) -> str:
    """Build unique selling proposition"""
    if hotel.get('usp'):
        return hotel['usp']
    if hotel.get('free_cancellation') or hotel.get('freeCancellation'):
        return "Free Cancellation"
    if hotel.get('refundable'):
        return "Fully Refundable"
    if hotel.get('payAtHotel'):
        return "Pay at hotel"
    return None


def _format_short_date(value) -> str:
    """Format date as 'DD Mon'"""
    if not value:
        return None
    try:
        from datetime import datetime
        if isinstance(value, str):
            date = datetime.fromisoformat(value.replace('Z', '+00:00'))
        else:
            date = value
        return date.strftime('%d %b')
    except (ValueError, TypeError, AttributeError):
        return None


def _normalize_hotel_for_ui(hotel: Dict[str, Any], check_in=None, check_out=None) -> Dict[str, Any]:
    """
    Normalize hotel data from EMT API to UI-friendly format
    
    Args:
        hotel: Raw hotel data from EMT API
        check_in: Check-in date string
        check_out: Check-out date string
    
    Returns:
        Normalized hotel data for template rendering
    """
    highlights = _parse_highlights(hotel.get('highlights'))
    amenities = _build_amenities(hotel, highlights)
    
    # Handle pricing with discount
    base_price = hotel.get('price')
    discount_value = _get_discount_value(hotel.get('discount'))
    
    adjusted_price = base_price
    if base_price and isinstance(base_price, dict) and base_price.get('amount'):
        try:
            base_amount = float(base_price['amount'])
            final_amount = max(0, base_amount - discount_value)
            if final_amount != base_amount:
                adjusted_price = {**base_price, 'amount': final_amount}
        except (ValueError, TypeError):
            pass
    
    price_label = _format_price(adjusted_price)
    
    rating_value = _get_rating_value(hotel)
    review_label = (
        hotel.get('review_summary') or 
        hotel.get('reviewText') or 
        _get_review_label(rating_value)
    )
    
    review_count = (
        hotel.get('reviewCount') or
        hotel.get('review_count') or
        hotel.get('totalReviews') or
        hotel.get('reviews') or
        hotel.get('review_text')
    )
    
    if isinstance(review_count, (int, float)):
        review_count = f"{int(review_count)} reviews"
    
    usp = _build_usp(hotel)
    
    # Format stay dates
    stay_start = _format_short_date(check_in)
    stay_end = _format_short_date(check_out)
    stay_info = f"{stay_start} - {stay_end}" if stay_start and stay_end else None
    
    return {
        "name": hotel.get('name') or 'Hotel',
        "image": hotel.get('hotelImage') or hotel.get('image_url') or hotel.get('thumbnail'),
        "rating": rating_value,
        "location": _resolve_location(hotel),
        "priceLabel": price_label,
        "pricePrefix": hotel.get('price', {}).get('prefix') if hotel.get('price', {}).get('prefix')  else 'From',
        "nightlySubtitle": hotel.get('price', {}).get('label') if hotel.get('price', {}).get('label')  else 'per night',
        "ratingValue": rating_value,
        "reviewLabel": review_label,
        "reviewCount": review_count,
        "stayInfo": stay_info,
        "amenities": amenities,
        "usp": usp,
        "deepLink": hotel.get('deepLink') or hotel.get('booking_url') or hotel.get('url'),
    }

# =====================================================================
# 🎨 FINAL RENDERER (PURE, SAFE, COMPATIBLE)
# =====================================================================
def render_hotel_results(hotel_results: Dict[str, Any]) -> str:
    """
    Renders hotel results into HTML.
    
    Args:
        hotel_results: Hotel search results from API
    
    Returns:
        HTML string with rendered hotel cards
    """
    # Unwrap structured_content if present
    if "structured_content" in hotel_results:
        hotel_results = hotel_results["structured_content"]
    
    # Extract hotels list
    hotels = hotel_results.get("hotels") or hotel_results.get("results", [])
    
    if not hotels:
        return "<div class='hotel-carousel'><p>No hotels available.</p></div>"
    
    # Get date info
    check_in = (
        hotel_results.get('check_in') or 
        hotel_results.get('check_in_date') or 
        hotel_results.get('checkIn')
    )
    check_out = (
        hotel_results.get('check_out') or 
        hotel_results.get('check_out_date') or 
        hotel_results.get('checkOut')
    )
    
    # Build title and subtitle
    city = hotel_results.get('city') or hotel_results.get('city_name') or ''
    title = f"Stays in {city}" if city else "Hotel results"
    
    # Build subtitle (date range + travelers)
    subtitle_parts = []
    
    if check_in and check_out:
        try:
            from datetime import datetime
            start_date = datetime.fromisoformat(check_in.replace('Z', '+00:00')) if isinstance(check_in, str) else check_in
            end_date = datetime.fromisoformat(check_out.replace('Z', '+00:00')) if isinstance(check_out, str) else check_out
            
            start_str = start_date.strftime('%d %b')
            end_str = end_date.strftime('%d %b')
            
            # Calculate nights
            nights = (end_date - start_date).days
            nights_text = f"{nights} night{'s' if nights > 1 else ''}" if nights > 0 else ""
            
            date_range = f"{start_str} - {end_str}"
            if nights_text:
                date_range += f" • {nights_text}"
            subtitle_parts.append(date_range)
        except:
            subtitle_parts.append("Flexible dates")
    
    # Add travelers info
    adults = hotel_results.get('num_adults') or hotel_results.get('adults')
    children = hotel_results.get('num_children') or hotel_results.get('children')
    rooms = hotel_results.get('num_rooms') or hotel_results.get('rooms')
    
    traveler_parts = []
    if adults:
        traveler_parts.append(f"{adults} adult{'s' if adults > 1 else ''}")
    if children:
        traveler_parts.append(f"{children} child{'ren' if children > 1 else ''}")
    if rooms:
        traveler_parts.append(f"{rooms} room{'s' if rooms > 1 else ''}")
    
    if traveler_parts:
        subtitle_parts.append(', '.join(traveler_parts))
    
    subtitle = ' • '.join(subtitle_parts)
    
    # Normalize hotels for UI
    hotels_ui = [
        _normalize_hotel_for_ui(hotel, check_in, check_out)
        for hotel in hotels
    ]
    
    # Remove empty normalizations
    hotels_ui = [h for h in hotels_ui if h and h.get('name')]
    
    if not hotels_ui:
        return "<div class='hotel-carousel'><p>No hotels available.</p></div>"
    
    # Render template
    template = _jinja_env.from_string(HOTEL_CAROUSEL_TEMPLATE)
    return template.render(
        title=title,
        subtitle=subtitle,
        hotels=hotels_ui,
        view_all_link=hotel_results.get('viewAll'),
    )
