"""Hotel Cancellation Renderer - Interactive multi-step HTML/JS flow"""
from typing import Dict, Any
from jinja2 import Environment, BaseLoader, select_autoescape

_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)

# =====================================================================
# HOTEL CANCELLATION FLOW TEMPLATE
# =====================================================================
CANCELLATION_FLOW_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

.emt-cancel-flow {
  font-family: poppins, sans-serif;
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  color: #202020;
}
.emt-cancel-flow * {
  box-sizing: border-box;
  font-family: inherit;
  margin: 0;
}

/* Step indicator */
.emt-cancel-steps {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
}
.emt-cancel-step-dot {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: #e0e0e0;
  transition: background 0.3s;
}
.emt-cancel-step-dot.active { background: #ef6614; }
.emt-cancel-step-dot.done { background: #00a664; }

/* Panels */
.emt-cancel-panel { display: none; }
.emt-cancel-panel.active { display: block; }

/* Form elements */
.emt-cancel-label {
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
  display: block;
  color: #202020;
}
.emt-cancel-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 12px;
  outline: none;
  transition: border 0.2s;
}
.emt-cancel-input:focus { border-color: #ef6614; }

.emt-cancel-select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 12px;
  background: #fff;
  outline: none;
}
.emt-cancel-select:focus { border-color: #ef6614; }

.emt-cancel-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 12px;
  outline: none;
  resize: vertical;
  min-height: 60px;
}
.emt-cancel-textarea:focus { border-color: #ef6614; }

.emt-cancel-btn {
  background: #ef6614;
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 40px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
  transition: background 0.2s;
}
.emt-cancel-btn:hover { background: #e75806; }
.emt-cancel-btn:disabled { background: #ccc; cursor: not-allowed; }

/* Room cards */
.emt-cancel-room-card {
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}
.emt-cancel-room-card.selected {
  border-color: #ef6614;
  background: #fff8f0;
}
.emt-cancel-room-card:hover { border-color: #ef6614; }

.emt-cancel-room-title {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
}
.emt-cancel-room-sub {
  font-size: 13px;
  color: #646d74;
}
.emt-cancel-room-policy {
  font-size: 12px;
  color: #868686;
  margin-top: 4px;
}
.emt-cancel-room-amount {
  font-size: 14px;
  font-weight: 600;
  margin-top: 4px;
}

/* Booking info header */
.emt-cancel-booking-info {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #646d74;
  line-height: 1.6;
}
.emt-cancel-booking-info strong {
  color: #202020;
}

/* Messages */
.emt-cancel-error {
  color: #d32f2f;
  font-size: 13px;
  margin: 8px 0;
  min-height: 18px;
}
.emt-cancel-success {
  color: #00a664;
  font-size: 13px;
  margin: 8px 0;
}

/* Result panel */
.emt-cancel-result {
  text-align: center;
  padding: 40px 20px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
}
.emt-cancel-result.success {
  border-color: #00a664;
  background: #f0faf5;
}
.emt-cancel-result.failure {
  border-color: #d32f2f;
  background: #fef0f0;
}
.emt-cancel-result-icon {
  font-size: 48px;
  margin-bottom: 12px;
}
.emt-cancel-result h3 {
  margin-bottom: 8px;
  font-size: 18px;
}
.emt-cancel-result p {
  color: #646d74;
  font-size: 14px;
}
.emt-cancel-refund-box {
  margin-top: 16px;
  padding: 12px;
  background: rgba(0,166,100,0.08);
  border-radius: 8px;
  font-size: 13px;
  text-align: left;
}

/* Heading */
.emt-cancel-heading {
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 600;
}
.emt-cancel-subtext {
  font-size: 13px;
  color: #646d74;
  margin-bottom: 16px;
}
</style>

<div class="emt-cancel-flow" id="emtCancelFlow" data-api-base="{{ api_base_url }}">
  <!-- Step Indicator -->
  <div class="emt-cancel-steps">
    <div class="emt-cancel-step-dot active" data-step="1"></div>
    <div class="emt-cancel-step-dot" data-step="2"></div>
    <div class="emt-cancel-step-dot" data-step="3"></div>
    <div class="emt-cancel-step-dot" data-step="4"></div>
  </div>

  <!-- Panel 1: Login -->
  <div class="emt-cancel-panel active" id="panelLogin">
    <h3 class="emt-cancel-heading">Cancel Hotel Booking</h3>
    <p class="emt-cancel-subtext">Enter your booking details to begin cancellation.</p>
    <label class="emt-cancel-label">Booking ID</label>
    <input class="emt-cancel-input" id="inputBookingId"
           placeholder="e.g. EMT1624718" value="{{ booking_id }}">
    <label class="emt-cancel-label">Email Address</label>
    <input class="emt-cancel-input" id="inputEmail" type="email"
           placeholder="Email used during booking" value="{{ email }}">
    <div class="emt-cancel-error" id="loginError"></div>
    <button class="emt-cancel-btn" id="btnLogin">Verify Booking</button>
  </div>

  <!-- Panel 2: Booking Details + Room Selection -->
  <div class="emt-cancel-panel" id="panelDetails">
    <h3 class="emt-cancel-heading">Select Room to Cancel</h3>
    <div id="bookingInfoBox" class="emt-cancel-booking-info"></div>
    <div id="roomsList"></div>
    <label class="emt-cancel-label">Reason for cancellation</label>
    <select class="emt-cancel-select" id="selectReason">
      <option value="Change of plans">Change of plans</option>
      <option value="Found better deal">Found a better deal</option>
      <option value="Trip cancelled">Trip cancelled</option>
      <option value="Wrong dates">Wrong dates booked</option>
      <option value="Personal reason">Personal reason</option>
      <option value="Other">Other</option>
    </select>
    <label class="emt-cancel-label">Remarks (optional)</label>
    <textarea class="emt-cancel-textarea" id="inputRemark"
              placeholder="Any additional remarks..."></textarea>
    <div class="emt-cancel-error" id="detailsError"></div>
    <button class="emt-cancel-btn" id="btnSendOtp">Send Cancellation OTP</button>
  </div>

  <!-- Panel 3: OTP Verification -->
  <div class="emt-cancel-panel" id="panelOtp">
    <h3 class="emt-cancel-heading">Enter OTP</h3>
    <p class="emt-cancel-subtext">
      An OTP has been sent to your registered contact. Enter it below to confirm cancellation.
    </p>
    <input class="emt-cancel-input" id="inputOtp" placeholder="Enter OTP" maxlength="6">
    <div class="emt-cancel-error" id="otpError"></div>
    <button class="emt-cancel-btn" id="btnConfirmCancel">Confirm Cancellation</button>
  </div>

  <!-- Panel 4: Result -->
  <div class="emt-cancel-panel" id="panelResult">
    <div class="emt-cancel-result" id="resultBox"></div>
  </div>
</div>

<script>
(function() {
  var flow = document.getElementById('emtCancelFlow');
  var apiBase = flow.dataset.apiBase || '';

  
  var state = {
    bookingId: '',
    email: '',
    bid: null,
    rooms: [],
    paymentUrl: '',
    selectedRooms: [],
  };


  var panels = {
    login: document.getElementById('panelLogin'),
    details: document.getElementById('panelDetails'),
    otp: document.getElementById('panelOtp'),
    result: document.getElementById('panelResult'),
  };
  var stepDots = flow.querySelectorAll('.emt-cancel-step-dot');

  function showPanel(name, stepNum) {
    Object.keys(panels).forEach(function(k) {
      panels[k].classList.remove('active');
    });
    panels[name].classList.add('active');
    for (var i = 0; i < stepDots.length; i++) {
      stepDots[i].classList.remove('active', 'done');
      if (i + 1 < stepNum) stepDots[i].classList.add('done');
      else if (i + 1 === stepNum) stepDots[i].classList.add('active');
    }
  }

  function setLoading(btn, loading) {
    btn.disabled = loading;
    btn.textContent = loading ? 'Please wait...' : btn.getAttribute('data-orig');
  }

  
  var buttons = flow.querySelectorAll('.emt-cancel-btn');
  for (var b = 0; b < buttons.length; b++) {
    buttons[b].setAttribute('data-orig', buttons[b].textContent);
  }

  function apiCall(endpoint, payload) {
    return fetch(apiBase + endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(function(res) { return res.json(); });
  }

  document.getElementById('btnLogin').addEventListener('click', function() {
    var btn = this;
    var bookingId = document.getElementById('inputBookingId').value.trim();
    var email = document.getElementById('inputEmail').value.trim();
    var errEl = document.getElementById('loginError');
    errEl.textContent = '';

    if (!bookingId || !email) {
      errEl.textContent = 'Please enter both booking ID and email.';
      return;
    }

    setLoading(btn, true);

    apiCall('/hotel-cancellation/guest-login', {
      booking_id: bookingId, email: email
    }).then(function(data) {
      if (!data.success) {
        errEl.textContent = data.message || 'Login failed. Check your details.';
        setLoading(btn, false);
        return;
      }

      state.bid = data.ids.bid;
      state.bookingId = bookingId;
      state.email = email;

      
      return apiCall('/hotel-cancellation/booking-details', {
        bid: state.bid
      });
    }).then(function(details) {
      if (!details) return;
      setLoading(btn, false);

      if (!details.success) {
        document.getElementById('loginError').textContent =
          'Login succeeded but failed to load booking details.';
        return;
      }

      state.rooms = details.rooms || [];
      state.paymentUrl = details.payment_url || '';
      renderBookingInfo(details);
      renderRooms();
      showPanel('details', 2);
    }).catch(function() {
      document.getElementById('loginError').textContent = 'Network error. Please try again.';
      setLoading(btn, false);
    });
  });

  function renderBookingInfo(details) {
    var infoBox = document.getElementById('bookingInfoBox');
    if (state.rooms.length > 0) {
      var r = state.rooms[0];
      var html = '';
      if (r.hotel_name) html += '<div><strong>Hotel:</strong> ' + r.hotel_name + '</div>';
      if (r.check_in) html += '<div><strong>Check-in:</strong> ' + r.check_in + '</div>';
      if (r.check_out) html += '<div><strong>Check-out:</strong> ' + r.check_out + '</div>';
      html += '<div><strong>Rooms:</strong> ' + state.rooms.length + '</div>';
      infoBox.innerHTML = html;
    } else {
      infoBox.innerHTML = '<div>No booking details available.</div>';
    }
  }

  function renderRooms() {
    var container = document.getElementById('roomsList');
    container.innerHTML = '';
    state.selectedRooms = [];

    state.rooms.forEach(function(room) {
      var card = document.createElement('div');
      card.className = 'emt-cancel-room-card';
      card.setAttribute('data-room-id', room.room_id || '');
      card.setAttribute('data-txn-id', room.transaction_id || '');
      card.setAttribute('data-pay-at-hotel', room.is_pay_at_hotel ? 'true' : 'false');

      var titleText = (room.room_type || 'Room') +
        (room.room_no ? ' - Room ' + room.room_no : '');
      var html = '<div class="emt-cancel-room-title">' + titleText + '</div>';

      if (room.guest_name) {
        html += '<div class="emt-cancel-room-sub">Guest: ' + room.guest_name + '</div>';
      }
      if (room.cancellation_policy) {
        html += '<div class="emt-cancel-room-policy">' + room.cancellation_policy + '</div>';
      }
      if (room.amount) {
        html += '<div class="emt-cancel-room-amount">Amount: &#8377;' + room.amount + '</div>';
      }

      card.innerHTML = html;
      card.addEventListener('click', function() {
        this.classList.toggle('selected');
        var roomId = this.getAttribute('data-room-id');
        var idx = state.selectedRooms.indexOf(roomId);
        if (idx === -1) {
          state.selectedRooms.push(roomId);
        } else {
          state.selectedRooms.splice(idx, 1);
        }
      });
      container.appendChild(card);
    });

    
    if (state.rooms.length === 1) {
      var singleCard = container.querySelector('.emt-cancel-room-card');
      if (singleCard) singleCard.click();
    }
  }

  
  document.getElementById('btnSendOtp').addEventListener('click', function() {
    var btn = this;
    var errEl = document.getElementById('detailsError');
    errEl.textContent = '';

    if (state.selectedRooms.length === 0) {
      errEl.textContent = 'Please select at least one room to cancel.';
      return;
    }

    var reason = document.getElementById('selectReason').value;
    if (!reason) {
      errEl.textContent = 'Please select a cancellation reason.';
      return;
    }

    setLoading(btn, true);

    apiCall('/hotel-cancellation/send-otp', {
      booking_id: state.bookingId,
      email: state.email
    }).then(function(data) {
      setLoading(btn, false);
      if (!data.success) {
        errEl.textContent = data.message || 'Failed to send OTP.';
        return;
      }
      showPanel('otp', 3);
    }).catch(function() {
      errEl.textContent = 'Network error. Please try again.';
      setLoading(btn, false);
    });
  });

  
  document.getElementById('btnConfirmCancel').addEventListener('click', function() {
    var btn = this;
    var otp = document.getElementById('inputOtp').value.trim();
    var errEl = document.getElementById('otpError');
    errEl.textContent = '';

    if (!otp) {
      errEl.textContent = 'Please enter the OTP.';
      return;
    }

    setLoading(btn, true);

    var reason = document.getElementById('selectReason').value;
    var remark = document.getElementById('inputRemark').value.trim();

   
    var selectedRoom = null;
    for (var i = 0; i < state.rooms.length; i++) {
      if (state.selectedRooms.indexOf(state.rooms[i].room_id) !== -1) {
        selectedRoom = state.rooms[i];
        break;
      }
    }

    var roomIdStr = state.selectedRooms.join(',');
    var txnId = selectedRoom ? (selectedRoom.transaction_id || '') : '';
    var isPayAtHotel = selectedRoom ? !!selectedRoom.is_pay_at_hotel : false;

    apiCall('/hotel-cancellation/request-cancellation', {
      booking_id: state.bookingId,
      email: state.email,
      otp: otp,
      room_id: roomIdStr,
      transaction_id: txnId,
      is_pay_at_hotel: isPayAtHotel,
      payment_url: state.paymentUrl,
      reason: reason,
      remark: remark,
    }).then(function(data) {
      setLoading(btn, false);

      var resultBox = document.getElementById('resultBox');
      if (data.success) {
        resultBox.className = 'emt-cancel-result success';
        var html = '<div class="emt-cancel-result-icon">&#10003;</div>';
        html += '<h3 style="color:#00a664">Cancellation Successful</h3>';
        html += '<p>' + (data.message || 'Your booking has been cancelled.') + '</p>';
        if (data.refund_info) {
          html += '<div class="emt-cancel-refund-box">';
          if (data.refund_info.refund_amount)
            html += '<div>Refund: <strong>&#8377;' + data.refund_info.refund_amount + '</strong></div>';
          if (data.refund_info.cancellation_charges)
            html += '<div>Charges: <strong>&#8377;' + data.refund_info.cancellation_charges + '</strong></div>';
          if (data.refund_info.refund_mode)
            html += '<div>Refund Mode: <strong>' + data.refund_info.refund_mode + '</strong></div>';
          html += '</div>';
        }
        resultBox.innerHTML = html;
      } else {
        resultBox.className = 'emt-cancel-result failure';
        resultBox.innerHTML =
          '<div class="emt-cancel-result-icon">&#10007;</div>' +
          '<h3 style="color:#d32f2f">Cancellation Failed</h3>' +
          '<p>' + (data.message || 'Please try again or contact support.') + '</p>';
      }
      showPanel('result', 4);
    }).catch(function() {
      errEl.textContent = 'Network error. Please try again.';
      setLoading(btn, false);
    });
  });
})();
</script>
"""


def render_cancellation_flow(
    booking_id: str = "",
    email: str = "",
    api_base_url: str = "/api",
) -> str:
    """
    Render the complete interactive cancellation flow HTML.

    Args:
        booking_id: Pre-fill booking ID (optional)
        email: Pre-fill email (optional)
        api_base_url: Base URL for API proxy endpoints

    Returns:
        Complete HTML string with embedded CSS and JavaScript
    """
    template = _jinja_env.from_string(CANCELLATION_FLOW_TEMPLATE)
    return template.render(
        booking_id=booking_id,
        email=email,
        api_base_url=api_base_url,
    )
