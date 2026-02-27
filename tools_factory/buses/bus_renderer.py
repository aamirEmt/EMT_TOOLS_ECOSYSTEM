from typing import Dict, Any, List, Optional
from jinja2 import Environment, BaseLoader
import uuid

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
  gap: 16px;
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
  min-width: 270px;
  width: 270px;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.bus-carousel .buschdr {
  padding: 0 0 10px;
  display: flex;
  gap: 8px;
  align-items: flex-start;
  border-bottom: 1px solid #e0e0e0;
}

.bus-carousel .businfo {
  flex: 1;
  min-width: 0;
}

.bus-carousel .businfo-top {
  display: flex;
  align-items: center;
  gap: 6px;
}

.bus-carousel .oprtname {
  font-size: 13px;
  font-weight: 600;
  color: #202020;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: default;
}

.bus-carousel .bustype {
  font-size: 10px;
  color: #868686;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: default;
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
  font-size: 16px;
  font-weight: 700;
  color: #202020;
}

.bus-carousel .seatsleft {
  font-size: 10px;
  color: #d32f2f;
  font-weight: 500;
  margin-top: 2px;
}

.bus-carousel .rtnvlu {
  background: #00a664;
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 10px;
  white-space: nowrap;
}

.bus-carousel .rtnvlu.low {
  background: #ff9800;
}

.bus-carousel .rtnvlu.poor {
  background: #f44336;
}

