"""Render HTML for the post-booking OTP verification step."""
import uuid
from jinja2 import Environment, BaseLoader, select_autoescape

_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)

INTERACTIVE_BOOKING_TEMPLATE = r"""
{% if is_otp_send %}
<style>
{{ styles }}
</style>

<div class="booking-details-carousel" id="{{ instance_id }}" data-booking-id="{{ booking_id }}" data-email="{{ email }}" data-download="{{ download | lower }}" data-api-endpoint="{{ api_endpoint }}">
  <main>
    <div class="hc-loading"><div class="hc-spinner"></div></div>
    <div class="hc-error-msg"></div>

    <div class="bkhd">
      <div class="bkttl">Verify Your Identity</div>
      <div class="bksub">Enter the OTP sent to your registered email/phone</div>
    </div>

    <div class="hc-step active" data-step="verify-otp">
      <div class="hc-verify-card">
        <div class="hc-verify-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>
          </svg>
        </div>
        <div class="hc-verify-title">Enter OTP</div>
        <p class="hc-verify-desc">
          We've sent a One-Time Password to your registered email &amp; phone number.
        </p>
        <div class="hc-otp-field">
          <input type="text" class="hc-login-otp-input" maxlength="10" placeholder="Enter OTP" autocomplete="one-time-code" />
        </div>
        <div class="hc-error-msg hc-step-error"></div>
        <button type="button" class="hc-submit-btn hc-verify-otp-btn">Verify &amp; Continue</button>
        <p class="hc-verify-footer">
          Didn't receive the OTP?
          <button type="button" class="hc-resend-otp-btn hc-resend-login-otp">Resend OTP</button>
        </p>
      </div>
    </div>
  </main>
</div>

<script>
(function() {
  'use strict';
  var container = document.getElementById('{{ instance_id }}');
  if (!container || container.dataset.initialized) return;
  container.dataset.initialized = 'true';

  var bookingId = container.dataset.bookingId;
  var email = container.dataset.email;
  var download = container.dataset.download === 'true';
  var apiEndpoint = container.dataset.apiEndpoint || '/tools/flight_post_booking';

  var loadingOverlay = container.querySelector('.hc-loading');
  var errorBanner = container.querySelector('main > .hc-error-msg');
  var verifyBtn = container.querySelector('.hc-verify-otp-btn');
  var resendBtn = container.querySelector('.hc-resend-otp-btn');
  var otpInput = container.querySelector('.hc-login-otp-input');

  function showLoading(show) {
    if (loadingOverlay) loadingOverlay.style.display = show ? 'flex' : 'none';
  }

  function showError(message) {
    if (errorBanner) {
      errorBanner.textContent = message || '';
      errorBanner.style.display = message ? 'block' : 'none';
    }
    var stepErr = container.querySelector('.hc-step-error');
    if (stepErr) {
      stepErr.textContent = message || '';
      stepErr.style.display = message ? 'block' : 'none';
    }
  }

  async function callTool(payload) {
    const resp = await fetch(apiEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return resp.json();
  }

  async function handleResend() {
    if (!resendBtn) return;
    resendBtn.disabled = true;
    resendBtn.textContent = 'Sending...';
    showError('');
    try {
      const res = await callTool({ action: 'start', booking_id: bookingId, email, download });
      if (res.is_error) throw new Error(res.response_text || 'Resend failed');
      resendBtn.textContent = 'OTP Sent!';
      setTimeout(() => { resendBtn.textContent = 'Resend OTP'; resendBtn.disabled = false; }, 3500);
    } catch (err) {
      showError(err.message || 'Resend failed');
      resendBtn.textContent = 'Resend OTP';
      resendBtn.disabled = false;
    }
  }

  async function handleVerify() {
    if (!verifyBtn) return;
    verifyBtn.disabled = true;
    showError('');
    const otp = (otpInput && otpInput.value || '').trim();
    if (!otp || otp.length < 4) {
      showError('Please enter a valid OTP.');
      verifyBtn.disabled = false;
      return;
    }

    showLoading(true);
    try {
      const res = await callTool({ action: 'verify_otp', booking_id: bookingId, email, otp, download });
      showLoading(false);
      if (res.is_error) throw new Error(res.response_text || 'Invalid OTP');
      const event = new CustomEvent('hc:post-booking:verified', { detail: res });
      window.dispatchEvent(event);
      verifyBtn.textContent = 'Verified!';
    } catch (err) {
      showLoading(false);
      showError(err.message || 'Verification failed');
      verifyBtn.disabled = false;
    }
  }

  resendBtn && resendBtn.addEventListener('click', handleResend);
  verifyBtn && verifyBtn.addEventListener('click', handleVerify);
})();
</script>
{% endif %}
"""

