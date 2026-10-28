# Adria MACH for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Release](https://img.shields.io/github/v/release/Rsydab/ha-adria-mach)](https://github.com/Rsydab/ha-adria-mach/releases)
[![Validate](https://github.com/Rsydab/ha-adria-mach/actions/workflows/validate.yml/badge.svg)](https://github.com/Rsydab/ha-adria-mach/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

What if your motorhome or caravan showed up in Home Assistant like any other room in the house?

What if you could see the fresh-water level, the gas bottle, the leisure battery and the inside
temperature from your sofa at home, while the vehicle is parked 200 km away?

What if the Alde heater could be switched on from an automation the evening before a trip, and the
outside lights turned off by a schedule?

That is what this integration does. It talks to the same MACH cloud as the official *MACH by Adria
Mobil* app, so it works wherever the vehicle has LTE coverage, with no extra hardware.

> **Note:** This is a community project. It is not affiliated with Adria Mobil or Solvesall, and it uses
> the app's cloud endpoints, which are not publicly documented. It can stop working if they change.

## Installation instructions

Requires a MACH **PLUS** system (the one with LTE and remote access) and a MACH account that already
controls the vehicle from the app.

- **Through HACS** (recommended)

  [![Open your Home Assistant instance and open a repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Rsydab&repository=ha-adria-mach&category=integration)

  1. Click the button above, or add `https://github.com/Rsydab/ha-adria-mach` as a custom repository
     (category *Integration*) in HACS.
  2. Download **Adria MACH**.
  3. Restart Home Assistant.

- **Manually**

  Copy `custom_components/adria_mach` into your Home Assistant `config/custom_components/` folder and
  restart Home Assistant.

## Quickstart

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=adria_mach)

1. Click the button above, or go to *Settings → Devices & services → Add integration* and search for
   **Adria MACH**.
2. Enter the email and password of your MACH account.
3. Your MACH unit is found automatically. If the account has several, pick one.

You now have a device called **Adria MACH** with the entities below. Values refresh every 60 seconds.

## Entities

| Kind | Entities |
|---|---|
| Sensors | Inside temperature, outside temperature, outside humidity, air pressure, fresh water, waste water, gas bottle 1, gas bottle 2, leisure battery (level, voltage, current), energy source |
| Diagnostic sensors | Gas sensor status and battery, heater notification, LTE signal, unit temperature, firmware |
| Binary sensors | Mains supply, Alde panel, heater running, water heater running, water pump |
| Lights | Internal lights, external lights |
| Switch | Heater (Alde air heater on/off) |
| Number | Heater setpoint, °C |
| Device tracker | Vehicle GPS position |

Entity names follow the language set in Home Assistant (English and Swedish are included).

## Upgrading

- Through HACS: HACS shows the update like any other integration. Download it and restart Home Assistant.
- Manually: replace the `custom_components/adria_mach` folder and restart.

## FAQ

### Is this an official Adria or Solvesall integration?

No. It was built by reading what the official app sends and receives, for personal use. There is no
public API documentation and no support from the manufacturer.

### Where does the data come from?

From the MACH cloud, the same backend the app uses over LTE. The integration logs in with your
account, fetches the full vehicle state in one request every 60 seconds, and sends commands the same
way the app does. Nothing talks to the vehicle directly, so it works from anywhere.

### Does it work with MACH Pure?

Not expected to. MACH Pure is Bluetooth-only and has no cloud connection.

### Why does a gas bottle show 0 % with status "error"?

That is the Mopeka gas sensor on the bottle not reporting, not the integration. The app shows the
same. Check the sensor's battery and placement.

### Why do the lights only have on/off?

The MACH exposes the main internal and external light circuits as on/off. Dimmable light groups and
scenes exist in the data and may be added later.

### What is the heater setpoint range?

The number entity allows 5–30 °C in whole degrees. That range is an assumption based on typical Alde
panels; the backend has only been tested with whole degrees.

### Can I change how often it polls?

Not yet. The interval is fixed at 60 seconds, which matches how often the app itself refreshes.

### Something stopped working after an app update

The cloud endpoints are undocumented and may change. Check the Home Assistant log for `adria_mach`
and open an issue with the log lines (never include your password or token).

### How do I uninstall it?

Remove the integration under *Settings → Devices & services*, then remove it in HACS (or delete the
`custom_components/adria_mach` folder) and restart Home Assistant.

## Development

`mach_client.py` in the repository root is a small standalone test client that logs in and prints the
main values. Copy `.env.example` to `.env`, fill in your account, and run `python mach_client.py`.
It never prints your password or token.
