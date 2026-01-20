from typing import Dict, Any, List, Optional
from jinja2 import Environment, BaseLoader, select_autoescape


_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)

# =====================================================================
# ✈️ FLIGHT RESULTS CAROUSEL TEMPLATES
# =====================================================================

# Base styles for all flight carousels
BASE_FLIGHT_STYLES = """
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

.flight-carousel {
  font-family: poppins, sans-serif;
}

.flight-carousel * {
  font-family: poppins, sans-serif;
  box-sizing: border-box;
  margin: 0;
}

.flight-carousel main {
  max-width: 700px;
  margin: auto;
  padding: 20px 0;
}

.flight-carousel .rslt-heading {
  margin-bottom: 12px;
}

.flight-carousel .rslttp {
  padding: 0 0 8px;
}

.flight-carousel .ntfctl {
  font-size: 15px;
  font-weight: 600;
  color: #202020;
  display: flex;
  gap: 5px;
  align-items: center;
}

.flight-carousel .ntfsbt {
  font-size: 8px;
  color: #868686;
  font-weight: 500;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.flight-carousel .fltcardbx {
  width: 100%;
  padding: 8px 6px;
}

.flight-carousel .rsltcvr {
  max-width: 100%;
  overflow-x: auto;
  display: flex;
  gap: 20px;
  cursor: grab;
}

.flight-carousel .rsltcvr::-webkit-scrollbar {
  height: 7px;
}

.flight-carousel .rsltcvr::-webkit-scrollbar-track {
  background: #fff;
}

.flight-carousel .rsltcvr::-webkit-scrollbar-thumb {
  background: #373737;
  border-radius: 5px;
}

.flight-carousel .rsltcvr:active {
  cursor: grabbing;
}

.flight-carousel .fltcard {
  padding: 10px;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  min-width: 250px;
  width: 250px;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.flight-carousel .ntfchdr {
  padding: 0 0 8px;
  display: flex;
  gap: 10px;
  align-items: center;
  border-bottom: 1px solid #e0e0e0;
}

.flight-carousel .ntflogo {
  height: 35px;
  width: 35px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.flight-carousel .ntflogo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.flight-carousel .ntfctlx {
  display: flex;
  justify-content: space-between;
  flex-direction: column;
  flex: 1;
}

.flight-carousel .fltbdy {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
}

.flight-carousel .flttme {
  font-size: 19px;
  font-weight: 600;
}

.flight-carousel .jrny {
  text-align: center;
}

.flight-carousel .jrnttl {
  font-size: 11px;
  color: #868686;
}

.flight-carousel .j-br {
  width: 55px;
  border-bottom: 1px solid #9e9da1;
  position: relative;
  margin: 4px 0;
}

.flight-carousel .j-br.lyovr::after {
  content: "";
  height: 6px;
  width: 6px;
  background: #2196f3;
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.flight-carousel .fltftr {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 8px;
  border-top: 1px solid #e0e0e0;
}

.flight-carousel .ntfsbt-ftr {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
}

.flight-carousel .st {
  color: #d05404;
  font-weight: 600;
}

.flight-carousel .fltprcbx {
    display: flex;
    flex-direction: column;
    align-items: flex-end; /* pushes both to the right */
    text-align: right;
    justify-content: space-between;
}

.flight-carousel .sbttl {
  font-size: 9px;
  color: #868686;
}

.flight-carousel .fltprc {
  font-size: 18px;
  font-weight: 700;
  margin-left: 15px;
}

.flight-carousel .bkbtn {
  border-radius: 40px;
  background: #ef6614;
  color: #fff;
  text-align: center;
  font-size: 12px;
  padding: 9px 15px;
  width: 100%;
  border: 0;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s ease;
}

.flight-carousel .bkbtn:hover {
  background: #e75806;
}

.flight-carousel .emt-empty {
  padding: 60px 20px;
  text-align: center;
  color: #646d74;
  font-size: 14px;
  font-weight: 500;
}

.flight-carousel .emt-inline-arrow {
  width: 14px;
  height: auto;
  object-fit: contain;
  vertical-align: baseline;
}

.flight-carousel .view-all-link {
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

.flight-carousel .view-all-link:hover {
  background: #2093ef;
  color: #fff;
  border-color: #2093ef;
}
"""

# Specific styles for domestic roundtrip
DOMESTIC_ROUNDTRIP_STYLES = """
.round-trip-selector .selector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.round-trip-selector .selector-heading {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.round-trip-selector .selector-heading .route {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
  color: #202020;
}

.round-trip-selector .selector-heading .meta {
  font-size: 12px;
  color: #646d74;
}

.round-trip-selector .selectable-flight {
  display: block;
  padding: 6px;
  border: 1px solid transparent;
  border-radius: 14px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  position: relative;
}

.round-trip-selector .selectable-flight:hover {
  border-color: #bcdffc;
}

.round-trip-selector .selectable-flight.is-selected {
  border-color: #2093ef;
  box-shadow: 0 6px 22px rgba(32, 147, 239, 0.12);
}

.round-trip-selector .selectable-flight__radio {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  cursor: pointer;
  user-select: none;
  font-weight: 600;
  color: #202020;
  position: relative;
}

.round-trip-selector .selectable-flight__hint {
  font-size: 12px;
  color: #646d74;
  font-weight: 500;
}

.round-trip-selector .selectable-flight input[type="radio"] {
  position: absolute;
  top: 0;
  left: 0;
  opacity: 0;
  pointer-events: none;
}

.round-trip-selector .selectable-flight .dtlchkmark {
  height: 16px;
  width: 16px;
  outline: 2px solid #e0e0e0;
  border-radius: 50%;
  transition: all 0.2s ease;
  display: inline-block;
  position: relative;
}

.round-trip-selector .selectable-flight.is-selected .dtlchkmark,
.round-trip-selector .selectable-flight .selectable-flight__radio:hover .dtlchkmark {
  outline-color: #2093ef;
}

.round-trip-selector .selectable-flight.is-selected .dtlchkmark {
  background-color: #2093ef;
  border: 2px solid #fff;
}

.round-trip-selector .selectable-flight.is-selected .dtlchkmark::after {
  content: "";
  position: absolute;
  inset: 3px;
  background: #fff;
  border-radius: 50%;
}

.round-trip-selector .selectable-flight .fltcard .bkbtn {
  display: none !important;
}

.round-trip-selector .book-action {
  margin-top: 18px;
  display: flex;
  justify-content: flex-end;
}

.round-trip-selector .book-action .bkbtn {
  width: auto;
  padding: 12px 22px;
  font-size: 14px;
  font-weight: 700;
}
"""