.bus-carousel .busbdy {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.bus-carousel .bustme {
  font-size: 15px;
  font-weight: 600;
  color: #202020;
}

.bus-carousel .jrny {
  text-align: center;
}

.bus-carousel .jrnttl {
  font-size: 10px;
  color: #868686;
}

.bus-carousel .j-br {
  width: 50px;
  border-bottom: 1px solid #9e9da1;
  position: relative;
  margin: 4px 0;
}

.bus-carousel .pointsrow {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.bus-carousel .pointbox {
  flex: 1;
  min-width: 0;
  position: relative;
}

.bus-carousel .pointlbl {
  font-size: 9px;
  color: #868686;
  text-transform: uppercase;
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.bus-carousel .pointlbl .dropdown-arrow {
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid #868686;
  transition: transform 0.2s ease;
}

.bus-carousel .pointbox.open .pointlbl .dropdown-arrow {
  transform: rotate(180deg);
}

.bus-carousel .pointval {
  font-size: 10px;
  color: #4b4b4b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: default;
}

.bus-carousel .points-dropdown {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 100;
  max-height: 150px;
  overflow-y: auto;
  margin-top: 4px;
}

.bus-carousel .pointbox.open .points-dropdown {
  display: block;
}

.bus-carousel .points-dropdown-item {
  padding: 8px 10px;
  font-size: 10px;
  color: #4b4b4b;
  border-bottom: 1px solid #f0f0f0;
}

.bus-carousel .points-dropdown-item:last-child {
  border-bottom: none;
}

.bus-carousel .points-dropdown-item .point-name {
  font-weight: 500;
}

.bus-carousel .points-dropdown-item .point-time {
  color: #868686;
  font-size: 9px;
  margin-top: 2px;
}

.bus-carousel .details-section {
  padding: 8px 0;
}

.bus-carousel .view-details-btn {
  width: 100%;
  padding: 8px 12px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  color: #4b4b4b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.bus-carousel .view-details-btn:hover:not(.disabled) {
  background: #e8e8e8;
  border-color: #ccc;
}

.bus-carousel .view-details-btn.disabled {
  color: #bdbdbd;
  cursor: not-allowed;
  background: #fafafa;
}

.bus-carousel .view-details-btn .details-arrow {
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid currentColor;
  transition: transform 0.2s ease;
}

.bus-carousel .details-section.open .view-details-btn .details-arrow {
  transform: rotate(180deg);
}

.bus-carousel .details-content {
  display: none;
  padding-top: 10px;
}

.bus-carousel .details-section.open .details-content {
  display: block;
}

.bus-carousel .busamnts {
  list-style: none;
  margin: 0;
  padding: 0;
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
  margin-top: 8px;
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
  min-width: 270px;
  width: 270px;
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

.bus-carousel .view-all-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #2093ef;
}

.bus-carousel .view-all-card::before,
.bus-carousel .view-all-card::after {
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

.bus-carousel .view-all-card::before {
  right: -3px;
  height: 98%;
  top: 1%;
  opacity: 0.7;
}

.bus-carousel .view-all-card::after {
  right: -6px;
  height: 96%;
  top: 2%;
  opacity: 0.5;
}

.bus-carousel .view-all-card-icon {
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

.bus-carousel .view-all-card-icon svg {
  width: 28px;
  height: 28px;
  color: #fff;
}

.bus-carousel .view-all-card-title {
  font-size: 18px;
  font-weight: 700;
  color: #202020;
  margin-bottom: 8px;
  text-align: center;
}

.bus-carousel .view-all-card-subtitle {
  font-size: 13px;
  color: #646d74;
  text-align: center;
  font-weight: 500;
  line-height: 1.4;
}

/* Seat Selection Modal Styles */
.bus-carousel .seat-modal-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1000;
  justify-content: center;
  align-items: center;
}

.bus-carousel .seat-modal-overlay.active {
  display: flex;
}

.bus-carousel .seat-modal {
  background: #fff;
  border-radius: 12px;
  max-width: 420px;
  width: 95%;
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  font-size: 11px;
}

.bus-carousel .seat-modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;
}

.bus-carousel .seat-modal-title {
  font-size: 16px;
  font-weight: 600;
  color: #202020;
}

.bus-carousel .seat-modal-subtitle {
  font-size: 12px;
  color: #868686;
  margin-top: 2px;
}

.bus-carousel .seat-modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #e0e0e0;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #666;
  transition: all 0.2s;
}

.bus-carousel .seat-modal-close:hover {
  background: #d0d0d0;
  color: #333;
}

.bus-carousel .seat-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bus-carousel .seat-layout-section {
  flex: 1;
  min-width: 0;
}

.bus-carousel .seat-legend {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.bus-carousel .legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 9px;
  color: #666;
}

.bus-carousel .legend-box {
  width: 14px;
  height: 14px;
  border-radius: 3px;
  border: 1px solid transparent;
}

.bus-carousel .legend-box.available {
  background: #e8f5e9;
  border-color: #4caf50;
}

.bus-carousel .legend-box.selected {
  background: #fff3e0;
  border-color: #ef6614;
}

.bus-carousel .legend-box.booked {
  background: #eeeeee;
  border-color: #9e9e9e;
}

.bus-carousel .legend-box.ladies {
  background: #fce4ec;
  border-color: #e91e63;
}

.bus-carousel .seat-decks {
  display: flex;
  gap: 20px;
}

.bus-carousel .seat-deck {
  flex: 1;
  background: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
}

.bus-carousel .deck-title {
  font-size: 12px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 12px;
  text-align: center;
  padding: 6px;
  background: #f0f0f0;
  border-radius: 4px;
}

.bus-carousel .seat-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}

.bus-carousel .seat-row {
  display: flex;
  gap: 4px;
}

.bus-carousel .seat {
  width: 26px;
  height: 26px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 7px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s;
  flex-direction: column;
  padding: 1px;
}

.bus-carousel .seat.sleeper {
  width: 52px;
}

.bus-carousel .seat.available {
  background: #e8f5e9;
  color: #2e7d32;
  border-color: #4caf50;
}

.bus-carousel .seat.available:hover {
  background: #c8e6c9;
  transform: scale(1.05);
}

.bus-carousel .seat.selected {
  background: #fff3e0;
  color: #e65100;
  border-color: #ef6614;
  box-shadow: 0 2px 8px rgba(239, 102, 20, 0.3);
}

.bus-carousel .seat.booked {
  background: #eeeeee;
  color: #9e9e9e;
  cursor: not-allowed;
}

.bus-carousel .seat.ladies {
  background: #fce4ec;
  color: #c2185b;
  border-color: #e91e63;
}

.bus-carousel .seat.empty {
  visibility: hidden;
}

.bus-carousel .seat-aisle {
  width: 16px;
}

.bus-carousel .points-section {
  width: 100%;
  flex-shrink: 0;
  border-top: 1px solid #e0e0e0;
  padding-top: 12px;
}

.bus-carousel .points-tabs {
  display: flex;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 12px;
}

.bus-carousel .points-tab {
  flex: 1;
  padding: 10px;
  text-align: center;
  font-size: 12px;
  font-weight: 500;
  color: #868686;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}

.bus-carousel .points-tab.active {
  color: #2093ef;
  border-bottom-color: #2093ef;
}

.bus-carousel .points-list {
  max-height: 300px;
  overflow-y: auto;
}

.bus-carousel .point-item {
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.bus-carousel .point-item:hover {
  background: #f5f5f5;
}

.bus-carousel .point-item.selected {
  border-color: #2093ef;
  background: #e3f2fd;
}

.bus-carousel .point-time {
  font-size: 13px;
  font-weight: 600;
  color: #202020;
}

.bus-carousel .point-name {
  font-size: 11px;
  color: #666;
  margin-top: 2px;
}

.bus-carousel .seat-modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
  background: #f8f9fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bus-carousel .selected-info {
  font-size: 12px;
  color: #666;
}

.bus-carousel .selected-info strong {
  color: #202020;
}

.bus-carousel .total-fare {
  font-size: 18px;
  font-weight: 700;
  color: #202020;
}

.bus-carousel .continue-btn {
  padding: 12px 32px;
  background: #ef6614;
  color: #fff;
  border: none;
  border-radius: 40px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.bus-carousel .continue-btn:hover:not(:disabled) {
  background: #e75806;
}

.bus-carousel .continue-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.bus-carousel .seat-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #868686;
}

/* Price filter buttons */
.bus-carousel .seat-price-filter {
  margin-bottom: 12px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}

.bus-carousel .price-btn {
  padding: 4px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: #fff;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.bus-carousel .price-btn.active {
  background: #ef6614;
  color: #fff;
  border-color: #ef6614;
}

.bus-carousel .price-btn:hover:not(.active) {
  background: #f5f5f5;
}

.bus-carousel .seat .seat-name {
  font-size: 7px;
  font-weight: 600;
  display: block;
  line-height: 1;
}

.bus-carousel .seat .seat-fare {
  font-size: 5px;
  opacity: 0.8;
  display: none;
}

.bus-carousel .seat-decks {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.bus-carousel .seat-deck {
  flex: 1;
  min-width: 200px;
  background: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
}

.bus-carousel .deck-title {
  font-size: 12px;
  font-weight: 600;
  color: #202020;
  margin-bottom: 12px;
  text-align: center;
  padding: 6px;
  background: #f0f0f0;
  border-radius: 4px;
}

.bus-carousel .seat-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}

.bus-carousel .seat-row {
  display: flex;
  gap: 4px;
}

.bus-carousel .seat-aisle {
  width: 16px;
}

"""
# BUS_CAROUSEL_STYLES = """
# @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

# .bus-carousel {
#   font-family: poppins, sans-serif;
# }

# .bus-carousel * {
#   font-family: poppins, sans-serif;
#   box-sizing: border-box;
#   margin: 0;
# }

# .bus-carousel main {
#   max-width: 700px;
#   margin: auto;
#   padding: 20px 0;
# }

# .bus-carousel .rslt-heading {
#   margin-bottom: 12px;
# }

# .bus-carousel .rslttp {
#   padding: 0 0 8px;
# }

# .bus-carousel .busctl {
#   font-size: 15px;
#   font-weight: 600;
#   color: #202020;
#   display: flex;
#   gap: 5px;
#   align-items: center;
# }

# .bus-carousel .bussbt {
#   font-size: 11px;
#   color: #868686;
#   font-weight: 500;
#   margin-top: 2px;
# }

# .bus-carousel .buscardbx {
#   width: 100%;
#   padding: 8px 6px;
# }

# .bus-carousel .rsltcvr {
#   width: 90%;
#   max-width: 100%;
#   overflow-x: auto;
#   display: flex;
#   gap: 20px;
#   cursor: grab;
# }

# .bus-carousel .rsltcvr::-webkit-scrollbar {
#   height: 7px;
# }

# .bus-carousel .rsltcvr::-webkit-scrollbar-track {
#   background: #fff;
# }

# .bus-carousel .rsltcvr::-webkit-scrollbar-thumb {
#   background: #373737;
#   border-radius: 5px;
# }

# .bus-carousel .rsltcvr:active {
#   cursor: grabbing;
# }

# .bus-carousel .buscard {
#   padding: 12px;
#   border-radius: 12px;
#   border: 1px solid #e0e0e0;
#   min-width: 300px;
#   width: 300px;
#   display: flex;
#   flex-direction: column;
#   background: #fff;
# }

# .bus-carousel .buschdr {
#   padding: 0 0 10px;
#   display: flex;
#   gap: 10px;
#   align-items: flex-start;
#   border-bottom: 1px solid #e0e0e0;
# }

# .bus-carousel .businfo {
#   flex: 1;
#   min-width: 0;
# }

# .bus-carousel .oprtname {
#   font-size: 14px;
#   font-weight: 600;
#   color: #202020;
#   white-space: nowrap;
#   overflow: hidden;
#   text-overflow: ellipsis;
# }

# .bus-carousel .bustype {
#   font-size: 11px;
#   color: #868686;
#   margin-top: 2px;
#   white-space: nowrap;
#   overflow: hidden;
#   text-overflow: ellipsis;
# }

# .bus-carousel .bustags {
#   display: flex;
#   gap: 4px;
#   margin-top: 6px;
#   flex-wrap: wrap;
# }

# .bus-carousel .bustag {
#   font-size: 9px;
#   padding: 2px 6px;
#   border-radius: 4px;
#   font-weight: 500;
# }

# .bus-carousel .bustag.ac {
#   background: #e3f2fd;
#   color: #1565c0;
# }

# .bus-carousel .bustag.nonac {
#   background: #fff3e0;
#   color: #e65100;
# }

# .bus-carousel .bustag.sleeper {
#   background: #f3e5f5;
#   color: #7b1fa2;
# }

# .bus-carousel .bustag.seater {
#   background: #e8f5e9;
#   color: #2e7d32;
# }

# .bus-carousel .bustag.volvo {
#   background: #fce4ec;
#   color: #c2185b;
# }

# .bus-carousel .busprcbx {
#   display: flex;
#   flex-direction: column;
#   align-items: flex-end;
#   text-align: right;
# }

# .bus-carousel .sbttl {
#   font-size: 9px;
#   color: #868686;
# }

# .bus-carousel .busprc {
#   font-size: 18px;
#   font-weight: 700;
#   color: #202020;
# }

# .bus-carousel .seatsleft {
#   font-size: 10px;
#   color: #d32f2f;
#   font-weight: 500;
#   margin-top: 2px;
# }

# .bus-carousel .busbdy {
#   display: flex;
#   align-items: center;
#   justify-content: space-between;
#   padding: 10px 0;
#   border-bottom: 1px solid #f0f0f0;
# }

# .bus-carousel .bustme {
#   font-size: 17px;
#   font-weight: 600;
#   color: #202020;
# }

# .bus-carousel .jrny {
#   text-align: center;
# }

# .bus-carousel .jrnttl {
#   font-size: 11px;
#   color: #868686;
# }

# .bus-carousel .j-br {
#   width: 55px;
#   border-bottom: 1px solid #9e9da1;
#   position: relative;
#   margin: 4px 0;
# }

# .bus-carousel .pointsrow {
#   display: flex;
#   justify-content: space-between;
#   gap: 10px;
#   padding: 8px 0;
#   border-bottom: 1px solid #f0f0f0;
# }

# .bus-carousel .pointbox {
#   flex: 1;
#   min-width: 0;
# }

# .bus-carousel .pointlbl {
#   font-size: 9px;
#   color: #868686;
#   text-transform: uppercase;
#   margin-bottom: 2px;
# }

# .bus-carousel .pointval {
#   font-size: 11px;
#   color: #4b4b4b;
#   white-space: nowrap;
#   overflow: hidden;
#   text-overflow: ellipsis;
# }

# .bus-carousel .ratingrow {
#   display: flex;
#   align-items: center;
#   gap: 8px;
#   padding: 8px 0;
# }

# .bus-carousel .rtnvlu {
#   background: #00a664;
#   color: #fff;
#   padding: 3px 8px;
#   border-radius: 6px;
#   font-weight: 600;
#   font-size: 11px;
# }

# .bus-carousel .rtnvlu.low {
#   background: #ff9800;
# }

# .bus-carousel .rtnvlu.poor {
#   background: #f44336;
# }

# .bus-carousel .busamnts {
#   list-style: none;
#   margin: 0;
#   padding: 8px 0;
#   font-size: 10px;
#   color: #4b4b4b;
#   display: flex;
#   flex-wrap: wrap;
#   gap: 4px;
# }

# .bus-carousel .busamnts li {
#   background: #f5f5f5;
#   padding: 3px 8px;
#   border-radius: 10px;
# }

# .bus-carousel .featuresrow {
#   display: flex;
#   gap: 8px;
#   flex-wrap: wrap;
#   padding: 6px 0;
# }

# .bus-carousel .featuretag {
#   font-size: 10px;
#   color: #04a77a;
#   display: flex;
#   align-items: center;
#   gap: 4px;
# }

# .bus-carousel .featuretag::before {
#   content: '✓';
#   font-weight: bold;
# }

# .bus-carousel .busftr {
#   display: flex;
#   flex-direction: column;
#   gap: 8px;
#   padding-top: 10px;
#   margin-top: auto;
# }

# .bus-carousel .bkbtn {
#   border-radius: 40px;
#   background: #ef6614;
#   color: #fff;
#   text-align: center;
#   font-size: 12px;
#   padding: 10px 15px;
#   width: 100%;
#   border: 0;
#   cursor: pointer;
#   text-decoration: none;
#   display: inline-block;
#   transition: all 0.2s ease;
#   font-weight: 600;
# }

# .bus-carousel .bkbtn:hover {
#   background: #e75806;
# }

# .bus-carousel .cancelpolicy {
#   font-size: 10px;
#   color: #646d74;
#   text-align: center;
# }

# .bus-carousel .cancelpolicy.cancellable {
#   color: #04a77a;
# }

# .bus-carousel .emt-empty {
#   padding: 60px 20px;
#   text-align: center;
#   color: #646d74;
#   font-size: 14px;
#   font-weight: 500;
# }

# .bus-carousel .emt-inline-arrow {
#   width: 14px;
#   height: auto;
#   object-fit: contain;
#   vertical-align: baseline;
# }

# .bus-carousel .view-all-link {
#   margin-left: 12px;
#   padding: 6px 14px;
#   background: #f5f5f5;
#   border: 1px solid #e0e0e0;
#   border-radius: 20px;
#   color: #2093ef;
#   text-decoration: none;
#   font-size: 12px;
#   font-weight: 600;
#   transition: all 0.2s ease;
#   white-space: nowrap;
# }

# .bus-carousel .view-all-link:hover {
#   background: #2093ef;
#   color: #fff;
#   border-color: #2093ef;
# }

# .bus-carousel .view-all-card {
#   display: flex;
#   align-items: center;
#   justify-content: center;
#   background: linear-gradient(135deg, #fff5f0 0%, #ffffff 100%);
#   border: 2px dashed #ef6614;
#   cursor: pointer;
#   transition: all 0.3s ease;
#   text-decoration: none;
# }

# .bus-carousel .view-all-card:hover {
#   background: linear-gradient(135deg, #ffebe0 0%, #fff5f0 100%);
#   transform: translateY(-2px);
#   box-shadow: 0 4px 12px rgba(239, 102, 20, 0.15);
# }

# .bus-carousel .view-all-content {
#   display: flex;
#   flex-direction: column;
#   align-items: center;
#   gap: 12px;
#   padding: 20px;
#   text-align: center;
# }

# .bus-carousel .view-all-icon svg {
#   width: 48px;
#   height: 48px;
# }

# .bus-carousel .view-all-title {
#   font-size: 16px;
#   font-weight: 600;
#   color: #ef6614;
# }

# .bus-carousel .view-all-subtitle {
#   font-size: 12px;
#   color: #868686;
# }
# """

BUS_CAROUSEL_TEMPLATE = """
<style>
{{ styles }}
</style>

<div class="bus-carousel  round-trip-selector" data-instance-id="{{ unique_id }}">
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
        <span>{{ bus_count }} bus{{ 'es' if bus_count != 1 else '' }} found</span>
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
              <div class="businfo-top">
                <div class="oprtname" title="{{ bus.operator_name_full }}">{{ bus.operator_name }}</div>
                {% if bus.rating %}
                <span class="rtnvlu {{ bus.rating_class }}">★ {{ bus.rating }}</span>
                {% endif %}
              </div>
              <div class="bustype" title="{{ bus.bus_type_full }}">{{ bus.bus_type }}</div>
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
            <div class="pointbox" onclick="this.classList.toggle('open')">
              <div class="pointlbl">
                Boarding
                {% if bus.all_boarding_points|length > 1 %}<span class="dropdown-arrow"></span>{% endif %}
              </div>
              <div class="pointval" title="{{ bus.boarding_point_full }}">{{ bus.boarding_point }}</div>
              {% if bus.all_boarding_points|length > 1 %}
              <div class="points-dropdown">
                {% for bp in bus.all_boarding_points %}
                <div class="points-dropdown-item">
                  <div class="point-name">{{ bp.name }}</div>
                  {% if bp.time %}<div class="point-time">{{ bp.time }}</div>{% endif %}
                </div>
                {% endfor %}
              </div>
              {% endif %}
            </div>
            <div class="pointbox" onclick="this.classList.toggle('open')">
              <div class="pointlbl">
                Dropping
                {% if bus.all_dropping_points|length > 1 %}<span class="dropdown-arrow"></span>{% endif %}
              </div>
              <div class="pointval" title="{{ bus.dropping_point_full }}">{{ bus.dropping_point }}</div>
              {% if bus.all_dropping_points|length > 1 %}
              <div class="points-dropdown">
                {% for dp in bus.all_dropping_points %}
                <div class="points-dropdown-item">
                  <div class="point-name">{{ dp.name }}</div>
                  {% if dp.time %}<div class="point-time">{{ dp.time }}</div>{% endif %}
                </div>
                {% endfor %}
              </div>
              {% endif %}
            </div>
          </div>

          <div class="details-section" onclick="if(this.querySelector('.view-details-btn').classList.contains('disabled')) return; this.classList.toggle('open')">
            <button type="button" class="view-details-btn {% if not bus.has_amenities %}disabled{% endif %}">
              View Details
              <span class="details-arrow"></span>
            </button>
            {% if bus.has_amenities %}
            <div class="details-content">
              {% if bus.amenities %}
              <ul class="busamnts">
                {% for amenity in bus.amenities %}<li>{{ amenity }}</li>{% endfor %}
              </ul>
              {% endif %}
              {% if bus.live_tracking or bus.m_ticket %}
              <div class="featuresrow">
                {% if bus.live_tracking %}<span class="featuretag">Live Tracking</span>{% endif %}
                {% if bus.m_ticket %}<span class="featuretag">M-Ticket</span>{% endif %}
              </div>
              {% endif %}
            </div>
            {% endif %}
          </div>

          <div class="busftr">
            <button type="button" class="bkbtn select-seats-btn" 
                    data-bus-id="{{ bus.bus_id }}"
                    data-route-id="{{ bus.route_id }}"
                    data-engine-id="{{ bus.engine_id }}"
                    data-operator-id="{{ bus.operator_id }}"
                    data-operator-name="{{ bus.operator_name_full }}"
                    data-bus-type="{{ bus.bus_type_full }}"
                    data-departure-time="{{ bus.departure_time }}"
                    data-arrival-time="{{ bus.arrival_time }}"
                    data-duration="{{ bus.duration }}"
                    data-is-seater="{{ bus.is_seater | lower }}"
                    data-is-sleeper="{{ bus.is_sleeper | lower }}"
                    data-booking-link="{{ bus.booking_link }}"
                    data-source-id="{{ source_id }}"
                    data-destination-id="{{ destination_id }}"
                    data-source-name="{{ source_city }}"
                    data-destination-name="{{ destination_city }}"
                    data-journey-date="{{ journey_date_raw }}">
              Select Seats
            </button>
            {% if bus.is_cancellable %}
            <div class="cancelpolicy cancellable">Free Cancellation</div>
            {% else %}
            <div class="cancelpolicy">Non-refundable</div>
            {% endif %}
          </div>
        </div>
        {% endfor %}
        
        {% if show_view_all_card and view_all_link %}
        <a href="{{ view_all_link }}" target="_blank" rel="noopener noreferrer" class="buscard view-all-card">
          <div class="view-all-card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
            </svg>
          </div>
          <div class="view-all-card-title">View All</div>
          <div class="view-all-card-subtitle">{{ total_bus_count }} buses on this route</div>
        </a>
        {% endif %}
      </div>
    </div>

    {% if not buses %}
    <div class="emt-empty">No buses found for this route</div>
    {% endif %}
  </main>
  <!-- Seat Selection Modal -->
<div class="seat-modal-overlay" id="seatModalOverlay">
  <div class="seat-modal">
    <div class="seat-modal-header">
      <div>
        <div class="seat-modal-title" id="modalBusOperator">Loading...</div>
        <div class="seat-modal-subtitle" id="modalBusType"></div>
      </div>
      <button type="button" class="seat-modal-close" onclick="closeSeatModal()">×</button>
    </div>
    
    <!-- Step Indicator -->
    <div class="step-indicator" style="display:flex;justify-content:center;gap:8px;padding:8px 12px;background:#f8f9fa;border-bottom:1px solid #e0e0e0;">
      <div class="step active" id="step1" style="display:flex;align-items:center;gap:4px;font-size:10px;color:#ef6614;font-weight:600;">
        <span style="width:18px;height:18px;border-radius:50%;background:#ef6614;color:#fff;display:flex;align-items:center;justify-content:center;font-size:9px;">1</span>
        Seats
      </div>
      <div style="color:#ccc;">→</div>
      <div class="step" id="step2" style="display:flex;align-items:center;gap:4px;font-size:10px;color:#999;">
        <span style="width:18px;height:18px;border-radius:50%;background:#e0e0e0;color:#666;display:flex;align-items:center;justify-content:center;font-size:9px;">2</span>
        Boarding
      </div>
      <div style="color:#ccc;">→</div>
      <div class="step" id="step3" style="display:flex;align-items:center;gap:4px;font-size:10px;color:#999;">
        <span style="width:18px;height:18px;border-radius:50%;background:#e0e0e0;color:#666;display:flex;align-items:center;justify-content:center;font-size:9px;">3</span>
        Dropping
      </div>
    </div>
    
    <div class="seat-modal-body">
      <!-- Step 1: Seat Selection -->
      <div class="modal-step" id="seatStep" style="display:block;">
        <div class="seat-layout-section">
          <div class="seat-legend">
            <div class="legend-item"><div class="legend-box available"></div>Available</div>
            <div class="legend-item"><div class="legend-box selected"></div>Selected</div>
            <div class="legend-item"><div class="legend-box booked"></div>Booked</div>
            <div class="legend-item"><div class="legend-box ladies"></div>Ladies</div>
          </div>
          <div id="seatLayoutContainer" class="seat-loading">Loading seat layout...</div>
        </div>
      </div>
      
      <!-- Step 2: Boarding Points -->
      <div class="modal-step" id="boardingStep" style="display:none;">
        <div style="font-size:12px;font-weight:600;margin-bottom:8px;color:#202020;">Select Boarding Point</div>
        <div id="boardingPointsList" class="points-list" style="max-height:280px;overflow-y:auto;"></div>
      </div>
      
      <!-- Step 3: Dropping Points -->
      <div class="modal-step" id="droppingStep" style="display:none;">
        <div style="font-size:12px;font-weight:600;margin-bottom:8px;color:#202020;">Select Dropping Point</div>
        <div id="droppingPointsList" class="points-list" style="max-height:280px;overflow-y:auto;"></div>
      </div>
    </div>
    
    <div class="seat-modal-footer">
      <div class="selected-info">
        <div>Seats: <strong id="selectedSeatsDisplay">None</strong></div>
        <div class="total-fare">₹<span id="totalFareDisplay">0</span></div>
      </div>
      <div style="display:flex;gap:8px;">
        <button type="button" class="continue-btn" id="backBtn" style="display:none;background:#666;" onclick="goToPrevStep()">← Back</button>
        <button type="button" class="continue-btn" id="nextBtn" disabled onclick="goToNextStep()">Next →</button>
        <button type="button" class="continue-btn" id="bookNowBtn" style="display:none;background:#00a664;" onclick="confirmAndRedirect()">Book Now</button>
      </div>
    </div>
  </div>
</div>

<script>
(function() {
  let currentBusData = null;
  let selectedSeats = [];
  let selectedBoardingPoint = null;
  let selectedDroppingPoint = null;
  let seatLayoutData = null;
  let boardingPoints = [];
  let droppingPoints = [];
  let currentStep = 1;
  
  window.openSeatModal = openSeatModal;
  window.closeSeatModal = closeSeatModal;
  window.confirmAndRedirect = confirmAndRedirect;
  window.selectSeat = selectSeat;
  window.selectBoardingPoint = selectBoardingPoint;
  window.selectDroppingPoint = selectDroppingPoint;
  window.filterByPrice = filterByPrice;
  window.goToNextStep = goToNextStep;
  window.goToPrevStep = goToPrevStep;
  
  function generateHexId() {
    var result = '';
    for (var i = 0; i < 32; i++) {
      result += Math.floor(Math.random() * 16).toString(16);
    }
    return result;
  }
  
  function generateId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
  
  function attachHandlers() {
    var buttons = document.querySelectorAll('.select-seats-btn');
    buttons.forEach(function(btn) {
      btn.onclick = function(e) {
        e.preventDefault();
        e.stopPropagation();
        var busData = {
          busId: this.dataset.busId || '',
          routeId: this.dataset.routeId || '',
          engineId: parseInt(this.dataset.engineId) || 0,
          operatorId: this.dataset.operatorId || '',
          operatorName: this.dataset.operatorName || '',
          busType: this.dataset.busType || '',
          departureTime: this.dataset.departureTime || '',
          arrivalTime: this.dataset.arrivalTime || '',
          duration: this.dataset.duration || '',
          isSeater: this.dataset.isSeater === 'true',
          isSleeper: this.dataset.isSleeper === 'true',
          bookingLink: this.dataset.bookingLink || '',
          sourceId: this.dataset.sourceId || '',
          destinationId: this.dataset.destinationId || '',
          sourceName: this.dataset.sourceName || '',
          destinationName: this.dataset.destinationName || '',
          journeyDate: this.dataset.journeyDate || ''
        };
        openSeatModal(busData);
      };
    });
  }
  
  setTimeout(attachHandlers, 100);
  setTimeout(attachHandlers, 500);
  setTimeout(attachHandlers, 1000);
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attachHandlers);
  } else {
    attachHandlers();
  }
  
  function updateStepIndicator(step) {
    currentStep = step;
    for (var i = 1; i <= 3; i++) {
      var stepEl = document.getElementById('step' + i);
      if (stepEl) {
        var span = stepEl.querySelector('span');
        if (i === step) {
          stepEl.style.color = '#ef6614';
          stepEl.style.fontWeight = '600';
          if (span) { span.style.background = '#ef6614'; span.style.color = '#fff'; }
        } else if (i < step) {
          stepEl.style.color = '#00a664';
          stepEl.style.fontWeight = '500';
          if (span) { span.style.background = '#00a664'; span.style.color = '#fff'; }
        } else {
          stepEl.style.color = '#999';
          stepEl.style.fontWeight = '400';
          if (span) { span.style.background = '#e0e0e0'; span.style.color = '#666'; }
        }
      }
    }
    
    document.getElementById('seatStep').style.display = step === 1 ? 'block' : 'none';
    document.getElementById('boardingStep').style.display = step === 2 ? 'block' : 'none';
    document.getElementById('droppingStep').style.display = step === 3 ? 'block' : 'none';
    
    document.getElementById('backBtn').style.display = step > 1 ? 'inline-block' : 'none';
    document.getElementById('nextBtn').style.display = step < 3 ? 'inline-block' : 'none';
    document.getElementById('bookNowBtn').style.display = step === 3 ? 'inline-block' : 'none';
    
    updateButtonStates();
  }
  
  function updateButtonStates() {
    var nextBtn = document.getElementById('nextBtn');
    var bookNowBtn = document.getElementById('bookNowBtn');
    
    if (currentStep === 1) {
      nextBtn.disabled = selectedSeats.length === 0;
    } else if (currentStep === 2) {
      nextBtn.disabled = !selectedBoardingPoint;
    } else if (currentStep === 3) {
      bookNowBtn.disabled = !selectedDroppingPoint;
    }
  }
  
  function goToNextStep() {
    if (currentStep === 1 && selectedSeats.length === 0) {
      alert('Please select at least one seat');
      return;
    }
    if (currentStep === 2 && !selectedBoardingPoint) {
      alert('Please select a boarding point');
      return;
    }
    if (currentStep < 3) {
      updateStepIndicator(currentStep + 1);
    }
  }
  
  function goToPrevStep() {
    if (currentStep > 1) {
      updateStepIndicator(currentStep - 1);
    }
  }
  
  function openSeatModal(busData) {
    currentBusData = busData;
    currentBusData.sid = generateHexId();
    currentBusData.vid = generateHexId();
    currentBusData.traceId = generateId();
    
    selectedSeats = [];
    selectedBoardingPoint = null;
    selectedDroppingPoint = null;
    seatLayoutData = null;
    currentStep = 1;
    
    var overlay = document.getElementById('seatModalOverlay');
    if (!overlay) {
      alert('Modal not found. Please refresh the page.');
      return;
    }
    
    document.getElementById('modalBusOperator').textContent = busData.operatorName || 'Bus Operator';
    document.getElementById('modalBusType').textContent = busData.busType || '';
    document.getElementById('seatLayoutContainer').innerHTML = '<div class="seat-loading">Loading seat layout...</div>';
    document.getElementById('boardingPointsList').innerHTML = '<div class="seat-loading">Loading...</div>';
    document.getElementById('droppingPointsList').innerHTML = '<div class="seat-loading">Loading...</div>';
    
    overlay.classList.add('active');
    updateStepIndicator(1);
    updateFooter();
    fetchSeatLayout(busData);
  }
  
  function closeSeatModal() {
    var overlay = document.getElementById('seatModalOverlay');
    if (overlay) overlay.classList.remove('active');
    currentBusData = null;
    selectedSeats = [];
    selectedBoardingPoint = null;
    selectedDroppingPoint = null;
    seatLayoutData = null;
    currentStep = 1;
  }
  
  function fetchSeatLayout(busData) {
    var searchReq = busData.sourceId + '|' + busData.destinationId + '|' + busData.sourceName + '|' + busData.destinationName + '|' + busData.journeyDate;
    
    var payload = {
      Idproof: 0,
      id: busData.busId,
      engineId: busData.engineId,
      sessionId: null,
      seater: busData.isSeater,
      sleeper: busData.isSleeper,
      bustype: busData.busType,
      travel: busData.operatorName,
      ArrivalTime: busData.arrivalTime,
      JourneyDate: busData.journeyDate,
      DepartureTime: busData.departureTime,
      searchReq: searchReq,
      duration: busData.duration,
      routeid: busData.routeId,
      bpId: '',
      dpId: '',
      isBpdp: false,
      Vid: busData.vid,
      SeatPrice: 0,
      stStatus: false,
      agentType: 'NAN',
      countryCode: null,
      TraceID: busData.traceId,
      Sid: busData.sid,
      OperatorId: busData.operatorId
    };
    
    fetch('/api/bus/seat-layout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(function(response) {
      if (!response.ok) throw new Error('API request failed: ' + response.status);
      return response.json();
    })
    .then(function(data) {
      seatLayoutData = data;
      seatLayoutData.Sid = busData.sid;
      seatLayoutData.Vid = busData.vid;
      seatLayoutData.TraceID = busData.traceId;
      
      if (data.error || (!data.Lower && !data.Upper && (!data.Seats || data.Seats.length === 0))) {
        showFallbackRedirect(busData, data.error || 'Seat layout not available');
        return;
      }
      
      renderSeatLayout(data);
      renderBoardingPoints(data.listBoardingPoint || []);
      renderDroppingPoints(data.listDropPoint || []);
    })
    .catch(function(error) {
      console.error('Seat layout fetch error:', error);
      showFallbackRedirect(busData, 'Unable to load seat layout');
    });
  }
  
  function showFallbackRedirect(busData, errorMsg) {
    document.getElementById('seatLayoutContainer').innerHTML = 
      '<div style="text-align:center;padding:30px 15px;">' +
        '<p style="font-size:12px;color:#666;margin-bottom:15px;">' + (errorMsg || 'Seat layout not available') + '</p>' +
        '<a href="' + (busData.bookingLink || '#') + '" target="_blank" rel="noopener noreferrer" ' +
           'style="display:inline-block;padding:10px 24px;background:#ef6614;color:#fff;' +
                  'text-decoration:none;border-radius:20px;font-weight:600;font-size:12px;">' +
          'Select on Website</a>' +
      '</div>';
    document.getElementById('nextBtn').style.display = 'none';
    document.getElementById('bookNowBtn').style.display = 'none';
  }
  
  function renderSeatLayout(data) {
    var container = document.getElementById('seatLayoutContainer');
    var html = '';
    
    if (data.setuniquefares && data.setuniquefares.length > 0) {
      html += '<div class="seat-price-filter" style="margin-bottom:8px;display:flex;gap:4px;flex-wrap:wrap;">';
      html += '<button type="button" class="price-btn active" onclick="filterByPrice(\'all\')" style="padding:3px 8px;font-size:9px;">All</button>';
      data.setuniquefares.forEach(function(f) {
        html += '<button type="button" class="price-btn" onclick="filterByPrice(' + f.baseFare + ')" style="padding:3px 8px;font-size:9px;">₹' + f.baseFare + '</button>';
      });
      html += '</div>';
    }
    
    html += '<div class="seat-decks" style="display:flex;gap:8px;flex-wrap:wrap;">';
    
    if (data.LowerShow && data.Lower) {
      html += '<div class="seat-deck" style="flex:1;min-width:140px;padding:8px;"><div class="deck-title" style="font-size:10px;padding:4px;">Lower Deck</div>';
      html += '<div class="seat-grid">' + renderDeck(data.Lower) + '</div></div>';
    }
    
    if (data.UpperShow && data.Upper) {
      html += '<div class="seat-deck" style="flex:1;min-width:140px;padding:8px;"><div class="deck-title" style="font-size:10px;padding:4px;">Upper Deck</div>';
      html += '<div class="seat-grid">' + renderDeck(data.Upper) + '</div></div>';
    }
    
    html += '</div>';
    container.innerHTML = html;
  }
  
  function renderDeck(deck) {
    if (!deck) return '';
    
    var columns = ['firstColumn', 'SecondColumn', 'ThirdColumn', 'FourthColumn', 'FifthColumn', 
                   'SixthColumn', 'seventhColumn', 'eightColumn', 'ninethColumn', 'tenthColumn',
                   'eleventhColumn', 'tevelthColumn', 'thirteenColumn', 'fourteenColumn'];
    
    var maxRows = 0;
    columns.forEach(function(col) {
      if (deck[col] && deck[col].length > maxRows) maxRows = deck[col].length;
    });
    
    if (maxRows === 0) return '';
    
    var html = '';
    for (var rowIdx = 0; rowIdx < maxRows; rowIdx++) {
      html += '<div class="seat-row" style="display:flex;gap:2px;justify-content:center;">';
      
      columns.forEach(function(col, colIdx) {
        if (!deck[col]) return;
        var seat = deck[col][rowIdx];
        if (!seat) return;
        
        if (colIdx === 2) html += '<div style="width:8px;"></div>';
        
        if (seat.seatType === 'noseat' || !seat.name) {
          html += '<div class="seat empty" style="width:24px;height:24px;visibility:hidden;"></div>';
        } else {
          var isAvailable = seat.available && String(seat.seatType).indexOf('unavailable') === -1;
          var isLadies = seat.ladiesSeat === 'True' || seat.ladiesSeat === true;
          var isSleeper = seat.isSleeper || seat.seatStyle === 'SL';
          
          var seatClass = 'seat';
          if (isSleeper) seatClass += ' sleeper';
          if (isAvailable) {
            seatClass += isLadies ? ' ladies' : ' available';
          } else {
            seatClass += ' booked';
          }
          
          var fare = seat.fare || seat.actualfare || 0;
          var baseFare = seat.baseFare || 0;
          
          var seatDataStr = JSON.stringify({
            id: seat.id,
            name: seat.name,
            fare: fare,
            baseFare: baseFare,
            actualfare: seat.actualfare || fare,
            encriSeat: seat.EncriSeat || '',
            seatType: isSleeper ? 'SL' : 'ST'
          }).replace(/"/g, '&quot;');
          
          var clickHandler = isAvailable ? ' onclick="selectSeat(this, ' + seatDataStr + ')"' : '';
          var width = isSleeper ? '48px' : '24px';
          
          html += '<div class="' + seatClass + '" data-seat-id="' + seat.id + '" data-fare="' + baseFare + '"' + clickHandler + 
                  ' style="width:' + width + ';height:24px;font-size:7px;border-radius:3px;display:flex;align-items:center;justify-content:center;" title="' + seat.name + ' - ₹' + fare + '">';
          html += seat.name;
          html += '</div>';
        }
      });
      
      html += '</div>';
    }
    return html;
  }
  
  function renderBoardingPoints(points) {
    boardingPoints = points || [];
    var container = document.getElementById('boardingPointsList');
    
    if (!points || points.length === 0) {
      container.innerHTML = '<div style="padding:15px;text-align:center;color:#868686;font-size:11px;">No boarding points</div>';
      return;
    }
    
    var html = '';
    points.forEach(function(point) {
      var name = point.bdLongName || point.bdPoint || 'Unknown';
      var time = point.time || '';
      var pointDataStr = JSON.stringify({ 
        id: point.bdid, 
        name: name, 
        time: time, 
        bdPoint: point.bdPoint,
        bdLongName: point.bdLongName,
        bdlocation: point.bdlocation,
        landmark: point.landmark,
        contactNumber: point.contactNumber
      }).replace(/"/g, '&quot;');
      
      html += '<div class="point-item" onclick="selectBoardingPoint(this, ' + pointDataStr + ')" style="padding:8px;border:1px solid #e0e0e0;border-radius:4px;margin-bottom:6px;cursor:pointer;font-size:10px;">';
      html += '<div style="font-weight:600;">' + time + '</div>';
      html += '<div style="color:#666;margin-top:2px;">' + name + '</div>';
      html += '</div>';
    });
    container.innerHTML = html;
  }
  
  function renderDroppingPoints(points) {
    droppingPoints = points || [];
    var container = document.getElementById('droppingPointsList');
    
    if (!points || points.length === 0) {
      container.innerHTML = '<div style="padding:15px;text-align:center;color:#868686;font-size:11px;">No dropping points</div>';
      return;
    }
    
    var html = '';
    points.forEach(function(point) {
      var name = point.dpName || 'Unknown';
      var time = point.dpTime || '';
      var pointDataStr = JSON.stringify({ 
        id: point.dpId, 
        name: name, 
        time: time,
        dpName: point.dpName,
        dpTime: point.dpTime,
        locatoin: point.locatoin
      }).replace(/"/g, '&quot;');
      
      html += '<div class="point-item" onclick="selectDroppingPoint(this, ' + pointDataStr + ')" style="padding:8px;border:1px solid #e0e0e0;border-radius:4px;margin-bottom:6px;cursor:pointer;font-size:10px;">';
      html += '<div style="font-weight:600;">' + time + '</div>';
      html += '<div style="color:#666;margin-top:2px;">' + name + '</div>';
      html += '</div>';
    });
    container.innerHTML = html;
  }
  
  function selectSeat(element, seatData) {
    if (element.classList.contains('booked')) return;
    
    var isSelected = element.classList.contains('selected');
    
    if (isSelected) {
      element.classList.remove('selected');
      element.classList.add('available');
      element.style.background = '#e8f5e9';
      element.style.borderColor = '#4caf50';
      element.style.color = '#2e7d32';
      selectedSeats = selectedSeats.filter(function(s) { return s.id !== seatData.id; });
    } else {
      element.classList.remove('available', 'ladies');
      element.classList.add('selected');
      element.style.background = '#fff3e0';
      element.style.borderColor = '#ef6614';
      element.style.color = '#e65100';
      selectedSeats.push(seatData);
    }
    
    updateFooter();
    updateButtonStates();
  }
  
  function selectBoardingPoint(element, pointData) {
    document.querySelectorAll('#boardingPointsList .point-item').forEach(function(el) { 
      el.classList.remove('selected'); 
      el.style.borderColor = '#e0e0e0';
      el.style.background = '#fff';
    });
    element.classList.add('selected');
    element.style.borderColor = '#2093ef';
    element.style.background = '#e3f2fd';
    selectedBoardingPoint = pointData;
    updateFooter();
    updateButtonStates();
  }
  
  function selectDroppingPoint(element, pointData) {
    document.querySelectorAll('#droppingPointsList .point-item').forEach(function(el) { 
      el.classList.remove('selected'); 
      el.style.borderColor = '#e0e0e0';
      el.style.background = '#fff';
    });
    element.classList.add('selected');
    element.style.borderColor = '#2093ef';
    element.style.background = '#e3f2fd';
    selectedDroppingPoint = pointData;
    updateFooter();
    updateButtonStates();
  }
  
  function updateFooter() {
    var seatsDisplay = selectedSeats.length > 0 
      ? selectedSeats.map(function(s) { return s.name; }).join(', ')
      : 'None';
    var totalFare = selectedSeats.reduce(function(sum, s) { return sum + (parseFloat(s.fare) || 0); }, 0);
    
    document.getElementById('selectedSeatsDisplay').textContent = seatsDisplay;
    document.getElementById('totalFareDisplay').textContent = totalFare.toLocaleString('en-IN');
  }
  
  function filterByPrice(price) {
    document.querySelectorAll('.price-btn').forEach(function(btn) { btn.classList.remove('active'); });
    if (event && event.target) event.target.classList.add('active');
    
    document.querySelectorAll('.seat.available, .seat.ladies').forEach(function(seat) {
      var seatFare = parseInt(seat.dataset.fare) || 0;
      if (price === 'all' || seatFare === price) {
        seat.style.opacity = '1';
        seat.style.pointerEvents = 'auto';
      } else {
        seat.style.opacity = '0.3';
        seat.style.pointerEvents = 'none';
      }
    });
  }
  
  function confirmAndRedirect() {
    if (!currentBusData || selectedSeats.length === 0 || !selectedBoardingPoint || !selectedDroppingPoint) {
      alert('Please complete all selections');
      return;
    }
    
    var seatsPayload = selectedSeats.map(function(s) {
      return {
        seatNo: s.name,
        seatType: s.seatType || 'ST',
        fare: s.fare,
        seatId: null,
        actualfare: s.actualfare || s.fare,
        gender: 'M',
        baseFare: s.baseFare || s.fare,
        EncriSeat: s.encriSeat
      };
    });
    
    var totalFare = selectedSeats.reduce(function(sum, s) { return sum + (parseFloat(s.fare) || 0); }, 0);
    
    var boardingPointObj = {
      bdPoint: selectedBoardingPoint.bdPoint || selectedBoardingPoint.name,
      bdLongName: selectedBoardingPoint.bdLongName || selectedBoardingPoint.name,
      bdid: selectedBoardingPoint.id,
      bdlocation: selectedBoardingPoint.bdlocation || '',
      landmark: selectedBoardingPoint.landmark || '',
      time: selectedBoardingPoint.time || '',
      contactNumber: selectedBoardingPoint.contactNumber || '',
      Count: 0
    };
    
    var droppingPointObj = {
      dpId: selectedDroppingPoint.id,
      dpName: selectedDroppingPoint.dpName || selectedDroppingPoint.name,
      locatoin: selectedDroppingPoint.locatoin || null,
      prime: null,
      dpTime: selectedDroppingPoint.time || selectedDroppingPoint.dpTime || '',
      Count: 0
    };
    
    var confirmPayload = {
      seats: seatsPayload,
      sessionId: null,
      totalFare: totalFare,
      boardingId: selectedBoardingPoint.id,
      boardingName: selectedBoardingPoint.name || '',
      boardingPoint: boardingPointObj,
      dropId: selectedDroppingPoint.id,
      DropingPoint: droppingPointObj,
      availableTripId: currentBusData.busId,
      source: currentBusData.sourceName,
      destination: currentBusData.destinationName,
      busOperator: currentBusData.operatorName,
      busType: currentBusData.busType,
      routeId: currentBusData.routeId,
      engineId: currentBusData.engineId,
      operator_id: currentBusData.operatorId,
      DepTime: currentBusData.departureTime,
      arrivalDate: currentBusData.arrivalTime,
      departureDate: null,
      Discount: 0,
      CashBack: 0,
      serviceFee: 0,
      STF: 0,
      TDS: 0,
      cpnCode: '',
      agentCode: '',
      agentType: '',
      agentMarkUp: 0,
      agentACBalance: 0,
      Sid: currentBusData.sid || (seatLayoutData && seatLayoutData.Sid) || '',
      Vid: currentBusData.vid || (seatLayoutData && seatLayoutData.Vid) || '',
      TraceId: currentBusData.traceId || (seatLayoutData && seatLayoutData.TraceID) || '',
      cancelPolicyList: (seatLayoutData && seatLayoutData.cancelPolicyList) || []
    };
    
    document.getElementById('bookNowBtn').disabled = true;
    document.getElementById('bookNowBtn').textContent = 'Processing...';
    
    fetch('/api/bus/confirm-seats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(confirmPayload)
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
      var form = document.createElement('form');
      form.method = 'POST';
      form.action = 'https://bus.easemytrip.com/Home/BusPayment';
      form.target = '_blank';
      
      var input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'userid';
      input.value = 'Emt';
      form.appendChild(input);
      
      document.body.appendChild(form);
      form.submit();
      document.body.removeChild(form);
      
      closeSeatModal();
    })
    .catch(function(error) {
      console.error('ConfirmSeats error:', error);
      if (currentBusData && currentBusData.bookingLink) {
        window.open(currentBusData.bookingLink, '_blank');
      }
      closeSeatModal();
    });
  }
  
  document.addEventListener('click', function(e) {
    var overlay = document.getElementById('seatModalOverlay');
    if (e.target === overlay) {
      closeSeatModal();
    }
  });
})();
</script>
</div>
"""

# BUS_CAROUSEL_TEMPLATE = """
# <style>
# {{ styles }}
# </style>

# <div class="bus-carousel">
#   <main>
#     <div class="rslttp rslt-heading">
#       <div class="busctl">
#         <span>{{ source_city }}</span>
#         <img
#           class="emt-inline-arrow"
#           src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='15.728' height='8.101' viewBox='0 0 15.728 8.101'%3E%3Cpath d='M16.536,135.588h0l-3.414-3.4a.653.653,0,0,0-.922.926l2.292,2.281H1.653a.653.653,0,1,0,0,1.307H14.492L12.2,138.985a.653.653,0,0,0,.922.926l3.414-3.4h0A.654.654,0,0,0,16.536,135.588Z' transform='translate(-1 -132)' fill='%23202020'/%3E%3C/svg%3E"
#           alt="→"
#         />
#         <span>{{ destination_city }}</span>
#         {% if view_all_link %}
#         <a href="{{ view_all_link }}" target="_blank" rel="noopener noreferrer" class="view-all-link">View All</a>
#         {% endif %}
#       </div>
#       <div class="bussbt">
#         <span>{{ journey_date }}</span> •
#         <span>{{ bus_count }} bus{{ 'es' if bus_count != 1 else '' }} found</span>
#         {% if ac_count %} • <span>{{ ac_count }} AC</span>{% endif %}
#         {% if non_ac_count %} • <span>{{ non_ac_count }} Non-AC</span>{% endif %}
#       </div>
#     </div>

#     <div class="buscardbx">
#       <div class="rsltcvr">
#         {% for bus in buses %}
#         <div class="buscard item">
#           <div class="buschdr">
#             <div class="businfo">
#               <div class="oprtname" title="{{ bus.operator_name }}">{{ bus.operator_name }}</div>
#               <div class="bustype" title="{{ bus.bus_type }}">{{ bus.bus_type }}</div>
#               <div class="bustags">
#                 {% if bus.is_ac %}<span class="bustag ac">AC</span>{% endif %}
#                 {% if bus.is_non_ac %}<span class="bustag nonac">Non-AC</span>{% endif %}
#                 {% if bus.is_volvo %}<span class="bustag volvo">Volvo</span>{% endif %}
#                 {% if bus.is_sleeper %}<span class="bustag sleeper">Sleeper</span>
#                 {% elif bus.is_seater %}<span class="bustag seater">Seater</span>{% endif %}
#               </div>
#             </div>
#             <div class="busprcbx">
#               <div class="sbttl">starts from</div>
#               <div class="busprc">{{ bus.fare }}</div>
#               {% if bus.seats_label %}<div class="seatsleft">{{ bus.seats_label }}</div>{% endif %}
#             </div>
#           </div>

#           <div class="busbdy">
#             <div class="bustme">{{ bus.departure_time }}</div>
#             <div class="jrny">
#               <div class="jrnttl">{{ bus.duration }}</div>
#               <div class="j-br"></div>
#             </div>
#             <div class="bustme">{{ bus.arrival_time }}</div>
#           </div>

#           <div class="pointsrow">
#             <div class="pointbox">
#               <div class="pointlbl">Boarding</div>
#               <div class="pointval" title="{{ bus.boarding_point }}">{{ bus.boarding_point }}</div>
#             </div>
#             <div class="pointbox">
#               <div class="pointlbl">Dropping</div>
#               <div class="pointval" title="{{ bus.dropping_point }}">{{ bus.dropping_point }}</div>
#             </div>
#           </div>

#           {% if bus.rating %}
#           <div class="ratingrow">
#             <span class="rtnvlu {{ bus.rating_class }}">★ {{ bus.rating }}</span>
#           </div>
#           {% endif %}

#           {% if bus.amenities %}
#           <ul class="busamnts">
#             {% for amenity in bus.amenities[:4] %}<li>{{ amenity }}</li>{% endfor %}
#             {% if bus.amenities|length > 4 %}<li>+{{ bus.amenities|length - 4 }} more</li>{% endif %}
#           </ul>
#           {% endif %}

#           {% if bus.live_tracking or bus.m_ticket %}
#           <div class="featuresrow">
#             {% if bus.live_tracking %}<span class="featuretag">Live Tracking</span>{% endif %}
#             {% if bus.m_ticket %}<span class="featuretag">M-Ticket</span>{% endif %}
#           </div>
#           {% endif %}

#           <div class="busftr">
#             <a href="{{ bus.booking_link }}" target="_blank" rel="noopener noreferrer" class="bkbtn">Book Now</a>
#             {% if bus.is_cancellable %}
#             <div class="cancelpolicy cancellable">Cancellation Available</div>
#             {% else %}
#             <div class="cancelpolicy">Non-refundable</div>
#             {% endif %}
#           </div>
#         </div>
#         {% endfor %}
        
#         {% if show_view_all_card and view_all_link %}
#         <a href="{{ view_all_link }}" target="_blank" rel="noopener noreferrer" class="buscard item view-all-card">
#           <div class="view-all-content">
#             <div class="view-all-icon">
#               <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ef6614" stroke-width="2">
#                 <circle cx="12" cy="12" r="10"></circle>
#                 <path d="M12 8v8M8 12h8"></path>
#               </svg>
#             </div>
#             <div class="view-all-text">
#               <div class="view-all-title">View All {{ total_bus_count }} Buses</div>
#               <div class="view-all-subtitle">See more options for this route</div>
#             </div>
#           </div>
#         </a>
#         {% endif %}
#       </div>
#     </div>

#     {% if not buses %}
#     <div class="emt-empty">No buses found for this route</div>
#     {% endif %}
#   </main>
# </div>
# """

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

    # return {
    #     "operator_name": _truncate_text(bus.get("operator_name") or bus.get("Travels") or "Unknown", 22),
    #     "bus_type": _truncate_text(bus.get("bus_type") or bus.get("busType") or "Bus", 30),
    #     "departure_time": _format_time(bus.get("departure_time") or bus.get("departureTime")),
    #     "arrival_time": _format_time(bus.get("arrival_time") or bus.get("ArrivalTime")),
    #     "duration": bus.get("duration") or "--",
    #     "fare": _format_currency(price),
    #     "seats_label": _get_seats_label(bus.get("available_seats") or bus.get("AvailableSeats")),
    #     "is_ac": bus.get("is_ac") or bus.get("AC", False),
    #     "is_non_ac": bus.get("is_non_ac") or bus.get("nonAC", False),
    #     "is_volvo": bus.get("is_volvo") or bus.get("isVolvo", False),
    #     "is_seater": bus.get("is_seater") or bus.get("seater", False),
    #     "is_sleeper": bus.get("is_sleeper") or bus.get("sleeper", False),
    #     "rating": normalized_rating,
    #     "rating_class": _get_rating_class(raw_rating),
    #     "boarding_point": _get_first_boarding_point(boarding_points),
    #     "dropping_point": _get_first_dropping_point(dropping_points),
    #     "amenities": _extract_amenities(amenities),
    #     "live_tracking": live_tracking,
    #     "m_ticket": m_ticket,
    #     "is_cancellable": is_cancellable,
    #     "booking_link": booking_link,
    # }


    # Get full names for tooltips
    operator_name_full = bus.get("operator_name") or bus.get("Travels") or "Unknown"
    bus_type_full = bus.get("bus_type") or bus.get("busType") or "Bus"
    
    # Process all boarding points for dropdown
    all_boarding_points = []
    for bp in boarding_points:
        bp_name = (bp.get("bd_long_name") or bp.get("bdLongName") or 
                   bp.get("bd_point") or bp.get("bdPoint") or "")
        bp_time = bp.get("time") or ""
        if bp_name:
            all_boarding_points.append({"name": bp_name, "time": bp_time})
    
    # Process all dropping points for dropdown
    all_dropping_points = []
    for dp in dropping_points:
        dp_name = dp.get("dp_name") or dp.get("dpName") or ""
        dp_time = dp.get("dp_time") or dp.get("dpTime") or ""
        if dp_name:
            all_dropping_points.append({"name": dp_name, "time": dp_time})

    return {
        "operator_name": _truncate_text(operator_name_full, 22),
        "operator_name_full": operator_name_full,
        "bus_type": _truncate_text(bus_type_full, 30),
        "bus_id": bus.get("bus_id", ""),
        "route_id": str(bus.get("route_id", "")),
        "engine_id": bus.get("engine_id", 0),
        "operator_id": str(bus.get("operator_id", "")),
        "bus_type_full": bus_type_full,
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
        "boarding_point_full": all_boarding_points[0]["name"] if all_boarding_points else "N/A",
        "all_boarding_points": all_boarding_points,
        "dropping_point": _get_first_dropping_point(dropping_points),
        "dropping_point_full": all_dropping_points[0]["name"] if all_dropping_points else "N/A",
        "all_dropping_points": all_dropping_points,
        "amenities": _extract_amenities(amenities),
        "has_amenities": len(_extract_amenities(amenities)) > 0,
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
    
    # Get raw journey date for API calls
    journey_date_raw = bus_results.get("journey_date", "")
    instance_id = uuid.uuid4().hex[:8]
    template = _jinja_env.from_string(BUS_CAROUSEL_TEMPLATE)
    return template.render(
        styles=BUS_CAROUSEL_STYLES,
        source_city=source_city,
        destination_city=destination_city,
        journey_date=journey_date,
        journey_date_raw=journey_date_raw,
        source_id=bus_results.get("source_id", ""),
        destination_id=bus_results.get("destination_id", ""),
        bus_count=bus_count,
        ac_count=ac_count,
        non_ac_count=non_ac_count,
        buses=buses_ui,
        view_all_link=bus_results.get("view_all_link"),
        show_view_all_card=False,
        total_bus_count=bus_count,
        instance_id=instance_id,
    )


# def render_bus_results_with_limit(
#     bus_results: Dict[str, Any],
#     display_limit: int = 5,
#     show_view_all: bool = True,
# ) -> str:
#     if "structured_content" in bus_results:
#         bus_results = bus_results["structured_content"]
    
#     buses = bus_results.get("buses", [])
    
#     if not buses:
#         return "<div class='bus-carousel'><main><div class='emt-empty'>No buses found for this route</div></main></div>"
    
#     total_buses = len(buses)
#     display_buses = buses[:display_limit]
    
#     buses_ui = [_normalize_bus_for_ui(bus) for bus in display_buses]
#     buses_ui = [b for b in buses_ui if b]
    
#     if not buses_ui:
#         return "<div class='bus-carousel'><main><div class='emt-empty'>No buses found for this route</div></main></div>"
    
#     source_city = bus_results.get("source_name") or bus_results.get("source_id", "")
#     destination_city = bus_results.get("destination_name") or bus_results.get("destination_id", "")
#     journey_date = _format_date(bus_results.get("journey_date"))
#     ac_count = bus_results.get("ac_count", 0)
#     non_ac_count = bus_results.get("non_ac_count", 0)
#     view_all_link = bus_results.get("view_all_link", "")
    
#     should_show_view_all = show_view_all and total_buses > display_limit and view_all_link
    
#     template = _jinja_env.from_string(BUS_CAROUSEL_TEMPLATE)
#     return template.render(
#         styles=BUS_CAROUSEL_STYLES,
#         source_city=source_city,
#         destination_city=destination_city,
#         journey_date=journey_date,
#         bus_count=total_buses,
#         ac_count=ac_count,
#         non_ac_count=non_ac_count,
#         buses=buses_ui,
#         view_all_link=view_all_link,
#         show_view_all_card=should_show_view_all,
#         total_bus_count=total_buses,
#     )

def render_bus_results_with_limit(
    bus_results: Dict[str, Any],
    display_limit: int = 5,
    show_view_all: bool = True,
    total_bus_count: int = None,  # NEW PARAMETER
) -> str:
    if "structured_content" in bus_results:
        bus_results = bus_results["structured_content"]
    
    buses = bus_results.get("buses", [])
    
    if not buses:
        return "<div class='bus-carousel'><main><div class='emt-empty'>No buses found for this route</div></main></div>"
    
    # Use passed total_bus_count if provided, otherwise use total_count from data, otherwise len(buses)
    if total_bus_count is None:
        total_bus_count = bus_results.get("total_count") or len(buses)
    
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
    
    # Always show View All card if link exists and show_view_all is True
    should_show_view_all = show_view_all and view_all_link
    instance_id = uuid.uuid4().hex[:8]
    template = _jinja_env.from_string(BUS_CAROUSEL_TEMPLATE)
    return template.render(
        styles=BUS_CAROUSEL_STYLES,
        source_city=source_city,
        destination_city=destination_city,
        journey_date=journey_date,
        bus_count=total_bus_count,  # Use total, not len(buses)
        ac_count=ac_count,
        non_ac_count=non_ac_count,
        buses=buses_ui,
        view_all_link=view_all_link,
        show_view_all_card=should_show_view_all,
        total_bus_count=total_bus_count,  # Use total for View All card
        instance_id=instance_id,
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