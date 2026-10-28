# Adria MACH for Home Assistant

Custom integration that reads your Adria MACH PLUS (Solvesall) vehicle through the MACH cloud,
so you can monitor it from Home Assistant wherever the vehicle is.

Read-only in this version: sensors, binary sensors and a GPS device tracker.
Control (lights, Alde heater) is planned once a first command has been verified.

## Install

### HACS (recommended)

1. HACS → three-dot menu → **Custom repositories** → add `https://github.com/Rsydab/ha-adria-mach`, category **Integration**.
2. Search for **Adria MACH** in HACS and download it.
3. Restart Home Assistant.

### Manual

Copy `custom_components/adria_mach` into your Home Assistant `config/custom_components/` and restart.

### Configure

Settings → Devices & services → Add integration → **Adria MACH**. Enter your MACH account
email, password and the unit id (the app shows it as "Establishing LTE connection to XXXXXXXXXXXX").

Polls the cloud every 60 seconds. The token lives 2 hours and is renewed automatically.

## Entities

Sensors: inside/outside temperature, outside humidity, air pressure, fresh and waste water,
gas bottle 1 and 2, leisure battery (SOC, voltage, current), heater setpoint, energy source,
plus diagnostics (gas sensor status/battery, heater notification, LTE signal, unit temperature, firmware).

Binary sensors: mains supply, Alde panel, heater on/running, water heater running,
internal and external lights, water pump.

Device tracker: vehicle GPS position.

## Notes

- Not affiliated with Adria Mobil or Solvesall. Uses the same cloud endpoints as the official app.
- Your credentials are stored by Home Assistant's config entry storage.