# Specific styles for international roundtrip
INTERNATIONAL_ROUNDTRIP_STYLES = """
.fltcardInternational {
  padding: 10px;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  min-width: 475px;
  width: 475px;
  background: #fff;
}

.trpcvr {
  display: flex;
  gap: 20px;
  justify-content: space-between;
}

.rndtrpcvr {
  flex: 1;
}

.trpdvdr {
  width: 1px;
  background: #e0e0e0;
}

.rndhd {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.rndttl {
  font-size: 16px;
  font-weight: 600;
}

.fltprcbx {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.arlnme {
  font-size: 14px;
  font-weight: 600;
}

.tryp {
  color: #2093ef;
}


.bkbtnInternational {
  margin-top: 10px;
  width: 100%;
  border-radius: 40px;
  background: #ef6614;
  color: #fff;
  font-size: 12px;
  padding: 9px 15px;
  border: 0;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s ease;
  text-align: center;
}

.bkbtnInternational:hover {
  background: #e75806;
}
"""

# =====================================================================
# ONE WAY FLIGHT TEMPLATE
# =====================================================================
ONEWAY_FLIGHT_TEMPLATE = """
<style>
{{ styles }}

/* FIX: inline route arrow size */
.emt-inline-arrow {
  width: 12px;
  height: 12px;
  margin: 0 6px;
  vertical-align: middle;
  display: inline-block;
}
</style>

<div class="flight-carousel">
  <main>
    <div class="rslttp rslt-heading">
      <div class="ntfctl">
        <span>{{ origin }}</span>
        <img
          class="emt-inline-arrow"
          src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='15.728' height='8.101' viewBox='0 0 15.728 8.101'%3E%3Cpath d='M16.536,135.588h0l-3.414-3.4a.653.653,0,0,0-.922.926l2.292,2.281H1.653a.653.653,0,1,0,0,1.307H14.492L12.2,138.985a.653.653,0,0,0,.922.926l3.414-3.4h0A.654.654,0,0,0,16.536,135.588Z' transform='translate(-1 -132)' fill='%23202020'/%3E%3C/svg%3E"
          alt="→"
        />
        <span>{{ destination }}</span>
        {% if view_all_link %}
        <a href="{{ view_all_link }}" target="_blank" rel="noopener noreferrer" class="view-all-link">View All</a>
        {% endif %}
      </div>
      <div class="ntfsbt">
        <span>Oneway</span> •
        <span>{{ departure_date }}</span> •
        {# <span>{{ flight_count }} option{{ 's' if flight_count != 1 else '' }}</span> #}
        <span>{{ cabin }}</span>
      </div>
    </div>

    <div class="fltcardbx">
      <div class="rsltcvr">
        {% for flight in flights %}
        <div class="fltcard item">
          <div class="ntfchdr">
            <div class="ntflogo">
              <img src="{{ flight.airline_logo }}" alt="{{ flight.airline_name }}" />
            </div>
            <div class="ntfctlx">
              <div class="ntfctl">
                <span>{{ flight.origin }}</span>
                <img
                  class="emt-inline-arrow"
                  src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='15.728' height='8.101' viewBox='0 0 15.728 8.101'%3E%3Cpath d='M16.536,135.588h0l-3.414-3.4a.653.653,0,0,0-.922.926l2.292,2.281H1.653a.653.653,0,1,0,0,1.307H14.492L12.2,138.985a.653.653,0,0,0,.922.926l3.414-3.4h0A.654.654,0,0,0,16.536,135.588Z' transform='translate(-1 -132)' fill='%23202020'/%3E%3C/svg%3E"
                  alt="→"
                />
                <span>{{ flight.destination }}</span>
              </div>
              <div class="ntfsbt">
                <span>{{ flight.airline_name }} {{ flight.flight_number }}</span>
              </div>
            </div>
            <div class="fltprcbx">
              <div class="fltprc">{{ flight.fare }}</div>
              <div class="sbttl">total fare</div>
            </div>
          </div>

          <div class="fltbdy">
            <div class="flttme">{{ flight.departure_time }}</div>
            <div class="jrny">
              <div class="jrnttl">{{ flight.journey_time }}</div>
              <div class="j-br{% if flight.has_stops %} lyovr{% endif %}"></div>
              <div class="jrnttl">{{ flight.stops_label }}</div>
            </div>
            <div class="flttme">{{ flight.arrival_time }}</div>
          </div>

          <div class="fltftr">
            <a
              href="{{ flight.booking_link }}"
              target="_blank"
              rel="noopener noreferrer"
              class="bkbtn"
            >
              Book Now
            </a>
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
  </main>
</div>
"""

