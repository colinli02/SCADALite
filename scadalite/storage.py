import os
import datetime
import time
from collections import defaultdict, deque
from .alarms import detect_alarm

history = defaultdict(lambda: deque(maxlen=500))
latest = {}

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, f"log_{datetime.date.today()}.csv")

_log_file = open(LOG_PATH, "a", newline="")
if os.stat(LOG_PATH).st_size == 0:
    _log_file.write("ts,tag,type,pv,sp,unit\n")


def log_record(rec):
    _log_file.write(f"{rec.ts},{rec.tag},{rec.type},{rec.pv},{rec.sp},{rec.unit}\n")
    _log_file.flush()


def handle_record(rec):
    t = time.time()
    history[rec.tag].append((t, rec.pv))
    latest[rec.tag] = rec
    log_record(rec)
    detect_alarm(rec)
