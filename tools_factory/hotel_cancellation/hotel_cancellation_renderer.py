"""Hotel Cancellation Booking Details Renderer (Display-Only)"""
from typing import Dict, Any
from jinja2 import Environment, BaseLoader, select_autoescape


def _truncate_text(text: str, max_length: int = 30) -> str:
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
# 🏨 INTERACTIVE BOOKING TEMPLATE (WITH JS FOR CANCEL FLOW)
# =====================================================================
INTERACTIVE_BOOKING_TEMPLATE = """
<style>

.booking-details-carousel {
  font-family: poppins, sans-serif;
  color: #202020;
  background: rgba(255, 255, 255, 0.92);
  position: relative;
}

.booking-details-carousel * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
}

.booking-details-carousel main {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px 0 30px;
  position: relative;
}

.booking-details-carousel .bkhd {
  margin-bottom: 16px;
}

.booking-details-carousel .bkttl {
  font-size: 18px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 4px;
}

.booking-details-carousel .bksub {
  font-size: 12px;
  color: #646d74;
  margin-top: 4px;
}

.booking-details-carousel .hotel-info {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 16px;
  border: 1px solid #e0e0e0;
}

.booking-details-carousel .hotel-name {
  font-size: 16px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.booking-details-carousel .hotel-name img {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.booking-details-carousel .hotel-address {
  font-size: 12px;
  color: #646d74;
  margin-bottom: 8px;
  display: flex;
  align-items: flex-start;
  gap: 4px;
}

.booking-details-carousel .hotel-address img {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  margin-top: 1px;
}

.booking-details-carousel .hotel-dates {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #202020;
  margin-top: 8px;
}

.booking-details-carousel .date-item {
  display: flex;
  flex-direction: column;
}

.booking-details-carousel .date-label {
  font-size: 10px;
  color: #868686;
  text-transform: uppercase;
  margin-bottom: 2px;
}

.booking-details-carousel .date-value {
  font-weight: 600;
}

.booking-details-carousel .rooms-title {
  font-size: 14px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 12px;
}

.booking-details-carousel .slider-shell {
  position: relative;
}

.booking-details-carousel .rsltcvr {
  width: 90%;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  cursor: grab;
}

.booking-details-carousel .rsltcvr:active {
  cursor: grabbing;
}

.booking-details-carousel .embla__container {
  display: flex;
  gap: 16px;
}

.booking-details-carousel .room-card {
  width: 280px;
  min-width: 280px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fff;
  padding: 14px;
  display: flex;
  flex-direction: column;
}

.booking-details-carousel .room-header {
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
  margin-bottom: 10px;
}

.booking-details-carousel .room-type {
  font-size: 15px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 0px;
}

.booking-details-carousel .room-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.booking-details-carousel .detail-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  font-size: 12px;
}

.booking-details-carousel .detail-label {
  color: #646d74;
  font-weight: 500;
}

.booking-details-carousel .detail-value {
  color: #202020;
  font-weight: 600;
  text-align: right;
  max-width: 60%;
}

.booking-details-carousel .amount-highlight {
  font-size: 16px;
  font-family: inter, sans-serif;
  color: #ef6614;
}

.booking-details-carousel .policy-text {
  font-size: 11px;
  color: #646d74;
  background: #fff8e1;
  padding: 8px;
  border-radius: 6px;
  border-left: 3px solid #ffc107;
  margin-top: 8px;
  line-height: 1.4;
  white-space: pre-line;
}

.booking-details-carousel .refundable {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #2e7d32;
  background: #e8f5e9;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 600;
  margin-top: 8px;
}

.booking-details-carousel .refundable::before {
  content: '✓';
  font-weight: bold;
}

.booking-details-carousel .non-refundable {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #d32f2f;
  background: #ffebee;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 600;
  margin-top: 8px;
}

.booking-details-carousel .non-refundable::before {
  content: '✗';
  font-weight: bold;
}

/* ---- Interactive step styles ---- */

.booking-details-carousel .hc-step {
  display: none;
}

.booking-details-carousel .hc-step.active {
  display: block;
}

.booking-details-carousel .hc-cancel-btn {
  display: block;
  width: 100%;
  margin-top: 12px;
  padding: 10px;
  background: linear-gradient(135deg, #ef6614 0%, #f58434 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: poppins, sans-serif;
  transition: opacity 0.2s;
}

.booking-details-carousel .hc-cancel-btn:hover {
  opacity: 0.85;
}

.booking-details-carousel .hc-form-group {
  margin-bottom: 16px;
}

.booking-details-carousel .hc-form-group label {
  display: block;
  font-size: 12px;
  color: #646d74;
  margin-bottom: 6px;
  font-weight: 500;
}

.booking-details-carousel .hc-reason-select,
.booking-details-carousel .hc-remark-textarea,
.booking-details-carousel .hc-otp-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-family: poppins, sans-serif;
  outline: none;
  transition: border-color 0.2s;
  background: #fff;
  color: #202020;
}

.booking-details-carousel .hc-reason-select:focus,
.booking-details-carousel .hc-remark-textarea:focus,
.booking-details-carousel .hc-otp-input:focus {
  border-color: #ef6614;
}

.booking-details-carousel .hc-loading {
  display: none;
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.85);
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 12px;
}

.booking-details-carousel .hc-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e0e0e0;
  border-top-color: #ef6614;
  border-radius: 50%;
  animation: hcSpin 0.8s linear infinite;
}

@keyframes hcSpin {
  to { transform: rotate(360deg); }
}

.booking-details-carousel .hc-error-msg {
  display: none;
  background: #ffebee;
  color: #d32f2f;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 12px;
  border-left: 3px solid #d32f2f;
}

.booking-details-carousel .hc-back-btn {
  background: none;
  border: 1px solid #e0e0e0;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  color: #646d74;
  font-family: poppins, sans-serif;
  transition: border-color 0.2s;
}

.booking-details-carousel .hc-back-btn:hover {
  border-color: #ef6614;
  color: #ef6614;
}

.booking-details-carousel .hc-submit-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #ef6614 0%, #f58434 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: poppins, sans-serif;
  transition: opacity 0.2s;
}

.booking-details-carousel .hc-submit-btn:hover {
  opacity: 0.85;
}

.booking-details-carousel .hc-selected-room-badge {
  background: #f5f5f5;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 16px;
  border-left: 3px solid #ef6614;
}

.booking-details-carousel .hc-btn-row {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.booking-details-carousel .hc-otp-hint {
  font-size: 13px;
  color: #646d74;
  margin-bottom: 16px;
  line-height: 1.5;
}

/* Success result styling */
.booking-details-carousel .hc-success-box {
  background: linear-gradient(135deg, #e8f5e9 0%, #f1f8f4 100%);
  border: 2px solid #4caf50;
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
}

.booking-details-carousel .hc-success-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(76, 175, 80, 0.3);
  animation: hcSuccessPop 0.6s ease-out;
}

@keyframes hcSuccessPop {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}

.booking-details-carousel .hc-success-icon svg {
  width: 36px;
  height: 36px;
  color: #fff;
}

.booking-details-carousel .hc-success-title {
  font-size: 20px;
  font-weight: 700;
  color: #2e7d32;
  margin-bottom: 16px;
}

.booking-details-carousel .hc-refund-box {
  background: linear-gradient(135deg, #fff8e1 0%, #fffbea 100%);
  border: 2px solid #ffc107;
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
  text-align: left;
}

.booking-details-carousel .hc-refund-title {
  font-size: 14px;
  font-weight: 600;
  color: #f57c00;
  margin-bottom: 10px;
}

.booking-details-carousel .hc-refund-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 4px 0;
}

.booking-details-carousel .hc-refund-label {
  color: #646d74;
}

.booking-details-carousel .hc-refund-value {
  font-weight: 600;
  color: #202020;
}

.booking-details-carousel .hc-refund-amount {
  font-size: 24px;
  font-weight: 700;
  color: #ef6614;
  font-family: inter, sans-serif;
  margin-bottom: 8px;
}

.booking-details-carousel .hc-footer-note {
  font-size: 12px;
  color: #868686;
  text-align: center;
  margin-top: 20px;
}

/* Dark mode support */
.booking-details-carousel.dark {
  background: #000;
  color: #fff;
}

.booking-details-carousel.dark .room-card,
.booking-details-carousel.dark .hotel-info {
  background: #000;
  border-color: #373737;
}

.booking-details-carousel.dark .room-header {
  border-color: #373737;
}

.booking-details-carousel.dark .bkttl,
.booking-details-carousel.dark .hotel-name,
.booking-details-carousel.dark .room-type,
.booking-details-carousel.dark .date-value,
.booking-details-carousel.dark .detail-value {
  color: #fff;
}

.booking-details-carousel.dark .bksub,
.booking-details-carousel.dark .hotel-address,
.booking-details-carousel.dark .room-number,
.booking-details-carousel.dark .date-label,
.booking-details-carousel.dark .detail-label {
  color: #bcbcbc;
}

.booking-details-carousel.dark .hc-loading {
  background: rgba(0,0,0,0.85);
}

.booking-details-carousel.dark .hc-reason-select,
.booking-details-carousel.dark .hc-remark-textarea,
.booking-details-carousel.dark .hc-otp-input {
  background: #1a1a1a;
  border-color: #373737;
  color: #fff;
}

.booking-details-carousel.dark .hc-error-msg {
  background: #3d0000;
  color: #ff8a80;
}

.booking-details-carousel.dark .hc-back-btn {
  border-color: #373737;
  color: #bcbcbc;
}

.booking-details-carousel.dark .hc-selected-room-badge {
  background: #1a1a1a;
  color: #fff;
}

.booking-details-carousel.dark .hc-success-box {
  background: linear-gradient(135deg, #1a3a1a 0%, #1f2d1f 100%);
}

.booking-details-carousel.dark .hc-success-title {
  color: #66bb6a;
}

.booking-details-carousel.dark .hc-refund-box {
  background: linear-gradient(135deg, #332a00 0%, #3d3200 100%);
}

.booking-details-carousel.dark .hc-refund-value {
  color: #fff;
}

.booking-details-carousel.dark .hc-refund-label {
  color: #bcbcbc;
}
</style>

<div class="booking-details-carousel round-trip-selector" data-instance-id="{{ instance_id }}">
  <main>
    <!-- Loading overlay -->
    <div class="hc-loading"><div class="hc-spinner"></div></div>

    <!-- Error banner -->
    <div class="hc-error-msg"></div>

    <!-- Header -->
    <div class="bkhd">
      <div class="bkttl">{{ title }}</div>
      <div class="bksub">{{ subtitle }}</div>
    </div>

    {% if hotel_info %}
    <div class="hotel-info">
      <div class="hotel-name"><img src="https://mybookings.easemytrip.com/Content/assest/img/hotel-blic.svg" alt="">{{ hotel_info.name }}</div>
      {% if hotel_info.address %}
      <div class="hotel-address"><img src="https://mybookings.easemytrip.com/Content/assest/img/ico-map.svg" alt="">{{ hotel_info.address }}</div>
      {% endif %}
      <div class="hotel-dates">
        {% if hotel_info.check_in %}
        <div class="date-item">
          <div class="date-label">Check-in</div>
          <div class="date-value">{{ hotel_info.check_in }}</div>
        </div>
        {% endif %}
        {% if hotel_info.check_out %}
        <div class="date-item">
          <div class="date-label">Check-out</div>
          <div class="date-value">{{ hotel_info.check_out }}</div>
        </div>
        {% endif %}
      </div>
    </div>
    {% endif %}

    <!-- STEP 1: Room details + cancel buttons -->
    <div class="hc-step active" data-step="details">
      <div class="rooms-title">Select a room to cancel</div>
      <div class="slider-shell">
        <div class="rsltcvr">
          <div class="embla__container">
            {% for room in rooms %}
            <div class="room-card">
              <div class="room-header">
                <div class="room-type">{{ room.room_type }}</div>
              </div>
              <div class="room-details">
                {% if room.amount %}
                <div class="detail-row">
                  <span class="detail-label">Amount</span>
                  <span class="detail-value amount-highlight">₹{{ room.amount }}</span>
                </div>
                {% endif %}
                {% if room.total_adults %}
                <div class="detail-row">
                  <span class="detail-label">Adults</span>
                  <span class="detail-value">{{ room.total_adults }}</span>
                </div>
                {% endif %}
                {% if room.is_pay_at_hotel is not none %}
                <div class="detail-row">
                  <span class="detail-label">Payment</span>
                  <span class="detail-value">{% if room.is_pay_at_hotel %}Pay at Hotel{% else %}Prepaid{% endif %}</span>
                </div>
                {% endif %}
                {% if room.cancellation_policy %}
                <div class="policy-text">{{ room.cancellation_policy }}</div>
                {% endif %}
                {% if room.is_refundable %}
                <div class="refundable">Refundable</div>
                {% elif room.is_refundable is not none %}
                <div class="non-refundable">Non-Refundable</div>
                {% endif %}
              </div>
              <button type="button" class="hc-cancel-btn" data-room-id="{{ room.room_id }}">Cancel This Room</button>
            </div>
            {% endfor %}
          </div>
        </div>
      </div>
    </div>

    <!-- STEP 2: Reason + Send OTP -->
    <div class="hc-step" data-step="reason">
      <div class="hc-selected-room-badge">
        Cancelling: <strong class="hc-selected-room-label"></strong>
      </div>
      <div class="hc-form-group">
        <label>Reason for cancellation</label>
        <select class="hc-reason-select">
          <option value="Change of plans">Change of plans</option>
          <option value="Found better deal">Found a better deal</option>
          <option value="Travel dates changed">Travel dates changed</option>
          <option value="Personal reasons">Personal reasons</option>
          <option value="Other">Other</option>
        </select>
      </div>
      <div class="hc-form-group">
        <label>Additional remarks (optional)</label>
        <textarea class="hc-remark-textarea" rows="3" placeholder="Any additional details..."></textarea>
      </div>
      <div class="hc-btn-row">
        <button type="button" class="hc-back-btn" data-back-to="details">Back</button>
        <button type="button" class="hc-submit-btn hc-send-otp-btn">Send OTP</button>
      </div>
    </div>

    <!-- STEP 3: OTP input + Confirm -->
    <div class="hc-step" data-step="otp">
      <div class="hc-selected-room-badge">
        Cancelling: <strong class="hc-selected-room-label"></strong>
      </div>
      <p class="hc-otp-hint">
        An OTP has been sent to your registered email and phone number. Please enter it below to confirm the cancellation.
      </p>
      <div class="hc-form-group">
        <label>Enter OTP</label>
        <input type="text" class="hc-otp-input" maxlength="10" placeholder="e.g., ABC123" autocomplete="one-time-code" />
      </div>
      <div class="hc-btn-row">
        <button type="button" class="hc-back-btn" data-back-to="reason">Back</button>
        <button type="button" class="hc-submit-btn hc-confirm-btn">Confirm Cancellation</button>
      </div>
    </div>

    <!-- STEP 4: Result -->
    <div class="hc-step" data-step="result">
      <div class="hc-result-content"></div>
    </div>

  </main>
</div>

<script>
(function() {
  'use strict';

  var instanceId = '{{ instance_id }}';
  var container = document.querySelector('[data-instance-id="' + instanceId + '"]');
  if (!container) return;
  if (container.hasAttribute('data-initialized')) return;
  container.setAttribute('data-initialized', 'true');

  var API_BASE = '{{ api_base_url }}';
  var OTP_URL = API_BASE + '/api/hotel-cancel/send-otp';
  var CANCEL_URL = API_BASE + '/api/hotel-cancel/confirm';
  var BID = '{{ bid }}';
  var BOOKING_ID = '{{ booking_id }}';
  var EMAIL = '{{ email }}';
  var ROOMS = {{ rooms_json | tojson }};
  var PAYMENT_URL = '{{ payment_url }}';

  var selectedRoom = null;

  /* ---- DOM references (scoped to container) ---- */
  var loadingOverlay = container.querySelector('.hc-loading');
  var errorBanner = container.querySelector('.hc-error-msg');

  /* ---- Utility functions ---- */
  function showStep(stepName) {
    var steps = container.querySelectorAll('.hc-step');
    for (var i = 0; i < steps.length; i++) {
      steps[i].classList.remove('active');
    }
    var target = container.querySelector('[data-step="' + stepName + '"]');
    if (target) target.classList.add('active');
    errorBanner.style.display = 'none';
  }

  function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
  }

  function showError(message) {
    errorBanner.textContent = message;
    errorBanner.style.display = 'block';
  }

  function updateRoomLabels() {
    if (!selectedRoom) return;
    var labels = container.querySelectorAll('.hc-selected-room-label');
    var text = selectedRoom.room_type;
    if (selectedRoom.room_no) text += ' (Room ' + selectedRoom.room_no + ')';
    if (selectedRoom.amount) text += ' — ₹' + selectedRoom.amount;
    for (var i = 0; i < labels.length; i++) {
      labels[i].textContent = text;
    }
  }

  /* ---- API helpers (direct EaseMyTrip calls) ---- */
  function sendOtp() {
    showLoading(true);
    errorBanner.style.display = 'none';
    return fetch(OTP_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ booking_id: BOOKING_ID, email: EMAIL })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      if (!data.isStatus) {
        showError(data.Msg || data.Message || 'Failed to send OTP. Please try again.');
        return null;
      }
      return data;
    })
    .catch(function(err) {
      showLoading(false);
      var msg = (err && err.message && err.message.indexOf('Failed to fetch') !== -1)
        ? 'Unable to reach the server. This may be a CORS issue in local testing — it should work in production.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  function confirmCancellation(otp, reason, remark) {
    showLoading(true);
    errorBanner.style.display = 'none';
    return fetch(CANCEL_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        booking_id: BOOKING_ID,
        email: EMAIL,
        otp: otp,
        reason: reason || 'Change of plans',
        remark: remark || '',
        room_id: selectedRoom ? String(selectedRoom.room_id) : '',
        transaction_id: selectedRoom ? String(selectedRoom.transaction_id) : '',
        is_pay_at_hotel: selectedRoom ? !!selectedRoom.is_pay_at_hotel : false,
        payment_url: PAYMENT_URL || ''
      })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      if (typeof data === 'string') {
        var success = data.toLowerCase().indexOf('success') !== -1;
        if (!success) {
          showError(data || 'Cancellation failed. Please try again.');
          return null;
        }
        return { Status: true, message: data };
      }
      if (!data.Status && !data.isStatus) {
        showError(data.LogMessage || data.Message || data.Msg || 'Cancellation failed. Please try again.');
        return null;
      }
      return data;
    })
    .catch(function(err) {
      showLoading(false);
      var msg = (err && err.message && err.message.indexOf('Failed to fetch') !== -1)
        ? 'Unable to reach the server. This may be a CORS issue in local testing — it should work in production.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  /* ---- Step 1: Room selection ---- */
  var cancelBtns = container.querySelectorAll('.hc-cancel-btn');
  for (var i = 0; i < cancelBtns.length; i++) {
    cancelBtns[i].addEventListener('click', function() {
      var roomId = this.getAttribute('data-room-id');
      selectedRoom = null;
      for (var j = 0; j < ROOMS.length; j++) {
        if (ROOMS[j].room_id === roomId) {
          selectedRoom = ROOMS[j];
          break;
        }
      }
      if (!selectedRoom) return;
      updateRoomLabels();
      showStep('reason');
    });
  }

  /* ---- Step 2: Send OTP ---- */
  var sendOtpBtn = container.querySelector('.hc-send-otp-btn');
  if (sendOtpBtn) {
    sendOtpBtn.addEventListener('click', function() {
      sendOtp().then(function(result) {
        if (result) showStep('otp');
      });
    });
  }

  /* ---- Step 3: Confirm cancellation ---- */
  var confirmBtn = container.querySelector('.hc-confirm-btn');
  if (confirmBtn) {
    confirmBtn.addEventListener('click', function() {
      var otpInput = container.querySelector('.hc-otp-input');
      var otp = otpInput ? otpInput.value.trim() : '';
      if (!otp || otp.length < 4) {
        showError('Please enter a valid OTP.');
        return;
      }

      var reasonSelect = container.querySelector('.hc-reason-select');
      var remarkTextarea = container.querySelector('.hc-remark-textarea');

      confirmCancellation(
        otp,
        reasonSelect ? reasonSelect.value : 'Change of plans',
        remarkTextarea ? remarkTextarea.value : ''
      ).then(function(result) {
        if (result) {
          renderResult(result);
          showStep('result');
        }
      });
    });
  }

  /* ---- Step 4: Render result (direct API response format) ---- */
  function renderResult(data) {
    var resultContainer = container.querySelector('.hc-result-content');

    var html = '<div class="hc-success-box">';
    html += '<div class="hc-success-icon"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg></div>';
    html += '<div class="hc-success-title">Cancellation Confirmed!</div>';

    /* Parse refund info from direct API response */
    var refundAmount = data.RefundAmount;
    var cancellationCharges = data.CancellationCharges;
    var refundMode = data.RefundMode;
    var detail = data.Data || {};

    if (detail.charge) cancellationCharges = detail.charge;
    if (detail.currency) refundMode = detail.currency;
    if (detail.Text) {
      html += '<p style="font-size:13px;color:#646d74;margin-bottom:12px;">' + detail.Text + '</p>';
    }

    if (refundAmount || cancellationCharges || refundMode) {
      html += '<div class="hc-refund-box">';
      html += '<div class="hc-refund-title">Refund Information</div>';
      if (refundAmount) {
        html += '<div class="hc-refund-amount">₹' + refundAmount + '</div>';
      }
      if (cancellationCharges) {
        html += '<div class="hc-refund-row"><span class="hc-refund-label">Cancellation Charges</span><span class="hc-refund-value">₹' + cancellationCharges + '</span></div>';
      }
      if (refundMode) {
        html += '<div class="hc-refund-row"><span class="hc-refund-label">Refund Mode</span><span class="hc-refund-value">' + refundMode + '</span></div>';
      }
      html += '</div>';
    }

    html += '</div>';
    html += '<div class="hc-footer-note">You will receive a confirmation email shortly. Refund will be processed within 5-7 business days.</div>';

    resultContainer.innerHTML = html;
  }

  /* ---- Back navigation ---- */
  var backBtns = container.querySelectorAll('.hc-back-btn');
  for (var i = 0; i < backBtns.length; i++) {
    backBtns[i].addEventListener('click', function() {
      var target = this.getAttribute('data-back-to');
      showStep(target);
    });
  }

})();
</script>
"""