# =====================================================================
# DOMESTIC ROUNDTRIP TEMPLATE
# =====================================================================
DOMESTIC_ROUNDTRIP_TEMPLATE = """
<style>
{{ styles }}

/* ===== Route arrow size fix (React parity) ===== */
.round-trip-selector .route img,
.round-trip-selector .emt-inline-arrow {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}
</style>

<div class="flight-carousel round-trip-selector" data-instance-id="{{ unique_id }}">
  <main>

    <!-- Onward Flights -->
    <div class="selector-header">
      <div class="selector-heading">
        <div class="route">
          <span>{{ onward_origin }}</span>
          <img
            class="emt-inline-arrow"
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='15.728' height='8.101' viewBox='0 0 15.728 8.101'%3E%3Cpath d='M16.536,135.588h0l-3.414-3.4a.653.653,0,0,0-.922.926l2.292,2.281H1.653a.653.653,0,1,0,0,1.307H14.492L12.2,138.985a.653.653,0,0,0,.922.926l3.414-3.4h0A.654.654,0,0,0,16.536,135.588Z' transform='translate(-1 -132)' fill='%23202020'/%3E%3C/svg%3E"
            alt="→"
          />
          <span>{{ onward_destination }}</span>
          {% if view_all_link %}
          <a href="{{ view_all_link }}" target="_blank" rel="noopener noreferrer" class="view-all-link">View All</a>
          {% endif %}
        </div>
        <div class="meta">
          <span>Onward</span> |
          <span>{{ onward_date }}</span> |
          {# <span>{{ onward_count }} option{{ 's' if onward_count != 1 else '' }}</span> #}
          <span>{{ cabin }}</span>
        </div>
      </div>
    </div>

    <div class="fltcardbx">
      <div class="rsltcvr">
        {% for flight in onward_flights %}
        <label class="selectable-flight" for="onward-{{ unique_id }}-{{ loop.index0 }}" data-flight='{{ flight | tojson }}' data-leg="onward">

          <div class="selectable-flight__radio">
          <input id="onward-{{ unique_id }}-{{ loop.index0 }}" type="radio" name="onward-flight-{{ unique_id }}" style="display: none;"/>
            <span class="dtlchkmark" aria-hidden="true"></span>
            <span class="selectable-flight__hint">Select Onward</span>
          </div>

          <div class="fltcard">
            <div class="ntfchdr">
              <div class="ntflogo">
                <img src="{{ flight.airline_logo }}" alt="{{ flight.airline_name }}" />
              </div>
              <div class="ntfctlx">
                <div class="ntfctl">
                  <span>{{ flight.origin }}</span>
                  <img
                    class="emt-inline-arrow"
                    src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='15.728' height='8.101' viewBox='0 0 15.728 8.101'%3E%3Cpath d='M16.536,135.588h0l-3.414-3.4a.653.653,0,0,0-.922.926l2.292,2.281H1.653a.653.653,0,1,0,0,1.307H14.492L12.2,138.985a.653.653,0,0,0,.922.926l3.414-3.4h0A.654.654,0,0,0,16.536,135.588Z' transform='translate(-1 -132)' fill='%23202020'/%3E%3C/svg%3E"
                    alt="→"
                  />
                  <span>{{ flight.destination }}</span>
                </div>
                <div class="ntfsbt">
                  <span>{{ flight.airline_name }} {{ flight.flight_number }}</span> • <span>Onward</span>
                </div>
              </div>
              <div class="fltprcbx">
              <div class="fltprc">{{ flight.fare }}</div>
              <div class="sbttl">total fare</div>
            </div>
            </div>

            <div class="fltbdy">
              <div class="flttme">{{ flight.departure_time }}</div>
              <div class="jrny">
                <div class="jrnttl">{{ flight.journey_time }}</div>
                <div class="j-br{% if flight.has_stops %} lyovr{% endif %}"></div>
                <div class="jrnttl">{{ flight.stops_label }}</div>
              </div>
              <div class="flttme">{{ flight.arrival_time }}</div>
            </div>
          </div>
        </label>
        {% endfor %}
      </div>
    </div>

    <!-- Return Flights -->
    <div class="selector-header" style="margin-top: 24px;">
      <div class="selector-heading">
        <div class="route">
          <span>{{ return_origin }}</span>
          <img
            class="route-arrow"
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23202020' stroke-width='2'%3E%3Cpath d='M5 12h14M12 5l7 7-7 7'/%3E%3C/svg%3E"
            alt="→"
          />
          <span>{{ return_destination }}</span>
        </div>
        <div class="meta">
          <span>Return</span> |
          <span>{{ return_date }}</span> |
          {# <span>{{ return_count }} option{{ 's' if return_count != 1 else '' }}</span> #}
          <span>{{ cabin }}</span>
        </div>
      </div>
    </div>

    <div class="fltcardbx">
      <div class="rsltcvr">
        {% for flight in return_flights %}
        <label class="selectable-flight" for="return-{{ unique_id }}-{{ loop.index0 }}" data-flight='{{ flight | tojson }}' data-leg="return">

        <div class="selectable-flight__radio">
          <input id="return-{{ unique_id }}-{{ loop.index0 }}" type="radio" name="return-flight-{{ unique_id }}" style="display: none;"/>
          <span class="dtlchkmark" aria-hidden="true"></span>
          <span class="selectable-flight__hint">Select Return</span>
        </div>

          <div class="fltcard">
            <div class="ntfchdr">
              <div class="ntflogo">
                <img src="{{ flight.airline_logo }}" alt="{{ flight.airline_name }}" />
              </div>
              <div class="ntfctlx">
                <div class="ntfctl">
                  <span>{{ flight.origin }}</span>
                  <img
                    class="emt-inline-arrow"
                    src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='15.728' height='8.101' viewBox='0 0 15.728 8.101'%3E%3Cpath d='M16.536,135.588h0l-3.414-3.4a.653.653,0,0,0-.922.926l2.292,2.281H1.653a.653.653,0,1,0,0,1.307H14.492L12.2,138.985a.653.653,0,0,0,.922.926l3.414-3.4h0A.654.654,0,0,0,16.536,135.588Z' transform='translate(-1 -132)' fill='%23202020'/%3E%3C/svg%3E"
                    alt="→"
                  />
                  <span>{{ flight.destination }}</span>
                </div>
                <div class="ntfsbt">
                  <span>{{ flight.airline_name }} {{ flight.flight_number }}</span> • <span>Return</span>
                </div>
              </div>
              <div class="fltprcbx">
                <div class="fltprc">{{ flight.fare }}</div>
                <div class="sbttl">total fare</div>
              </div>
            </div>

            <div class="fltbdy">
              <div class="flttme">{{ flight.departure_time }}</div>
              <div class="jrny">
                <div class="jrnttl">{{ flight.journey_time }}</div>
                <div class="j-br{% if flight.has_stops %} lyovr{% endif %}"></div>
                <div class="jrnttl">{{ flight.stops_label }}</div>
              </div>
              <div class="flttme">{{ flight.arrival_time }}</div>
            </div>
          </div>
        </label>
        {% endfor %}
      </div>
    </div>

    <div class="book-action">
   <button type="button" class="bkbtn" disabled style="margin-right:40px;">
     Book Now
   </button>
    </div>

  </main>
</div>

<script>
(function () {
  'use strict';

  const instanceId = '{{ unique_id }}';
  const container = document.querySelector(`[data-instance-id="${instanceId}"]`);

  if (!container) {
    console.error(`[${instanceId}] Widget container not found. Ensure HTML has data-instance-id="{{ unique_id }}"`);
    return;
  }
  
  if (container.hasAttribute('data-initialized')) {
    return;
  }
  
  container.setAttribute('data-initialized', 'true');
  container.classList.add('initialized');

  const widgetId = 'widget_' + instanceId;
  console.log(`[${widgetId}] Initializing...`);
  
  let selectedOnwardFlightData = null;
  let selectedReturnFlightData = null;
  const passengers = {{ passengers | tojson }};

  /* ---------------- HELPERS (Extracted) ---------------- */

 const getSafeNumber = (value, fallback = 0) => {
    const num = Number(value);
    return Number.isFinite(num) ? num : fallback;
  };

  const cleanCode = (value, fallback = "") => {
    if (!value || typeof value !== "string") return fallback;
    return value.trim().toUpperCase();
  };

  const cleanCodeNoSpaces = (value, fallback = "") =>
    cleanCode(value, fallback).replace(/\s+/g, "");

  const normalizeCabin = (value) => {
    if (!value || typeof value !== "string") return "Economy";
    const lower = value.trim().toLowerCase();
    if (lower === "economy") return "Economy";
    if (lower === "business") return "Business";
    if (lower === "first") return "First";
    return value.trim();
  };

  const normalizeFlightNumber = (value) => {
    if (value === undefined || value === null) return "";
    return String(value).replace(/\s+/g, "");
  };

  const parseTextualDate = (value) => {
    const str = String(value);
    const match = str.match(/(\d{1,2})[^\dA-Za-z]*([A-Za-z]{3})[^\d]*?(\d{4})/);
    if (!match) return "";
    const [, dRaw, monRaw, yRaw] = match;
    const monthMap = {
      jan: "01", feb: "02", mar: "03", apr: "04", may: "05", jun: "06",
      jul: "07", aug: "08", sep: "09", oct: "10", nov: "11", dec: "12"
    };
    const m = monthMap[monRaw.toLowerCase()];
    if (!m) return "";
    const d = String(dRaw).padStart(2, "0");
    return `${yRaw}-${m}-${d}`;
  };

  const toDateString = (value) => {
    if (!value) return "";
    if (typeof value === "string") {
      const isoMatch = value.match(/^(\d{4}-\d{2}-\d{2})/);
      if (isoMatch) return isoMatch[1];
      const tIndex = value.indexOf("T");
      if (tIndex > 0) {
        const datePart = value.slice(0, tIndex);
        const isoPart = datePart.match(/^(\d{4}-\d{2}-\d{2})/);
        if (isoPart) return isoPart[1];
      }
      const parsedText = parseTextualDate(value);
      if (parsedText) return parsedText;
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    return date.toISOString().slice(0, 10);
  };

  const toTimeString = (value) => {
    if (!value) return "";
    if (typeof value === "string") {
      const raw = value.includes("T") ? value.split("T")[1] : value;
      const digits = raw.replace(/[^0-9]/g, "");
      if (digits.length >= 1) return digits.padStart(4, "0").slice(0, 4);
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    return `${hours}${minutes}`;
  };

  const composeDateTime = (dateValue, timeValue) => {
    const datePart = toDateString(dateValue);
    const timePart = toTimeString(timeValue);
    if (datePart && timePart) return `${datePart}T${timePart}`;
    if (typeof dateValue === "string" && dateValue.includes("T")) {
      const fallbackDate = toDateString(dateValue);
      const fallbackTime = toTimeString(dateValue);
      if (fallbackDate && fallbackTime) return `${fallbackDate}T${fallbackTime}`;
    }
    if (typeof timeValue === "string" && timeValue.includes("T")) return timeValue;
    return datePart || "";
  };

  const extractFare = (flight) => {
    const fareOption = flight?.fare_options?.[0] || flight?.fare_options?.fare;
    const candidates = [
      fareOption?.total_fare,
      fareOption?.total,
      fareOption?.base_fare,
      flight?.fare,
      flight?.price
    ];
    for (const candidate of candidates) {
      const num = getSafeNumber(candidate, null);
      if (num !== null) return num;
    }
    return 0;
  };

  const formatPrice = (value) => getSafeNumber(value, 0).toFixed(2);

  const extractSegments = (flight) => {
    const legs = Array.isArray(flight?.legs) ? flight.legs : [];
    const segmentsSource = legs.length ? legs : [flight || {}];

    return segmentsSource.map((leg) => {
      const departureDate = toDateString(
        leg.departure_date || leg.departureDate || leg.departure_time_iso || 
        leg.departure_time || leg.departureDateTime
      );
      const arrivalDate = toDateString(
        leg.arrival_date || leg.arrivalDate || leg.arrival_time_iso || 
        leg.arrival_time || leg.arrivalDateTime
      );
      const cabin = normalizeCabin(
        leg.cabin || leg.cabin_class || leg.cabinClass || flight?.cabin || "Economy"
      );
      const bookingCode = cleanCodeNoSpaces(
        leg.booking_code || leg.bookingCode || leg.booking_class || leg.fare_class ||
        flight?.booking_code || flight?.bookingCode || flight?.booking_class || 
        flight?.fare_class || ""
      ) || "Y";
      const flightNumber = normalizeFlightNumber(
        leg.flight_number || leg.flightNumber || flight?.flight_number || flight?.flightNumber || ""
      );
      const carrier = cleanCode(
        leg.airline_code || leg.carrier || flight?.airline_code || 
        flight?.carrier || flight?.marketing_carrier
      ) || "";

      return {
        origin: cleanCode(leg.origin || flight?.origin || ""),
        destination: cleanCode(leg.destination || flight?.destination || ""),
        bookingCode,
        flightNumber,
        carrier,
        cabin,
        departureDate,
        arrivalDate,
        departureTime: toTimeString(leg.departure_time_iso || leg.departure_time || leg.departureDateTime),
        arrivalTime: toTimeString(leg.arrival_time_iso || leg.arrival_time || leg.arrivalDateTime)
      };
    });
  };
 const buildSegmentString = (segment, id) => {
    const departureDateTime = composeDateTime(segment.departureDate, segment.departureTime);
    const arrivalDateTime = composeDateTime(segment.arrivalDate || segment.departureDate, segment.arrivalTime);

    const parts = [
      `Origin=${segment.origin || ""}`,
      `BookingCode=${segment.bookingCode || ""}`,
      `Destination=${segment.destination || ""}`,
      `FlightNumber=${segment.flightNumber || ""}`,
      `Carrier=${segment.carrier || ""}`,
      `DepartureDate=${departureDateTime}`,
      `id=${id}`,
      `Cabin=${segment.cabin || ""}`,
      `ArrivalDate=${arrivalDateTime}`
    ];
    return parts.join(",");
  };

  const encodeSegmentParam = (segment) =>
    encodeURIComponent(segment || "")
      .replace(/%2C/g, ",")
      .replace(/%3D/g, "=");


  const buildRoundTripDeepLink = (onwardFlight, returnFlight, options = {}) => {
    const {
      adults = 1,
      children = 0,
      infants = 0,
      referralId = "UserID",
      language = "ln-hi",
      displayedCurrency = "INR",
      userCurrency = "INR",
      pointOfSaleCountry = "IN",
      cc = ""
    } = options;

    if (!onwardFlight || !returnFlight) return "";

    const onwardSegments = extractSegments(onwardFlight);
    const returnSegments = extractSegments(returnFlight);

    if (!onwardSegments.length || !returnSegments.length) return "";

    const onwardFirst = onwardSegments[0];
    const onwardLast = onwardSegments[onwardSegments.length - 1];
    const returnFirst = returnSegments[0];
    const returnLast = returnSegments[returnSegments.length - 1];

    const baseUrl = "https://flight.easemytrip.com/RemoteSearchHandlers/index";
    const price = formatPrice(extractFare(onwardFlight) + extractFare(returnFlight));

    const query = {
      Adult: adults ?? 1,
      Child: children ?? 0,
      Infant: infants ?? 0,
      ReferralId: referralId || "UserID",
      UserLanguage: language || "en",
      DisplayedPriceCurrency: displayedCurrency || "INR",
      UserCurrency: userCurrency || displayedCurrency || "INR",
      DisplayedPrice: price,
      PointOfSaleCountry: pointOfSaleCountry || "IN",
      TripType: "RoundTrip",
      Origin1: onwardFirst.origin,
      Destination1: onwardLast.destination,
      DepartureDate1: onwardFirst.departureDate,
      Cabin1: onwardFirst.cabin || "Economy",
      BookingCode1: onwardFirst.bookingCode,
      FlightNumber1: onwardFirst.flightNumber,
      Origin2: returnFirst.origin,
      Destination2: returnLast.destination,
      DepartureDate2: returnFirst.departureDate,
      Cabin2: returnFirst.cabin || "Economy",
      BookingCode2: returnFirst.bookingCode,
      FlightNumber2: returnFirst.flightNumber,
      cc: cc || "",
      Slice1: Array.from({ length: onwardSegments.length }, (_, i) => i + 1).join(","),
      Slice2: Array.from({ length: returnSegments.length }, (_, i) => onwardSegments.length + i + 1).join(",")
    };

    const segments = [...onwardSegments, ...returnSegments];
    const baseQuery = Object.entries(query)
      .map(([key, val]) => `${key}=${encodeURIComponent(val ?? "")}`)
      .join("&");
    const segmentQuery = segments
      .map((segment, idx) => `Segment${idx + 1}=${encodeSegmentParam(buildSegmentString(segment, idx + 1))}`)
      .join("&");

    return `${baseUrl}?${baseQuery}&${segmentQuery}`;
  };


  /* ---------------- EVENT LOGIC ---------------- */

  function updateUI(name, target) {
    container.querySelectorAll(`input[name="${name}"]`).forEach(input => {
      input.closest('.selectable-flight').classList.toggle('is-selected', input === target);
    });
  }

  container.addEventListener('change', function (e) {
    if (e.target.type !== 'radio') return;

    const wrapper = e.target.closest('.selectable-flight');
    const flightUI = JSON.parse(wrapper.dataset.flight);
    const leg = wrapper.dataset.leg;

    if (leg === 'onward') {
      selectedOnwardFlightData = flightUI.raw_data || flightUI;
      updateUI(`onward-flight-${instanceId}`, e.target);
    } else {
      selectedReturnFlightData = flightUI.raw_data || flightUI;
      updateUI(`return-flight-${instanceId}`, e.target);
    }

    const btn = container.querySelector('.bkbtn');
    if (btn) btn.disabled = !(selectedOnwardFlightData && selectedReturnFlightData);
  });

  const bookButton = container.querySelector('.bkbtn');
  if (bookButton) {
    bookButton.addEventListener('click', function(e) {
      if (!selectedOnwardFlightData || !selectedReturnFlightData) return;
      
      const link = buildRoundTripDeepLink(selectedOnwardFlightData, selectedReturnFlightData, {
          adults: {{ passengers.adults | default(1) }},
          children: {{ passengers.children | default(0) }},
          infants: {{ passengers.infants | default(0) }},
          referralId: "{{ referral_id | default('UserID') }}"
      });
      
      if (link) window.open(link, '_blank', 'noopener,noreferrer');
    });
  }
})();
</script>
"""