# Minimal subset of styles extracted from provided interactive template (focused on OTP card)
OTP_STYLES = r"""
.booking-details-carousel { font-family: poppins, sans-serif; color: #202020; background: rgba(255, 255, 255, 0.92); position: relative; }
.booking-details-carousel * { font-family: inherit; box-sizing: border-box; margin: 0; }
.booking-details-carousel main { max-width: 520px; margin: 0 auto; padding: 20px 0 30px; position: relative; }
.booking-details-carousel .hc-loading { display:none; position:absolute; inset:0; background:rgba(255,255,255,0.85); align-items:center; justify-content:center; z-index:10; border-radius:12px; }
.booking-details-carousel .hc-spinner { width:36px; height:36px; border:3px solid #e0e0e0; border-top-color:#ef6614; border-radius:50%; animation: hcSpin .8s linear infinite; }
@keyframes hcSpin { to { transform: rotate(360deg); } }
.booking-details-carousel .bkttl { font-size: 18px; font-weight: 600; color: #202020; margin-bottom: 6px; }
.booking-details-carousel .bksub { font-size: 12px; color: #646d74; margin-bottom: 14px; }
.booking-details-carousel .hc-verify-card { background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%); border:1px solid #e0e0e0; border-radius:16px; padding:16px 18px; text-align:center; box-shadow:0 12px 34px rgba(0,0,0,0.06); }
.booking-details-carousel .hc-verify-icon { width:50px; height:50px; margin:0 auto 6px; background:linear-gradient(135deg, #ef6614 0%, #f58434 100%); border-radius:50%; display:flex; align-items:center; justify-content:center; color:#fff; box-shadow:0 4px 16px rgba(239, 102, 20, 0.25); }
.booking-details-carousel .hc-verify-title { font-size: 18px; font-weight: 700; margin-bottom: 6px; color:#202020; }
.booking-details-carousel .hc-verify-desc { font-size: 13px; color: #646d74; line-height:1.5; margin-bottom: 10px; }
.booking-details-carousel .hc-otp-field { margin-bottom: 12px; }
.booking-details-carousel .hc-login-otp-input { width: 100%; max-width: 240px; padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 12px; font-size: 15px; font-weight: 600; text-align: center; letter-spacing: 4px; font-family: inter, sans-serif; outline: none; transition: border-color 0.2s, box-shadow 0.2s; background: #fff; color: #202020; }
.booking-details-carousel .hc-login-otp-input:focus { border-color:#ef6614; box-shadow:0 0 0 3px rgba(239,102,20,0.1); }
.booking-details-carousel .hc-submit-btn { width: 80%; max-width: 240px; margin: 6px auto 0; padding: 10px 12px; border:none; border-radius:10px; background: linear-gradient(135deg, #ef6614 0%, #f58434 100%); color:#fff; font-weight:700; cursor:pointer; transition: opacity 0.2s; }
.booking-details-carousel .hc-submit-btn:hover { opacity: 0.9; }
.booking-details-carousel .hc-submit-btn[disabled] { opacity:0.6; cursor:not-allowed; }
.booking-details-carousel .hc-verify-footer { font-size: 12px; color: #999; margin-top: 10px; line-height: 1.4; }
.booking-details-carousel .hc-resend-otp-btn { background: none; border: none; color: #2196f3; font-size: 12px; font-weight: 700; cursor: pointer; padding: 0; text-decoration: none; }
.booking-details-carousel .hc-resend-otp-btn:hover { text-decoration: underline; color: #1565c0; }
.booking-details-carousel .hc-resend-otp-btn:disabled { color: #999; cursor: not-allowed; text-decoration: none; }
.booking-details-carousel .hc-error-msg { display:none; color:#d32f2f; padding:4px 8px; border-radius:8px; font-size:12px; margin:8px 0; }
.booking-details-carousel .hc-step-error { text-align:center; }
</style>
"""


def render_otp_verification_view(
    booking_id: str,
    email: str,
    is_otp_send: bool,
    download: bool = False,
    api_endpoint: str = "/tools/flight_post_booking",
) -> str:
    """Render the OTP verification card HTML."""
    instance_id = f"otp-{uuid.uuid4().hex}"
    template = _jinja_env.from_string(INTERACTIVE_BOOKING_TEMPLATE)
    return template.render(
        instance_id=instance_id,
        booking_id=booking_id,
        email=email,
        is_otp_send=is_otp_send,
        download=download,
        api_endpoint=api_endpoint,
        styles=OTP_STYLES,
    )
