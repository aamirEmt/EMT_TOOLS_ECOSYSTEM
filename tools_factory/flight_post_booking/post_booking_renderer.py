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
{{ styles | safe }}
</style>

<div class="booking-details-carousel round-trip-selector" data-instance-id="{{ instance_id }}">
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

    <div class="hc-step" data-step="download-ticket">
      <div class="hc-verify-card">
        <div class="hc-verify-icon hc-success-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <div class="hc-verify-title">Verified!</div>
        <p class="hc-verify-desc">Your identity has been confirmed. Click the button below to download your ticket.</p>
        <div class="hc-error-msg hc-step-error"></div>
        <button type="button" class="hc-submit-btn hc-download-ticket-btn">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" style="vertical-align:middle;margin-right:6px;">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"/>
          </svg>
          Download Ticket
        </button>
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
  var VERIFY_OTP_URL       = API_BASE + '/api/post-booking/verify-otp';
  var RESEND_OTP_URL       = API_BASE + '/api/post-booking/resend-otp';
  var DOWNLOAD_TICKET_URL  = API_BASE + '/api/post-booking/download-ticket';
  var BOOKING_ID = '{{ booking_id }}';
  var EMAIL      = '{{ email }}';
  var DOWNLOAD   = {{ 'true' if download else 'false' }};

  /* ---- state set after verification ---- */
  var _bid             = null;
  var _transactionType = null;

  /* ---- DOM references (scoped to container) ---- */
  var loadingOverlay = container.querySelector('.hc-loading');
  var globalErrorBanner = container.querySelector('main > .hc-error-msg');

  /* ---- Utility functions ---- */
  function hideAllErrors() {
    var errs = container.querySelectorAll('.hc-error-msg');
    for (var i = 0; i < errs.length; i++) errs[i].style.display = 'none';
  }

  function showError(message) {
    hideAllErrors();
    var activeStep = container.querySelector('.hc-step.active');
    var inlineErr = activeStep ? activeStep.querySelector('.hc-step-error') : null;
    var target = inlineErr || globalErrorBanner;
    target.textContent = message;
    target.style.display = 'block';
  }

  function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
  }

  function switchStep(stepName) {
    var steps = container.querySelectorAll('.hc-step');
    for (var i = 0; i < steps.length; i++) {
      steps[i].classList.remove('active');
    }
    var next = container.querySelector('[data-step="' + stepName + '"]');
    if (next) next.classList.add('active');
  }

  /* ---- API helpers ---- */
  function downloadTicket() {
    showLoading(true);
    hideAllErrors();
    return fetch(DOWNLOAD_TICKET_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bid: _bid, transaction_type: _transactionType })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      var url = null;
      if (data.structured_content) {
        url = data.structured_content.download_url || data.structured_content.redirect_url;
      } else if (data.download_url) {
        url = data.download_url;
      } else if (data.url) {
        url = data.url;
      }
      if (url) {
        window.open(url, '_blank');
      } else {
        showError(data.response_text || data.message || 'Could not get download link. Please try again.');
      }
    })
    .catch(function(err) {
      showLoading(false);
      var msg = (err && err.message && err.message.indexOf('Failed to fetch') !== -1)
        ? 'Unable to reach the server. Please try again.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
    });
  }

  function verifyOtp(otp) {
    showLoading(true);
    hideAllErrors();
    return fetch(VERIFY_OTP_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ booking_id: BOOKING_ID, email: EMAIL, otp: otp, download: DOWNLOAD })
    })
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      showLoading(false);
      /* Handle multiple response formats:
         - ToolResponseFormat: { is_error: false, structured_content: { redirect_url, ... } }
         - Direct API:         { isVerify: "true", Message: "..." }
         - Wrapped:            { structured_content: { success: true }, response_text: "..." }
         - Status-based:       { isStatus: true, Msg: "..." } */
      var isVerified = false;
      var msg = '';

      if (data.is_error !== undefined) {
        isVerified = !data.is_error;
        msg = data.response_text || '';
      } else if (data.structured_content) {
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
        ? 'Unable to reach the server. This may be a CORS issue in local testing — it should work in production.'
        : 'Network error. Please check your connection and try again.';
      showError(msg);
      return null;
    });
  }

  /* ---- Step 0: Verify OTP button ---- */
  var verifyBtn = container.querySelector('.hc-verify-otp-btn');
  var otpInput  = container.querySelector('.hc-login-otp-input');
  if (verifyBtn) {
    verifyBtn.addEventListener('click', function() {
      var otp = otpInput ? otpInput.value.trim() : '';
      if (!otp || otp.length < 4) {
        showError('Please enter a valid OTP.');
        return;
      }
      verifyBtn.disabled = true;
      verifyOtp(otp).then(function(result) {
        if (result) {
          var sc = result.structured_content || {};
          _bid             = sc.bid || null;
          _transactionType = sc.transaction_type || null;
          window.dispatchEvent(new CustomEvent('hc:post-booking:verified', { detail: result }));
          switchStep('download-ticket');
        } else {
          verifyBtn.disabled = false;
        }
      });
    });
  }

  /* ---- Download Ticket button ---- */
  var downloadBtn = container.querySelector('.hc-download-ticket-btn');
  if (downloadBtn) {
    downloadBtn.addEventListener('click', function() {
      if (!_bid) {
        showError('Booking ID not found. Please restart the verification.');
        return;
      }
      downloadBtn.disabled = true;
      downloadBtn.textContent = 'Downloading...';
      downloadTicket().then(function() {
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" style="vertical-align:middle;margin-right:6px;"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"/></svg>Download Ticket';
      });
    });
  }

  /* ---- Resend OTP button ---- */
  var resendLoginOtpBtn = container.querySelector('.hc-resend-login-otp');
  if (resendLoginOtpBtn) {
    resendLoginOtpBtn.addEventListener('click', function() {
      var btn = this;
      btn.disabled = true;
      btn.textContent = 'Sending...';
      fetch(RESEND_OTP_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ booking_id: BOOKING_ID, email: EMAIL, download: DOWNLOAD })
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
.booking-details-carousel .hc-otp-field { margin-bottom: 16px; }
.booking-details-carousel .hc-otp-field .hc-login-otp-input { width: 100%; max-width: 240px; padding: 10px 16px; border: 2px solid #e0e0e0; border-radius: 12px; font-size: 14px; font-weight: 600; text-align: center; letter-spacing: 4px; font-family: inter, sans-serif; outline: none; transition: border-color 0.2s, box-shadow 0.2s; background: #fff; color: #202020; }
.booking-details-carousel .hc-otp-field .hc-login-otp-input:focus { border-color:#ef6614; box-shadow:0 0 0 3px rgba(239,102,20,0.1); }
.booking-details-carousel .hc-otp-field .hc-login-otp-input::placeholder { font-size: 14px; letter-spacing: 0; font-weight: 400; color: #bbb; }
.booking-details-carousel .hc-verify-card .hc-submit-btn { width: 80%; max-width: 240px; padding: 8px 7px; }
.booking-details-carousel .hc-submit-btn { width: 80%; max-width: 240px; margin: 6px auto 0; padding: 10px 12px; border:none; border-radius:10px; background: linear-gradient(135deg, #ef6614 0%, #f58434 100%); color:#fff; font-weight:700; cursor:pointer; transition: opacity 0.2s; display:block; }
.booking-details-carousel .hc-submit-btn:hover { opacity: 0.9; }
.booking-details-carousel .hc-submit-btn[disabled] { opacity:0.6; cursor:not-allowed; }
.booking-details-carousel .hc-verify-footer { font-size: 11px; color: #999; margin-top: 16px; line-height: 1.4; }
.booking-details-carousel .hc-resend-otp-btn { background: none; border: none; color: #2196f3; font-size: 12px; font-weight: 600; cursor: pointer; padding: 0; margin-top: 8px; text-decoration: none; display: inline-block; }
.booking-details-carousel .hc-resend-otp-btn:hover { text-decoration: underline; color: #1565c0; }
.booking-details-carousel .hc-resend-otp-btn:disabled { color: #999; cursor: not-allowed; text-decoration: none; }
.booking-details-carousel .hc-error-msg { display:none; color:#d32f2f; padding:4px 14px; border-radius:8px; font-size:12px; margin-bottom:4px; margin-top:-4px; }
.booking-details-carousel .hc-step-error { text-align:center; }
.booking-details-carousel .hc-step { display: none; }
.booking-details-carousel .hc-step.active { display: block; }
.booking-details-carousel .hc-success-icon { background: linear-gradient(135deg, #2e7d32 0%, #43a047 100%); box-shadow: 0 4px 16px rgba(46, 125, 50, 0.25); }
"""


def render_otp_verification_view(
    booking_id: str,
    email: str,
    is_otp_send: bool,
    download: bool = False,
    api_base_url: str = "",
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
        api_base_url=api_base_url,
        styles=OTP_STYLES,
    )