# =====================================================================
# 🎨 RENDERER FUNCTION
# =====================================================================
def render_cancellation_flow(booking_id: str, email: str) -> str:
    """
    Render booking details as display-only HTML (no forms, no API calls).

    This is a PLACEHOLDER that returns a message. The actual booking details
    should be fetched and rendered by the tool itself using render_booking_details().

    Args:
        booking_id: Booking ID
        email: User email

    Returns:
        HTML string with message
    """
    template = _jinja_env.from_string("""
    <div class="booking-details-carousel">
      <main style="max-width: 700px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; color: #646d74; padding: 40px 20px;">
          <p style="font-size: 14px; margin-bottom: 10px;">Loading booking details for <strong>{{ booking_id }}</strong>...</p>
          <p style="font-size: 12px; color: #868686;">Please use chatbot mode for hotel cancellation.</p>
        </div>
      </main>
    </div>
    """)
    return template.render(booking_id=booking_id)


def render_booking_details(
    booking_details: Dict[str, Any],
    booking_id: str = "",
    email: str = "",
    bid: str = "",
    api_base_url: str = "",
) -> str:
    """
    Render booking details as interactive HTML with cancellation flow.

    Renders an interactive template with embedded JS that calls backend
    endpoints for OTP and cancellation (server-side session with cookies).

    Args:
        booking_details: Booking details from API including hotel info, guest info, and rooms
        booking_id: Booking ID (used for API calls)
        email: User email (used for API calls)
        bid: Encrypted booking ID from guest login (used as EmtScreenID/Bid in API calls)
        api_base_url: Base URL of the chatbot API (e.g. 'http://localhost:8000')

    Returns:
        HTML string with rendered interactive booking details
    """
    # Extract hotel information (from nested hotel_info dict)
    hotel_info_raw = booking_details.get("hotel_info", {})
    guest_info_raw = booking_details.get("guest_info", [])

    hotel_info = None
    if hotel_info_raw.get("hotel_name"):
        hotel_info = {
            "name": hotel_info_raw.get("hotel_name", "Hotel"),
            "address": hotel_info_raw.get("address", ""),
            "check_in": _format_date(hotel_info_raw.get("check_in")),
            "check_out": _format_date(hotel_info_raw.get("check_out")),
            "duration": hotel_info_raw.get("duration"),
            "total_fare": hotel_info_raw.get("total_fare"),
        }

    # Get guest names
    guest_names = []
    for guest in guest_info_raw:
        name = f"{guest.get('title', '')} {guest.get('first_name', '')} {guest.get('last_name', '')}".strip()
        if name and name not in guest_names:
            guest_names.append(name)

    # Extract rooms
    rooms = booking_details.get("rooms", [])

    if not rooms:
        return """
        <div class="booking-details-carousel">
          <main style="max-width: 700px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; color: #646d74; padding: 40px 20px;">
              <p style="font-size: 14px;">No rooms found in this booking.</p>
            </div>
          </main>
        </div>
        """

    # Normalize rooms for display
    rooms_ui = []
    for room in rooms:
        # Clean and format cancellation policy
        policy = room.get("cancellation_policy", "")
        # Policy is already cleaned by _strip_html_tags in service

        rooms_ui.append({
            "room_type": room.get("room_type", "Standard Room"),
            "room_no": room.get("room_no"),
            "room_id": room.get("room_id"),
            "transaction_id": room.get("transaction_id"),
            "amount": room.get("amount"),
            "is_pay_at_hotel": room.get("is_pay_at_hotel"),
            "cancellation_policy": policy,
            "is_refundable": room.get("is_refundable"),
            "total_adults": room.get("total_adults"),
            "meal_type": room.get("meal_type"),
        })

    # Build title and subtitle
    booking_id = booking_details.get("booking_id", "")
    title = f"Booking Details - {booking_id}" if booking_id else "Booking Details"

    subtitle_parts = []
    if hotel_info and hotel_info["check_in"] and hotel_info["check_out"]:
        subtitle_parts.append(f"{hotel_info['check_in']} to {hotel_info['check_out']}")
    if hotel_info and hotel_info.get("duration"):
        subtitle_parts.append(f"{hotel_info['duration']} nights")
    subtitle_parts.append(f"{len(rooms)} room{'s' if len(rooms) > 1 else ''}")
    if guest_names:
        subtitle_parts.append(", ".join(guest_names))
    subtitle = " • ".join(subtitle_parts)

    payment_url = booking_details.get("payment_url", "")

    # Render interactive template with embedded JS for full cancel flow
    import uuid
    instance_id = str(uuid.uuid4())[:8]

    # Prepare room data for JS embedding
    rooms_json = [
        {
            "room_id": r.get("room_id"),
            "room_type": r.get("room_type"),
            "room_no": r.get("room_no"),
            "transaction_id": r.get("transaction_id"),
            "is_pay_at_hotel": r.get("is_pay_at_hotel"),
            "amount": r.get("amount"),
        }
        for r in rooms_ui
    ]

    template = _jinja_env.from_string(INTERACTIVE_BOOKING_TEMPLATE)
    return template.render(
        title=title,
        subtitle=subtitle,
        hotel_info=hotel_info,
        rooms=rooms_ui,
        payment_url=payment_url,
        instance_id=instance_id,
        bid=bid,
        booking_id=booking_id,
        email=email,
        rooms_json=rooms_json,
        api_base_url=api_base_url,
    )


