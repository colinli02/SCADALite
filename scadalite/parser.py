from dataclasses import dataclass
from typing import Optional
import datetime


@dataclass
class TagRecord:
    tag: str
    type: str
    pv: float
    sp: Optional[float]
    unit: str
    ts: str


def parse_line(line: str) -> Optional[TagRecord]:
    line = line.strip()
    if not line:
        return None

    if "TAG=" in line:
        try:
            parts = dict(kv.split("=", 1) for kv in line.split(";") if "=" in kv)
            return TagRecord(
                tag=parts["TAG"],
                type=parts.get("TYPE", "ai"),
                pv=float(parts["PV"]),
                sp=float(parts["SP"]) if "SP" in parts else None,
                unit=parts.get("UNIT", ""),
                ts=parts.get("TS", datetime.datetime.utcnow().isoformat()),
            )
        except:
            return None

    try:
        tag, typ, pv, sp, unit = [x.strip() for x in line.split(",")]
        return TagRecord(
            tag=tag,
            type=typ,
            pv=float(pv),
            sp=float(sp) if sp else None,
            unit=unit,
            ts=datetime.datetime.utcnow().isoformat(),
        )
    except:
        return None
