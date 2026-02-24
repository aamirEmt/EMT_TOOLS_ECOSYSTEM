"""Cancellation Booking Details Renderer (Display-Only)"""
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

.booking-details-carousel .hc-pay-pending {
  color: #f57c00;
  font-weight: 600;
  font-size: 12px;
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
  color: #d32f2f;
  padding: 4px 14px;
  border-radius: 8px;
  font-size: 12px;
  margin-bottom: 4px;
  margin-top: -4px;
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
  padding: 10px 24px;
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

/* Verify OTP card */
.booking-details-carousel .hc-verify-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  padding: 5px 12px;
  text-align: center;
  max-width: 400px;
  margin: 0 auto;
}

.booking-details-carousel .hc-verify-icon {
  width: 50px;
  height: 50px;
  margin: 0 auto 4px;
  background: linear-gradient(135deg, #ef6614 0%, #f58434 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 16px rgba(239, 102, 20, 0.25);
}

.booking-details-carousel .hc-verify-title {
  font-size: 18px;
  font-weight: 700;
  color: #202020;
  margin-bottom: 8px;
}

.booking-details-carousel .hc-verify-desc {
  font-size: 13px;
  color: #646d74;
  line-height: 1.5;
  margin-bottom: 9px;
}

.booking-details-carousel .hc-otp-field {
  margin-bottom: 16px;
}

.booking-details-carousel .hc-otp-field .hc-login-otp-input {
  width: 100%;
  max-width: 240px;
  padding: 10px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  text-align: center;
  letter-spacing: 4px;
  font-family: inter, sans-serif;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #fff;
  color: #202020;
}

.booking-details-carousel .hc-otp-field .hc-login-otp-input:focus {
  border-color: #ef6614;
  box-shadow: 0 0 0 3px rgba(239, 102, 20, 0.1);
}

.booking-details-carousel .hc-otp-field .hc-login-otp-input::placeholder {
  font-size: 14px;
  letter-spacing: 0;
  font-weight: 400;
  color: #bbb;
}

.booking-details-carousel .hc-verify-card .hc-submit-btn {
  width: 80%;
  max-width: 240px;
  padding: 8px 7px;
}

.booking-details-carousel .hc-verify-footer {
  font-size: 11px;
  color: #999;
  margin-top: 16px;
  line-height: 1.4;
}

.booking-details-carousel .hc-resend-otp-btn {
  background: none;
  border: none;
  color: #2196f3;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  margin-top: 8px;
  text-decoration: none;
  display: inline-block;
}
.booking-details-carousel .hc-resend-otp-btn:hover {
  text-decoration: underline;
  color: #1565c0;
}
.booking-details-carousel .hc-resend-otp-btn:disabled {
  color: #999;
  cursor: not-allowed;
  text-decoration: none;
}

.booking-details-carousel .hc-verify-icon--cancel {
  background: linear-gradient(135deg, #d32f2f 0%, #ef5350 100%);
  box-shadow: 0 4px 16px rgba(211, 47, 47, 0.25);
}

.booking-details-carousel .hc-verify-card .hc-otp-input {
  width: 100%;
  max-width: 240px;
  padding: 8px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 500;
  text-align: center;
  letter-spacing: 4px;
  font-family: inter, sans-serif;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #fff;
  color: #202020;
}

.booking-details-carousel .hc-verify-card .hc-otp-input:focus {
  border-color: #ef6614;
  box-shadow: 0 0 0 3px rgba(239, 102, 20, 0.1);
}

.booking-details-carousel .hc-verify-card .hc-otp-input::placeholder {
  font-size: 14px;
  letter-spacing: 0;
  font-weight: 400;
  color: #bbb;
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

.booking-details-carousel.dark .hc-pay-pending {
  color: #ffb74d;
}

.booking-details-carousel.dark .hc-verify-card {
  background: linear-gradient(135deg, #1a1a1a 0%, #111 100%);
  border-color: #373737;
}

.booking-details-carousel.dark .hc-verify-title {
  color: #fff;
}

.booking-details-carousel.dark .hc-verify-desc {
  color: #bcbcbc;
}

.booking-details-carousel.dark .hc-otp-field .hc-login-otp-input {
  background: #000;
  border-color: #373737;
  color: #fff;
}

.booking-details-carousel.dark .hc-otp-field .hc-login-otp-input:focus {
  border-color: #ef6614;
  box-shadow: 0 0 0 3px rgba(239, 102, 20, 0.2);
}

.booking-details-carousel.dark .hc-verify-footer {
  color: #666;
}

.booking-details-carousel.dark .hc-verify-card .hc-otp-input {
  background: #000;
  border-color: #373737;
  color: #fff;
}

.booking-details-carousel.dark .hc-verify-card .hc-otp-input:focus {
  border-color: #ef6614;
  box-shadow: 0 0 0 3px rgba(239, 102, 20, 0.2);
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
      <div class="bksub"{% if is_otp_send %} style="display:none"{% endif %}>{{ subtitle }}</div>
    </div>

    <!-- STEP 0: Login OTP verification -->
    {% if is_otp_send %}
    <div class="hc-step active" data-step="verify-otp">
      <div class="hc-verify-card">
        <div class="hc-verify-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>
          </svg>
        </div>
        <div class="hc-verify-title">Verify Your Identity</div>
        <p class="hc-verify-desc">
          We've sent a One-Time Password to your registered email &amp; phone number. Enter it below to continue.
        </p>
        <div class="hc-otp-field">
          <input type="text" class="hc-login-otp-input" maxlength="10" placeholder="Enter OTP" autocomplete="one-time-code" />
        </div>
        <div class="hc-error-msg hc-step-error"></div>
        <button type="button" class="hc-submit-btn hc-verify-otp-btn">Verify &amp; Continue</button>
        <p class="hc-verify-footer">Didn't receive the OTP? <button type="button" class="hc-resend-otp-btn hc-resend-login-otp">Resend OTP</button></p>
      </div>
    </div>
    {% endif %}

    <!-- STEP 1: Room details + cancel buttons -->
    <div class="hc-step {{ 'active' if not is_otp_send and not all_cancelled else '' }}" data-step="details">
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
      <div class="rooms-title">Room Details</div>
      <div class="slider-shell">
        <div class="rsltcvr">
          <div class="embla__container">
            {% for room in rooms %}
            <div class="room-card"{% if room.is_cancelled %} style="opacity: 0.5; pointer-events: none;"{% endif %}>
              <div class="room-header">
                <div class="room-type">{{ room.room_type }}{% if room.is_cancelled %} <span style="background:#ffebee;color:#c62828;font-size:11px;padding:2px 8px;border-radius:4px;margin-left:8px;">Cancelled</span>{% endif %}</div>
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
                  <span class="detail-value">
                    {% if room.is_pay_at_hotel %}
                    <span class="hc-pay-pending">Payment Pending</span>
                    {% else %}
                    Prepaid
                    {% endif %}
                  </span>
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
            </div>
            {% endfor %}
          </div>
        </div>
      </div>
      {% if not all_cancelled %}
      <button type="button" class="hc-cancel-btn hc-single-cancel-btn" style="margin-top:16px;">Cancel</button>
      {% endif %}
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
      <div class="hc-verify-card">
        <div class="hc-verify-icon hc-verify-icon--cancel">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/>
          </svg>
        </div>
        <div class="hc-verify-title">Confirm Cancellation</div>
        <p class="hc-verify-desc">
          A cancellation OTP has been sent to your registered email &amp; phone. Enter it below to confirm.
        </p>
        <div class="hc-otp-field">
          <input type="text" class="hc-otp-input" maxlength="10" placeholder="Enter OTP" autocomplete="one-time-code" />
        </div>
        <div class="hc-error-msg hc-step-error"></div>
        <div class="hc-btn-row" style="justify-content: center;">
          <button type="button" class="hc-back-btn" data-back-to="reason">Back</button>
          <button type="button" class="hc-submit-btn hc-confirm-btn">Confirm Cancellation</button>
        </div>
        <p class="hc-verify-footer">
          This action cannot be undone. Refund will be processed as per cancellation policy.<br>
          Didn't receive the OTP? <button type="button" class="hc-resend-otp-btn hc-resend-cancel-otp">Resend OTP</button>
        </p>
      </div>
    </div>

    <!-- STEP 4: Result -->
    <div class="hc-step" data-step="result">
      <div class="hc-result-content"></div>
    </div>

    <!-- STEP: Already Cancelled -->
    <div class="hc-step {{ 'active' if not is_otp_send and all_cancelled else '' }}" data-step="cancelled">
      <div style="text-align:center;padding:30px 20px;">
        <div style="width:56px;height:56px;margin:0 auto 14px;background:#ffebee;border-radius:50%;display:flex;align-items:center;justify-content:center;">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="#c62828" style="width:28px;height:28px;">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </div>
        <h3 style="font-size:17px;font-weight:700;color:#1a1a2e;margin:0 0 8px;">Booking Already Cancelled</h3>
        <p style="font-size:13px;color:#646d74;margin:0 0 14px;">All rooms in this booking have already been cancelled.</p>
        <div style="background:#f8f9fa;border-radius:8px;padding:10px 14px;display:inline-block;">
          <span style="font-size:12px;color:#646d74;">No further action is needed. If you have questions about your refund, please contact support.</span>
        </div>
      </div>
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
  var VERIFY_OTP_URL = API_BASE + '/api/hotel-cancel/verify-otp';
  var OTP_URL = API_BASE + '/api/hotel-cancel/send-otp';
  var CANCEL_URL = API_BASE + '/api/hotel-cancel/confirm';
  var RESEND_LOGIN_OTP_URL = API_BASE + '/api/hotel-cancel/resend-login-otp';
  var BID = '{{ bid }}';
  var BOOKING_ID = '{{ booking_id }}';
  var EMAIL = '{{ email }}';
  var ROOMS = {{ rooms_json | tojson }};
  var ALL_CANCELLED = {{ 'true' if all_cancelled else 'false' }};

  var selectedRoom = null;

  /* ---- DOM references (scoped to container) ---- */
  var loadingOverlay = container.querySelector('.hc-loading');
  var globalErrorBanner = container.querySelector('main > .hc-error-msg');

  /* ---- Utility functions ---- */
  function hideAllErrors() {
    var errs = container.querySelectorAll('.hc-error-msg');
    for (var i = 0; i < errs.length; i++) errs[i].style.display = 'none';
  }

  function showStep(stepName) {
    var steps = container.querySelectorAll('.hc-step');
    for (var i = 0; i < steps.length; i++) {
      steps[i].classList.remove('active');
    }
    var target = container.querySelector('[data-step="' + stepName + '"]');
    if (target) target.classList.add('active');
    hideAllErrors();
  }

  function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
  }

  function showError(message) {
    hideAllErrors();
    var activeStep = container.querySelector('.hc-step.active');
    var inlineErr = activeStep ? activeStep.querySelector('.hc-step-error') : null;
    var target = inlineErr || globalErrorBanner;
    target.textContent = message;
    target.style.display = 'block';
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

  /* ---- API helpers ---- */
  function verifyLoginOtp(otp) {
    showLoading(true);
    hideAllErrors();
    return fetch(VERIFY_OTP_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ booking_id: BOOKING_ID, email: EMAIL, otp: otp })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      /* Handle multiple response formats:
         - Direct API: { isVerify: "true", Message: "valid otp." }
         - Tool response: { success: true, message: "..." }
         - Wrapped: { structured_content: { success: true }, response_text: "..." }
         - Status-based: { isStatus: true, Msg: "..." } */
      var isVerified = false;
      var msg = '';

      if (data.structured_content) {
        isVerified = !!data.structured_content.success;
        msg = data.structured_content.message || data.response_text || '';
      } else if (data.isVerify !== undefined) {
        isVerified = String(data.isVerify).toLowerCase() === 'true';
        msg = data.Message || data.Msg || '';
      } else if (data.success !== undefined) {
        isVerified = !!data.success;
        msg = data.message || data.Message || '';
      } else if (data.isStatus !== undefined) {
        isVerified = !!data.isStatus;
        msg = data.Msg || data.Message || '';
      }

      if (!isVerified) {
        showError(msg || 'Invalid OTP. Please check and try again.');
        return null;
      }
      return data;
    })
    .catch(function(err) {
      showLoading(false);
      var msg = (err && err.message && err.message.indexOf('Failed to fetch') !== -1)
        ? 'Something Went Wrong Please Try Again.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  function sendOtp() {
    showLoading(true);
    hideAllErrors();
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
        ? 'Something Went Wrong Please Try Again.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  function confirmCancellation(otp, reason, remark) {
    showLoading(true);
    hideAllErrors();
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
        is_pay_at_hotel: selectedRoom ? !!selectedRoom.is_pay_at_hotel : false
      })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      if (typeof data === 'string') {
        var success = data.toLowerCase().indexOf('success') !== -1;
        if (!success) {
          var isOtpError = data.toLowerCase().indexOf('otp') !== -1;
          var fallback = isOtpError ? 'Invalid OTP. Please check and try again.' : 'Cancellation failed. Please try again.';
          showError(data || fallback);
          return null;
        }
        return { Status: true, message: data };
      }
      if (!data.Status && !data.isStatus) {
        var msg = data.LogMessage || data.Message || data.Msg || '';
        var isOtpError = msg.toLowerCase().indexOf('otp') !== -1;
        var fallback = isOtpError ? 'Invalid OTP. Please check and try again.' : 'Cancellation failed. Please try again.';
        showError(msg || fallback);
        return null;
      }
      return data;
    })
    .catch(function(err) {
      showLoading(false);
      var msg = (err && err.message && err.message.indexOf('Failed to fetch') !== -1)
        ? 'Something Went Wrong Please Try Again.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  /* ---- Step 0: Verify login OTP ---- */
  var verifyOtpBtn = container.querySelector('.hc-verify-otp-btn');
  if (verifyOtpBtn) {
    verifyOtpBtn.addEventListener('click', function() {
      var otpInput = container.querySelector('.hc-login-otp-input');
      var otp = otpInput ? otpInput.value.trim() : '';
      if (!otp || otp.length < 4) {
        showError('Please enter a valid OTP.');
        return;
      }
      verifyLoginOtp(otp).then(function(result) {
        if (result) {
          var sub = container.querySelector('.bksub');
          if (sub) sub.style.display = '';
          if (ALL_CANCELLED) { showStep('cancelled'); }
          else { showStep('details'); }
        }
      });
    });
  }

  /* ---- Resend login OTP ---- */
  var resendLoginOtpBtn = container.querySelector('.hc-resend-login-otp');
  if (resendLoginOtpBtn) {
    resendLoginOtpBtn.addEventListener('click', function() {
      var btn = this;
      btn.disabled = true;
      btn.textContent = 'Sending...';
      fetch(RESEND_LOGIN_OTP_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ booking_id: BOOKING_ID, email: EMAIL })
      })
      .then(function(resp) { return resp.json(); })
      .then(function(data) {
        btn.textContent = 'OTP Sent!';
        setTimeout(function() { btn.textContent = 'Resend OTP'; btn.disabled = false; }, 3000);
      })
      .catch(function() {
        showError('Failed to resend OTP. Please try again.');
        btn.textContent = 'Resend OTP';
        btn.disabled = false;
      });
    });
  }

  /* ---- Step 1: Single cancel button ---- */
  var singleCancelBtn = container.querySelector('.hc-single-cancel-btn');
  if (singleCancelBtn) {
    singleCancelBtn.addEventListener('click', function() {
      selectedRoom = null;
      for (var j = 0; j < ROOMS.length; j++) {
        if (!ROOMS[j].is_cancelled) {
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

  /* ---- Resend cancellation OTP ---- */
  var resendCancelOtpBtn = container.querySelector('.hc-resend-cancel-otp');
  if (resendCancelOtpBtn) {
    resendCancelOtpBtn.addEventListener('click', function() {
      var btn = this;
      btn.disabled = true;
      btn.textContent = 'Sending...';
      sendOtp().then(function(result) {
        if (result) {
          btn.textContent = 'OTP Sent!';
        } else {
          btn.textContent = 'Resend OTP';
        }
        btn.disabled = false;
        setTimeout(function() { btn.textContent = 'Resend OTP'; }, 3000);
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
    is_otp_send: bool = False,
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
        is_otp_send: Whether a login OTP was auto-sent (shows verify OTP step first)

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
            "is_cancelled": room.get("is_cancelled", False),
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
            "is_cancelled": r.get("is_cancelled", False),
        }
        for r in rooms_ui
    ]

    all_cancelled = booking_details.get("all_cancelled", False)

    template = _jinja_env.from_string(INTERACTIVE_BOOKING_TEMPLATE)
    return template.render(
        title=title,
        subtitle=subtitle,
        hotel_info=hotel_info,
        rooms=rooms_ui,
        instance_id=instance_id,
        bid=bid,
        booking_id=booking_id,
        email=email,
        rooms_json=rooms_json,
        api_base_url=api_base_url,
        is_otp_send=is_otp_send,
        all_cancelled=all_cancelled,
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


# =====================================================================
# 🚆 TRAIN INTERACTIVE BOOKING TEMPLATE (WITH JS FOR CANCEL FLOW)
# =====================================================================
TRAIN_BOOKING_TEMPLATE = """
<style>

.train-cancel-carousel {
  font-family: poppins, sans-serif;
  color: #202020;
  background: rgba(255, 255, 255, 0.92);
  position: relative;
}

.train-cancel-carousel * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
}

.train-cancel-carousel main {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px 0 30px;
  position: relative;
}

.train-cancel-carousel .tc-header {
  margin-bottom: 16px;
}

.train-cancel-carousel .tc-title {
  font-size: 18px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 4px;
}

.train-cancel-carousel .tc-subtitle {
  font-size: 12px;
  color: #646d74;
  margin-top: 4px;
}

.train-cancel-carousel .tc-train-info {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 16px;
  border: 1px solid #e0e0e0;
}

.train-cancel-carousel .tc-train-name {
  font-size: 16px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.train-cancel-carousel .tc-route {
  font-size: 13px;
  color: #202020;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.train-cancel-carousel .tc-route-arrow {
  color: #ef6614;
  font-weight: 600;
}

.train-cancel-carousel .tc-details-row {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #202020;
  margin-top: 8px;
  flex-wrap: wrap;
}

.train-cancel-carousel .tc-detail-item {
  display: flex;
  flex-direction: column;
}

.train-cancel-carousel .tc-detail-label {
  font-size: 10px;
  color: #868686;
  text-transform: uppercase;
  margin-bottom: 2px;
}

.train-cancel-carousel .tc-detail-value {
  font-weight: 600;
}

.train-cancel-carousel .tc-pax-section {
  margin-bottom: 16px;
}

.train-cancel-carousel .tc-pax-title {
  font-size: 14px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 12px;
}

.train-cancel-carousel .tc-select-all {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 13px;
  color: #646d74;
  cursor: pointer;
}

.train-cancel-carousel .tc-select-all input[type="checkbox"] {
  accent-color: #ef6614;
  width: 16px;
  height: 16px;
}

.train-cancel-carousel .tc-pax-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.train-cancel-carousel .tc-pax-table th {
  background: #f8f9fa;
  padding: 8px 10px;
  text-align: left;
  font-weight: 600;
  color: #646d74;
  font-size: 11px;
  text-transform: uppercase;
  border-bottom: 2px solid #e0e0e0;
}

.train-cancel-carousel .tc-pax-table td {
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  color: #202020;
}

.train-cancel-carousel .tc-pax-table tr:hover {
  background: #fef6f0;
}

.train-cancel-carousel .tc-pax-table input[type="checkbox"] {
  accent-color: #ef6614;
  width: 16px;
  height: 16px;
}

.train-cancel-carousel .tc-status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.train-cancel-carousel .tc-status-cnf {
  background: #e8f5e9;
  color: #2e7d32;
}

.train-cancel-carousel .tc-status-other {
  background: #fff3e0;
  color: #e65100;
}

.train-cancel-carousel .tc-price-info {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 16px;
  border: 1px solid #e0e0e0;
}

.train-cancel-carousel .tc-price-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 4px 0;
}

.train-cancel-carousel .tc-price-label {
  color: #646d74;
}

.train-cancel-carousel .tc-price-value {
  font-weight: 600;
  color: #202020;
}

.train-cancel-carousel .tc-price-total {
  font-size: 16px;
  color: #ef6614;
  font-family: inter, sans-serif;
}

/* Reuse common interactive styles from hotel template */
.train-cancel-carousel .hc-step { display: none; }
.train-cancel-carousel .hc-step.active { display: block; }

.train-cancel-carousel .hc-cancel-btn {
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
.train-cancel-carousel .hc-cancel-btn:hover { opacity: 0.85; }
.train-cancel-carousel .hc-cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.train-cancel-carousel .hc-loading {
  display: none;
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.85);
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 12px;
}

.train-cancel-carousel .hc-spinner {
  width: 36px; height: 36px;
  border: 3px solid #e0e0e0;
  border-top-color: #ef6614;
  border-radius: 50%;
  animation: tcSpin 0.8s linear infinite;
}
@keyframes tcSpin { to { transform: rotate(360deg); } }

.train-cancel-carousel .hc-error-msg {
  display: none;
  color: #d32f2f;
  padding: 4px 14px;
  border-radius: 8px;
  font-size: 12px;
  margin-bottom: 4px;
  margin-top: -4px;
}

.train-cancel-carousel .hc-verify-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  padding: 5px 12px;
  text-align: center;
  max-width: 400px;
  margin: 0 auto;
}

.train-cancel-carousel .hc-verify-icon {
  width: 50px; height: 50px;
  margin: 0 auto 4px;
  background: linear-gradient(135deg, #ef6614 0%, #f58434 100%);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  box-shadow: 0 4px 16px rgba(239, 102, 20, 0.25);
}

.train-cancel-carousel .hc-verify-title {
  font-size: 18px; font-weight: 700; color: #202020; margin-bottom: 8px;
}

.train-cancel-carousel .hc-verify-desc {
  font-size: 13px; color: #646d74; line-height: 1.5; margin-bottom: 9px;
}

.train-cancel-carousel .hc-otp-field { margin-bottom: 16px; }

.train-cancel-carousel .hc-login-otp-input {
  width: 100%; max-width: 240px;
  padding: 10px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 14px; font-weight: 600;
  text-align: center; letter-spacing: 4px;
  font-family: inter, sans-serif;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #fff; color: #202020;
}
.train-cancel-carousel .hc-login-otp-input:focus {
  border-color: #ef6614;
  box-shadow: 0 0 0 3px rgba(239, 102, 20, 0.1);
}
.train-cancel-carousel .hc-login-otp-input::placeholder {
  font-size: 14px; letter-spacing: 0; font-weight: 400; color: #bbb;
}

.train-cancel-carousel .hc-submit-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, #ef6614 0%, #f58434 100%);
  color: #fff; border: none; border-radius: 8px;
  font-size: 14px; font-weight: 600; cursor: pointer;
  font-family: poppins, sans-serif;
  transition: opacity 0.2s;
}
.train-cancel-carousel .hc-submit-btn:hover { opacity: 0.85; }

.train-cancel-carousel .hc-back-btn {
  background: none;
  border: 1px solid #e0e0e0;
  padding: 8px 16px; border-radius: 8px;
  font-size: 12px; cursor: pointer;
  color: #646d74; font-family: poppins, sans-serif;
  transition: border-color 0.2s;
}
.train-cancel-carousel .hc-back-btn:hover { border-color: #ef6614; color: #ef6614; }

.train-cancel-carousel .hc-btn-row {
  display: flex; gap: 8px; margin-top: 16px;
}

.train-cancel-carousel .hc-verify-icon--cancel {
  background: linear-gradient(135deg, #d32f2f 0%, #ef5350 100%);
  box-shadow: 0 4px 16px rgba(211, 47, 47, 0.25);
}

.train-cancel-carousel .hc-otp-input {
  width: 100%; max-width: 240px;
  padding: 8px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 18px; font-weight: 600;
  text-align: center; letter-spacing: 4px;
  font-family: inter, sans-serif;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #fff; color: #202020;
}
.train-cancel-carousel .hc-otp-input:focus {
  border-color: #ef6614;
  box-shadow: 0 0 0 3px rgba(239, 102, 20, 0.1);
}
.train-cancel-carousel .hc-otp-input::placeholder {
  font-size: 14px; letter-spacing: 0; font-weight: 400; color: #bbb;
}

.train-cancel-carousel .hc-verify-footer {
  font-size: 11px; color: #999; margin-top: 16px; line-height: 1.4;
}

.train-cancel-carousel .hc-selected-room-badge {
  background: #f5f5f5;
  padding: 10px 14px; border-radius: 8px;
  font-size: 13px; margin-bottom: 16px;
  border-left: 3px solid #ef6614;
}

/* Success result */
.train-cancel-carousel .hc-success-box {
  background: linear-gradient(135deg, #e8f5e9 0%, #f1f8f4 100%);
  border: 2px solid #4caf50; border-radius: 16px;
  padding: 32px 24px; text-align: center;
}
.train-cancel-carousel .hc-success-icon {
  width: 64px; height: 64px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 20px rgba(76, 175, 80, 0.3);
  animation: tcSuccessPop 0.6s ease-out;
}
@keyframes tcSuccessPop {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}
.train-cancel-carousel .hc-success-icon svg { width: 36px; height: 36px; color: #fff; }
.train-cancel-carousel .hc-success-title {
  font-size: 20px; font-weight: 700; color: #2e7d32; margin-bottom: 16px;
}
.train-cancel-carousel .hc-refund-box {
  background: linear-gradient(135deg, #fff8e1 0%, #fffbea 100%);
  border: 2px solid #ffc107; border-radius: 12px;
  padding: 16px; margin-top: 16px; text-align: left;
}
.train-cancel-carousel .hc-refund-title { font-size: 14px; font-weight: 600; color: #f57c00; margin-bottom: 10px; }
.train-cancel-carousel .hc-refund-row { display: flex; justify-content: space-between; font-size: 13px; padding: 4px 0; }
.train-cancel-carousel .hc-refund-label { color: #646d74; }
.train-cancel-carousel .hc-refund-value { font-weight: 600; color: #202020; }
.train-cancel-carousel .hc-refund-amount { font-size: 24px; font-weight: 700; color: #ef6614; font-family: inter, sans-serif; margin-bottom: 8px; }
.train-cancel-carousel .hc-footer-note { font-size: 12px; color: #868686; text-align: center; margin-top: 20px; }

.train-cancel-carousel .hc-resend-otp-btn {
  background: none; border: none; color: #2196f3; font-size: 12px; font-weight: 600;
  cursor: pointer; padding: 0; margin-top: 8px; text-decoration: none; display: inline-block;
}
.train-cancel-carousel .hc-resend-otp-btn:hover { text-decoration: underline; color: #1565c0; }
.train-cancel-carousel .hc-resend-otp-btn:disabled { color: #999; cursor: not-allowed; text-decoration: none; }

/* Dark mode */
.train-cancel-carousel.dark { background: #000; color: #fff; }
.train-cancel-carousel.dark .tc-train-info,
.train-cancel-carousel.dark .tc-price-info { background: #000; border-color: #373737; }
.train-cancel-carousel.dark .tc-title,
.train-cancel-carousel.dark .tc-train-name,
.train-cancel-carousel.dark .tc-detail-value,
.train-cancel-carousel.dark .tc-price-value,
.train-cancel-carousel.dark .tc-pax-table td { color: #fff; }
.train-cancel-carousel.dark .tc-subtitle,
.train-cancel-carousel.dark .tc-detail-label,
.train-cancel-carousel.dark .tc-price-label,
.train-cancel-carousel.dark .tc-pax-table th { color: #bcbcbc; }
.train-cancel-carousel.dark .tc-pax-table th { background: #111; border-color: #373737; }
.train-cancel-carousel.dark .tc-pax-table td { border-color: #222; }
.train-cancel-carousel.dark .tc-pax-table tr:hover { background: #1a1a1a; }
.train-cancel-carousel.dark .hc-loading { background: rgba(0,0,0,0.85); }
.train-cancel-carousel.dark .hc-error-msg { background: #3d0000; color: #ff8a80; }
.train-cancel-carousel.dark .hc-verify-card { background: linear-gradient(135deg, #1a1a1a 0%, #111 100%); border-color: #373737; }
.train-cancel-carousel.dark .hc-verify-title { color: #fff; }
.train-cancel-carousel.dark .hc-verify-desc { color: #bcbcbc; }
.train-cancel-carousel.dark .hc-login-otp-input,
.train-cancel-carousel.dark .hc-otp-input { background: #000; border-color: #373737; color: #fff; }
.train-cancel-carousel.dark .hc-login-otp-input:focus,
.train-cancel-carousel.dark .hc-otp-input:focus { border-color: #ef6614; box-shadow: 0 0 0 3px rgba(239, 102, 20, 0.2); }
.train-cancel-carousel.dark .hc-back-btn { border-color: #373737; color: #bcbcbc; }
.train-cancel-carousel.dark .hc-selected-room-badge { background: #1a1a1a; color: #fff; }
.train-cancel-carousel.dark .hc-success-box { background: linear-gradient(135deg, #1a3a1a 0%, #1f2d1f 100%); }
.train-cancel-carousel.dark .hc-success-title { color: #66bb6a; }
.train-cancel-carousel.dark .hc-refund-box { background: linear-gradient(135deg, #332a00 0%, #3d3200 100%); }
.train-cancel-carousel.dark .hc-refund-value { color: #fff; }
.train-cancel-carousel.dark .hc-refund-label { color: #bcbcbc; }
.train-cancel-carousel.dark .hc-verify-footer { color: #666; }

</style>

<div class="train-cancel-carousel round-trip-selector" data-instance-id="{{ instance_id }}">
  <main>
    <div class="hc-loading"><div class="hc-spinner"></div></div>
    <div class="hc-error-msg"></div>

    <div class="tc-header">
      <div class="tc-title">{{ title }}</div>
      <div class="tc-subtitle"{% if is_otp_send %} style="display:none"{% endif %}>{{ subtitle }}</div>
    </div>

    <!-- STEP 0: Login OTP verification -->
    {% if is_otp_send %}
    <div class="hc-step active" data-step="verify-otp">
      <div class="hc-verify-card">
        <div class="hc-verify-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>
          </svg>
        </div>
        <div class="hc-verify-title">Verify Your Identity</div>
        <p class="hc-verify-desc">We've sent a One-Time Password to your registered email &amp; phone number. Enter it below to continue.</p>
        <div class="hc-otp-field">
          <input type="text" class="hc-login-otp-input" maxlength="10" placeholder="Enter OTP" autocomplete="one-time-code" />
        </div>
        <div class="hc-error-msg hc-step-error"></div>
        <button type="button" class="hc-submit-btn hc-verify-otp-btn">Verify &amp; Continue</button>
        <p class="hc-verify-footer">Didn't receive the OTP? <button type="button" class="hc-resend-otp-btn hc-resend-login-otp">Resend OTP</button></p>
      </div>
    </div>
    {% endif %}

    <!-- STEP 1: Passenger selection -->
    <div class="hc-step {{ 'active' if not is_otp_send and not all_cancelled else '' }}" data-step="details">
      {% if train_info %}
      <div class="tc-train-info">
        <div class="tc-train-name">🚆 {{ train_info.train_name }} ({{ train_info.train_number }})</div>
        <div class="tc-route">
          <span>{{ train_info.from_station_name }}</span>
          <span class="tc-route-arrow">→</span>
          <span>{{ train_info.to_station_name }}</span>
        </div>
        <div class="tc-details-row">
          {% if train_info.departure_date %}
          <div class="tc-detail-item">
            <div class="tc-detail-label">Departure</div>
            <div class="tc-detail-value">{{ train_info.departure_date }} {{ train_info.departure_time }}</div>
          </div>
          {% endif %}
          {% if train_info.arrival_date %}
          <div class="tc-detail-item">
            <div class="tc-detail-label">Arrival</div>
            <div class="tc-detail-value">{{ train_info.arrival_date }} {{ train_info.arrival_time }}</div>
          </div>
          {% endif %}
          {% if train_info.duration %}
          <div class="tc-detail-item">
            <div class="tc-detail-label">Duration</div>
            <div class="tc-detail-value">{{ train_info.duration }}</div>
          </div>
          {% endif %}
          {% if train_info.travel_class %}
          <div class="tc-detail-item">
            <div class="tc-detail-label">Class</div>
            <div class="tc-detail-value">{{ train_info.travel_class }}</div>
          </div>
          {% endif %}
          {% if pnr_number %}
          <div class="tc-detail-item">
            <div class="tc-detail-label">PNR</div>
            <div class="tc-detail-value">{{ pnr_number }}</div>
          </div>
          {% endif %}
        </div>
      </div>
      {% endif %}
      <div class="tc-pax-section">
        <div class="tc-pax-title">Select passengers to cancel</div>
        <label class="tc-select-all">
          <input type="checkbox" class="tc-select-all-cb" /> Select All Passengers
        </label>
        <table class="tc-pax-table">
          <thead>
            <tr>
              <th></th>
              <th>Passenger</th>
              <th>Type</th>
              <th>Seat</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {% for pax in passengers %}
            <tr{% if pax.is_cancelled %} style="opacity: 0.5;"{% endif %}>
              <td><input type="checkbox" class="tc-pax-cb" data-pax-id="{{ pax.pax_id }}"{% if pax.is_cancelled %} disabled{% endif %} /></td>
              <td>{{ pax.title }} {{ pax.name }}</td>
              <td>{{ pax.pax_type }}</td>
              <td>
                {% if pax.coach_number and pax.seat_no and pax.seat_no != "0" %}
                  {{ pax.coach_number }}/{{ pax.seat_no }}{% if pax.seat_type %} ({{ pax.seat_type }}){% endif %}
                {% else %}
                  -
                {% endif %}
              </td>
              <td>
                {% if pax.is_cancelled %}
                <span class="tc-status-badge" style="background:#ffebee;color:#c62828;">Cancelled</span>
                {% else %}
                <span class="tc-status-badge {{ 'tc-status-cnf' if pax.booking_status == 'CNF' else 'tc-status-other' }}">
                  {{ pax.booking_status }}
                </span>
                {% endif %}
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>

      {% if price_info %}
      <div class="tc-price-info">
        {% if price_info.total_fare %}
        <div class="tc-price-row">
          <span class="tc-price-label">Total Fare</span>
          <span class="tc-price-value tc-price-total">₹{{ price_info.total_fare }}</span>
        </div>
        {% endif %}
        {% if price_info.base_fare %}
        <div class="tc-price-row">
          <span class="tc-price-label">Base Fare</span>
          <span class="tc-price-value">₹{{ price_info.base_fare }}</span>
        </div>
        {% endif %}
        {% if price_info.is_free_cancellation %}
        <div class="tc-price-row">
          <span class="tc-price-label">Free Cancellation</span>
          <span class="tc-price-value" style="color: #2e7d32;">✓ Yes (₹{{ price_info.free_cancellation_amount }})</span>
        </div>
        {% endif %}
      </div>
      {% endif %}

      <button type="button" class="hc-cancel-btn tc-proceed-btn" disabled>Cancel Selected Passengers</button>
    </div>

    <!-- STEP 2: Send OTP -->
    <div class="hc-step" data-step="otp">
      <div class="hc-selected-room-badge">
        Cancelling: <strong class="tc-selected-pax-label"></strong>
      </div>
      <div class="hc-verify-card">
        <div class="hc-verify-icon hc-verify-icon--cancel">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/>
          </svg>
        </div>
        <div class="hc-verify-title">Confirm Cancellation</div>
        <p class="hc-verify-desc">A cancellation OTP has been sent to your registered email &amp; phone. Enter it below to confirm.</p>
        <div class="hc-otp-field">
          <input type="text" class="hc-otp-input" maxlength="10" placeholder="Enter OTP" autocomplete="one-time-code" />
        </div>
        <div class="hc-error-msg hc-step-error"></div>
        <div class="hc-btn-row" style="justify-content: center;">
          <button type="button" class="hc-back-btn" data-back-to="details">Back</button>
          <button type="button" class="hc-submit-btn tc-confirm-btn">Confirm Cancellation</button>
        </div>
        <p class="hc-verify-footer">
          This action cannot be undone. Refund will be processed as per IRCTC cancellation policy.<br>
          Didn't receive the OTP? <button type="button" class="hc-resend-otp-btn hc-resend-cancel-otp">Resend OTP</button>
        </p>
      </div>
    </div>

    <!-- STEP 3: Result -->
    <div class="hc-step" data-step="result">
      <div class="hc-result-content"></div>
    </div>

    <!-- STEP: Already Cancelled -->
    <div class="hc-step {{ 'active' if not is_otp_send and all_cancelled else '' }}" data-step="cancelled">
      <div style="text-align:center;padding:30px 20px;">
        <div style="width:56px;height:56px;margin:0 auto 14px;background:#ffebee;border-radius:50%;display:flex;align-items:center;justify-content:center;">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="#c62828" style="width:28px;height:28px;">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </div>
        <h3 style="font-size:17px;font-weight:700;color:#1a1a2e;margin:0 0 8px;">Booking Already Cancelled</h3>
        <p style="font-size:13px;color:#646d74;margin:0 0 14px;">All passengers in this booking have already been cancelled.</p>
        <div style="background:#f8f9fa;border-radius:8px;padding:10px 14px;display:inline-block;">
          <span style="font-size:12px;color:#646d74;">No further action is needed. If you have questions about your refund, please contact support.</span>
        </div>
      </div>
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
  var VERIFY_OTP_URL = API_BASE + '/api/hotel-cancel/verify-otp';
  var OTP_URL = API_BASE + '/api/hotel-cancel/send-otp';
  var CANCEL_URL = API_BASE + '/api/hotel-cancel/confirm';
  var RESEND_LOGIN_OTP_URL = API_BASE + '/api/hotel-cancel/resend-login-otp';
  var BID = '{{ bid }}';
  var BOOKING_ID = '{{ booking_id }}';
  var EMAIL = '{{ email }}';
  var PASSENGERS = {{ passengers_json | tojson }};
  var RESERVATION_ID = '{{ reservation_id }}';
  var PNR_NUMBER = '{{ pnr_number }}';
  var EMT_SCREEN_ID = '{{ emt_screen_id }}';
  var ALL_CANCELLED = {{ 'true' if all_cancelled else 'false' }};

  var selectedPaxIds = [];

  var loadingOverlay = container.querySelector('.hc-loading');
  var globalErrorBanner = container.querySelector('main > .hc-error-msg');

  function hideAllErrors() {
    var errs = container.querySelectorAll('.hc-error-msg');
    for (var i = 0; i < errs.length; i++) errs[i].style.display = 'none';
  }

  function showStep(stepName) {
    var steps = container.querySelectorAll('.hc-step');
    for (var i = 0; i < steps.length; i++) steps[i].classList.remove('active');
    var target = container.querySelector('[data-step="' + stepName + '"]');
    if (target) target.classList.add('active');
    hideAllErrors();
  }

  function showLoading(show) { loadingOverlay.style.display = show ? 'flex' : 'none'; }
  function showError(msg) {
    hideAllErrors();
    var activeStep = container.querySelector('.hc-step.active');
    var inlineErr = activeStep ? activeStep.querySelector('.hc-step-error') : null;
    var target = inlineErr || globalErrorBanner;
    target.textContent = msg;
    target.style.display = 'block';
  }

  function updateSelectedLabel() {
    var labels = container.querySelectorAll('.tc-selected-pax-label');
    var text = selectedPaxIds.length + ' passenger(s)';
    for (var i = 0; i < labels.length; i++) labels[i].textContent = text;
  }

  function updateProceedBtn() {
    var btn = container.querySelector('.tc-proceed-btn');
    var cbs = container.querySelectorAll('.tc-pax-cb:not(:disabled):checked');
    selectedPaxIds = [];
    for (var i = 0; i < cbs.length; i++) selectedPaxIds.push(cbs[i].getAttribute('data-pax-id'));
    btn.disabled = selectedPaxIds.length === 0;
  }

  /* Checkbox handlers */
  var selectAllCb = container.querySelector('.tc-select-all-cb');
  var paxCbs = container.querySelectorAll('.tc-pax-cb');
  var activePaxCbs = container.querySelectorAll('.tc-pax-cb:not(:disabled)');

  if (selectAllCb) {
    selectAllCb.addEventListener('change', function() {
      for (var i = 0; i < activePaxCbs.length; i++) activePaxCbs[i].checked = this.checked;
      updateProceedBtn();
    });
  }
  for (var i = 0; i < activePaxCbs.length; i++) {
    activePaxCbs[i].addEventListener('change', function() {
      updateProceedBtn();
      if (selectAllCb) {
        var allChecked = container.querySelectorAll('.tc-pax-cb:not(:disabled):checked').length === activePaxCbs.length;
        selectAllCb.checked = allChecked;
      }
    });
  }

  /* API helpers */
  function verifyLoginOtp(otp) {
    showLoading(true);
    hideAllErrors();
    return fetch(VERIFY_OTP_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ booking_id: BOOKING_ID, email: EMAIL, otp: otp })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      var isVerified = false;
      var msg = '';
      if (data.structured_content) {
        isVerified = !!data.structured_content.success;
        msg = data.structured_content.message || data.response_text || '';
      } else if (data.isVerify !== undefined) {
        isVerified = String(data.isVerify).toLowerCase() === 'true';
        msg = data.Message || data.Msg || '';
      } else if (data.success !== undefined) {
        isVerified = !!data.success;
        msg = data.message || data.Message || '';
      } else if (data.isStatus !== undefined) {
        isVerified = !!data.isStatus;
        msg = data.Msg || data.Message || '';
      }
      if (!isVerified) {
        showError(msg || 'Invalid OTP. Please check and try again.');
        return null;
      }
      return data;
    })
    .catch(function(err) {
      showLoading(false);
      var msg = (err && err.message && err.message.indexOf('Failed to fetch') !== -1)
        ? 'Something Went Wrong Please Try Again.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  function sendOtp() {
    showLoading(true);
    hideAllErrors();
    return fetch(OTP_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ booking_id: BOOKING_ID, email: EMAIL })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      if (!data.isStatus) { showError(data.Msg || data.Message || 'Failed to send OTP. Please try again.'); return null; }
      return data;
    })
    .catch(function(err) {
      showLoading(false);
      var msg = (err && err.message && err.message.indexOf('Failed to fetch') !== -1)
        ? 'Something Went Wrong Please Try Again.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  function confirmCancellation(otp) {
    showLoading(true);
    hideAllErrors();
    var paxIdPayload = selectedPaxIds.map(function(id) { return 'canidout(' + id + ')'; });
    var allCbs = container.querySelectorAll('.tc-pax-cb');
    var allPaxIds = [];
    for (var i = 0; i < allCbs.length; i++) allPaxIds.push('canidout(' + allCbs[i].getAttribute('data-pax-id') + ')');
    return fetch(CANCEL_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        booking_id: BOOKING_ID,
        email: EMAIL,
        otp: otp,
        pax_ids: paxIdPayload,
        all_pax_ids: allPaxIds,
        reservation_id: RESERVATION_ID,
        pnr_number: PNR_NUMBER,
        total_passenger: selectedPaxIds.length,
        transaction_type: 'Train'
      })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      if (typeof data === 'string') {
        var success = data.toLowerCase().indexOf('success') !== -1;
        if (!success) {
          var isOtpError = data.toLowerCase().indexOf('otp') !== -1;
          var fallback = isOtpError ? 'Invalid OTP. Please check and try again.' : 'Cancellation failed. Please try again.';
          showError(data || fallback);
          return null;
        }
        return { Status: true, message: data };
      }
      if (!data.Status && !data.isStatus) {
        var msg = data.LogMessage || data.Message || data.Msg || '';
        var isOtpError = msg.toLowerCase().indexOf('otp') !== -1;
        var fallback = isOtpError ? 'Invalid OTP. Please check and try again.' : 'Cancellation failed. Please try again.';
        showError(msg || fallback);
        return null;
      }
      return data;
    })
    .catch(function(err) {
      showLoading(false);
      var msg = (err && err.message && err.message.indexOf('Failed to fetch') !== -1)
        ? 'Something Went Wrong Please Try Again.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  /* Step 0: Verify login OTP */
  var verifyOtpBtn = container.querySelector('.hc-verify-otp-btn');
  if (verifyOtpBtn) {
    verifyOtpBtn.addEventListener('click', function() {
      var otpInput = container.querySelector('.hc-login-otp-input');
      var otp = otpInput ? otpInput.value.trim() : '';
      if (!otp || otp.length < 4) { showError('Please enter a valid OTP.'); return; }
      verifyLoginOtp(otp).then(function(result) {
        if (result) {
          var sub = container.querySelector('.tc-subtitle');
          if (sub) sub.style.display = '';
          if (ALL_CANCELLED) { showStep('cancelled'); }
          else { showStep('details'); }
        }
      });
    });
  }

  /* Resend login OTP */
  var resendLoginOtpBtn = container.querySelector('.hc-resend-login-otp');
  if (resendLoginOtpBtn) {
    resendLoginOtpBtn.addEventListener('click', function() {
      var btn = this;
      btn.disabled = true;
      btn.textContent = 'Sending...';
      fetch(RESEND_LOGIN_OTP_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ booking_id: BOOKING_ID, email: EMAIL })
      })
      .then(function(resp) { return resp.json(); })
      .then(function() {
        btn.textContent = 'OTP Sent!';
        setTimeout(function() { btn.textContent = 'Resend OTP'; btn.disabled = false; }, 3000);
      })
      .catch(function() {
        showError('Failed to resend OTP. Please try again.');
        btn.textContent = 'Resend OTP';
        btn.disabled = false;
      });
    });
  }

  /* Step 1: Proceed with selected passengers */
  var proceedBtn = container.querySelector('.tc-proceed-btn');
  if (proceedBtn) {
    proceedBtn.addEventListener('click', function() {
      if (selectedPaxIds.length === 0) return;
      updateSelectedLabel();
      sendOtp().then(function(result) { if (result) showStep('otp'); });
    });
  }

  /* Step 2: Confirm cancellation */
  var confirmBtn = container.querySelector('.tc-confirm-btn');
  if (confirmBtn) {
    confirmBtn.addEventListener('click', function() {
      var otpInput = container.querySelector('.hc-otp-input');
      var otp = otpInput ? otpInput.value.trim() : '';
      if (!otp || otp.length < 4) { showError('Please enter a valid OTP.'); return; }
      confirmCancellation(otp).then(function(result) {
        if (result) { renderResult(result); showStep('result'); }
      });
    });
  }

  /* Resend cancellation OTP */
  var resendCancelOtpBtn = container.querySelector('.hc-resend-cancel-otp');
  if (resendCancelOtpBtn) {
    resendCancelOtpBtn.addEventListener('click', function() {
      var btn = this;
      btn.disabled = true;
      btn.textContent = 'Sending...';
      sendOtp().then(function(result) {
        if (result) {
          btn.textContent = 'OTP Sent!';
        } else {
          btn.textContent = 'Resend OTP';
        }
        btn.disabled = false;
        setTimeout(function() { btn.textContent = 'Resend OTP'; }, 3000);
      });
    });
  }

  /* Step 3: Render result */
  function renderResult(data) {
    var resultContainer = container.querySelector('.hc-result-content');
    var html = '<div class="hc-success-box">';
    html += '<div class="hc-success-icon"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg></div>';
    html += '<div class="hc-success-title">Cancellation Confirmed!</div>';

    var refundAmount = data.RefundAmount;
    var cancellationCharges = data.CancellationCharges;
    var refundMode = data.RefundMode;
    var detail = data.Data || {};
    if (detail.charge) cancellationCharges = detail.charge;
    if (detail.currency) refundMode = detail.currency;
    if (detail.Text) html += '<p style="font-size:13px;color:#646d74;margin-bottom:12px;">' + detail.Text + '</p>';

    if (refundAmount || cancellationCharges || refundMode) {
      html += '<div class="hc-refund-box"><div class="hc-refund-title">Refund Information</div>';
      if (refundAmount) html += '<div class="hc-refund-amount">₹' + refundAmount + '</div>';
      if (cancellationCharges) html += '<div class="hc-refund-row"><span class="hc-refund-label">Cancellation Charges</span><span class="hc-refund-value">₹' + cancellationCharges + '</span></div>';
      if (refundMode) html += '<div class="hc-refund-row"><span class="hc-refund-label">Refund Mode</span><span class="hc-refund-value">' + refundMode + '</span></div>';
      html += '</div>';
    }

    html += '</div>';
    html += '<div class="hc-footer-note">You will receive a confirmation email shortly. Refund will be processed as per IRCTC cancellation policy.</div>';
    resultContainer.innerHTML = html;
  }

  /* Back navigation */
  var backBtns = container.querySelectorAll('.hc-back-btn');
  for (var i = 0; i < backBtns.length; i++) {
    backBtns[i].addEventListener('click', function() { showStep(this.getAttribute('data-back-to')); });
  }

})();
</script>
"""


def render_train_booking_details(
    booking_details: Dict[str, Any],
    booking_id: str = "",
    email: str = "",
    bid: str = "",
    api_base_url: str = "",
    is_otp_send: bool = False,
) -> str:
    """
    Render train booking details as interactive HTML with cancellation flow.

    Args:
        booking_details: Train booking details from API
        booking_id: Booking ID
        email: User email
        bid: Encrypted booking ID from guest login
        api_base_url: Base URL of the chatbot API
        is_otp_send: Whether a login OTP was auto-sent

    Returns:
        HTML string with rendered interactive train booking details
    """
    train_info = booking_details.get("train_info", {})
    passengers = booking_details.get("passengers", [])
    price_info = booking_details.get("price_info", {})
    pnr_number = booking_details.get("pnr_number", "")
    reservation_id = booking_details.get("reservation_id", "")
    emt_screen_id = booking_details.get("emt_screen_id", "")

    if not passengers:
        return """
        <div class="train-cancel-carousel">
          <main style="max-width: 700px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; color: #646d74; padding: 40px 20px;">
              <p style="font-size: 14px;">No passengers found in this booking.</p>
            </div>
          </main>
        </div>
        """

    # Build title and subtitle
    title = f"Train Booking - {booking_id}" if booking_id else "Train Booking Details"
    subtitle_parts = []
    if train_info.get("train_name"):
        subtitle_parts.append(f"{train_info['train_name']} ({train_info.get('train_number', '')})")
    if train_info.get("from_station_name") and train_info.get("to_station_name"):
        subtitle_parts.append(f"{train_info['from_station_name']} → {train_info['to_station_name']}")
    subtitle_parts.append(f"{len(passengers)} passenger(s)")
    if pnr_number:
        subtitle_parts.append(f"PNR: {pnr_number}")
    subtitle = " • ".join(subtitle_parts)

    import uuid
    instance_id = str(uuid.uuid4())[:8]

    # Prepare passenger data for JS
    passengers_json = [
        {
            "pax_id": p.get("pax_id"),
            "name": f"{p.get('title', '')} {p.get('name', '')}".strip(),
            "pax_type": p.get("pax_type"),
            "seat_no": p.get("seat_no"),
            "coach_number": p.get("coach_number"),
            "booking_status": p.get("booking_status"),
            "current_status": p.get("current_status", ""),
            "is_cancelled": p.get("is_cancelled", False),
        }
        for p in passengers
    ]

    all_cancelled = booking_details.get("all_cancelled", False)

    template = _jinja_env.from_string(TRAIN_BOOKING_TEMPLATE)
    return template.render(
        title=title,
        subtitle=subtitle,
        train_info=train_info,
        passengers=passengers,
        price_info=price_info,
        pnr_number=pnr_number,
        reservation_id=reservation_id,
        emt_screen_id=emt_screen_id,
        instance_id=instance_id,
        bid=bid,
        booking_id=booking_id,
        email=email,
        passengers_json=passengers_json,
        api_base_url=api_base_url,
        is_otp_send=is_otp_send,
        all_cancelled=all_cancelled,
    )


# =====================================================================
# 🚌 BUS INTERACTIVE BOOKING TEMPLATE (WITH JS FOR CANCEL FLOW)
# =====================================================================
BUS_BOOKING_TEMPLATE = """
<style>

.bus-cancel-carousel {
  font-family: poppins, sans-serif;
  color: #202020;
  background: rgba(255, 255, 255, 0.92);
  position: relative;
}

.bus-cancel-carousel * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
}

.bus-cancel-carousel main {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px 0 30px;
  position: relative;
}

.bus-cancel-carousel .hc-loading {
  display: none;
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.85);
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 12px;
}

.bus-cancel-carousel .hc-spinner {
  width: 36px; height: 36px;
  border: 3px solid #e0e0e0;
  border-top-color: #ef6614;
  border-radius: 50%;
  animation: bcSpin 0.8s linear infinite;
}
@keyframes bcSpin { to { transform: rotate(360deg); } }

.bus-cancel-carousel .hc-error-msg {
  display: none;
  color: #d32f2f;
  padding: 4px 14px;
  border-radius: 8px;
  font-size: 12px;
  margin-bottom: 4px;
  margin-top: -4px;
}

.bus-cancel-carousel .bc-header {
  margin-bottom: 16px;
}
.bus-cancel-carousel .bc-title {
  font-size: 18px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 4px;
}
.bus-cancel-carousel .bc-subtitle {
  font-size: 12px;
  color: #646d74;
  margin-top: 4px;
}

.bus-cancel-carousel .bc-bus-info {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 16px;
  border: 1px solid #e0e0e0;
}
.bus-cancel-carousel .bc-route {
  font-size: 16px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.bus-cancel-carousel .bc-route-arrow {
  color: #ef6614;
  font-weight: 600;
}
.bus-cancel-carousel .bc-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 16px;
  margin-top: 8px;
}
.bus-cancel-carousel .bc-info-item {
  font-size: 12px;
  color: #646d74;
}
.bus-cancel-carousel .bc-info-item strong {
  color: #202020;
  font-weight: 600;
}

.bus-cancel-carousel .bc-pax-section {
  margin-bottom: 16px;
}
.bus-cancel-carousel .bc-pax-title {
  font-size: 14px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 12px;
}
.bus-cancel-carousel .bc-select-all {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 13px;
  color: #646d74;
  cursor: pointer;
}
.bus-cancel-carousel .bc-select-all input[type="checkbox"] {
  accent-color: #ef6614;
  width: 16px; height: 16px;
}
.bus-cancel-carousel .bc-pax-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.bus-cancel-carousel .bc-pax-table th {
  background: #f8f9fa;
  padding: 8px 10px;
  text-align: left;
  font-weight: 600;
  color: #646d74;
  font-size: 11px;
  text-transform: uppercase;
  border-bottom: 2px solid #e0e0e0;
}
.bus-cancel-carousel .bc-pax-table td {
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  color: #202020;
}
.bus-cancel-carousel .bc-pax-table tr:hover {
  background: #fef6f0;
}
.bus-cancel-carousel .bc-pax-table input[type="checkbox"] {
  accent-color: #ef6614;
  width: 16px; height: 16px;
}

.bus-cancel-carousel .bc-status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}
.bus-cancel-carousel .bc-status-confirm {
  background: #e8f5e9;
  color: #2e7d32;
}
.bus-cancel-carousel .bc-status-other {
  background: #fff3e0;
  color: #e65100;
}

.bus-cancel-carousel .bc-proceed-btn {
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
.bus-cancel-carousel .bc-proceed-btn:hover { opacity: 0.85; }
.bus-cancel-carousel .bc-proceed-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bus-cancel-carousel .hc-step { display: none; }
.bus-cancel-carousel .hc-step.active { display: block; }

.bus-cancel-carousel .hc-verify-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  padding: 5px 12px;
  text-align: center;
  max-width: 400px;
  margin: 0 auto;
}

.bus-cancel-carousel .hc-verify-icon {
  width: 50px; height: 50px;
  margin: 0 auto 4px;
  background: linear-gradient(135deg, #ef6614 0%, #f58434 100%);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  box-shadow: 0 4px 16px rgba(239, 102, 20, 0.25);
}

.bus-cancel-carousel .hc-verify-title {
  font-size: 18px; font-weight: 700; color: #202020; margin-bottom: 8px;
}

.bus-cancel-carousel .hc-verify-desc {
  font-size: 13px; color: #646d74; line-height: 1.5; margin-bottom: 9px;
}

.bus-cancel-carousel .hc-otp-field { margin-bottom: 16px; }

.bus-cancel-carousel .hc-login-otp-input {
  width: 100%; max-width: 240px;
  padding: 10px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 14px; font-weight: 600;
  text-align: center; letter-spacing: 4px;
  font-family: inter, sans-serif;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #fff; color: #202020;
}
.bus-cancel-carousel .hc-login-otp-input:focus {
  border-color: #ef6614;
  box-shadow: 0 0 0 3px rgba(239, 102, 20, 0.1);
}
.bus-cancel-carousel .hc-login-otp-input::placeholder {
  font-size: 14px; letter-spacing: 0; font-weight: 400; color: #bbb;
}

.bus-cancel-carousel .hc-otp-input {
  width: 100%; max-width: 240px;
  padding: 8px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 18px; font-weight: 500;
  text-align: center; letter-spacing: 4px;
  font-family: inter, sans-serif;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #fff; color: #202020;
}
.bus-cancel-carousel .hc-otp-input:focus {
  border-color: #ef6614;
  box-shadow: 0 0 0 3px rgba(239, 102, 20, 0.1);
}
.bus-cancel-carousel .hc-otp-input::placeholder {
  font-size: 14px; letter-spacing: 0; font-weight: 400; color: #bbb;
}

.bus-cancel-carousel .hc-submit-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, #ef6614 0%, #f58434 100%);
  color: #fff; border: none; border-radius: 8px;
  font-size: 14px; font-weight: 600; cursor: pointer;
  font-family: poppins, sans-serif;
  transition: opacity 0.2s;
}
.bus-cancel-carousel .hc-submit-btn:hover { opacity: 0.85; }

.bus-cancel-carousel .hc-verify-card .hc-submit-btn {
  width: 80%; max-width: 240px; padding: 8px 7px;
}

.bus-cancel-carousel .hc-verify-footer {
  font-size: 11px; color: #999; margin-top: 16px; line-height: 1.4;
}

.bus-cancel-carousel .hc-back-btn {
  background: none;
  border: 1px solid #e0e0e0;
  padding: 8px 16px; border-radius: 8px;
  font-size: 12px; cursor: pointer;
  color: #646d74; font-family: poppins, sans-serif;
  transition: border-color 0.2s;
}
.bus-cancel-carousel .hc-back-btn:hover { border-color: #ef6614; color: #ef6614; }

.bus-cancel-carousel .hc-btn-row {
  display: flex; gap: 8px; margin-top: 16px;
}

.bus-cancel-carousel .hc-verify-icon--cancel {
  background: linear-gradient(135deg, #d32f2f 0%, #ef5350 100%);
  box-shadow: 0 4px 16px rgba(211, 47, 47, 0.25);
}

.bus-cancel-carousel .hc-selected-room-badge {
  background: #f5f5f5;
  padding: 10px 14px; border-radius: 8px;
  font-size: 13px; margin-bottom: 16px;
  border-left: 3px solid #ef6614;
}

.bus-cancel-carousel .hc-resend-otp-btn {
  background: none; border: none; color: #2196f3; font-size: 12px; font-weight: 600;
  cursor: pointer; padding: 0; margin-top: 8px; text-decoration: none; display: inline-block;
}
.bus-cancel-carousel .hc-resend-otp-btn:hover { text-decoration: underline; color: #1565c0; }
.bus-cancel-carousel .hc-resend-otp-btn:disabled { color: #999; cursor: not-allowed; text-decoration: none; }

/* Success result */
.bus-cancel-carousel .hc-success-box {
  background: linear-gradient(135deg, #e8f5e9 0%, #f1f8f4 100%);
  border: 2px solid #4caf50; border-radius: 16px;
  padding: 32px 24px; text-align: center;
}
.bus-cancel-carousel .hc-success-icon {
  width: 64px; height: 64px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 20px rgba(76, 175, 80, 0.3);
  animation: bcSuccessPop 0.6s ease-out;
}
@keyframes bcSuccessPop {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}
.bus-cancel-carousel .hc-success-icon svg { width: 36px; height: 36px; color: #fff; }
.bus-cancel-carousel .hc-success-title {
  font-size: 20px; font-weight: 700; color: #2e7d32; margin-bottom: 16px;
}
.bus-cancel-carousel .hc-refund-box {
  background: linear-gradient(135deg, #fff8e1 0%, #fffbea 100%);
  border: 2px solid #ffc107; border-radius: 12px;
  padding: 16px; margin-top: 16px; text-align: left;
}
.bus-cancel-carousel .hc-refund-title { font-size: 14px; font-weight: 700; color: #f57f17; margin-bottom: 12px; }
.bus-cancel-carousel .hc-refund-amount { font-size: 28px; font-weight: 700; color: #2e7d32; margin-bottom: 8px; }
.bus-cancel-carousel .hc-refund-row { display: flex; justify-content: space-between; font-size: 13px; color: #646d74; padding: 4px 0; }
.bus-cancel-carousel .hc-footer-note { font-size: 12px; color: #999; margin-top: 16px; }

/* Cancellation policy table */
.bus-cancel-carousel .bc-policy-section {
  margin-top: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
}
.bus-cancel-carousel .bc-policy-header {
  font-size: 13px;
  font-weight: 600;
  color: #202020;
  padding: 10px 14px;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}
.bus-cancel-carousel .bc-policy-body {
  max-height: 200px;
  overflow-y: auto;
}
.bus-cancel-carousel .bc-policy-body::-webkit-scrollbar {
  width: 4px;
}
.bus-cancel-carousel .bc-policy-body::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}
.bus-cancel-carousel .bc-policy-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.bus-cancel-carousel .bc-policy-table th {
  background: #f8f9fa;
  padding: 8px 12px;
  text-align: left;
  font-weight: 600;
  color: #646d74;
  font-size: 11px;
  text-transform: uppercase;
  border-bottom: 2px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 1;
}
.bus-cancel-carousel .bc-policy-table td {
  padding: 9px 12px;
  border-bottom: 1px solid #f0f0f0;
  color: #202020;
}
.bus-cancel-carousel .bc-policy-table tr:last-child td {
  border-bottom: none;
}
.bus-cancel-carousel .bc-policy-table tr:hover {
  background: #fef6f0;
}
.bus-cancel-carousel .bc-policy-charge {
  font-weight: 600;
  white-space: nowrap;
}
/* Style any raw HTML tables from API inside the policy */
.bus-cancel-carousel .bc-policy-raw {
  max-height: 200px;
  overflow-y: auto;
  padding: 0;
}
.bus-cancel-carousel .bc-policy-raw::-webkit-scrollbar {
  width: 4px;
}
.bus-cancel-carousel .bc-policy-raw::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}
.bus-cancel-carousel .bc-policy-raw table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.bus-cancel-carousel .bc-policy-raw table th,
.bus-cancel-carousel .bc-policy-raw table td {
  padding: 9px 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}
.bus-cancel-carousel .bc-policy-raw table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #646d74;
  font-size: 11px;
  text-transform: uppercase;
  border-bottom: 2px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 1;
}
.bus-cancel-carousel .bc-policy-raw table tr:hover {
  background: #fef6f0;
}
.bus-cancel-carousel .bc-policy-raw table tr:last-child td {
  border-bottom: none;
}
.bus-cancel-carousel .bc-policy-raw ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.bus-cancel-carousel .bc-policy-raw li {
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 12px;
  color: #202020;
}
.bus-cancel-carousel .bc-policy-raw li:last-child {
  border-bottom: none;
}

</style>

<div class="round-trip-selector bus-cancel-carousel" data-instance-id="{{ instance_id }}">
  <main>
    <div class="hc-loading"><div class="hc-spinner"></div></div>
    <div class="hc-error-msg"></div>

    <div class="bc-header">
      <div class="bc-title">{{ title }}</div>
      <div class="bc-subtitle"{% if is_otp_send %} style="display:none"{% endif %}>{{ subtitle }}</div>
    </div>

    <!-- STEP 0: Login OTP verification -->
    {% if is_otp_send %}
    <div class="hc-step active" data-step="verify-otp">
      <div class="hc-verify-card">
        <div class="hc-verify-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>
          </svg>
        </div>
        <div class="hc-verify-title">Verify Your Identity</div>
        <p class="hc-verify-desc">We've sent a One-Time Password to your registered email &amp; phone number. Enter it below to continue.</p>
        <div class="hc-otp-field">
          <input type="text" class="hc-login-otp-input" maxlength="10" placeholder="Enter OTP" autocomplete="one-time-code" />
        </div>
        <div class="hc-error-msg hc-step-error"></div>
        <button type="button" class="hc-submit-btn hc-verify-otp-btn">Verify &amp; Continue</button>
        <p class="hc-verify-footer">Didn't receive the OTP? <button type="button" class="hc-resend-otp-btn hc-resend-login-otp">Resend OTP</button></p>
      </div>
    </div>
    {% endif %}

    <!-- STEP 1: Passenger selection -->
    <div class="hc-step {{ 'active' if not is_otp_send and not all_cancelled else '' }}" data-step="details">
      {% if bus_info %}
      <div class="bc-bus-info">
        <div class="bc-route">
          {{ bus_info.source }}<span class="bc-route-arrow"> → </span>{{ bus_info.destination }}
        </div>
        <div class="bc-info-grid">
          {% if bus_info.travels_operator %}<div class="bc-info-item"><strong>Operator:</strong> {{ bus_info.travels_operator }}</div>{% endif %}
          {% if bus_info.bus_type %}<div class="bc-info-item"><strong>Type:</strong> {{ bus_info.bus_type }}</div>{% endif %}
          {% if bus_info.date_of_journey %}<div class="bc-info-item"><strong>Journey:</strong> {{ bus_info.date_of_journey }}</div>{% endif %}
          {% if bus_info.departure_time %}<div class="bc-info-item"><strong>Departure:</strong> {{ bus_info.departure_time }}</div>{% endif %}
          {% if bus_info.arrival_time %}<div class="bc-info-item"><strong>Arrival:</strong> {{ bus_info.arrival_time }}</div>{% endif %}
          {% if bus_info.bus_duration %}<div class="bc-info-item"><strong>Duration:</strong> {{ bus_info.bus_duration }}</div>{% endif %}
          {% if bus_info.bp_location %}<div class="bc-info-item"><strong>Boarding:</strong> {{ bus_info.bp_location }}</div>{% endif %}
          {% if bus_info.ticket_no %}<div class="bc-info-item"><strong>Ticket:</strong> {{ bus_info.ticket_no }}</div>{% endif %}
          {% if bus_info.total_fare %}<div class="bc-info-item"><strong>Total Fare:</strong> ₹{{ bus_info.total_fare }}</div>{% endif %}
        </div>
        {% if bus_info.cancellation_policy_html or bus_info.cancellation_policy %}
        <div class="bc-policy-section">
          {% if bus_info.cancellation_policy_html %}
          <div class="bc-policy-raw bc-policy-body">{{ bus_info.cancellation_policy_html | safe }}</div>
          {% else %}
          <div class="bc-policy-body">
            <table class="bc-policy-table">
              <thead><tr><th>Cancellation Time</th><th>Cancellation Charges</th></tr></thead>
              <tbody>
                {% for line in bus_info.cancellation_policy.split('\n') %}
                {% if line.strip() %}
                <tr>
                  <td>{{ line.strip().lstrip('• ') }}</td>
                  <td></td>
                </tr>
                {% endif %}
                {% endfor %}
              </tbody>
            </table>
          </div>
          {% endif %}
        </div>
        {% endif %}
      </div>
      {% endif %}
      <div class="bc-pax-section">
        <div class="bc-pax-title">Select passengers to cancel</div>
        <label class="bc-select-all">
          <input type="checkbox" class="bc-select-all-cb" /> Select All Passengers
        </label>
        <table class="bc-pax-table">
          <thead>
            <tr>
              <th></th>
              <th>Passenger</th>
              <th>Seat</th>
              <th>Fare</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {% for pax in passengers %}
            <tr{% if pax.is_cancelled %} style="opacity: 0.5;"{% endif %}>
              <td><input type="checkbox" class="bc-pax-cb" data-seat-no="{{ pax.seat_no }}"{% if pax.is_cancelled %} disabled{% endif %} /></td>
              <td>{{ pax.title }} {{ pax.first_name }} {{ pax.last_name }}</td>
              <td>{{ pax.seat_no }}</td>
              <td>₹{{ pax.fare }}</td>
              <td>
                {% if pax.is_cancelled %}
                <span class="bc-status-badge" style="background:#ffebee;color:#c62828;">Cancelled</span>
                {% else %}
                <span class="bc-status-badge {{ 'bc-status-confirm' if pax.status == 'Confirm' else 'bc-status-other' }}">
                  {{ pax.status }}
                </span>
                {% endif %}
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
      <div class="hc-selected-room-badge" style="display:none;">
        Cancelling: <strong class="bc-selected-label"></strong>
      </div>
      <button type="button" class="bc-proceed-btn" disabled>Proceed to Cancel</button>
    </div>

    <!-- STEP 2: OTP confirmation -->
    <div class="hc-step" data-step="otp">
      <div class="hc-verify-card">
        <div class="hc-verify-icon hc-verify-icon--cancel">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/>
          </svg>
        </div>
        <div class="hc-verify-title">Confirm Cancellation</div>
        <p class="hc-verify-desc">Enter the OTP sent to your registered email/phone to confirm the cancellation.</p>
        <div class="hc-otp-field">
          <input type="text" class="hc-otp-input" maxlength="10" placeholder="Enter OTP" autocomplete="one-time-code" />
        </div>
        <div class="hc-error-msg hc-step-error"></div>
        <div class="hc-btn-row" style="justify-content: center;">
          <button type="button" class="hc-back-btn" data-back-to="details">Back</button>
          <button type="button" class="hc-submit-btn bc-confirm-btn">Confirm Cancellation</button>
        </div>
        <p class="hc-verify-footer">
          This action cannot be undone. Refund will be processed as per cancellation policy.<br>
          Didn't receive the OTP? <button type="button" class="hc-resend-otp-btn hc-resend-cancel-otp">Resend OTP</button>
        </p>
      </div>
    </div>

    <!-- STEP 3: Result -->
    <div class="hc-step" data-step="result">
      <div class="hc-result-content"></div>
    </div>

    <!-- STEP: Already Cancelled -->
    <div class="hc-step {{ 'active' if not is_otp_send and all_cancelled else '' }}" data-step="cancelled">
      <div style="text-align:center;padding:30px 20px;">
        <div style="width:56px;height:56px;margin:0 auto 14px;background:#ffebee;border-radius:50%;display:flex;align-items:center;justify-content:center;">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="#c62828" style="width:28px;height:28px;">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </div>
        <h3 style="font-size:17px;font-weight:700;color:#1a1a2e;margin:0 0 8px;">Booking Already Cancelled</h3>
        <p style="font-size:13px;color:#646d74;margin:0 0 14px;">All passengers in this booking have already been cancelled.</p>
        <div style="background:#f8f9fa;border-radius:8px;padding:10px 14px;display:inline-block;">
          <span style="font-size:12px;color:#646d74;">No further action is needed. If you have questions about your refund, please contact support.</span>
        </div>
      </div>
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
  var VERIFY_OTP_URL = API_BASE + '/api/hotel-cancel/verify-otp';
  var OTP_URL = API_BASE + '/api/hotel-cancel/send-otp';
  var CANCEL_URL = API_BASE + '/api/hotel-cancel/confirm';
  var RESEND_LOGIN_OTP_URL = API_BASE + '/api/hotel-cancel/resend-login-otp';
  var BID = '{{ bid }}';
  var BOOKING_ID = '{{ booking_id }}';
  var EMAIL = '{{ email }}';
  var PASSENGERS = {{ passengers_json | tojson }};
  var ALL_CANCELLED = {{ 'true' if all_cancelled else 'false' }};

  var selectedSeats = [];

  var loadingOverlay = container.querySelector('.hc-loading');
  var globalErrorBanner = container.querySelector('main > .hc-error-msg');

  function hideAllErrors() {
    var errs = container.querySelectorAll('.hc-error-msg');
    for (var i = 0; i < errs.length; i++) errs[i].style.display = 'none';
  }

  function showStep(stepName) {
    var steps = container.querySelectorAll('.hc-step');
    for (var i = 0; i < steps.length; i++) steps[i].classList.remove('active');
    var target = container.querySelector('[data-step="' + stepName + '"]');
    if (target) target.classList.add('active');
    hideAllErrors();
  }

  function showLoading(show) { loadingOverlay.style.display = show ? 'flex' : 'none'; }
  function showError(msg) {
    hideAllErrors();
    var activeStep = container.querySelector('.hc-step.active');
    var inlineErr = activeStep ? activeStep.querySelector('.hc-step-error') : null;
    var target = inlineErr || globalErrorBanner;
    target.textContent = msg;
    target.style.display = 'block';
  }

  /* Back buttons */
  var backBtns = container.querySelectorAll('.hc-back-btn');
  for (var i = 0; i < backBtns.length; i++) {
    backBtns[i].addEventListener('click', function() { showStep(this.getAttribute('data-back-to')); });
  }

  function updateSelectedLabel() {
    var labels = container.querySelectorAll('.bc-selected-label');
    var badge = container.querySelector('.hc-selected-room-badge');
    var text = selectedSeats.length + ' seat(s): ' + selectedSeats.join(', ');
    for (var i = 0; i < labels.length; i++) labels[i].textContent = text;
    if (badge) badge.style.display = selectedSeats.length > 0 ? 'block' : 'none';
  }

  function updateProceedBtn() {
    var btn = container.querySelector('.bc-proceed-btn');
    var cbs = container.querySelectorAll('.bc-pax-cb:not(:disabled):checked');
    selectedSeats = [];
    for (var i = 0; i < cbs.length; i++) selectedSeats.push(cbs[i].getAttribute('data-seat-no'));
    btn.disabled = selectedSeats.length === 0;
  }

  /* Checkbox handlers */
  var selectAllCb = container.querySelector('.bc-select-all-cb');
  var activePaxCbs = container.querySelectorAll('.bc-pax-cb:not(:disabled)');

  if (selectAllCb) {
    selectAllCb.addEventListener('change', function() {
      for (var i = 0; i < activePaxCbs.length; i++) activePaxCbs[i].checked = this.checked;
      updateProceedBtn();
    });
  }
  for (var i = 0; i < activePaxCbs.length; i++) {
    activePaxCbs[i].addEventListener('change', function() {
      updateProceedBtn();
      if (selectAllCb) {
        var allChecked = container.querySelectorAll('.bc-pax-cb:not(:disabled):checked').length === activePaxCbs.length;
        selectAllCb.checked = allChecked;
      }
    });
  }

  /* API helpers */
  function verifyLoginOtp(otp) {
    showLoading(true);
    hideAllErrors();
    return fetch(VERIFY_OTP_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ booking_id: BOOKING_ID, email: EMAIL, otp: otp })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      var isVerified = false;
      var msg = '';
      if (data.structured_content) {
        isVerified = !!data.structured_content.success;
        msg = data.structured_content.message || data.response_text || '';
      } else if (data.isVerify !== undefined) {
        isVerified = String(data.isVerify).toLowerCase() === 'true';
        msg = data.Message || data.Msg || '';
      } else if (data.success !== undefined) {
        isVerified = !!data.success;
        msg = data.message || data.Message || '';
      } else if (data.isStatus !== undefined) {
        isVerified = !!data.isStatus;
        msg = data.Msg || data.Message || '';
      }
      if (!isVerified) {
        showError(msg || 'Invalid OTP. Please check and try again.');
        return null;
      }
      return data;
    })
    .catch(function(err) {
      showLoading(false);
      var msg = (err && err.message && err.message.indexOf('Failed to fetch') !== -1)
        ? 'Something Went Wrong Please Try Again.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  function sendOtp() {
    showLoading(true);
    hideAllErrors();
    return fetch(OTP_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ booking_id: BOOKING_ID, email: EMAIL })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      if (!data.isStatus) { showError(data.Msg || data.Message || 'Failed to send OTP. Please try again.'); return null; }
      return data;
    })
    .catch(function(err) {
      showLoading(false);
      var msg = (err && err.message && err.message.indexOf('Failed to fetch') !== -1)
        ? 'Something Went Wrong Please Try Again.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  function confirmCancellation(otp) {
    showLoading(true);
    hideAllErrors();
    return fetch(CANCEL_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        booking_id: BOOKING_ID,
        email: EMAIL,
        otp: otp,
        seats: selectedSeats.join(','),
        transaction_type: 'Bus'
      })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      if (typeof data === 'string') {
        var success = data.toLowerCase().indexOf('success') !== -1 || data.toLowerCase().indexOf('cancel') !== -1;
        if (!success) {
          var isOtpError = data.toLowerCase().indexOf('otp') !== -1;
          var fallback = isOtpError ? 'Invalid OTP. Please check and try again.' : 'Cancellation failed. Please try again.';
          showError(data || fallback);
          return null;
        }
        return { Status: true, message: data };
      }
      if (!data.Status && !data.isStatus) {
        var msg = data.LogMessage || data.Message || data.Msg || '';
        var isOtpError = msg.toLowerCase().indexOf('otp') !== -1;
        var fallback = isOtpError ? 'Invalid OTP. Please check and try again.' : 'Cancellation failed. Please try again.';
        showError(msg || fallback);
        return null;
      }
      return data;
    })
    .catch(function(err) {
      showLoading(false);
      var msg = (err && err.message && err.message.indexOf('Failed to fetch') !== -1)
        ? 'Something Went Wrong Please Try Again.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  /* Step 0: Verify login OTP */
  var verifyOtpBtn = container.querySelector('.hc-verify-otp-btn');
  if (verifyOtpBtn) {
    verifyOtpBtn.addEventListener('click', function() {
      var otpInput = container.querySelector('.hc-login-otp-input');
      var otp = otpInput ? otpInput.value.trim() : '';
      if (!otp || otp.length < 4) { showError('Please enter a valid OTP.'); return; }
      verifyLoginOtp(otp).then(function(result) {
        if (result) {
          var sub = container.querySelector('.bc-subtitle');
          if (sub) sub.style.display = '';
          if (ALL_CANCELLED) { showStep('cancelled'); }
          else { showStep('details'); }
        }
      });
    });
  }

  /* Resend login OTP */
  var resendLoginOtpBtn = container.querySelector('.hc-resend-login-otp');
  if (resendLoginOtpBtn) {
    resendLoginOtpBtn.addEventListener('click', function() {
      var btn = this;
      btn.disabled = true;
      btn.textContent = 'Sending...';
      fetch(RESEND_LOGIN_OTP_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ booking_id: BOOKING_ID, email: EMAIL })
      })
      .then(function(resp) { return resp.json(); })
      .then(function() {
        btn.textContent = 'OTP Sent!';
        setTimeout(function() { btn.textContent = 'Resend OTP'; btn.disabled = false; }, 3000);
      })
      .catch(function() {
        showError('Failed to resend OTP. Please try again.');
        btn.textContent = 'Resend OTP';
        btn.disabled = false;
      });
    });
  }

  /* Step 1: Proceed with selected passengers */
  var proceedBtn = container.querySelector('.bc-proceed-btn');
  if (proceedBtn) {
    proceedBtn.addEventListener('click', function() {
      if (selectedSeats.length === 0) return;
      updateSelectedLabel();
      sendOtp().then(function(result) { if (result) showStep('otp'); });
    });
  }

  /* Step 2: Confirm cancellation */
  var confirmBtn = container.querySelector('.bc-confirm-btn');
  if (confirmBtn) {
    confirmBtn.addEventListener('click', function() {
      var otpInput = container.querySelector('.hc-otp-input');
      var otp = otpInput ? otpInput.value.trim() : '';
      if (!otp || otp.length < 4) { showError('Please enter a valid OTP.'); return; }
      confirmCancellation(otp).then(function(result) {
        if (result) { renderResult(result); showStep('result'); }
      });
    });
  }

  /* Resend cancellation OTP */
  var resendCancelOtpBtn = container.querySelector('.hc-resend-cancel-otp');
  if (resendCancelOtpBtn) {
    resendCancelOtpBtn.addEventListener('click', function() {
      var btn = this;
      btn.disabled = true;
      btn.textContent = 'Sending...';
      sendOtp().then(function(result) {
        if (result) { btn.textContent = 'OTP Sent!'; }
        else { btn.textContent = 'Resend OTP'; }
        btn.disabled = false;
        setTimeout(function() { btn.textContent = 'Resend OTP'; }, 3000);
      });
    });
  }

  /* Step 3: Render result */
  function renderResult(data) {
    var resultContainer = container.querySelector('.hc-result-content');
    var html = '<div class="hc-success-box">';
    html += '<div class="hc-success-icon"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg></div>';
    html += '<div class="hc-success-title">Cancellation Confirmed!</div>';

    var refundData = data.Data || {};
    var refundAmount = refundData.refundAmount;
    var cancellationCharges = refundData.cancellationCharges;
    var remarks = refundData.Remarks;
    var pnrNo = refundData.PNRNo;

    if (refundAmount !== undefined || cancellationCharges !== undefined) {
      html += '<div class="hc-refund-box"><div class="hc-refund-title">Refund Information</div>';
      if (refundAmount !== undefined) html += '<div class="hc-refund-amount">₹' + refundAmount + '</div>';
      if (cancellationCharges !== undefined) html += '<div class="hc-refund-row"><span>Cancellation Charges</span><span>₹' + cancellationCharges + '</span></div>';
      if (pnrNo) html += '<div class="hc-refund-row"><span>Ticket No</span><span>' + pnrNo + '</span></div>';
      if (remarks) html += '<div class="hc-refund-row"><span>Status</span><span>' + remarks + '</span></div>';
      html += '</div>';
    }

    html += '<div class="hc-footer-note">You will receive a confirmation email shortly. Refund will be processed as per cancellation policy.</div>';
    html += '</div>';
    resultContainer.innerHTML = html;
  }

})();
</script>
"""


def render_bus_booking_details(
    booking_details: Dict[str, Any],
    booking_id: str = "",
    email: str = "",
    bid: str = "",
    api_base_url: str = "",
    is_otp_send: bool = False,
) -> str:
    """
    Render bus booking details as interactive HTML with cancellation flow.

    Args:
        booking_details: Bus booking details from API
        booking_id: Booking ID
        email: User email
        bid: Encrypted booking ID from guest login
        api_base_url: Base URL of the chatbot API
        is_otp_send: Whether a login OTP was auto-sent

    Returns:
        HTML string with rendered interactive bus booking details
    """
    bus_info = booking_details.get("bus_info", {})
    passengers = booking_details.get("passengers", [])
    price_info = booking_details.get("price_info", {})
    ticket_no = booking_details.get("ticket_no", "")

    if not passengers:
        return """
        <div class="bus-cancel-carousel">
          <main style="max-width: 700px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; color: #646d74; padding: 40px 20px;">
              <p style="font-size: 14px;">No passengers found in this booking.</p>
            </div>
          </main>
        </div>
        """

    # Build title and subtitle
    title = f"Bus Booking - {booking_id}" if booking_id else "Bus Booking Details"
    subtitle_parts = []
    if bus_info.get("travels_operator"):
        subtitle_parts.append(bus_info["travels_operator"])
    if bus_info.get("source") and bus_info.get("destination"):
        subtitle_parts.append(f"{bus_info['source']} → {bus_info['destination']}")
    subtitle_parts.append(f"{len(passengers)} passenger(s)")
    if ticket_no:
        subtitle_parts.append(f"Ticket: {ticket_no}")
    subtitle = " • ".join(subtitle_parts)

    import uuid
    instance_id = str(uuid.uuid4())[:8]

    # Prepare passenger data for JS
    passengers_json = [
        {
            "seat_no": p.get("seat_no"),
            "name": f"{p.get('title', '')} {p.get('first_name', '')} {p.get('last_name', '')}".strip(),
            "fare": p.get("fare"),
            "status": p.get("status", ""),
            "is_cancelled": p.get("is_cancelled", False),
        }
        for p in passengers
    ]

    all_cancelled = booking_details.get("all_cancelled", False)

    template = _jinja_env.from_string(BUS_BOOKING_TEMPLATE)
    return template.render(
        title=title,
        subtitle=subtitle,
        bus_info=bus_info,
        passengers=passengers,
        price_info=price_info,
        instance_id=instance_id,
        bid=bid,
        booking_id=booking_id,
        email=email,
        passengers_json=passengers_json,
        api_base_url=api_base_url,
        is_otp_send=is_otp_send,
        all_cancelled=all_cancelled,
    )


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


ALREADY_CANCELLED_TEMPLATE = """
<div class="round-trip-selector booking-details-carousel" style="max-width:700px;margin:0 auto;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <main style="padding:20px;">
    <div style="text-align:center;padding:40px 20px;">
      <div style="width:64px;height:64px;margin:0 auto 16px;background:#ffebee;border-radius:50%;display:flex;align-items:center;justify-content:center;">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="#c62828" style="width:32px;height:32px;">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </div>
      <h3 style="font-size:18px;font-weight:700;color:#1a1a2e;margin:0 0 8px;">Booking Already Cancelled</h3>
      <p style="font-size:14px;color:#646d74;margin:0 0 16px;">
        {{ type_label }} booking <strong>{{ booking_id }}</strong> has already been cancelled.
      </p>
      {% if info_line %}
      <p style="font-size:13px;color:#888;margin:0 0 16px;">{{ info_line }}</p>
      {% endif %}
      <div style="background:#f8f9fa;border-radius:8px;padding:12px 16px;display:inline-block;">
        <span style="font-size:13px;color:#646d74;">No further action is needed. If you have questions about your refund, please contact support.</span>
      </div>
    </div>
  </main>
</div>
"""


def render_already_cancelled(
    booking_id: str,
    transaction_type: str = "Hotel",
    details: Dict[str, Any] = None,
) -> str:
    """
    Render an 'Already Cancelled' card when all rooms/passengers are cancelled.

    Args:
        booking_id: The booking ID
        transaction_type: "Hotel" or "Train"
        details: Booking details dict (for extracting info like hotel name, train name)

    Returns:
        HTML string with already-cancelled message
    """
    details = details or {}
    type_label = transaction_type

    info_line = ""
    if transaction_type == "Hotel":
        hotel_info = details.get("hotel_info", {})
        if hotel_info.get("hotel_name"):
            info_line = hotel_info["hotel_name"]
    elif transaction_type == "Train":
        train_info = details.get("train_info", {})
        parts = []
        if train_info.get("train_name"):
            parts.append(train_info["train_name"])
        if train_info.get("from_station_name") and train_info.get("to_station_name"):
            parts.append(f"{train_info['from_station_name']} → {train_info['to_station_name']}")
        info_line = " • ".join(parts)

    template = _jinja_env.from_string(ALREADY_CANCELLED_TEMPLATE)
    return template.render(
        booking_id=booking_id,
        type_label=type_label,
        info_line=info_line,
    )


# Flight cancellation mode labels
FLIGHT_CANCELLATION_MODE_LABELS = {
    "1": "I decided to cancel my flight",
    "2": "Airline cancelled my scheduled flight",
    "3": "I missed my flight",
    "4": "I have already cancelled my tickets from the airlines with cancellation charges (Already Cancelled from Airline)",
}


# =====================================================================
# ✈️ FLIGHT INTERACTIVE BOOKING TEMPLATE (WITH JS FOR CANCEL FLOW)
# =====================================================================
FLIGHT_BOOKING_TEMPLATE = """
<style>

.flight-cancel-carousel {
  font-family: poppins, sans-serif;
  color: #202020;
  background: rgba(255, 255, 255, 0.92);
  position: relative;
}

.flight-cancel-carousel * {
  font-family: inherit;
  box-sizing: border-box;
  margin: 0;
}

.flight-cancel-carousel main {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px 0 30px;
  position: relative;
}

.flight-cancel-carousel .fc-header {
  margin-bottom: 16px;
}

.flight-cancel-carousel .fc-title {
  font-size: 18px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 4px;
}

.flight-cancel-carousel .fc-subtitle {
  font-size: 12px;
  color: #646d74;
  margin-top: 4px;
}

.flight-cancel-carousel .fc-segment-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 12px;
  border: 1px solid #e0e0e0;
}

.flight-cancel-carousel .fc-segment-bound {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  color: #ef6614;
  letter-spacing: 1px;
  margin-bottom: 6px;
}

.flight-cancel-carousel .fc-airline-row {
  font-size: 15px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.flight-cancel-carousel .fc-route {
  font-size: 13px;
  color: #202020;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.flight-cancel-carousel .fc-route-arrow {
  color: #ef6614;
  font-weight: 600;
}

.flight-cancel-carousel .fc-details-row {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #202020;
  margin-top: 8px;
  flex-wrap: wrap;
}

.flight-cancel-carousel .fc-detail-item {
  display: flex;
  flex-direction: column;
}

.flight-cancel-carousel .fc-detail-label {
  font-size: 10px;
  color: #868686;
  text-transform: uppercase;
  margin-bottom: 2px;
}

.flight-cancel-carousel .fc-detail-value {
  font-weight: 600;
}

.flight-cancel-carousel .fc-pax-section {
  margin-bottom: 16px;
}

.flight-cancel-carousel .fc-pax-title {
  font-size: 14px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 12px;
}

.flight-cancel-carousel .fc-bound-label {
  font-size: 12px;
  font-weight: 700;
  color: #ef6614;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 12px 0 6px;
  padding-bottom: 4px;
  border-bottom: 1px solid #f0f0f0;
}

.flight-cancel-carousel .fc-select-all {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 13px;
  color: #646d74;
  cursor: pointer;
}

.flight-cancel-carousel .fc-select-all input[type="checkbox"] {
  accent-color: #ef6614;
  width: 16px;
  height: 16px;
}

.flight-cancel-carousel .fc-pax-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  margin-bottom: 8px;
}

.flight-cancel-carousel .fc-pax-table th {
  background: #f8f9fa;
  padding: 7px 4px;
  text-align: left;
  font-weight: 700;
  color: #646d74;
  font-size: 10px;
  text-transform: uppercase;
  border-bottom: 2px solid #e0e0e0;
}

.flight-cancel-carousel .fc-pax-table td {
  padding: 5px;
  font-size: 11px;
  border-bottom: 2px solid #f0f0f0;
  color: #202020;
}

.flight-cancel-carousel .fc-pax-table tr:hover {
  background: #fef6f0;
}

.flight-cancel-carousel .fc-pax-table input[type="checkbox"] {
  accent-color: #ef6614;
  width: 16px;
  height: 16px;
}

.flight-cancel-carousel .fc-status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.flight-cancel-carousel .fc-status-confirmed {
  background: #e8f5e9;
  color: #2e7d32;
}

.flight-cancel-carousel .fc-status-cancelled {
  background: #ffebee;
  color: #c62828;
}

.flight-cancel-carousel .fc-status-other {
  background: #fff3e0;
  color: #e65100;
}

.flight-cancel-carousel .fc-price-info {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 16px;
  border: 1px solid #e0e0e0;
}

.flight-cancel-carousel .fc-price-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 4px 0;
}

.flight-cancel-carousel .fc-price-label {
  color: #646d74;
}

.flight-cancel-carousel .fc-price-value {
  font-weight: 600;
  color: #202020;
}

.flight-cancel-carousel .fc-price-total {
  font-size: 16px;
  color: #ef6614;
}

.flight-cancel-carousel .fc-policy-section {
  background: #fffbf0;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 16px;
  border: 1px solid #ffe0b2;
}

.flight-cancel-carousel .fc-policy-title {
  font-size: 13px;
  font-weight: 600;
  color: #e65100;
  margin-bottom: 8px;
}

.flight-cancel-carousel .fc-policy-item {
  font-size: 12px;
  color: #646d74;
  padding: 3px 0;
}

/* Cancellation Mode Selection */
.flight-cancel-carousel .fc-mode-section {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.flight-cancel-carousel .fc-mode-title {
  font-size: 13px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 12px;
  line-height: 1.4;
}

.flight-cancel-carousel .fc-mode-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.flight-cancel-carousel .fc-mode-option {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fafafa;
}

.flight-cancel-carousel .fc-mode-option:hover {
  background: #f5f5f5;
  border-color: #ef6614;
}

.flight-cancel-carousel .fc-mode-option:has(input:checked) {
  background: #fef6f0;
  border-color: #ef6614;
  border-width: 2px;
}

.flight-cancel-carousel .fc-mode-radio {
  accent-color: #ef6614;
  width: 18px;
  height: 18px;
  margin-top: 2px;
  flex-shrink: 0;
  cursor: pointer;
}

.flight-cancel-carousel .fc-mode-label {
  font-size: 13px;
  color: #202020;
  line-height: 1.4;
  flex: 1;
  cursor: pointer;
}

/* File Upload Section */
.flight-cancel-carousel .fc-file-upload-section {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.flight-cancel-carousel .fc-file-upload-title {
  font-size: 13px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 6px;
}

.flight-cancel-carousel .fc-file-upload-description {
  font-size: 11px;
  color: #646d74;
  margin-bottom: 12px;
}

.flight-cancel-carousel .fc-file-upload-wrapper {
  margin-bottom: 12px;
}

.flight-cancel-carousel .fc-file-input {
  display: none;
}

.flight-cancel-carousel .fc-file-upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #ef6614;
  color: #fff;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: background 0.2s;
  border: none;
}

.flight-cancel-carousel .fc-file-upload-btn:hover {
  background: #d55a12;
}

.flight-cancel-carousel .fc-file-upload-btn svg {
  flex-shrink: 0;
}

.flight-cancel-carousel .fc-file-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 8px;
}

.flight-cancel-carousel .fc-file-icon {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 6px;
  font-size: 20px;
}

.flight-cancel-carousel .fc-file-details {
  flex: 1;
  min-width: 0;
}

.flight-cancel-carousel .fc-file-name {
  font-size: 13px;
  font-weight: 500;
  color: #202020;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.flight-cancel-carousel .fc-file-size {
  font-size: 11px;
  color: #646d74;
}

.flight-cancel-carousel .fc-file-remove {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 50%;
  color: #646d74;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.flight-cancel-carousel .fc-file-remove:hover {
  background: #fee;
  border-color: #f44336;
  color: #f44336;
}

.flight-cancel-carousel .fc-file-progress {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
}

.flight-cancel-carousel .fc-file-progress-bar {
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 6px;
  position: relative;
}

.flight-cancel-carousel .fc-file-progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 0;
  background: #ef6614;
  transition: width 0.3s;
  animation: progress-indeterminate 1.5s infinite;
}

@keyframes progress-indeterminate {
  0% { left: -35%; right: 100%; }
  60% { left: 100%; right: -90%; }
  100% { left: 100%; right: -90%; }
}

.flight-cancel-carousel .fc-file-progress-text {
  font-size: 11px;
  color: #646d74;
  text-align: center;
}

.flight-cancel-carousel .fc-file-error {
  padding: 8px 12px;
  background: #fee;
  border: 1px solid #f44336;
  border-radius: 6px;
  color: #c62828;
  font-size: 11px;
}

.flight-cancel-carousel .fc-pnr-info {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.flight-cancel-carousel .fc-pnr-item {
  background: #e3f2fd;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  color: #1565c0;
  font-weight: 600;
}

/* Reuse common interactive styles */
.flight-cancel-carousel .hc-step { display: none; }
.flight-cancel-carousel .hc-step.active { display: block; }

.flight-cancel-carousel .hc-cancel-btn {
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
.flight-cancel-carousel .hc-cancel-btn:hover { opacity: 0.85; }
.flight-cancel-carousel .hc-cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.flight-cancel-carousel .hc-loading {
  display: none;
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.85);
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 12px;
}

.flight-cancel-carousel .hc-spinner {
  width: 36px; height: 36px;
  border: 3px solid #e0e0e0;
  border-top-color: #ef6614;
  border-radius: 50%;
  animation: fcSpin 0.8s linear infinite;
}
@keyframes fcSpin { to { transform: rotate(360deg); } }

.flight-cancel-carousel .hc-error-msg {
  display: none;
  color: #d32f2f;
  padding: 4px 14px;
  border-radius: 8px;
  font-size: 12px;
  margin-bottom: 4px;
  margin-top: -4px;
}

.flight-cancel-carousel .hc-verify-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  padding: 5px 12px;
  text-align: center;
  max-width: 400px;
  margin: 0 auto;
}

.flight-cancel-carousel .hc-verify-icon {
  width: 50px; height: 50px;
  margin: 0 auto 4px;
  background: linear-gradient(135deg, #ef6614 0%, #f58434 100%);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  box-shadow: 0 4px 16px rgba(239, 102, 20, 0.25);
}

.flight-cancel-carousel .hc-verify-title {
  font-size: 18px; font-weight: 700; color: #202020; margin-bottom: 8px;
}

.flight-cancel-carousel .hc-verify-desc {
  font-size: 13px; color: #646d74; line-height: 1.5; margin-bottom: 9px;
}

.flight-cancel-carousel .hc-otp-field { margin-bottom: 16px; }

.flight-cancel-carousel .hc-login-otp-input {
  width: 100%; max-width: 240px;
  padding: 10px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 14px; font-weight: 600;
  text-align: center; letter-spacing: 4px;
  font-family: inter, sans-serif;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #fff; color: #202020;
}
.flight-cancel-carousel .hc-login-otp-input:focus {
  border-color: #ef6614;
  box-shadow: 0 0 0 3px rgba(239, 102, 20, 0.1);
}
.flight-cancel-carousel .hc-login-otp-input::placeholder {
  font-size: 14px; letter-spacing: 0; font-weight: 400; color: #bbb;
}

.flight-cancel-carousel .hc-submit-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, #ef6614 0%, #f58434 100%);
  color: #fff; border: none; border-radius: 8px;
  font-size: 14px; font-weight: 600; cursor: pointer;
  font-family: poppins, sans-serif;
  transition: opacity 0.2s;
}
.flight-cancel-carousel .hc-submit-btn:hover { opacity: 0.85; }

.flight-cancel-carousel .hc-back-btn {
  background: none;
  border: 1px solid #e0e0e0;
  padding: 8px 16px; border-radius: 8px;
  font-size: 12px; cursor: pointer;
  color: #646d74; font-family: poppins, sans-serif;
  transition: border-color 0.2s;
}
.flight-cancel-carousel .hc-back-btn:hover { border-color: #ef6614; color: #ef6614; }

.flight-cancel-carousel .hc-btn-row {
  display: flex; gap: 8px; margin-top: 16px;
}

.flight-cancel-carousel .hc-verify-icon--cancel {
  background: linear-gradient(135deg, #d32f2f 0%, #ef5350 100%);
  box-shadow: 0 4px 16px rgba(211, 47, 47, 0.25);
}

.flight-cancel-carousel .hc-otp-input {
  width: 100%; max-width: 240px;
  padding: 8px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 18px; font-weight: 600;
  text-align: center; letter-spacing: 4px;
  font-family: inter, sans-serif;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #fff; color: #202020;
}
.flight-cancel-carousel .hc-otp-input:focus {
  border-color: #ef6614;
  box-shadow: 0 0 0 3px rgba(239, 102, 20, 0.1);
}
.flight-cancel-carousel .hc-otp-input::placeholder {
  font-size: 14px; letter-spacing: 0; font-weight: 400; color: #bbb;
}

.flight-cancel-carousel .hc-verify-footer {
  font-size: 11px; color: #999; margin-top: 16px; line-height: 1.4;
}

.flight-cancel-carousel .hc-selected-room-badge {
  background: #f5f5f5;
  padding: 10px 14px; border-radius: 8px;
  font-size: 13px; margin-bottom: 16px;
  border-left: 3px solid #ef6614;
}

.flight-cancel-carousel .hc-resend-otp-btn {
  background: none; border: none; color: #2196f3; font-size: 12px; font-weight: 600;
  cursor: pointer; padding: 0; margin-top: 8px; text-decoration: none; display: inline-block;
}
.flight-cancel-carousel .hc-resend-otp-btn:hover { text-decoration: underline; color: #1565c0; }
.flight-cancel-carousel .hc-resend-otp-btn:disabled { color: #999; cursor: not-allowed; text-decoration: none; }

/* Success result */
.flight-cancel-carousel .hc-success-box {
  background: linear-gradient(135deg, #e8f5e9 0%, #f1f8f4 100%);
  border: 2px solid #4caf50; border-radius: 16px;
  padding: 32px 24px; text-align: center;
}
.flight-cancel-carousel .hc-success-icon {
  width: 64px; height: 64px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 20px rgba(76, 175, 80, 0.3);
  animation: fcSuccessPop 0.6s ease-out;
}
@keyframes fcSuccessPop {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}
.flight-cancel-carousel .hc-success-icon svg { width: 36px; height: 36px; color: #fff; }
.flight-cancel-carousel .hc-success-title {
  font-size: 20px; font-weight: 700; color: #2e7d32; margin-bottom: 16px;
}
.flight-cancel-carousel .hc-refund-box {
  background: linear-gradient(135deg, #fff8e1 0%, #fffbea 100%);
  border: 2px solid #ffc107; border-radius: 12px;
  padding: 16px; margin-top: 16px; text-align: left;
}
.flight-cancel-carousel .hc-refund-title { font-size: 14px; font-weight: 600; color: #f57c00; margin-bottom: 10px; }
.flight-cancel-carousel .hc-refund-row { display: flex; justify-content: space-between; font-size: 13px; padding: 4px 0; }
.flight-cancel-carousel .hc-refund-label { color: #646d74; }
.flight-cancel-carousel .hc-refund-value { font-weight: 600; color: #202020; }
.flight-cancel-carousel .hc-refund-amount { font-size: 24px; font-weight: 700; color: #ef6614; font-family: inter, sans-serif; margin-bottom: 8px; }
.flight-cancel-carousel .hc-footer-note { font-size: 12px; color: #868686; text-align: center; margin-top: 20px; }

/* Dark mode */
.flight-cancel-carousel.dark { background: #000; color: #fff; }
.flight-cancel-carousel.dark .fc-segment-card,
.flight-cancel-carousel.dark .fc-price-info { background: #000; border-color: #373737; }
.flight-cancel-carousel.dark .fc-title,
.flight-cancel-carousel.dark .fc-airline-row,
.flight-cancel-carousel.dark .fc-detail-value,
.flight-cancel-carousel.dark .fc-price-value,
.flight-cancel-carousel.dark .fc-pax-table td { color: #fff; }
.flight-cancel-carousel.dark .fc-subtitle,
.flight-cancel-carousel.dark .fc-detail-label,
.flight-cancel-carousel.dark .fc-price-label,
.flight-cancel-carousel.dark .fc-pax-table th { color: #bcbcbc; }
.flight-cancel-carousel.dark .fc-pax-table th { background: #111; border-color: #373737; }
.flight-cancel-carousel.dark .fc-pax-table td { border-color: #222; }
.flight-cancel-carousel.dark .fc-pax-table tr:hover { background: #1a1a1a; }
.flight-cancel-carousel.dark .fc-policy-section { background: #1a1500; border-color: #5a4000; }
.flight-cancel-carousel.dark .fc-mode-section {
  background: #000;
  border-color: #373737;
}
.flight-cancel-carousel.dark .fc-mode-title {
  color: #fff;
}
.flight-cancel-carousel.dark .fc-mode-option {
  background: #0a0a0a;
  border-color: #373737;
}
.flight-cancel-carousel.dark .fc-mode-option:hover {
  background: #1a1a1a;
  border-color: #ef6614;
}
.flight-cancel-carousel.dark .fc-mode-option:has(input:checked) {
  background: #1a1a0a;
  border-color: #ef6614;
}
.flight-cancel-carousel.dark .fc-mode-label {
  color: #fff;
}
.flight-cancel-carousel.dark .fc-file-upload-section {
  background: #000;
  border-color: #373737;
}
.flight-cancel-carousel.dark .fc-file-upload-title {
  color: #fff;
}
.flight-cancel-carousel.dark .fc-file-upload-description {
  color: #bcbcbc;
}
.flight-cancel-carousel.dark .fc-file-preview {
  background: #0a0a0a;
  border-color: #373737;
}
.flight-cancel-carousel.dark .fc-file-icon {
  background: #000;
}
.flight-cancel-carousel.dark .fc-file-name {
  color: #fff;
}
.flight-cancel-carousel.dark .fc-file-size {
  color: #bcbcbc;
}
.flight-cancel-carousel.dark .fc-file-remove {
  background: #000;
  border-color: #373737;
  color: #bcbcbc;
}
.flight-cancel-carousel.dark .fc-file-remove:hover {
  background: #3d0000;
  border-color: #f44336;
  color: #ff8a80;
}
.flight-cancel-carousel.dark .fc-file-progress {
  background: #0a0a0a;
}
.flight-cancel-carousel.dark .fc-file-progress-bar {
  background: #373737;
}
.flight-cancel-carousel.dark .fc-file-error {
  background: #3d0000;
  border-color: #f44336;
  color: #ff8a80;
}
.flight-cancel-carousel.dark .fc-pnr-item { background: #0a1929; color: #64b5f6; }
.flight-cancel-carousel.dark .hc-loading { background: rgba(0,0,0,0.85); }
.flight-cancel-carousel.dark .hc-error-msg { background: #3d0000; color: #ff8a80; }
.flight-cancel-carousel.dark .hc-verify-card { background: linear-gradient(135deg, #1a1a1a 0%, #111 100%); border-color: #373737; }
.flight-cancel-carousel.dark .hc-verify-title { color: #fff; }
.flight-cancel-carousel.dark .hc-verify-desc { color: #bcbcbc; }
.flight-cancel-carousel.dark .hc-login-otp-input,
.flight-cancel-carousel.dark .hc-otp-input { background: #000; border-color: #373737; color: #fff; }
.flight-cancel-carousel.dark .hc-login-otp-input:focus,
.flight-cancel-carousel.dark .hc-otp-input:focus { border-color: #ef6614; box-shadow: 0 0 0 3px rgba(239, 102, 20, 0.2); }
.flight-cancel-carousel.dark .hc-back-btn { border-color: #373737; color: #bcbcbc; }
.flight-cancel-carousel.dark .hc-selected-room-badge { background: #1a1a1a; color: #fff; }
.flight-cancel-carousel.dark .hc-success-box { background: linear-gradient(135deg, #1a3a1a 0%, #1f2d1f 100%); }
.flight-cancel-carousel.dark .hc-success-title { color: #66bb6a; }
.flight-cancel-carousel.dark .hc-refund-box { background: linear-gradient(135deg, #332a00 0%, #3d3200 100%); }
.flight-cancel-carousel.dark .hc-refund-value { color: #fff; }
.flight-cancel-carousel.dark .hc-refund-label { color: #bcbcbc; }
.flight-cancel-carousel.dark .hc-verify-footer { color: #666; }

</style>

<div class="flight-cancel-carousel round-trip-selector" data-instance-id="{{ instance_id }}">
  <main>
    <div class="hc-loading"><div class="hc-spinner"></div></div>
    <div class="hc-error-msg"></div>

    <div class="fc-header">
      <div class="fc-title">{{ title }}</div>
      <div class="fc-subtitle"{% if is_otp_send %} style="display:none"{% endif %}>{{ subtitle }}</div>
    </div>

    <!-- STEP 0: Login OTP verification -->
    {% if is_otp_send %}
    <div class="hc-step active" data-step="verify-otp">
      <div class="hc-verify-card">
        <div class="hc-verify-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>
          </svg>
        </div>
        <div class="hc-verify-title">Verify Your Identity</div>
        <p class="hc-verify-desc">We've sent a One-Time Password to your registered email &amp; phone number. Enter it below to continue.</p>
        <div class="hc-otp-field">
          <input type="text" class="hc-login-otp-input" maxlength="10" placeholder="Enter OTP" autocomplete="one-time-code" />
        </div>
        <div class="hc-error-msg hc-step-error"></div>
        <button type="button" class="hc-submit-btn hc-verify-otp-btn">Verify &amp; Continue</button>
        <p class="hc-verify-footer">Didn't receive the OTP? <button type="button" class="hc-resend-otp-btn hc-resend-login-otp">Resend OTP</button></p>
      </div>
    </div>
    {% endif %}

    <!-- STEP 1: Flight details + Passenger selection -->
    <div class="hc-step {{ 'active' if not is_otp_send and not all_cancelled else '' }}" data-step="details">

      <!-- Flight Segments -->
      {% for seg in flight_segments %}
      <div class="fc-segment-card">
        {% if seg.bound_type %}
        <div class="fc-segment-bound">
          {% if 'out' in seg.bound_type|lower %}Outbound{% elif 'in' in seg.bound_type|lower %}Inbound{% else %}{{ seg.bound_type }}{% endif %}
        </div>
        {% endif %}
        <div class="fc-airline-row">✈️ {{ seg.airline_name }} {{ seg.flight_number }}</div>
        <div class="fc-route">
          <span>{{ seg.origin }}{% if seg.origin_airport %} ({{ seg.origin_airport | truncate_text(25) }}){% endif %}</span>
          <span class="fc-route-arrow">→</span>
          <span>{{ seg.destination }}{% if seg.destination_airport %} ({{ seg.destination_airport | truncate_text(25) }}){% endif %}</span>
        </div>
        <div class="fc-details-row">
          {% if seg.departure_date %}
          <div class="fc-detail-item">
            <div class="fc-detail-label">Departure</div>
            <div class="fc-detail-value">{{ seg.departure_date }} {{ seg.departure_time }}</div>
          </div>
          {% endif %}
          {% if seg.arrival_date %}
          <div class="fc-detail-item">
            <div class="fc-detail-label">Arrival</div>
            <div class="fc-detail-value">{{ seg.arrival_date }} {{ seg.arrival_time }}</div>
          </div>
          {% endif %}
          {% if seg.duration %}
          <div class="fc-detail-item">
            <div class="fc-detail-label">Duration</div>
            <div class="fc-detail-value">{{ seg.duration }}</div>
          </div>
          {% endif %}
          {% if seg.cabin_class %}
          <div class="fc-detail-item">
            <div class="fc-detail-label">Class</div>
            <div class="fc-detail-value">{{ seg.cabin_class }}</div>
          </div>
          {% endif %}
          {% if seg.origin_terminal %}
          <div class="fc-detail-item">
            <div class="fc-detail-label">Terminal</div>
            <div class="fc-detail-value">T{{ seg.origin_terminal }} → T{{ seg.destination_terminal }}</div>
          </div>
          {% endif %}
          {% if seg.check_in_baggage %}
          <div class="fc-detail-item">
            <div class="fc-detail-label">Baggage</div>
            <div class="fc-detail-value">{{ seg.check_in_baggage }}</div>
          </div>
          {% endif %}
        </div>
      </div>
      {% endfor %}


      <!-- Passenger Selection -->
      <div class="fc-pax-section">
        <div class="fc-pax-title">Select passengers to cancel</div>
        <label class="fc-select-all">
          <input type="checkbox" class="fc-select-all-cb" /> Select All Passengers
        </label>

        {% if outbound_passengers %}
        <div class="fc-bound-label">Outbound</div>
        <table class="fc-pax-table">
          <thead>
            <tr>
              <th></th>
              <th>Passenger</th>
              <th>Type</th>
              <th>Ticket</th>
              <th>Status</th>
              <th>Cancel Charge</th>
            </tr>
          </thead>
          <tbody>
            {% for pax in outbound_passengers %}
            <tr{% if pax.is_cancelled or not pax.is_cancellable %} style="opacity: 0.5;"{% endif %}>
              <td><input type="checkbox" class="fc-pax-cb" data-pax-id="{{ pax.pax_id }}" data-bound="outbound"{% if pax.is_cancelled or not pax.is_cancellable %} disabled{% endif %} /></td>
              <td>{{ pax.title }} {{ pax.first_name }} {{ pax.last_name }}</td>
              <td>{{ pax.pax_type }}</td>
              <td>{{ pax.ticket_number or '-' }}</td>
              <td>
                {% if pax.is_cancelled %}
                <span class="fc-status-badge fc-status-cancelled">Cancelled</span>
                {% elif pax.status %}
                <span class="fc-status-badge {{ 'fc-status-confirmed' if pax.status|lower == 'confirmed' or pax.status|lower == 'booked' else 'fc-status-other' }}">{{ pax.status }}</span>
                {% endif %}
              </td>
              <td>{% if pax.cancellation_charge %}₹{{ pax.cancellation_charge }}{% else %}-{% endif %}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
        {% endif %}

        {% if inbound_passengers %}
        <div class="fc-bound-label">Inbound</div>
        <table class="fc-pax-table">
          <thead>
            <tr>
              <th></th>
              <th>Passenger</th>
              <th>Type</th>
              <th>Ticket</th>
              <th>Status</th>
              <th>Cancel Charge</th>
            </tr>
          </thead>
          <tbody>
            {% for pax in inbound_passengers %}
            <tr{% if pax.is_cancelled or not pax.is_cancellable %} style="opacity: 0.5;"{% endif %}>
              <td><input type="checkbox" class="fc-pax-cb" data-pax-id="{{ pax.pax_id }}" data-bound="inbound"{% if pax.is_cancelled or not pax.is_cancellable %} disabled{% endif %} /></td>
              <td>{{ pax.title }} {{ pax.first_name }} {{ pax.last_name }}</td>
              <td>{{ pax.pax_type }}</td>
              <td>{{ pax.ticket_number or '-' }}</td>
              <td>
                {% if pax.is_cancelled %}
                <span class="fc-status-badge fc-status-cancelled">Cancelled</span>
                {% elif pax.status %}
                <span class="fc-status-badge {{ 'fc-status-confirmed' if pax.status|lower == 'confirmed' or pax.status|lower == 'booked' else 'fc-status-other' }}">{{ pax.status }}</span>
                {% endif %}
              </td>
              <td>{% if pax.cancellation_charge %}₹{{ pax.cancellation_charge }}{% else %}-{% endif %}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
        {% endif %}
      </div>

      <!-- Cancellation Mode Selection -->
      {% if possible_modes %}
      <div class="fc-mode-section">
        <div class="fc-mode-title">Why did you cancel your flight bookings? Kindly, select any one of the following reasons mentioned below that led to your flight cancellation.</div>
        <div class="fc-mode-options">
          {% for mode in possible_modes %}
          <label class="fc-mode-option">
            <input type="radio" name="fc-cancel-mode-{{ instance_id }}" class="fc-mode-radio" value="{{ mode }}" />
            <span class="fc-mode-label">{{ mode_labels.get(mode, "Mode " + mode) }}</span>
          </label>
          {% endfor %}
        </div>
      </div>
      {% endif %}

      <!-- File Upload Section (Mode 2 Only) -->
      <div class="fc-file-upload-section" style="display: none;">
        <div class="fc-file-upload-title">Upload Cancellation Proof</div>
        <div class="fc-file-upload-description">Please upload airline cancellation proof (JPEG, PNG, or PDF, max 5MB)</div>

        <div class="fc-file-upload-wrapper">
          <input type="file" id="fc-file-input-{{ instance_id }}" class="fc-file-input"
                 accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf" />
          <label for="fc-file-input-{{ instance_id }}" class="fc-file-upload-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <span class="fc-file-btn-text">Choose File</span>
          </label>
        </div>

        <div class="fc-file-info" style="display: none;">
          <div class="fc-file-preview">
            <div class="fc-file-icon"></div>
            <div class="fc-file-details">
              <div class="fc-file-name"></div>
              <div class="fc-file-size"></div>
            </div>
            <button type="button" class="fc-file-remove" aria-label="Remove file">×</button>
          </div>
          <div class="fc-file-progress" style="display: none;">
            <div class="fc-file-progress-bar"></div>
            <div class="fc-file-progress-text">Uploading...</div>
          </div>
        </div>

        <div class="fc-file-error" style="display: none;"></div>
      </div>

      <!-- Cancellation Policy (moved below, optional) -->
      {% if cancellation_policy %}
      <div class="fc-policy-section">
        <div class="fc-policy-title">Cancellation Policy</div>
        {% for sector in cancellation_policy %}
          {% for pol in sector.policies %}
          <div class="fc-policy-item">
            {% if pol.policy_text %}{{ pol.policy_text }}{% else %}{{ pol.charge_type }}: ₹{{ pol.charge_value }}{% if pol.from_date %} ({{ pol.from_date }} - {{ pol.to_date }}){% endif %}{% endif %}
          </div>
          {% endfor %}
        {% endfor %}
      </div>
      {% endif %}

      <!-- Price Info -->
      {% if price_info and price_info.total_fare %}
      <div class="fc-price-info">
        <div class="fc-price-row">
          <span class="fc-price-label">Total Fare</span>
          <span class="fc-price-value fc-price-total">₹{{ price_info.total_fare }}</span>
        </div>
        {% if price_info.total_base_fare %}
        <div class="fc-price-row">
          <span class="fc-price-label">Base Fare</span>
          <span class="fc-price-value">₹{{ price_info.total_base_fare }}</span>
        </div>
        {% endif %}
        {% if price_info.total_tax %}
        <div class="fc-price-row">
          <span class="fc-price-label">Taxes &amp; Fees</span>
          <span class="fc-price-value">₹{{ price_info.total_tax }}</span>
        </div>
        {% endif %}
      </div>
      {% endif %}

      <button type="button" class="hc-cancel-btn fc-proceed-btn" disabled>Cancel Selected Passengers</button>
    </div>

    <!-- STEP 2: Send OTP & Confirm -->
    <div class="hc-step" data-step="otp">
      <div class="hc-selected-room-badge">
        Cancelling: <strong class="fc-selected-pax-label"></strong>
      </div>
      <div class="hc-verify-card">
        <div class="hc-verify-icon hc-verify-icon--cancel">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/>
          </svg>
        </div>
        <div class="hc-verify-title">Confirm Cancellation</div>
        <p class="hc-verify-desc">A cancellation OTP has been sent to your registered email &amp; phone. Enter it below to confirm.</p>
        <div class="hc-otp-field">
          <input type="text" class="hc-otp-input" maxlength="10" placeholder="Enter OTP" autocomplete="one-time-code" />
        </div>
        <div class="hc-error-msg hc-step-error"></div>
        <div class="hc-btn-row" style="justify-content: center;">
          <button type="button" class="hc-back-btn" data-back-to="details">Back</button>
          <button type="button" class="hc-submit-btn fc-confirm-btn">Confirm Cancellation</button>
        </div>
        <p class="hc-verify-footer">
          This action cannot be undone. Refund will be processed as per airline cancellation policy.<br>
          Didn't receive the OTP? <button type="button" class="hc-resend-otp-btn hc-resend-cancel-otp">Resend OTP</button>
        </p>
      </div>
    </div>

    <!-- STEP 3: Result -->
    <div class="hc-step" data-step="result">
      <div class="hc-result-content"></div>
    </div>

    <!-- STEP: Already Cancelled -->
    <div class="hc-step {{ 'active' if not is_otp_send and all_cancelled else '' }}" data-step="cancelled">
      <div style="text-align:center;padding:30px 20px;">
        <div style="width:56px;height:56px;margin:0 auto 14px;background:#ffebee;border-radius:50%;display:flex;align-items:center;justify-content:center;">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="#c62828" style="width:28px;height:28px;">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </div>
        <h3 style="font-size:17px;font-weight:700;color:#1a1a2e;margin:0 0 8px;">Booking Already Cancelled</h3>
        <p style="font-size:13px;color:#646d74;margin:0 0 14px;">All passengers in this flight booking have already been cancelled.</p>
        <div style="background:#f8f9fa;border-radius:8px;padding:10px 14px;display:inline-block;">
          <span style="font-size:12px;color:#646d74;">No further action is needed. If you have questions about your refund, please contact support.</span>
        </div>
      </div>
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
  var VERIFY_OTP_URL = API_BASE + '/api/hotel-cancel/verify-otp';
  var OTP_URL = API_BASE + '/api/hotel-cancel/send-otp';
  var CANCEL_URL = API_BASE + '/api/hotel-cancel/confirm';
  var RESEND_LOGIN_OTP_URL = API_BASE + '/api/hotel-cancel/resend-login-otp';
  var BID = '{{ bid }}';
  var BOOKING_ID = '{{ booking_id }}';
  var EMAIL = '{{ email }}';
  var ALL_CANCELLED = {{ 'true' if all_cancelled else 'false' }};

  var selectedOutbound = [];
  var selectedInbound = [];
  var selectedMode = null;

  var loadingOverlay = container.querySelector('.hc-loading');
  var globalErrorBanner = container.querySelector('main > .hc-error-msg');

  function hideAllErrors() {
    var errs = container.querySelectorAll('.hc-error-msg');
    for (var i = 0; i < errs.length; i++) errs[i].style.display = 'none';
  }

  function showStep(stepName) {
    var steps = container.querySelectorAll('.hc-step');
    for (var i = 0; i < steps.length; i++) steps[i].classList.remove('active');
    var target = container.querySelector('[data-step="' + stepName + '"]');
    if (target) target.classList.add('active');
    hideAllErrors();
  }

  function showLoading(show) { loadingOverlay.style.display = show ? 'flex' : 'none'; }
  function showError(msg) {
    hideAllErrors();
    var activeStep = container.querySelector('.hc-step.active');
    var inlineErr = activeStep ? activeStep.querySelector('.hc-step-error') : null;
    var target = inlineErr || globalErrorBanner;
    target.textContent = msg;
    target.style.display = 'block';
  }

  function updateSelectedLabel() {
    var total = selectedOutbound.length + selectedInbound.length;
    var labels = container.querySelectorAll('.fc-selected-pax-label');
    var text = total + ' passenger(s)';
    for (var i = 0; i < labels.length; i++) labels[i].textContent = text;
  }

  function updateProceedBtn() {
    var btn = container.querySelector('.fc-proceed-btn');
    var cbs = container.querySelectorAll('.fc-pax-cb:not(:disabled):checked');
    selectedOutbound = [];
    selectedInbound = [];
    for (var i = 0; i < cbs.length; i++) {
      var paxId = cbs[i].getAttribute('data-pax-id');
      var bound = cbs[i].getAttribute('data-bound');
      if (bound === 'inbound') {
        selectedInbound.push(paxId);
      } else {
        selectedOutbound.push(paxId);
      }
    }
    var hasPaxSelected = (selectedOutbound.length + selectedInbound.length) > 0;
    var hasModeSelected = selectedMode !== null;
    var hasModesAvailable = container.querySelectorAll('.fc-mode-radio').length > 0;
    var requiresFile = selectedMode === '2';
    var hasFile = uploadedFile !== null;
    // If modes available, require both; otherwise only passengers (backward compat)
    // If Mode 2 is selected, also require file upload
    btn.disabled = !hasPaxSelected || (hasModesAvailable && !hasModeSelected) || (requiresFile && !hasFile);
  }

  /* Checkbox handlers */
  var selectAllCb = container.querySelector('.fc-select-all-cb');
  var paxCbs = container.querySelectorAll('.fc-pax-cb');
  var activePaxCbs = container.querySelectorAll('.fc-pax-cb:not(:disabled)');

  if (selectAllCb) {
    selectAllCb.addEventListener('change', function() {
      for (var i = 0; i < activePaxCbs.length; i++) activePaxCbs[i].checked = this.checked;
      updateProceedBtn();
    });
  }
  for (var i = 0; i < activePaxCbs.length; i++) {
    activePaxCbs[i].addEventListener('change', function() {
      updateProceedBtn();
      if (selectAllCb) {
        var allChecked = container.querySelectorAll('.fc-pax-cb:not(:disabled):checked').length === activePaxCbs.length;
        selectAllCb.checked = allChecked;
      }
    });
  }

  /* File Upload Variables */
  var uploadedFile = null;
  var uploadedFileUrl = null;
  var fileInput = container.querySelector('.fc-file-input');
  var fileUploadSection = container.querySelector('.fc-file-upload-section');
  var fileInfo = container.querySelector('.fc-file-info');
  var filePreview = container.querySelector('.fc-file-preview');
  var fileProgress = container.querySelector('.fc-file-progress');
  var fileError = container.querySelector('.fc-file-error');

  /* Mode radio button handler */
  var modeRadios = container.querySelectorAll('.fc-mode-radio');
  for (var i = 0; i < modeRadios.length; i++) {
    modeRadios[i].addEventListener('change', function() {
      selectedMode = this.value;
      // Show file upload section only for Mode 2
      if (fileUploadSection) {
        if (this.value === '2') {
          fileUploadSection.style.display = 'block';
        } else {
          fileUploadSection.style.display = 'none';
          clearUploadedFile();
        }
      }
      updateProceedBtn();
    });
  }

  /* File Upload Helper Functions */
  function clearUploadedFile() {
    uploadedFile = null;
    uploadedFileUrl = null;
    if (fileInput) fileInput.value = '';
    if (fileInfo) fileInfo.style.display = 'none';
    if (fileError) fileError.style.display = 'none';
  }

  function showFileError(msg) {
    if (fileError) {
      fileError.textContent = msg;
      fileError.style.display = 'block';
    }
  }

  function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function getFileIcon(fileType) {
    if (fileType.includes('pdf')) return '📄';
    if (fileType.includes('image')) return '🖼️';
    return '📎';
  }

  /* File Input Change Handler */
  if (fileInput) {
    fileInput.addEventListener('change', function(e) {
      var file = e.target.files[0];
      if (!file) return;

      // Clear previous errors
      if (fileError) fileError.style.display = 'none';

      // Validate file type
      var validTypes = ['image/jpeg', 'image/png', 'application/pdf'];
      if (!validTypes.includes(file.type)) {
        showFileError('Invalid file type. Please upload JPEG, PNG, or PDF files only.');
        fileInput.value = '';
        return;
      }

      // Validate file size (5MB max)
      var maxSize = 5 * 1024 * 1024;
      if (file.size > maxSize) {
        showFileError('File size exceeds 5MB. Please choose a smaller file.');
        fileInput.value = '';
        return;
      }

      // Store file and show preview
      uploadedFile = file;
      uploadedFileUrl = null;

      // Update preview
      var fileName = container.querySelector('.fc-file-name');
      var fileSize = container.querySelector('.fc-file-size');
      var fileIcon = container.querySelector('.fc-file-icon');

      if (fileName) fileName.textContent = file.name;
      if (fileSize) fileSize.textContent = formatFileSize(file.size);
      if (fileIcon) fileIcon.textContent = getFileIcon(file.type);
      if (fileInfo) fileInfo.style.display = 'block';

      updateProceedBtn();
    });
  }

  /* Remove File Button Handler */
  var removeFileBtn = container.querySelector('.fc-file-remove');
  if (removeFileBtn) {
    removeFileBtn.addEventListener('click', function() {
      clearUploadedFile();
      updateProceedBtn();
    });
  }

  /* File Upload Function */
  function uploadCancellationFile(file, headers) {
    return new Promise(function(resolve, reject) {
      if (fileProgress) fileProgress.style.display = 'block';
      if (fileError) fileError.style.display = 'none';

      // Generate timestamped filename
      var now = new Date();
      var day = String(now.getDate()).padStart(2, '0');
      var month = String(now.getMonth() + 1).padStart(2, '0');
      var year = now.getFullYear();
      var hour = String(now.getHours()).padStart(2, '0');
      var minute = String(now.getMinutes()).padStart(2, '0');
      var second = String(now.getSeconds()).padStart(2, '0');

      var nameParts = file.name.split('.');
      var extension = nameParts.pop();
      var baseName = nameParts.join('.');
      var newFileName = baseName + '-' + day + month + year + hour + minute + second + '.' + extension;

      // Upload to API
      var uploadUrl = API_BASE + '/api/flight-cancel/upload-file';

      var uploadHeaders = {
        'betid': headers.betid || '',
        'UserName': 'EMT',
        'Password': '123',
        'paxidout': headers.paxidout || '',
        'paxidin': headers.paxidin || '',
        'possibleMode': '2',
        'totalpaxout': headers.totalpaxout || '0',
        'totalpaxin': headers.totalpaxin || '0',
        'IscouponApply': 'false',
        'UploadImageURL': newFileName,
        'IsImage': 'false'
      };

      fetch(uploadUrl, {
        method: 'POST',
        headers: uploadHeaders,
        body: file
      })
      .then(function(resp) {
        if (!resp.ok) throw new Error('Upload failed with status ' + resp.status);
        return resp.text();
      })
      .then(function(data) {
        if (fileProgress) fileProgress.style.display = 'none';
        try {
          var result = JSON.parse(data);
          uploadedFileUrl = result.fileUrl || result.FileUrl || newFileName;
          resolve({ fileName: newFileName, fileUrl: uploadedFileUrl, response: result });
        } catch (e) {
          uploadedFileUrl = newFileName;
          resolve({ fileName: newFileName, fileUrl: newFileName, response: data });
        }
      })
      .catch(function(err) {
        if (fileProgress) fileProgress.style.display = 'none';
        showFileError('File upload failed: ' + (err.message || 'Unknown error'));
        reject(err);
      });
    });
  }

  /* API helpers */
  function verifyLoginOtp(otp) {
    showLoading(true);
    hideAllErrors();
    return fetch(VERIFY_OTP_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ booking_id: BOOKING_ID, email: EMAIL, otp: otp })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      var isVerified = false;
      var msg = '';
      if (data.structured_content) {
        isVerified = !!data.structured_content.success;
        msg = data.structured_content.message || data.response_text || '';
      } else if (data.isVerify !== undefined) {
        isVerified = String(data.isVerify).toLowerCase() === 'true';
        msg = data.Message || data.Msg || '';
      } else if (data.success !== undefined) {
        isVerified = !!data.success;
        msg = data.message || data.Message || '';
      } else if (data.isStatus !== undefined) {
        isVerified = !!data.isStatus;
        msg = data.Msg || data.Message || '';
      }
      if (!isVerified) {
        showError(msg || 'Invalid OTP. Please check and try again.');
        return null;
      }
      return data;
    })
    .catch(function(err) {
      showLoading(false);
      var msg = (err && err.message && err.message.indexOf('Failed to fetch') !== -1)
        ? 'Something Went Wrong Please Try Again.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  function sendOtp() {
    showLoading(true);
    hideAllErrors();
    return fetch(OTP_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ booking_id: BOOKING_ID, email: EMAIL, transaction_type: 'Flight' })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      var success = false;
      if (data.structured_content) {
        success = !!data.structured_content.success;
      } else {
        success = !!(data.isStatus || data.IsStatus);
      }
      if (!success) {
        var msg = (data.structured_content && data.structured_content.message) || data.Msg || data.Message || 'Failed to send OTP. Please try again.';
        showError(msg);
        return null;
      }
      return data;
    })
    .catch(function(err) {
      showLoading(false);
      var msg = (err && err.message && err.message.indexOf('Failed to fetch') !== -1)
        ? 'Something Went Wrong Please Try Again.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  function confirmCancellation(otp) {
    showLoading(true);
    hideAllErrors();
    return fetch(CANCEL_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        booking_id: BOOKING_ID,
        email: EMAIL,
        otp: otp,
        outbound_pax_ids: selectedOutbound.join(','),
        inbound_pax_ids: selectedInbound.join(','),
        transaction_type: 'Flight',
        mode: selectedMode || '1'  // Default to '1' for backward compatibility
      })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      if (typeof data === 'string') {
        var success = data.toLowerCase().indexOf('success') !== -1 || data.toLowerCase().indexOf('cancel') !== -1;
        if (!success) {
          var isOtpError = data.toLowerCase().indexOf('otp') !== -1;
          var fallback = isOtpError ? 'Invalid OTP. Please check and try again.' : 'Cancellation failed. Please try again.';
          showError(data || fallback);
          return null;
        }
        return { Status: true, message: data };
      }
      var isSuccess = data.isRequested || data.isCancelled || data.isValidOTP || (data.Status === true) || data.isStatus;
      if (!isSuccess) {
        var msg = data.LogMessage || data.Message || data.Msg || data.msg || '';
        var isOtpError = msg.toLowerCase().indexOf('otp') !== -1;
        var fallback = isOtpError ? 'Invalid OTP. Please check and try again.' : 'Cancellation failed. Please try again.';
        showError(msg || fallback);
        return null;
      }
      return data;
    })
    .catch(function(err) {
      showLoading(false);
      var msg = (err && err.message && err.message.indexOf('Failed to fetch') !== -1)
        ? 'Something Went Wrong Please Try Again.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  /* Step 0: Verify login OTP */
  var verifyOtpBtn = container.querySelector('.hc-verify-otp-btn');
  if (verifyOtpBtn) {
    verifyOtpBtn.addEventListener('click', function() {
      var otpInput = container.querySelector('.hc-login-otp-input');
      var otp = otpInput ? otpInput.value.trim() : '';
      if (!otp || otp.length < 4) { showError('Please enter a valid OTP.'); return; }
      verifyLoginOtp(otp).then(function(result) {
        if (result) {
          var sub = container.querySelector('.fc-subtitle');
          if (sub) sub.style.display = '';
          if (ALL_CANCELLED) { showStep('cancelled'); }
          else { showStep('details'); }
        }
      });
    });
  }

  /* Resend login OTP */
  var resendLoginOtpBtn = container.querySelector('.hc-resend-login-otp');
  if (resendLoginOtpBtn) {
    resendLoginOtpBtn.addEventListener('click', function() {
      var btn = this;
      btn.disabled = true;
      btn.textContent = 'Sending...';
      fetch(RESEND_LOGIN_OTP_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ booking_id: BOOKING_ID, email: EMAIL })
      })
      .then(function(resp) { return resp.json(); })
      .then(function() {
        btn.textContent = 'OTP Sent!';
        setTimeout(function() { btn.textContent = 'Resend OTP'; btn.disabled = false; }, 3000);
      })
      .catch(function() {
        showError('Failed to resend OTP. Please try again.');
        btn.textContent = 'Resend OTP';
        btn.disabled = false;
      });
    });
  }

  /* Step 1: Proceed with selected passengers */
  var proceedBtn = container.querySelector('.fc-proceed-btn');
  if (proceedBtn) {
    proceedBtn.addEventListener('click', function() {
      if (selectedOutbound.length + selectedInbound.length === 0) return;
      hideAllErrors();

      // Check if file upload is required and handle upload first
      if (selectedMode === '2' && uploadedFile && !uploadedFileUrl) {
        showLoading(true);

        var uploadHeaders = {
          betid: BOOKING_ID,
          paxidout: selectedOutbound.join(','),
          paxidin: selectedInbound.join(','),
          totalpaxout: String(selectedOutbound.length),
          totalpaxin: String(selectedInbound.length)
        };

        uploadCancellationFile(uploadedFile, uploadHeaders)
          .then(function(result) {
            showLoading(false);
            // File uploaded successfully, now send OTP
            updateSelectedLabel();
            sendOtp().then(function(result) { if (result) showStep('otp'); });
          })
          .catch(function(err) {
            showLoading(false);
            showError('Failed to upload file. Please try again.');
          });
      } else {
        // No file upload needed or already uploaded, proceed to OTP
        updateSelectedLabel();
        sendOtp().then(function(result) { if (result) showStep('otp'); });
      }
    });
  }

  /* Step 2: Confirm cancellation */
  var confirmBtn = container.querySelector('.fc-confirm-btn');
  if (confirmBtn) {
    confirmBtn.addEventListener('click', function() {
      var otpInput = container.querySelector('.hc-otp-input');
      var otp = otpInput ? otpInput.value.trim() : '';
      if (!otp || otp.length < 4) { showError('Please enter a valid OTP.'); return; }
      confirmCancellation(otp).then(function(result) {
        if (result) { renderResult(result); showStep('result'); }
      });
    });
  }

  /* Resend cancellation OTP */
  var resendCancelOtpBtn = container.querySelector('.hc-resend-cancel-otp');
  if (resendCancelOtpBtn) {
    resendCancelOtpBtn.addEventListener('click', function() {
      var btn = this;
      btn.disabled = true;
      btn.textContent = 'Sending...';
      sendOtp().then(function(result) {
        if (result) {
          btn.textContent = 'OTP Sent!';
        } else {
          btn.textContent = 'Resend OTP';
        }
        btn.disabled = false;
        setTimeout(function() { btn.textContent = 'Resend OTP'; }, 3000);
      });
    });
  }

  /* Step 3: Render result */
  function renderResult(data) {
    var resultContainer = container.querySelector('.hc-result-content');
    var html = '<div class="hc-success-box">';
    html += '<div class="hc-success-icon"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg></div>';
    html += '<div class="hc-success-title">Cancellation Confirmed!</div>';

    var msg = data.msg || data.Message || data.Msg || data.message || '';
    var requestId = data.RequestId || data.requestId || '';
    if (msg) html += '<p style="font-size:13px;color:#646d74;margin-bottom:12px;">' + msg + '</p>';
    if (requestId) html += '<p style="font-size:12px;color:#868686;margin-bottom:12px;">Request ID: ' + requestId + '</p>';

    var refundAmount = data.RefundAmount;
    var cancellationCharges = data.CancellationCharges;
    var refundMode = data.RefundMode;

    if (refundAmount || cancellationCharges || refundMode) {
      html += '<div class="hc-refund-box"><div class="hc-refund-title">Refund Information</div>';
      if (refundAmount) html += '<div class="hc-refund-amount">₹' + refundAmount + '</div>';
      if (cancellationCharges) html += '<div class="hc-refund-row"><span class="hc-refund-label">Cancellation Charges</span><span class="hc-refund-value">₹' + cancellationCharges + '</span></div>';
      if (refundMode) html += '<div class="hc-refund-row"><span class="hc-refund-label">Refund Mode</span><span class="hc-refund-value">' + refundMode + '</span></div>';
      html += '</div>';
    }

    html += '</div>';
    html += '<div class="hc-footer-note">You will receive a confirmation email shortly. Refund will be processed as per airline cancellation policy.</div>';
    resultContainer.innerHTML = html;
  }

  /* Back navigation */
  var backBtns = container.querySelectorAll('.hc-back-btn');
  for (var i = 0; i < backBtns.length; i++) {
    backBtns[i].addEventListener('click', function() { showStep(this.getAttribute('data-back-to')); });
  }

})();
</script>
"""


def render_flight_booking_details(
    booking_details: Dict[str, Any],
    booking_id: str = "",
    email: str = "",
    bid: str = "",
    api_base_url: str = "",
    is_otp_send: bool = False,
) -> str:
    """
    Render flight booking details as interactive HTML with cancellation flow.

    Args:
        booking_details: Flight booking details from API
        booking_id: Booking ID
        email: User email
        bid: Encrypted booking ID from guest login
        api_base_url: Base URL of the chatbot API
        is_otp_send: Whether a login OTP was auto-sent

    Returns:
        HTML string with rendered interactive flight booking details
    """
    flight_segments = booking_details.get("flight_segments", [])
    outbound_passengers = booking_details.get("outbound_passengers", [])
    inbound_passengers = booking_details.get("inbound_passengers", [])
    price_info = booking_details.get("price_info", {})
    pnr_info = booking_details.get("pnr_info", [])
    cancellation_policy = booking_details.get("cancellation_policy", [])

    # Extract possible modes from passengers (all should have same modes)
    possible_mode_str = None
    for pax in outbound_passengers + inbound_passengers:
        if pax.get("possible_mode"):
            possible_mode_str = pax["possible_mode"]
            break

    # Parse possible modes (e.g., "1-2-3-4" -> ["1", "2", "3", "4"])
    possible_modes = []
    if possible_mode_str:
        possible_modes = [m.strip() for m in str(possible_mode_str).split("-") if m.strip()]

    if not flight_segments and not outbound_passengers:
        return """
        <div class="flight-cancel-carousel">
          <main style="max-width: 700px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; color: #646d74; padding: 40px 20px;">
              <p style="font-size: 14px;">No flight details found in this booking.</p>
            </div>
          </main>
        </div>
        """

    # Build title and subtitle
    title = f"Flight Booking - {booking_id}" if booking_id else "Flight Booking Details"
    subtitle_parts = []
    if flight_segments:
        seg = flight_segments[0]
        if seg.get("airline_name"):
            subtitle_parts.append(f"{seg['airline_name']} {seg.get('flight_number', '')}")
        if seg.get("origin") and seg.get("destination"):
            subtitle_parts.append(f"{seg['origin']} → {seg['destination']}")
    total_pax = len(outbound_passengers) + len(inbound_passengers)
    subtitle_parts.append(f"{total_pax} passenger(s)")
    for pnr in pnr_info:
        if pnr.get("airline_pnr"):
            subtitle_parts.append(f"PNR: {pnr['airline_pnr']}")
            break
    subtitle = " • ".join(subtitle_parts)

    import uuid
    instance_id = str(uuid.uuid4())[:8]

    all_cancelled = booking_details.get("all_cancelled", False)

    template = _jinja_env.from_string(FLIGHT_BOOKING_TEMPLATE)
    return template.render(
        title=title,
        subtitle=subtitle,
        flight_segments=flight_segments,
        outbound_passengers=outbound_passengers,
        inbound_passengers=inbound_passengers,
        price_info=price_info,
        pnr_info=pnr_info,
        cancellation_policy=cancellation_policy,
        instance_id=instance_id,
        bid=bid,
        booking_id=booking_id,
        email=email,
        api_base_url=api_base_url,
        is_otp_send=is_otp_send,
        all_cancelled=all_cancelled,
        possible_modes=possible_modes,
        mode_labels=FLIGHT_CANCELLATION_MODE_LABELS,
    )