def _format_date(date_str: str) -> str:
    """Format date string for display"""
    if not date_str:
        return None

    try:
        from datetime import datetime
        # Try parsing various date formats
        for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"]:
            try:
                date = datetime.strptime(date_str.split("T")[0], fmt)
                return date.strftime("%d %b %Y")
            except ValueError:
                continue
        return date_str
    except Exception:
        return date_str


# =====================================================================
# 🎉 CANCELLATION SUCCESS TEMPLATE (BEAUTIFUL CONFIRMATION UI)
# =====================================================================
CANCELLATION_SUCCESS_TEMPLATE = """
<style>

.cancellation-success {
  font-family: poppins, sans-serif;
  color: #202020;
  background: rgba(255, 255, 255, 0.92);
  position: relative;
}

.cancellation-success * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
}

.cancellation-success main {
  max-width: 600px;
  margin: 0 auto;
  padding: 30px 20px;
}

.cancellation-success .success-container {
  background: linear-gradient(135deg, #e8f5e9 0%, #f1f8f4 100%);
  border: 2px solid #4caf50;
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
}

.cancellation-success .success-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(76, 175, 80, 0.3);
  animation: successPop 0.6s ease-out;
}

@keyframes successPop {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}

.cancellation-success .success-icon svg {
  width: 48px;
  height: 48px;
  color: #fff;
}

.cancellation-success .success-title {
  font-size: 24px;
  font-weight: 700;
  color: #2e7d32;
  margin-bottom: 12px;
}

.cancellation-success .details-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-top: 24px;
  text-align: left;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.cancellation-success .details-title {
  font-size: 16px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e0e0e0;
}

.cancellation-success .detail-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  font-size: 14px;
  border-bottom: 1px solid #f5f5f5;
}

.cancellation-success .detail-item:last-child {
  border-bottom: none;
}

.cancellation-success .detail-label {
  color: #646d74;
  font-weight: 500;
}

.cancellation-success .detail-value {
  color: #202020;
  font-weight: 600;
  text-align: right;
}

.cancellation-success .refund-highlight {
  background: linear-gradient(135deg, #fff8e1 0%, #fffbea 100%);
  border: 2px solid #ffc107;
  border-radius: 12px;
  padding: 16px;
  margin-top: 20px;
}

.cancellation-success .refund-title {
  font-size: 15px;
  font-weight: 600;
  color: #f57c00;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.cancellation-success .refund-amount {
  font-size: 28px;
  font-weight: 700;
  color: #ef6614;
  font-family: inter, sans-serif;
  margin-bottom: 8px;
}

.cancellation-success .refund-details {
  font-size: 12px;
  color: #666;
  line-height: 1.5;
}

.cancellation-success .footer-note {
  font-size: 12px;
  color: #868686;
  text-align: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

/* Dark mode support */
.cancellation-success.dark {
  background: #000;
  color: #fff;
}

.cancellation-success.dark .success-container {
  background: linear-gradient(135deg, #1a3a1a 0%, #1f2d1f 100%);
  border-color: #4caf50;
}

.cancellation-success.dark .success-title {
  color: #66bb6a;
}

.cancellation-success.dark .details-section {
  background: #1a1a1a;
  border-color: #373737;
}

.cancellation-success.dark .details-title {
  color: #fff;
  border-color: #373737;
}

.cancellation-success.dark .detail-label {
  color: #bcbcbc;
}

.cancellation-success.dark .detail-value {
  color: #fff;
}

.cancellation-success.dark .refund-highlight {
  background: linear-gradient(135deg, #332a00 0%, #3d3200 100%);
  border-color: #ffc107;
}

</style>

<div class="cancellation-success">
  <main>
    <div class="success-container">
      <div class="success-icon">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
        </svg>
      </div>

      <h1 class="success-title">Cancellation Confirmed!</h1>

      <div class="details-section">
        <div class="details-title">Cancellation Details</div>

        {% if booking_id %}
        <div class="detail-item">
          <span class="detail-label">Booking ID</span>
          <span class="detail-value">{{ booking_id }}</span>
        </div>
        {% endif %}

        {% if hotel_name %}
        <div class="detail-item">
          <span class="detail-label">Hotel</span>
          <span class="detail-value">{{ hotel_name }}</span>
        </div>
        {% endif %}

        {% if room_type %}
        <div class="detail-item">
          <span class="detail-label">Room Type</span>
          <span class="detail-value">{{ room_type }}</span>
        </div>
        {% endif %}

        {% if cancellation_date %}
        <div class="detail-item">
          <span class="detail-label">Cancelled On</span>
          <span class="detail-value">{{ cancellation_date }}</span>
        </div>
        {% endif %}
      </div>

      {% if refund_info %}
      <div class="refund-highlight">
        <div class="refund-title">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
            <path d="M5.255 5.786a.237.237 0 0 0 .241.247h.825c.138 0 .248-.113.266-.25.09-.656.54-1.134 1.342-1.134.686 0 1.314.343 1.314 1.168 0 .635-.374.927-.965 1.371-.673.489-1.206 1.06-1.168 1.987l.003.217a.25.25 0 0 0 .25.246h.811a.25.25 0 0 0 .25-.25v-.105c0-.718.273-.927 1.01-1.486.609-.463 1.244-.977 1.244-2.056 0-1.511-1.276-2.241-2.673-2.241-1.267 0-2.655.59-2.75 2.286zm1.557 5.763c0 .533.425.927 1.01.927.609 0 1.028-.394 1.028-.927 0-.552-.42-.94-1.029-.94-.584 0-1.009.388-1.009.94z"/>
          </svg>
          Refund Information
        </div>
        <div class="refund-amount">₹{{ refund_info.refund_amount }}</div>
        <div class="refund-details">
          Cancellation charges: ₹{{ refund_info.cancellation_charges }}<br>
          {% if refund_info.refund_mode %}Refund mode: {{ refund_info.refund_mode }}{% endif %}
        </div>
      </div>
      {% endif %}

    </div>

    <div class="footer-note">
      Thank you for using EaseMyTrip. We hope to serve you again soon!
    </div>
  </main>
</div>
"""


def render_cancellation_success(cancellation_result: Dict[str, Any]) -> str:
    """
    Render beautiful cancellation success confirmation UI.

    Args:
        cancellation_result: Cancellation result including refund info

    Returns:
        HTML string with success confirmation
    """
    from datetime import datetime

    # Extract refund information
    refund_info = cancellation_result.get("refund_info")
    if refund_info:
        refund_data = {
            "refund_amount": refund_info.get("refund_amount", "0"),
            "cancellation_charges": refund_info.get("cancellation_charges", "0"),
            "refund_mode": refund_info.get("refund_mode", "Original payment method"),
        }
    else:
        refund_data = None

    # Get current date for cancellation date
    cancellation_date = datetime.now().strftime("%d %b %Y, %I:%M %p")

    # Render template
    template = _jinja_env.from_string(CANCELLATION_SUCCESS_TEMPLATE)
    return template.render(
        booking_id=cancellation_result.get("booking_id"),
        hotel_name=cancellation_result.get("hotel_name"),
        room_type=cancellation_result.get("room_type"),
        cancellation_date=cancellation_date,
        refund_info=refund_data,
    )