# =====================================================================
# INTERNATIONAL ROUNDTRIP TEMPLATE
# =====================================================================
INTERNATIONAL_ROUNDTRIP_TEMPLATE = """
<style>
{{ styles }}
</style>
<div class="flight-carousel">
  <main>
  <div class="rslttp rslt-heading">
  <div class="ntfctl">
    <span>{{ origin }}</span>
    <img
      class="emt-inline-arrow"
      src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='15.728' height='8.101' viewBox='0 0 15.728 8.101'%3E%3Cpath d='M16.536,135.588h0l-3.414-3.4a.653.653,0,0,0-.922.926l2.292,2.281H1.653a.653.653,0,1,0,0,1.307H14.492L12.2,138.985a.653.653,0,0,0,.922.926l3.414-3.4h0A.654.654,0,0,0,16.536,135.588Z' transform='translate(-1 -132)' fill='%23202020'/%3E%3C/svg%3E"
      alt="→"
    />
    <span>{{ destination }}</span>
    <img
      class="emt-inline-arrow"
      src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='15.728' height='8.101' viewBox='0 0 15.728 8.101'%3E%3Cpath d='M16.536,135.588h0l-3.414-3.4a.653.653,0,0,0-.922.926l2.292,2.281H1.653a.653.653,0,1,0,0,1.307H14.492L12.2,138.985a.653.653,0,0,0,.922.926l3.414-3.4h0A.654.654,0,0,0,16.536,135.588Z' transform='translate(-1 -132)' fill='%23202020'/%3E%3C/svg%3E"
      alt="→"
    />
    <span>{{ origin }}</span>
    {% if view_all_link %}
    <a href="{{ view_all_link }}" target="_blank" rel="noopener noreferrer" class="view-all-link">View All</a>
    {% endif %}
  </div>
  <div class="ntfsbt">
    <span>Roundtrip</span> •
    <span>{{ onward_date }} – {{ return_date }}</span> •
    {# <span>{{ combo_count }} option{{ 's' if combo_count != 1 else '' }}</span> #}
    <span>{{ cabin }}</span>
  </div>
</div>
    <div class="fltcardbx">
      <div class="rsltcvr">
        {% for combo in combos %}
        <div class="fltcardInternational item">
          <!-- HEADER -->
          <div class="rndhd">
            <div class="rndttl">Roundtrip</div>
            <div class="fltprcbx">
              <div class="fltprc">{{ combo.fare }}</div>
              <div class="sbttl">total fare</div>
            </div>
          </div>

          <div class="trpcvr">
            <!-- ONWARD -->
            <div class="rndtrpcvr">
              <div class="ntfctl">
                <span>{{ combo.onward.origin }}</span>
                <img
                  class="emt-inline-arrow"
                  src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='15.728' height='8.101' viewBox='0 0 15.728 8.101'%3E%3Cpath d='M16.536,135.588h0l-3.414-3.4a.653.653,0,0,0-.922.926l2.292,2.281H1.653a.653.653,0,1,0,0,1.307H14.492L12.2,138.985a.653.653,0,0,0,.922.926l3.414-3.4h0A.654.654,0,0,0,16.536,135.588Z' transform='translate(-1 -132)' fill='%23202020'/%3E%3C/svg%3E"
                  alt="→"
                />
                <span>{{ combo.onward.destination }}</span>
              </div>

              <div class="ntfchdr">
                <div class="ntflogo">
                  <img src="{{ combo.onward.airline_logo }}" alt="{{ combo.onward.airline_name }}" />
                </div>
                <div class="ntfctlx">
                  <div class="arlnme">{{ combo.onward.airline_name }}</div>
                  <div class="ntfsbt">
                    <span class="tryp">Onward</span> •
                    {{ combo.onward.flight_number }} •
                    {{ combo.onward.departure_date }}
                  </div>
                </div>
              </div>

              <div class="fltbdy">
                <div class="flttme">{{ combo.onward.departure_time }}</div>
                <div class="jrny">
                  <div class="jrnttl">{{ combo.onward.journey_time }}</div>
                  <div class="j-br{% if combo.onward.has_stops %} lyovr{% endif %}"></div>
                  <div class="jrnttl">{{ combo.onward.stops_label }}</div>
                </div>
                <div class="flttme">{{ combo.onward.arrival_time }}</div>
              </div>
            </div>

            <div class="trpdvdr"></div>

            <!-- RETURN -->
            <div class="rndtrpcvr">
              <div class="ntfctl">
                <span>{{ combo.return.origin }}</span>
                <img
                  class="emt-inline-arrow"
                  src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='15.728' height='8.101' viewBox='0 0 15.728 8.101'%3E%3Cpath d='M16.536,135.588h0l-3.414-3.4a.653.653,0,0,0-.922.926l2.292,2.281H1.653a.653.653,0,1,0,0,1.307H14.492L12.2,138.985a.653.653,0,0,0,.922.926l3.414-3.4h0A.654.654,0,0,0,16.536,135.588Z' transform='translate(-1 -132)' fill='%23202020'/%3E%3C/svg%3E"
                  alt="→"
                />
                <span>{{ combo.return.destination }}</span>
              </div>

              <div class="ntfchdr">
                <div class="ntflogo">
                  <img src="{{ combo.return.airline_logo }}" alt="{{ combo.return.airline_name }}" />
                </div>
                <div class="ntfctlx">
                  <div class="arlnme">{{ combo.return.airline_name }}</div>
                  <div class="ntfsbt">
                    <span class="tryp">Return</span> •
                    {{ combo.return.flight_number }} •
                    {{ combo.return.departure_date }}
                  </div>
                </div>
              </div>

              <div class="fltbdy">
                <div class="flttme">{{ combo.return.departure_time }}</div>
                <div class="jrny">
                  <div class="jrnttl">{{ combo.return.journey_time }}</div>
                  <div class="j-br{% if combo.return.has_stops %} lyovr{% endif %}"></div>
                  <div class="jrnttl">{{ combo.return.stops_label }}</div>
                </div>
                <div class="flttme">{{ combo.return.arrival_time }}</div>
              </div>
            </div>
          </div>

          <a href="{{ combo.booking_link }}" target="_blank" rel="noopener noreferrer" class="bkbtnInternational">
            Book Now
          </a>
        </div>
        {% endfor %}
      </div>
    </div>
    
    {% if not combos %}
    <div class="emt-empty">No roundtrip combinations found</div>
    {% endif %}
  </main>
</div>
"""


# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def _format_currency(value: float) -> str:
    """Format price in Indian Rupees"""
    if not isinstance(value, (int, float)) or value < 0:
        return "₹0"
    try:
        return f"₹{int(value):,}"
    except:
        return f"₹{value}"


def _format_time(time_value: Any) -> str:
    """Format time from various formats to HH:MM"""
    if not time_value:
        return "--:--"
    
    time_str = str(time_value)
    
    # If it's in HH:MM or HHMM format
    if ":" in time_str:
        parts = time_str.split(":")
        if len(parts) >= 2:
            return f"{parts[0].zfill(2)}:{parts[1][:2].zfill(2)}"
    
    # If it's in HHMM format
    digits = ''.join(filter(str.isdigit, time_str))
    if len(digits) >= 4:
        return f"{digits[:2]}:{digits[2:4]}"
    elif len(digits) >= 2:
        return f"{digits[:2].zfill(2)}:00"
    
    return "--:--"


from typing import Any
from datetime import datetime

def _format_date(date_value: Any) -> str:
    """Format date as Day, DD MMM YYYY"""
    if not date_value:
        return "--"

    try:
        if isinstance(date_value, str):
            s = date_value.strip()

            # Try ISO formats first (date or datetime, with or without Z)
            try:
                dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
            except ValueError:
                # Handle: Thu-26Feb2026, Tue-07Feb2026, etc.
                dt = datetime.strptime(s, "%a-%d%b%Y")
        else:
            dt = date_value

        return dt.strftime("%a, %d %b %Y")

    except Exception:
        return str(date_value)


