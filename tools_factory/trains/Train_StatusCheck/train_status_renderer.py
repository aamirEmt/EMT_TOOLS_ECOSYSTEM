"""Train Status HTML Renderer.

This module renders train status data into HTML using Jinja2 templates.
Uses vertical timeline UI consistent with the route check renderer.
"""

from typing import Dict, Any
from jinja2 import Environment, BaseLoader, select_autoescape


_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
)


TRAIN_STATUS_TEMPLATE = """
<style>
/* --- SAME AS YOUR ORIGINAL TRAIN_STATUS_TEMPLATE --- */
/* (UNCHANGED, because it already uses inline onclick for Show All) */
""" + """
"""  # ⬅️ KEEP YOUR EXISTING FULL TRAIN_STATUS_TEMPLATE HERE UNCHANGED
# (I’m not repeating it to avoid accidental truncation — use exactly what you already pasted above)


TRAIN_DATES_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,100..900&family=Poppins:wght@300;400;500;600;700&display=swap');

.train-dates-widget {
  font-family: 'Poppins', sans-serif;
  color: #202020;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
}

.train-dates-widget * {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.tdt-header { margin-bottom: 16px; }
.tdt-title { font-size: 16px; font-weight: 600; color: #202020; }
.tdt-subtitle { font-size: 12px; color: #646d74; margin-top: 4px; }

.tdt-dates { display: flex; flex-direction: column; gap: 8px; }

.tdt-date-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tdt-date-item:hover {
  border-color: #2093ef;
  background: #f0f7ff;
}

.tdt-date-item.loading {
  opacity: 0.6;
  pointer-events: none;
}

.tdt-date-info { display: flex; flex-direction: column; }

.tdt-date-main { font-size: 14px; font-weight: 500; color: #202020; }
.tdt-date-day { font-size: 12px; color: #646d74; }

.tdt-date-display {
  font-size: 12px;
  font-weight: 500;
  color: #2093ef;
  background: #e3f2fd;
  padding: 4px 8px;
  border-radius: 4px;
}

.tdt-loading-text {
  font-size: 12px;
  font-weight: 500;
  color: #2093ef;
}

.tdt-error {
  padding: 16px;
  text-align: center;
  color: #d32f2f;
  font-size: 13px;
}
</style>

<div class="train-dates-widget" data-train-number="{{ train_number }}">
  <div class="tdt-header">
    <div class="tdt-title">Train {{ train_number }}</div>
    <div class="tdt-subtitle">Select a date to check status</div>
  </div>

  <div class="tdt-dates">
    {% for date in available_dates %}
    <div class="tdt-date-item"
         data-date="{{ date.date }}"
         onclick="(async function(el){
  var AUTOSUGGEST_URL='https://autosuggest.easemytrip.com/api/auto/train_name?useby=popularu&key=jNUYK0Yj5ibO6ZVIkfTiFA==';
  var LIVE_STATUS_URL='https://railways.easemytrip.com/TrainService/TrainLiveStatus';

  function parseRunningDays(str){
    if(!str||str.length!==7)return[];
    var d=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],r=[];
    for(var i=0;i<7;i++)if(str[i]==='1')r.push(d[i]);
    return r;
  }

  function calcDuration(depTime,arrTime,depDay,arrDay){
    if(!depTime||!arrTime||depTime==='--'||arrTime==='--')return '';
    try{
      var dp=depTime.split(':'),ap=arrTime.split(':');
      var depMin=parseInt(dp[0])*60+parseInt(dp[1]);
      var arrMin=parseInt(ap[0])*60+parseInt(ap[1]);
      var total=arrMin-depMin+(arrDay-depDay)*1440;
      if(total<0)total+=1440;
      var h=Math.floor(total/60),m=total%60;
      if(h>=24){var d=Math.floor(h/24);h=h%24;return d+'d '+h+'h '+m+'m';}
      return h+'h '+m+'m';
    }catch(e){return '';}
  }

  function formatDate(dateStr){
    if(!dateStr)return '';
    try{
      var p=dateStr.split('-');
      var months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      var dayNames=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
      var dt=new Date(parseInt(p[2]),parseInt(p[1])-1,parseInt(p[0]));
      return p[0]+' '+months[parseInt(p[1])-1]+' '+p[2]+', '+dayNames[dt.getDay()];
    }catch(e){return dateStr;}
  }

  function processLiveStations(stations){
    var result=[],total=stations.length;
    for(var i=0;i<total;i++){
      var s=stations[i];
      var isOrigin=i===0,isDest=i===total-1;
      var arr=(isOrigin||s.schArrTime==='Source'||s.schArrTime==='00:00')?'--':(s.schArrTime||'');
      var dep=(isDest||s.schDepTime==='00:00')?'--':(s.schDepTime||'');
      var halt=s.Halt||'--';
      result.push({
        station_code:s.stnCode||'',
        station_name:s.StationName||'',
        arrival_time:arr,
        departure_time:dep,
        halt_time:(halt&&halt!=='--')?halt:null,
        day:parseInt(s.dayCnt||'1')||1,
        distance:s.distance||'',
        platform:s.pfNo||null,
        is_origin:isOrigin,
        is_destination:isDest,
        actual_arrival:(s.actArr&&s.actArr!=='No Delay')?s.actArr:null,
        actual_departure:s.actDep||null,
        delay_departure:s.delayDep||null,
        is_current_station:!!s.isCurrentStation
      });
    }
    return result;
  }

  var widget=el.closest('.train-dates-widget');
  var trainNumber=widget.dataset.trainNumber;
  var dateStr=el.dataset.date;

  el.classList.add('loading');
  try{
    var apiDate=dateStr.replace(/-/g,'/');

    var autoRes=await fetch(AUTOSUGGEST_URL,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({request:trainNumber})});
    var autoData=await autoRes.json();

    var trainName='',trainNo=trainNumber,srcCode='',destCode='';
    if(autoData&&autoData.length>0){
      trainName=autoData[0].TrainName||'';
      trainNo=autoData[0].TrainNo||trainNumber;
      srcCode=autoData[0].SrcStnCode||'';
      destCode=autoData[0].DestStnCode||'';
    }

    var statusRes=await fetch(LIVE_STATUS_URL,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
      TrainNo:trainNo+(trainName?'-'+trainName:''),
      selectedDate:apiDate,
      Srchtype:'',
      fromSrc:srcCode,
      DestStnCode:destCode
    })});

    var statusData=await statusRes.json();
    if(statusData.ErrorMessage){
      widget.innerHTML='<div class=\\\"tdt-error\\\">'+statusData.ErrorMessage+'</div>';
      return;
    }

    var liveStations=statusData.LiveStationList||[];
    var stations=processLiveStations(liveStations);

    if(!stations.length){
      widget.innerHTML='<div class=\\\"tdt-error\\\">No station information available</div>';
      return;
    }

    var origin=stations[0],destination=stations[stations.length-1];
    var duration=calcDuration(origin.departure_time,destination.arrival_time,origin.day,destination.day);
    var formattedDate=formatDate(dateStr);

    var currentIdx=null,lastIdx=null;
    for(var k=0;k<stations.length;k++){
      if(stations[k].is_current_station)currentIdx=k;
      if(stations[k].actual_departure)lastIdx=k;
    }
    if(currentIdx===null&&lastIdx!==null)currentIdx=lastIdx;

    var data={
      train_number:trainNo,
      train_name:trainName||origin.station_name+' - '+destination.station_name+' Express',
      runs_on:parseRunningDays((statusData._TrainDetails||{}).Running_Days||''),
      origin_code:origin.station_code,
      destination_code:destination.station_code,
      departure_time:origin.departure_time||'--',
      arrival_time:destination.arrival_time||'--',
      journey_duration:duration,
      formatted_date:formattedDate,
      stations:stations,
      is_live:true,
      distance_percentage:statusData.distancePercentage||'',
      current_station_index:currentIdx
    };

    widget.outerHTML = (window.buildStatusHtml || function(){return '<div style=\\\"padding:20px\\\">Renderer missing</div>'; })(data);

  }catch(err){
    console.error(err);
    widget.innerHTML='<div class=\\\"tdt-error\\\">Failed to fetch status. Please try again.</div>';
  }
})(this)">
      <div class="tdt-date-info">
        <span class="tdt-date-main">{{ date.formatted_date }}</span>
        <span class="tdt-date-day">{{ date.day_name }}</span>
      </div>
      {% if date.display_day %}
      <span class="tdt-date-display">{{ date.display_day }}</span>
      {% endif %}
    </div>
    {% endfor %}
  </div>
