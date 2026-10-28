# Adria MACH for Home Assistant

Custom integration that reads your Adria MACH PLUS (Solvesall) vehicle through the MACH cloud,
so you can monitor it from Home Assistant wherever the vehicle is.

Sensors, binary sensors, a GPS device tracker, and control of the internal and external
lights, the Alde heater on/off and its setpoint.

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
gas bottle 1 and 2, leisure battery (SOC, voltage, current), energy source,
plus diagnostics (gas sensor status/battery, heater notification, LTE signal, unit temperature, firmware).

Binary sensors: mains supply, Alde panel, heater running, water heater running, water pump.

Device tracker: vehicle GPS position.

Lights: internal lights, external lights (on/off).

Switch: heater (Alde air heater on/off).

Number: heater setpoint (°C). The 5–30 °C range is an assumption based on typical Alde
panels; only whole degrees have been tested.

## Notes

- Not affiliated with Adria Mobil or Solvesall. Uses the same cloud endpoints as the official app.
- Your credentials are stored by Home Assistant's config entry storage.