def _format_stops(stops: int) -> str:
    """Format stops count"""
    if not isinstance(stops, int) or stops <= 0:
        return "Non Stop"
    if stops == 1:
        return "1 Stop"
    return f"{stops} Stops"


def _extract_seats_label(flight: Dict[str, Any]) -> str:
    """Extract seats left label"""
    seats = flight.get('seats_left') or flight.get('available_seats') or flight.get('seat_left')
    
    if not seats:
        return "Limited Seats"
    
    try:
        seats_num = int(seats)
        if seats_num <= 0:
            return "Limited Seats"
        return f"{seats_num} Seats Left"
    except:
        return "Limited Seats"


def _resolve_airline_logo(flight: Dict[str, Any]) -> str:
    """Get airline logo URL"""
    # Try to get from legs
    legs = flight.get('legs', [])
    if legs and len(legs) > 0:
        airline_code = legs[0].get('airline_code')
        if airline_code:
            return f"https://flight.easemytrip.com/Content/AirlineLogon/{airline_code}.png"
    
    # Fallback to flight level
    airline_code = flight.get('airline_code')
    if airline_code:
        return f"https://flight.easemytrip.com/Content/AirlineLogon/{airline_code}.png"
    
    # Default placeholder
    return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23e0e0e0'%3E%3Cpath d='M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z'/%3E%3C/svg%3E"