</div>
"""


def render_train_status_results(status_result: Dict[str, Any]) -> str:
    import uuid

    if status_result.get("error"):
        error_msg = status_result.get("message", "Unknown error")
        return f"""
        <div style="font-family: Poppins, sans-serif; max-width: 400px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 12px; padding: 30px 20px; text-align: center; background: #fff;">
          <div style="font-size: 13px; font-weight: 500; color: #202020;">Unable to fetch train status</div>
          <div style="font-size: 11px; color: #868686; margin-top: 6px;">{error_msg}</div>
        </div>
        """

    instance_id = uuid.uuid4().hex[:8]
    all_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    stations = status_result.get("stations", [])

    visible_stops = []
    hidden_stops = stations

    current_station_index_visible = None

    template = _jinja_env.from_string(TRAIN_STATUS_TEMPLATE)
    return template.render(
        instance_id=instance_id,
        all_days=all_days,
        visible_stops=visible_stops,
        hidden_stops=hidden_stops,
        visible_count=len(visible_stops),
        total_stations=len(stations),
        current_station_index_visible=current_station_index_visible,
        **status_result,
    )


def render_train_dates(dates_result: Dict[str, Any]) -> str:
    if dates_result.get("error"):
        error_msg = dates_result.get("message", "Unknown error")
        return f"""
        <div class="train-dates-widget">
          <div style="padding: 20px; text-align: center; color: #646d74;">
            <div style="font-size: 14px;">{error_msg}</div>
          </div>
        </div>
        """

    template = _jinja_env.from_string(TRAIN_DATES_TEMPLATE)
    return template.render(**dates_result)
