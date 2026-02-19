"""Render HTML for the post-booking OTP verification step."""
from jinja2 import Environment, BaseLoader, select_autoescape

_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)

OTP_TEMPLATE = r"""
{% if is_otp_send %}
<div class="hc-post-booking" data-booking-id="{{ booking_id }}" data-email="{{ email }}" data-download="{{ download | lower }}">
  <style>
    .hc-post-booking { font-family: "Inter", system-ui, -apple-system, sans-serif; color:#1f2937; }
    .hc-step { display:block; }
    .hc-verify-card { background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:18px; box-shadow:0 10px 30px rgba(17,24,39,0.06); max-width:520px; }
    .hc-verify-icon { width:48px; height:48px; border-radius:12px; background:#eef2ff; display:grid; place-items:center; color:#4f46e5; margin-bottom:12px; }
    .hc-verify-title { font-size:18px; font-weight:700; margin-bottom:6px; }
    .hc-verify-desc { font-size:14px; color:#4b5563; margin-bottom:14px; line-height:1.4; }
    .hc-otp-field input { width:100%; padding:12px; font-size:16px; border:1px solid #d1d5db; border-radius:10px; outline:none; transition: border-color .2s, box-shadow .2s; }
    .hc-otp-field input:focus { border-color:#4f46e5; box-shadow:0 0 0 3px rgba(79,70,229,0.15); }
    .hc-submit-btn { width:100%; margin-top:12px; padding:12px; border:none; border-radius:10px; background:#4f46e5; color:#fff; font-weight:600; cursor:pointer; transition: transform .1s ease, box-shadow .2s; }
    .hc-submit-btn:active { transform: translateY(1px); }
    .hc-submit-btn[disabled] { opacity:0.6; cursor:not-allowed; }
    .hc-verify-footer { margin-top:10px; font-size:13px; color:#6b7280; }
    .hc-verify-footer button { background:none; border:none; color:#4f46e5; font-weight:600; cursor:pointer; }
    .hc-error-msg { color:#b91c1c; font-size:13px; min-height:16px; margin-top:8px; }
  </style>

  <div class="hc-step active" data-step="verify-otp">
    <div class="hc-verify-card">
      <div class="hc-verify-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>
        </svg>
      </div>
      <div class="hc-verify-title">Verify Your Identity</div>
      <p class="hc-verify-desc">
        We've sent a One-Time Password to your registered email & phone number. Enter it below to continue.
      </p>
      <div class="hc-otp-field">
        <input type="text" class="hc-login-otp-input" maxlength="10" placeholder="Enter OTP" autocomplete="one-time-code" />
      </div>
      <div class="hc-error-msg hc-step-error"></div>
      <button type="button" class="hc-submit-btn hc-verify-otp-btn">Verify & Continue</button>
      <p class="hc-verify-footer">Didn't receive the OTP? <button type="button" class="hc-resend-otp-btn hc-resend-login-otp">Resend OTP</button></p>
    </div>
  </div>
</div>

<script>
(function(){
  const root = document.currentScript?.previousElementSibling;
  if (!root) return;
  const bookingId = root.dataset.bookingId;
  const email = root.dataset.email;
  const download = root.dataset.download === "true";
  const apiEndpoint = root.dataset.apiEndpoint || "/tools/flight_post_booking";
  const otpInput = root.querySelector(".hc-login-otp-input");
  const verifyBtn = root.querySelector(".hc-verify-otp-btn");
  const resendBtn = root.querySelector(".hc-resend-otp-btn");
  const errorBox = root.querySelector(".hc-step-error");

  async function callApi(payload) {
    const resp = await fetch(apiEndpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return resp.json();
  }

  async function handleResend() {
    resendBtn.disabled = true;
    errorBox.textContent = "";
    try {
      const res = await callApi({ action: "start", booking_id: bookingId, email, download });
      if (res.is_error) throw new Error(res.response_text || "Resend failed");
      resendBtn.textContent = "OTP Sent";
      setTimeout(() => { resendBtn.textContent = "Resend OTP"; resendBtn.disabled = false; }, 4000);
    } catch (e) {
      errorBox.textContent = e.message || "Resend failed";
      resendBtn.disabled = false;
    }
  }

  async function handleVerify() {
    verifyBtn.disabled = true;
    errorBox.textContent = "";
    try {
      const otp = otpInput.value.trim();
      if (!otp) throw new Error("Please enter OTP");
      const res = await callApi({ action: "verify_otp", booking_id: bookingId, email, otp, download });
      if (res.is_error) throw new Error(res.response_text || "Invalid OTP");
      // Emit event so host app can proceed
      const event = new CustomEvent("hc:post-booking:verified", { detail: res });
      window.dispatchEvent(event);
    } catch (e) {
      errorBox.textContent = e.message || "Verification failed";
      verifyBtn.disabled = false;
    }
  }

  resendBtn?.addEventListener("click", handleResend);
  verifyBtn?.addEventListener("click", handleVerify);
})();
</script>
{% endif %}
"""


def render_otp_verification_view(
    booking_id: str,
    email: str,
    is_otp_send: bool,
    download: bool = False,
) -> str:
    """Render the OTP verification card HTML."""
    template = _jinja_env.from_string(OTP_TEMPLATE)
    return template.render(
        booking_id=booking_id,
        email=email,
        is_otp_send=is_otp_send,
        download=download,
    )

