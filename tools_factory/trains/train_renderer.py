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
# 🚂 TRAIN RESULTS CAROUSEL TEMPLATE (EASEMYTRIP STYLE)
# =====================================================================
TRAIN_CAROUSEL_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

.train-carousel {
  font-family: poppins, sans-serif;
  color: #202020;
  background: rgba(255, 255, 255, 0.92);
  position: relative;
}

.train-carousel * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
}

.train-carousel main {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px 0 30px;
}

.train-carousel .trnhd {
  margin-bottom: 12px;
}

.train-carousel .trnttl {
  width: 90%;
  font-size: 18px;
  font-weight: 600;
  color: #202020;
}

.train-carousel .trnsub {
  font-size: 12px;
  color: #646d74;
  margin-top: 4px;
}

.train-carousel .slider-shell {
  position: relative;
}

.train-carousel .rsltcvr {
  width: 90%;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  cursor: grab;
}

.train-carousel .rsltcvr:active {
  cursor: grabbing;
}

.train-carousel .embla__container {
  display: flex;
  gap: 20px;
}

.train-carousel .trncard {
  width: 320px;
  min-width: 260px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fff;
  padding: 14px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.train-carousel .trn-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
  margin-bottom: 10px;
  gap: 10px;
}

.train-carousel .trn-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.train-carousel .trn-details {
  flex: 1;
}

.train-carousel .trn-name {
  font-size: 15px;
  font-weight: 600;
  color: #202020;
  line-height: 1.3;
}

.train-carousel .trn-route {
  font-size: 11px;
  color: #646d74;
  margin-top: 4px;
}

.train-carousel .trn-number {
    font-weight: 500;
    font-size: 14px;
    width: auto;
    padding: 3px 5px;
    color: #313131;
    background: #F2F9FF;
    border: 1px solid #B6D5F0;
    border-radius: 3px;
    float: left;
}

.train-carousel .trn-timing {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
}

.train-carousel .trn-time-block {
  text-align: center;
  flex: 1;
}

.train-carousel .trn-time {
  font-size: 16px;
  font-weight: 700;
  color: #202020;
  font-family: inter, sans-serif;
}

.train-carousel .trn-station {
  font-size: 10px;
  color: #868686;
  margin-top: 2px;
  text-transform: uppercase;
}

.train-carousel .trn-duration-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 8px;
  min-width: 80px;
}

.train-carousel .trn-duration {
  font-size: 10px;
  color: #646d74;
  font-weight: 500;
  white-space: nowrap;
  margin-bottom: 4px;
}

.train-carousel .trn-duration-line {
  width: 100%;
  height: 1px;
  background: #ccc;
  position: relative;
}

.train-carousel .trn-duration-line::before,
.train-carousel .trn-duration-line::after {
  content: '';
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ccc;
}

.train-carousel .trn-duration-line::before {
  left: 0;
}

.train-carousel .trn-duration-line::after {
  right: 0;
}

.train-carousel .trn-distance {
  font-size: 9px;
  color: #868686;
  margin-top: 4px;
}

.train-carousel .trn-days {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.train-carousel .trn-day {
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 4px;
  background: #e8f5e9;
  color: #2e7d32;
  font-weight: 500;
}

.train-carousel .trn-day.inactive {
  background: #f5f5f5;
  color: #bdbdbd;
}

/* Class Carousel inside train card */
.train-carousel .class-carousel-wrapper {
  margin-top: auto;
}

.train-carousel .class-carousel {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: thin;
  scrollbar-color: #ccc transparent;
}

.train-carousel .class-carousel::-webkit-scrollbar {
  height: 4px;
}

.train-carousel .class-carousel::-webkit-scrollbar-track {
  background: transparent;
}

.train-carousel .class-carousel::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}

