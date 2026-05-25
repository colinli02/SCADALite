# SCADALite

SCADALite is a lightweight, Python-based SCADA-style dashboard that reads
telemetry from either:

- Simulation mode (fake data)
- A COM/Serial device (Arduino, microcontrollers, PLCs, etc.)

It supports:

- Live trending
- Pause/Resume
- Alarm detection (HI/LO)
- Configurable alarms
- Historical log loading
- Config-driven graph selection

File structure:

scadalite/
│
├── app.py          ← GUI
├── streams.py      ← simulation + COM
├── parser.py       ← TagRecord + parse_line
├── alarms.py       ← alarm_rules + active_alarms + detect_alarm
├── storage.py      ← history + latest + log_record + handle_record
├── config.py
└── main.py

---

## Installation

```bash
git clone https://github.com/colinli02/scadalite
cd scadalite
pip install -r requirements.txt
```

## Running

run the main.py file from cd

py -m scadalite.main

or run the .bat file