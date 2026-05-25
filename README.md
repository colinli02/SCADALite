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

## File Structure

```text
scadalite/
│
├── app.py          ← GUI
├── streams.py      ← simulation + COM
├── parser.py       ← TagRecord + parse_line
├── alarms.py       ← alarm_rules + active_alarms + detect_alarm
├── storage.py      ← history + latest + log_record + handle_record
├── config.py
└── main.py
```

## Installation

```bash
git clone https://github.com/colinli02/scadalite
cd scadalite
pip install -r requirements.txt
```

## Configuration and Usage

Modify `config.yaml` with the tags you want to use. See the current config for examples.

## Tag Types

SCADALite parses every incoming telemetry line into a `TagRecord` with the following fields:

- **TAG** — name of the measurement
- **TYPE** — the kind of signal
- **PV** — process value (numeric reading)
- **SP** — setpoint (optional)
- **UNIT** — engineering units (optional)
- **TS** — timestamp

### Available Signal Types

| Type | Meaning |
|------|----------|
| **ai** | Analog input (sensor value, e.g., speed, temperature, level) |
| **do** | Digital output (0/1 command, e.g., heater on/off) |
| **CONST** | Constant value defined in `config.yaml` |

## COM Input Formats

SCADALite supports multiple input formats depending on how much information you want to send.

### Simple Format

TYPE defaults to `ai`.

#### Simple Format Syntax

```text
TAG PV
```

#### Simple Format Example

```text
PUMP1_SPEED 1500
```

#### Parsed Values

- `TYPE = ai`
- `PV = 1500`
- `SP = (empty)`
- `UNIT = (empty)`

### Key/Value Format

Explicitly specify `TYPE`, `SP`, and `UNIT`.

#### Key/Value Example

```text
TAG=PUMP1_SPEED;TYPE=ai;PV=1332.8;SP=1500;UNIT=RPM;
```

#### Supported Fields

- `TYPE`
- `PV`
- `SP`
- `UNIT`

### CSV Format

#### CSV Syntax

```text
TAG,TYPE,PV,SP,UNIT
```

#### CSV Example

```text
PUMP1_SPEED,ai,1332.8,1500,RPM
```

## Constants

You can define constant tags directly in `config.yaml`.

### Constant Configuration Example

```yaml
constants:
  TARGET_SPEED: 1500
  TARGET_LEVEL: 80
```

These appear with:

- `TYPE = CONST`
- `PV = your constant value`
- `SP = (empty)`

Constants are graphed by default.

## Running SCADALite

Run from the project root (cd)

```bash
py -m scadalite.main
```

Or run the `.bat` file directly on Windows