.train-carousel .class-card {
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

.train-carousel .class-card:hover {
  border-color: #ef6614;
  box-shadow: 0 2px 8px rgba(239, 102, 20, 0.15);
}

.train-carousel .class-code {
  font-size: 13px;
  font-weight: 700;
  color: #202020;
}

.train-carousel .class-fare {
  font-size: 14px;
  font-weight: 700;
  color: #202020;
  font-family: inter, sans-serif;
  margin-top: 6px;
}

.train-carousel .class-fare-updated {
  font-size: 8px;
  color: #868686;
  margin-top: 2px;
}

.train-carousel .class-availability {
  font-size: 9px;
  margin-top: auto;
  padding-top: 4px;
  font-weight: 500;
}

.train-carousel .class-availability.available {
  color: #2e7d32;
}

.train-carousel .class-availability.waitlist {
  color: #f57c00;
}

.train-carousel .class-availability.rac {
  color: #1976d2;
}

.train-carousel .class-availability.unavailable {
  color: #d32f2f;
}

.train-carousel .class-book-btn {
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

.train-carousel .class-book-btn:hover {
  background: #e75806;
}

.train-carousel .class-book-btn.disabled {
  background: #ccc;
  color: #888;
  cursor: not-allowed;
  pointer-events: none;
  opacity: 0.6;
}

.train-carousel .class-book-btn.disabled:hover {
  background: #ccc;
}

.train-carousel .class-refresh-btn {
  margin-top: 6px;
  padding: 7px 8px;
  background: #fff;
  color: #2093ef;
  border: 1px solid #2093ef;
  border-radius: 6px;
  font-size: 9px;
  font-weight: 600;
  cursor: pointer;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.2s ease;
}

.train-carousel .class-refresh-btn:hover {
  background: #2093ef;
  color: #fff;
}

.train-carousel .class-refresh-btn.loading {
  pointer-events: none;
  opacity: 0.7;
}

.train-carousel .class-refresh-btn .refresh-icon {
  width: 12px;
  height: 12px;
}

.train-carousel .class-refresh-btn.loading .refresh-icon {
  animation: spin 1s linear infinite;
}

.train-carousel .class-refresh-icon-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  padding: 0;
}

.train-carousel .class-refresh-icon-btn:hover {
  background: #f5f5f5;
  border-color: #2093ef;
}

.train-carousel .class-refresh-icon-btn.loading {
  pointer-events: none;
  opacity: 0.7;
}

.train-carousel .class-refresh-icon-btn img {
  width: 14px;
  height: 14px;
}

.train-carousel .class-refresh-icon-btn.loading img {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.train-carousel .view-all-link {
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

.train-carousel .view-all-link:hover {
  background: #2093ef;
  color: #fff;
  border-color: #2093ef;
}

.train-carousel .train-carousel__empty {
  text-align: center;
  color: #646d74;
  padding: 60px 20px;
  font-size: 14px;
}

/* View All Card Styles */
.train-carousel .view-all-card {
  width: 320px;
  min-width: 260px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 280px;
  position: relative;
  overflow: visible;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  color: inherit;
}

.train-carousel .view-all-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #2093ef;
}

.train-carousel .view-all-card::before,
.train-carousel .view-all-card::after {
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

.train-carousel .view-all-card::before {
  right: -3px;
  height: 98%;
  top: 1%;
  opacity: 0.7;
}

.train-carousel .view-all-card::after {
  right: -6px;
  height: 96%;
  top: 2%;
  opacity: 0.5;
}

.train-carousel .view-all-card-icon {
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

.train-carousel .view-all-card-icon svg {
  width: 28px;
  height: 28px;
  color: #fff;
}

.train-carousel .view-all-card-title {
  font-size: 18px;
  font-weight: 700;
  color: #202020;
  margin-bottom: 8px;
  text-align: center;
}

.train-carousel .view-all-card-subtitle {
  font-size: 13px;
  color: #646d74;
  text-align: center;
  font-weight: 500;
  line-height: 1.4;
}

/* Dark mode support */
.train-carousel.dark {
  background: #000;
  color: #fff;
}

.train-carousel.dark .trncard {
  background: #000;
  border-color: #373737;
}

.train-carousel.dark .trn-header,
.train-carousel.dark .trncard {
  border-color: #373737;
  color: #fff;
}

.train-carousel.dark .trn-name,
.train-carousel.dark .trn-time,
.train-carousel.dark .class-code,
.train-carousel.dark .class-fare {
  color: #fff;
}

.train-carousel.dark .trn-number,
.train-carousel.dark .trn-route,
.train-carousel.dark .trn-station,
.train-carousel.dark .trn-duration,
.train-carousel.dark .trn-distance,
.train-carousel.dark .trnsub,
.train-carousel.dark .class-fare-updated {
  color: #bcbcbc;
}

.train-carousel.dark .trn-timing {
  background: #1a1a1a;
}

.train-carousel.dark .class-card {
  background: #1a1a1a;
  border-color: #373737;
}
</style>

<div class="train-carousel round-trip-selector" data-instance-id="train-carousel-{{ instance_id }}">
  <main>
    <div class="trnhd">
      <div class="trnttl">
        {{ title }}
        {% if view_all_link %}
        <a href="{{ view_all_link }}" target="_blank" rel="noopener noreferrer" class="view-all-link">View All</a>
        {% endif %}
      </div>
      <div class="trnsub">{{ subtitle }}</div>
    </div>

    {% if trains %}
    <div class="slider-shell">
      <div class="rsltcvr">
        <div class="embla__container">
        {% for train in trains %}
          <div class="trncard">
            <div class="trn-header">
              <div class="trn-info">
                <div class="trn-details">
                  <div class="trn-name">{{ train.train_name | truncate_text(22) }}</div>
                  <div class="trn-route">{{ train.from_station_code }} → {{ train.to_station_code }}</div>
                </div>
                <div class="trn-number">{{ train.train_number }}</div>
              </div>
            </div>

            <div class="trn-timing">
              <div class="trn-time-block">
                <div class="trn-time">{{ train.departure_time }}</div>
                <div class="trn-station">{{ train.from_station_code }}</div>
              </div>
              <div class="trn-duration-block">
                <div class="trn-duration">{{ train.duration }}</div>
                <div class="trn-duration-line"></div>
                {% if train.distance %}
                <div class="trn-distance">{{ train.distance }} km</div>
                {% endif %}
              </div>
              <div class="trn-time-block">
                <div class="trn-time">{{ train.arrival_time }}</div>
                <div class="trn-station">{{ train.to_station_code }}</div>
              </div>
            </div>

            {% if train.running_days %}
            <div class="trn-days">
              {% for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] %}
              <span class="trn-day {% if day not in train.running_days %}inactive{% endif %}">{{ day }}</span>
              {% endfor %}
            </div>
            {% endif %}

            <div class="class-carousel-wrapper">
              <div class="class-carousel">
                {% for cls in train.classes %}
                {% set is_regret = 'REGRET' in cls.availability_status or 'NOT AVAILABLE' in cls.availability_status or 'TRAIN CANCELLED' in cls.availability_status %}
                {% set is_bookable = 'AVAILABLE' in cls.availability_status or 'WL' in cls.availability_status or 'RAC' in cls.availability_status or cls.availability_status == 'Check Online' %}
                {% set needs_refresh = cls.availability_status in ['N/A', 'Tap To Refresh', 'Check Online', ''] or not cls.availability_status %}
                <div class="class-card" data-train-no="{{ train.train_number }}" data-class-code="{{ cls.class_code }}" data-from-code="{{ train.from_station_code }}" data-to-code="{{ train.to_station_code }}" data-quota="{{ cls.quota or quota }}" data-journey-date="{{ journey_date_api }}" data-from-display="{{ from_display }}" data-to-display="{{ to_display }}">
                  <button type="button" class="class-refresh-icon-btn" title="Refresh availability">
                    <img src="https://railways.easemytrip.com/img/refresh-icon.svg" alt="Refresh" />
                  </button>
                  <div class="class-code">{{ cls.class_code }}</div>
                  {% if cls.fare != "0" %}
                  <div class="class-fare">₹{{ cls.fare }}</div>
                  {% if cls.fare_updated %}
                  <div class="class-fare-updated">{{ cls.fare_updated }}</div>
                  {% endif %}
                  {% endif %}
                  <div class="class-availability {% if is_regret %}unavailable{% elif 'WL' in cls.availability_status %}waitlist{% elif 'RAC' in cls.availability_status %}rac{% elif 'AVAILABLE' in cls.availability_status %}available{% elif cls.availability_status == 'Check Online' %}{% else %}unavailable{% endif %}">
                    {% if needs_refresh and cls.quota == 'TQ' %}Tatkal{% else %}{{ cls.availability_status | truncate_text(15) }}{% endif %}
                  </div>
                  {% if needs_refresh %}
                  <button type="button" class="class-refresh-btn">
                    <svg class="refresh-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Tap To Refresh
                  </button>
                  {% elif cls.book_now %}
                  <a href="{% if is_regret %}javascript:void(0){% else %}{{ cls.book_now }}{% endif %}" {% if not is_regret %}target="_blank" rel="noopener noreferrer"{% endif %} class="class-book-btn {% if is_regret %}disabled{% endif %}">{% if cls.quota == 'TQ' %}Book Tatkal{% else %}Book Now{% endif %}</a>
                  {% endif %}
                </div>
                {% endfor %}
              </div>
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
          <div class="view-all-card-subtitle">Explore more train options</div>
        </a>
        {% endif %}
        </div>
      </div>
    </div>
    {% else %}
    <div class="train-carousel__empty">No trains found for the selected route and date.</div>
    {% endif %}
  </main>
</div>

<script>
function buildBookNowUrl(card, classCode) {
  const trainNo = card.dataset.trainNo;
  const fromCode = card.dataset.fromCode;
  const toCode = card.dataset.toCode;
  const quota = card.dataset.quota || 'GN';
  const journeyDate = card.dataset.journeyDate;
  const fromDisplay = card.dataset.fromDisplay;
  const toDisplay = card.dataset.toDisplay;

  const dateParts = journeyDate.split('/');
  const dateFormatted = `${parseInt(dateParts[0])}-${parseInt(dateParts[1])}-${dateParts[2]}`;

  const fromName = fromDisplay.split('(')[0].trim().replace(/ /g, '-');
  const toName = toDisplay.split('(')[0].trim().replace(/ /g, '-');

  return `https://railways.easemytrip.com/TrainInfo/${fromName}-to-${toName}/${classCode}/${trainNo}/${fromCode}/${toCode}/${quota}/${dateFormatted}`;
}

async function refreshAvailability(btn) {
  const card = btn.closest('.class-card');
  const trainNo = card.dataset.trainNo;
  const classCode = card.dataset.classCode;
  const fromCode = card.dataset.fromCode;
  const toCode = card.dataset.toCode;
  const quota = card.dataset.quota || 'GN';
  const journeyDate = card.dataset.journeyDate;
  const fromDisplay = card.dataset.fromDisplay;
  const toDisplay = card.dataset.toDisplay;

  const iconBtn = card.querySelector('.class-refresh-icon-btn');
  if (iconBtn) {
    iconBtn.classList.add('loading');
  }

  const isIconBtn = btn.classList.contains('class-refresh-icon-btn');
  if (!isIconBtn) {
    btn.classList.add('loading');
    btn.innerHTML = '<svg class="refresh-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg> Loading...';
  }

  try {
    const payload = {
      cls: classCode,
      trainNo: trainNo,
      quotaSelectdd: quota,
      fromstation: fromCode,
      tostation: toCode,
      e: `${journeyDate}|${fromDisplay}|${toDisplay}`,
      lstSearch: {
        SelectQuta: "",
        arrivalTime: "",
        atasOpted: "",
        avlClasses: [{ code: "", Name: "", TotalPrice: "" }],
        departureTime: "",
        distance: "",
        duration: "",
        flexiFlag: "",
        fromStnName: "",
        fromStnCode: "",
        runningFri: "",
        runningMon: "",
        runningSat: "",
        runningSun: "",
        runningThu: "",
        runningTue: "",
        runningWed: "",
        toStnCode: "",
        toStnName: "",
        trainName: "",
        trainNumber: "",
        trainType: [{ code: "", Name: "", TotalPrice: null }],
        JourneyDate: null,
        ArrivalDate: "",
        departuredate: "",
        _TrainAvilFare: [],
        DistanceFromSrc: "",
        DistanceFromDest: "",
        DeptTime_12: null,
        ArrTime_12: null,
        TrainClassWiseFare: [],
        isCheckAvaibility: false,
        isShowClass: false,
        isShowQuota: false,
        NearByStation: ""
      },

      Searchsource: "",
      Searchdestination: "",
      tkn: "",
      IPAdress: ""
    };


    const response = await fetch('https://railways.easemytrip.com/Train/AvailToCheck', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    let availability = 'N/A';
    let fareUpdated = '';
    let totalFare = null;

    if (data.avlDayList && data.avlDayList.length > 0) {
      availability = data.avlDayList[0].availablityStatusNew || 'N/A';
    }
    if (data.creationTime) {
      fareUpdated = data.creationTime;
    }
    if (data.totalFare) {
      totalFare = data.totalFare;
    }

    if (totalFare && totalFare !== '0') {
      let fareEl = card.querySelector('.class-fare');
      if (!fareEl) {
        fareEl = document.createElement('div');
        fareEl.className = 'class-fare';
        const classCodeEl = card.querySelector('.class-code');
        if (classCodeEl) {
          classCodeEl.after(fareEl);
        }
      }
      fareEl.textContent = '₹' + totalFare;
    }

    const availabilityEl = card.querySelector('.class-availability');
    if (availabilityEl) {
      availabilityEl.textContent = availability.length > 15 ? availability.substring(0, 15) + '...' : availability;

      availabilityEl.classList.remove('available', 'waitlist', 'rac', 'unavailable');
      if (availability.includes('REGRET') || availability.includes('NOT AVAILABLE') || availability.includes('CANCELLED')) {
        availabilityEl.classList.add('unavailable');
      } else if (availability.includes('WL')) {
        availabilityEl.classList.add('waitlist');
      } else if (availability.includes('RAC')) {
        availabilityEl.classList.add('rac');
      } else if (availability.includes('AVAILABLE')) {
        availabilityEl.classList.add('available');
      } else {
        availabilityEl.classList.add('unavailable');
      }
    }

    if (fareUpdated) {
      let fareUpdatedEl = card.querySelector('.class-fare-updated');
      if (!fareUpdatedEl) {
        fareUpdatedEl = document.createElement('div');
        fareUpdatedEl.className = 'class-fare-updated';
        const fareEl = card.querySelector('.class-fare');
        if (fareEl) {
          fareEl.after(fareUpdatedEl);
        } else {
          const availabilityEl = card.querySelector('.class-availability');
          if (availabilityEl) {
            availabilityEl.before(fareUpdatedEl);
          }
        }
      }
      fareUpdatedEl.textContent = fareUpdated;
    }

    if (iconBtn) {
      iconBtn.classList.remove('loading');
    }

    const textRefreshBtn = card.querySelector('.class-refresh-btn');
    if (textRefreshBtn) {
      textRefreshBtn.remove();
    }

    const bookBtn = card.querySelector('.class-book-btn');
    if (!bookBtn) {
      const newBookBtn = document.createElement('a');
      newBookBtn.className = 'class-book-btn';
      newBookBtn.textContent = quota === 'TQ' ? 'Book Tatkal' : 'Book Now';
      newBookBtn.target = '_blank';
      newBookBtn.rel = 'noopener noreferrer';

      const isRegret = availability.includes('REGRET') ||
                       availability.includes('NOT AVAILABLE') ||
                       availability.includes('CANCELLED');

      if (isRegret) {
        newBookBtn.href = 'javascript:void(0)';
        newBookBtn.classList.add('disabled');
      } else {
        const bookNowUrl = buildBookNowUrl(card, classCode);
        newBookBtn.href = bookNowUrl;
      }

      card.appendChild(newBookBtn);
    }

  } catch (error) {
    console.error('Error refreshing availability:', error);

    if (iconBtn) {
      iconBtn.classList.remove('loading');
    }

    const isIconBtn = btn.classList.contains('class-refresh-icon-btn');
    if (!isIconBtn) {
      btn.classList.remove('loading');
      btn.innerHTML = '<svg class="refresh-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg> Retry';
    }
  }
}

document.querySelectorAll('.class-refresh-icon-btn, .class-refresh-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    refreshAvailability(this);
  });
});
</script>
"""


# =====================================================================
# 🔧 NORMALIZER — TRAIN DATA → UI MODEL
# =====================================================================
def _get_availability_class(status: str) -> str:
    """Determine CSS class for availability status"""
    if not status:
        return "unavailable"
    status_upper = status.upper()
    if "AVAILABLE" in status_upper:
        return "available"
    if "WL" in status_upper or "WAITLIST" in status_upper:
        return "waitlist"
    if "RAC" in status_upper:
        return "rac"
    return "unavailable"


def _parse_fare_updated(fare_updated: str) -> str:
    """Extract the time portion from fare_updated string (e.g., '7 hours ago')"""
    if not fare_updated:
        return ""
    # Return as-is since it's already in the right format like "7 hours ago"
    return fare_updated


def _normalize_train_for_ui(train: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize train data for UI rendering.

    Args:
        train: Raw train data from search results

    Returns:
        Normalized train data for template rendering
    """
    classes = []
    tatkal_classes = []
    general_classes = []
    other_classes = []

    # First, separate classes by quota
    for cls in train.get("classes", []):
        quota = cls.get("quota", "GN")
        class_data = {
            "class_code": cls.get("class_code", ""),
            "fare": cls.get("fare", "0"),
            "fare_updated": _parse_fare_updated(cls.get("fare_updated", "")),
            "availability_status": cls.get("availability_status", "N/A"),
            "book_now": cls.get("book_now", ""),
            "quota": quota,
            "quota_name": cls.get("quota_name", ""),
        }

        if quota == "TQ":
            tatkal_classes.append(class_data)
        elif quota == "GN":
            general_classes.append(class_data)
        else:
            other_classes.append(class_data)

    # Prioritize: Tatkal first, then general, then other quotas
    classes = tatkal_classes + general_classes + other_classes

    return {
        "train_number": train.get("train_number", ""),
        "train_name": train.get("train_name", ""),
        "from_station_code": train.get("from_station_code", ""),
        "from_station_name": train.get("from_station_name", ""),
        "to_station_code": train.get("to_station_code", ""),
        "to_station_name": train.get("to_station_name", ""),
        "departure_time": train.get("departure_time", ""),
        "arrival_time": train.get("arrival_time", ""),
        "duration": train.get("duration", ""),
        "distance": train.get("distance", ""),
        "departure_date": train.get("departure_date", ""),
        "arrival_date": train.get("arrival_date", ""),
        "running_days": train.get("running_days", []),
        "classes": classes,
    }


def _format_journey_date(date_str: str) -> str:
    """Format journey date for display"""
    if not date_str:
        return ""
    try:
        from datetime import datetime
        # Parse DD-MM-YYYY format
        dt = datetime.strptime(date_str, "%d-%m-%Y")
        return dt.strftime("%d %b %Y")
    except ValueError:
        return date_str


# =====================================================================
# 🎨 FINAL RENDERER
# =====================================================================
def render_train_results(train_results: Dict[str, Any]) -> str:
    """
    Renders train results into HTML.

    Args:
        train_results: Train search results from API

    Returns:
        HTML string with rendered train cards
    """
    # Unwrap structured_content if present
    if "structured_content" in train_results:
        train_results = train_results["structured_content"]

    # Extract trains list
    trains = train_results.get("trains", [])

    if not trains:
        return "<div class='train-carousel'><div class='train-carousel__empty'>No trains found for the selected route and date.</div></div>"

    # Extract route info
    from_station = train_results.get("from_station", "")
    to_station = train_results.get("to_station", "")
    journey_date = train_results.get("journey_date", "")

    # Extract station names from "Station Name (CODE)" format
    from_name = from_station.split("(")[0].strip() if "(" in from_station else from_station
    to_name = to_station.split("(")[0].strip() if "(" in to_station else to_station

    # Build title
    title = f"Trains from {from_name} to {to_name}" if from_name and to_name else "Train Results"

    # Build subtitle
    subtitle_parts = []
    if journey_date:
        formatted_date = _format_journey_date(journey_date)
        if formatted_date:
            subtitle_parts.append(formatted_date)

    total_count = train_results.get("total_count", len(trains))
    subtitle_parts.append(f"{total_count} train{'s' if total_count != 1 else ''} found")

    quota = train_results.get("quota", "GN")
    quota_labels = {
        "GN": "General",
        "TQ": "Tatkal",
        "SS": "Senior Citizen",
        "LD": "Ladies",
    }
    if quota in quota_labels:
        subtitle_parts.append(f"{quota_labels[quota]} Quota")

    subtitle = " • ".join(subtitle_parts)

    # Normalize trains for UI
    trains_ui = [_normalize_train_for_ui(train) for train in trains]

    # Remove empty normalizations
    trains_ui = [t for t in trains_ui if t and t.get("train_number")]

    if not trains_ui:
        return "<div class='train-carousel'><div class='train-carousel__empty'>No trains found for the selected route and date.</div></div>"

    # Convert journey_date to API format (DD/MM/YYYY) for refresh calls
    journey_date_api = ""
    if journey_date:
        # Journey date is already in DD-MM-YYYY format, just replace hyphens with slashes
        journey_date_api = journey_date.replace("-", "/")

    # Generate unique instance ID for script injection
    import uuid
    instance_id = str(uuid.uuid4())[:8]

    # Render template
    template = _jinja_env.from_string(TRAIN_CAROUSEL_TEMPLATE)
    return template.render(
        title=title,
        subtitle=subtitle,
        trains=trains_ui,
        view_all_link=train_results.get("view_all_link"),
        quota=quota,
        journey_date_api=journey_date_api,
        from_display=from_station,
        to_display=to_station,
        instance_id=instance_id,
    )