def _normalize_flight_for_ui(flight: Dict[str, Any], trip_type: str = "Oneway") -> Dict[str, Any]:
    """Normalize a single flight for UI rendering"""
    legs = flight.get('legs', [])
    first_leg = legs[0] if legs else flight
    last_leg = legs[-1] if legs else flight
    
    departure_date = _format_date(
    first_leg.get('departure_date') or flight.get('departure_date'))

    # Get fare
    fare_options = flight.get('fare_options', [])
    cheapest_fare = fare_options[0] if fare_options else {}
    fare_amount = cheapest_fare.get('total_fare') or cheapest_fare.get('base_fare') or flight.get('fare') or 0
    
    # Get basic info
    origin = flight.get('origin') or first_leg.get('origin') or '--'
    destination = flight.get('destination') or last_leg.get('destination') or '--'
    airline_name = first_leg.get('airline_name') or flight.get('airline_name') or 'Airline'
    flight_number = first_leg.get('flight_number') or flight.get('flight_number') or ''
    
    # Get times
    departure_time = _format_time(first_leg.get('departure_time') or flight.get('departure_time'))
    arrival_time = _format_time(last_leg.get('arrival_time') or flight.get('arrival_time'))
    
    # Get journey time
    journey_time = flight.get('journey_time') or first_leg.get('duration') or ''
    
    # Get stops
    total_stops = flight.get('total_stops', 0)
    if not isinstance(total_stops, int):
        try:
            total_stops = int(total_stops)
        except:
            total_stops = len(legs) - 1 if len(legs) > 1 else 0
    
    # Get booking link
    booking_link = flight.get('deepLink') or flight.get('deep_link') or flight.get('bookingLink') or '#'
    
    return {
        'origin': origin,
        'destination': destination,
        'airline_name': airline_name,
        'flight_number': flight_number,
        'airline_logo': _resolve_airline_logo(flight),
        'departure_time': departure_time,
        'arrival_time': arrival_time,
        'journey_time': journey_time,
        'stops_label': _format_stops(total_stops),
        'has_stops': total_stops > 0,
        'seats_label': _extract_seats_label(flight),
        'fare': _format_currency(fare_amount),
        'booking_link': booking_link,
        'trip_type': trip_type,
        'departure_date': departure_date,
        'raw_data': flight,  # Keep raw flight data for deeplink building
    }

def _calculate_journey_time(legs: List[Dict[str, Any]]) -> str:
    total_minutes = 0

    for leg in legs:
        dur = leg.get("duration") or ""
        # expected formats: "09h 50m", "3h 35m", "04h05m"
        if "h" in dur:
            parts = dur.replace("m", "").split("h")
            hours = int(parts[0].strip() or 0)
            minutes = int(parts[1].strip() or 0)
            total_minutes += hours * 60 + minutes

    if total_minutes <= 0:
        return "--"

    return f"{total_minutes // 60}h {total_minutes % 60}m"


def _normalize_stops(stops: Any) -> int:
    try:
        return int(stops)
    except Exception:
        return 0

