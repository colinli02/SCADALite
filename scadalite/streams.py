import time
import random
import datetime
import serial
from .parser import parse_line


def simulation_stream(stop_event, callback):
    sp_speed = 1500
    sp_level = 80
    speed = 1400.0
    level = 70.0

    while not stop_event.is_set():
        speed += random.uniform(-10, 10)
        level += random.uniform(-0.5, 0.5)
        now = datetime.datetime.utcnow().isoformat()

        lines = [
            f"TAG=PUMP1_SPEED;TYPE=ai;PV={speed:.1f};SP={sp_speed};UNIT=RPM;TS={now}",
            f"TAG=TANK1_LEVEL;TYPE=ai;PV={level:.1f};SP={sp_level};UNIT=%;TS={now}",
            f"TAG=HEATER_CMD;TYPE=do;PV={int(level < 75)};UNIT=BOOL;TS={now}",
        ]

        for line in lines:
            rec = parse_line(line)
            if rec:
                callback(rec)

        time.sleep(0.5)


def com_stream(stop_event, callback, port, baud):
    ser = serial.Serial(port, baudrate=baud, timeout=1)
    while not stop_event.is_set():
        line = ser.readline().decode(errors="ignore").strip()
        if not line:
            continue
        rec = parse_line(line)
        if rec:
            callback(rec)
