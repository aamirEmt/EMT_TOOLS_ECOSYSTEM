# app/utils.py
import uuid
import time
from datetime import datetime

def gen_trace_id(prefix="trace"):
    return f"{prefix}{int(time.time()*1000)}{str(uuid.uuid4())[:6]}"

def today_str():
    return datetime.utcnow().strftime("%Y-%m-%d")