def _normalize_international_combo_for_ui(combo: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Normalize an international roundtrip combo for UI rendering"""

    onward_flight = combo.get('onward_flight') or combo.get('onwardFlight')
    return_flight = combo.get('return_flight') or combo.get('returnFlight')

    if not onward_flight or not return_flight:
        return None

    onward_legs = onward_flight.get('legs', [])
    return_legs = return_flight.get('legs', [])

    if not onward_legs or not return_legs:
        return None

    onward_first = onward_legs[0]
    onward_last = onward_legs[-1]
    return_first = return_legs[0]
    return_last = return_legs[-1]

    combo_fare = (
        combo.get('combo_fare')
        or combo.get('totalFare')
        or combo.get('total_fare')
        or combo.get('fare')
    )

    if not combo_fare:
        onward_opts = onward_flight.get('fare_options', [])
        return_opts = return_flight.get('fare_options', [])
        combo_fare = (
            (onward_opts[0].get('total_fare', 0) if onward_opts else 0)
            + (return_opts[0].get('total_fare', 0) if return_opts else 0)
        )

    booking_link = combo.get('deepLink') or combo.get('deep_link') or '#'

    onward_stops = _normalize_stops(onward_flight.get('total_stops', 0))
    return_stops = _normalize_stops(return_flight.get('total_stops', 0))

    return {
        'fare': _format_currency(combo_fare),
        'booking_link': booking_link,

        'onward': {
            'origin': onward_first.get('origin', '--'),
            'destination': onward_last.get('destination', '--'),
            'airline_name': onward_first.get('airline_name', 'Airline'),
            'airline_logo': _resolve_airline_logo(onward_flight),
            'flight_number': onward_first.get('flight_number', ''),
            'departure_date': _format_date(onward_first.get('departure_date')),
            'departure_time': _format_time(onward_first.get('departure_time')),
            'arrival_time': _format_time(onward_last.get('arrival_time')),

            # 🔥 added for jrny block
            'journey_time': _calculate_journey_time(onward_legs),
            'stops_label': _format_stops(onward_stops),
            'has_stops': onward_stops > 0,
            'stops_count': onward_stops,
        },

        'return': {
            'origin': return_first.get('origin', '--'),
            'destination': return_last.get('destination', '--'),
            'airline_name': return_first.get('airline_name', 'Airline'),
            'airline_logo': _resolve_airline_logo(return_flight),
            'flight_number': return_first.get('flight_number', ''),
            'departure_date': _format_date(return_first.get('departure_date')),
            'departure_time': _format_time(return_first.get('departure_time')),
            'arrival_time': _format_time(return_last.get('arrival_time')),

            # 🔥 added for jrny block
            'journey_time': _calculate_journey_time(return_legs),
            'stops_label': _format_stops(return_stops),
            'has_stops': return_stops > 0,
            'stops_count': return_stops,
        },
    }


# =====================================================================
# MAIN RENDER FUNCTIONS
# =====================================================================

def render_oneway_flights(flight_results: Dict[str, Any]) -> str:
    """
    Render one-way flight results carousel.
    
    Args:
        flight_results: Dictionary containing flight search results with keys:
            - outbound_flights: List of flight dictionaries
            - origin: Origin airport code
            - destination: Destination airport code
    
    Returns:
        HTML string for the flight carousel
    """
    flights = flight_results.get('outbound_flights', [])
    
    if not flights:
        return "<div class='flight-carousel'><main><div class='emt-empty'>No flights found</div></main></div>"
    
    # Get origin and destination
    origin = flight_results.get('origin') or flights[0].get('origin') or '--'
    destination = flight_results.get('destination') or flights[0].get('destination') or '--'
    
    # Normalize flights
    flights_ui = [_normalize_flight_for_ui(flight, 'Oneway') for flight in flights]
    flights_ui = [f for f in flights_ui if f]

    # Get departure date from search context only
    departure_date = _format_date(flight_results.get('outbound_date') or flight_results.get('departure_date'))
    
    # Render template
    template = _jinja_env.from_string(ONEWAY_FLIGHT_TEMPLATE)
    return template.render(
        styles=BASE_FLIGHT_STYLES,
        origin=origin,
        destination=destination,
        flight_count=len(flights_ui),  # Keep for compatibility
        flights=flights_ui,
        departure_date=departure_date,
        cabin=flight_results.get('cabin', 'Economy'),
        view_all_link=flight_results.get('viewAll'),
    )


def render_domestic_roundtrip_flights(flight_results: Dict[str, Any], unique_id: str) -> str:
    """
    Render domestic roundtrip flight results with selection interface.
    """

    onward_flights = flight_results.get('outbound_flights', [])
    return_flights = flight_results.get('return_flights', [])

    if not onward_flights or not return_flights:
        return (
            "<div class='flight-carousel'>"
            "<main><div class='emt-empty'>No flights found</div></main>"
            "</div>"
        )

    # --------------------------------------------------
    # Route info
    # --------------------------------------------------
    onward_origin = flight_results.get('origin') or onward_flights[0].get('origin') or '--'
    onward_destination = flight_results.get('destination') or onward_flights[0].get('destination') or '--'
    return_origin = onward_destination
    return_destination = onward_origin

    # --------------------------------------------------
    # Normalize flights for UI
    # --------------------------------------------------
    onward_ui = [_normalize_flight_for_ui(f, 'Onward') for f in onward_flights]
    return_ui = [_normalize_flight_for_ui(f, 'Return') for f in return_flights]

    onward_ui = [f for f in onward_ui if f]
    return_ui = [f for f in return_ui if f]

    # Get dates from search context only
    onward_date = _format_date(flight_results.get('outbound_date') or flight_results.get('departure_date'))
    return_date = _format_date(flight_results.get('return_date'))

    # --------------------------------------------------
    # ✅ PASSENGER CONTEXT (FIXED)
    # --------------------------------------------------
    passengers = flight_results.get("passengers") or {
        "adults": flight_results.get("adults", 1),
        "children": flight_results.get("children", 0),
        "infants": flight_results.get("infants", 0),
    }

    # --------------------------------------------------
    # Render template
    # --------------------------------------------------
    combined_styles = f"{BASE_FLIGHT_STYLES}\n{DOMESTIC_ROUNDTRIP_STYLES}"
    template = _jinja_env.from_string(DOMESTIC_ROUNDTRIP_TEMPLATE)

    return template.render(
        styles=combined_styles,
        onward_origin=onward_origin,
        onward_destination=onward_destination,
        onward_count=len(onward_ui),  # Keep for compatibility
        onward_flights=onward_ui,
        return_origin=return_origin,
        return_destination=return_destination,
        return_count=len(return_ui),  # Keep for compatibility
        return_flights=return_ui,
        onward_date=onward_date,
        return_date=return_date,
        cabin=flight_results.get('cabin', 'Economy'),
        view_all_link=flight_results.get('viewAll'),
        unique_id=unique_id,
        # ✅ this is what your JS reads
        passengers=passengers,
        referral_id='UserID',
        language='ln-hi',
        currency='INR',
        pos_country='IN',
    )

def render_international_roundtrip_flights(flight_results: Dict[str, Any]) -> str:
    combos = flight_results.get('international_combos', [])

    combos_ui = [_normalize_international_combo_for_ui(c) for c in combos]
    combos_ui = [c for c in combos_ui if c]

    if not combos_ui:
        return "<div class='flight-carousel'><main><div class='emt-empty'>No roundtrip combinations found</div></main></div>"

    first_combo = combos_ui[0]

    origin = first_combo['onward']['origin']
    destination = first_combo['onward']['destination']
    
    # Get dates from search context (more reliable than individual flights)
    onward_date = _format_date(flight_results.get('outbound_date') or flight_results.get('departure_date'))
    return_date = _format_date(flight_results.get('return_date'))


    combined_styles = f"{BASE_FLIGHT_STYLES}\n{INTERNATIONAL_ROUNDTRIP_STYLES}"
    template = _jinja_env.from_string(INTERNATIONAL_ROUNDTRIP_TEMPLATE)

    return template.render(
        styles=combined_styles,
        combos=combos_ui,
        origin=origin,
        destination=destination,
        onward_date=onward_date,
        return_date=return_date,
        combo_count=len(combos_ui),  # Keep for compatibility
        cabin=flight_results.get('cabin', 'Economy'),
        view_all_link=flight_results.get('viewAll'),
    )

def render_flight_results(flight_results: Dict[str, Any]) -> str:
    """
    Main function to render flight results based on trip type.
    Automatically detects trip type and renders appropriate UI.
    
    Args:
        flight_results: Dictionary containing flight search results
    
    Returns:
        HTML string for the appropriate flight carousel
    """
    # Check if international roundtrip
    if flight_results.get('is_international') and flight_results.get('is_roundtrip'):
        return render_international_roundtrip_flights(flight_results)
    
    # Check if domestic roundtrip
    elif flight_results.get('is_roundtrip'):
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return render_domestic_roundtrip_flights(flight_results,unique_id)
    
    # Default to one-way
    else:
        return render_oneway_flights(flight_results)
