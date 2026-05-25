active_alarms = {}
alarm_rules = {}


def detect_alarm(rec):
    rules = alarm_rules.get(rec.tag, {})
    hi = rules.get("hi")
    lo = rules.get("lo")

    if hi is not None and rec.pv > hi:
        active_alarms[rec.tag] = f"HI ALARM: {rec.tag} = {rec.pv}"
    elif lo is not None and rec.pv < lo:
        active_alarms[rec.tag] = f"LO ALARM: {rec.tag} = {rec.pv}"
    else:
        active_alarms.pop(rec.tag, None)
