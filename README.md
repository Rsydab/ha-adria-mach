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

You now have a device called **Adria MACH** with the entities below. Values refresh every 60 seconds
by default; change it with the gear icon on the integration (30–600 seconds).

## Entities

Entity ids below are for a device named "Adria MACH". Entity names follow the language set in
Home Assistant (English and Swedish are included).

<details>
<summary><b>Sensors</b> (13)</summary>

| Entity | What it shows |
|---|---|
| `sensor.adria_mach_notifications` | Number of notifications in the MACH's own notification centre |
| `sensor.adria_mach_inside_temperature` | Inside temperature, °C |
| `sensor.adria_mach_outside_temperature` | Outside temperature, °C |
| `sensor.adria_mach_outside_humidity` | Outside humidity, % |
| `sensor.adria_mach_air_pressure` | Air pressure, hPa |
| `sensor.adria_mach_fresh_water` | Fresh water tank, % |
| `sensor.adria_mach_waste_water` | Waste water tank, % |
| `sensor.adria_mach_gas_bottle_1` | Gas bottle 1, % |
| `sensor.adria_mach_gas_bottle_2` | Gas bottle 2, % |
| `sensor.adria_mach_leisure_battery` | Leisure battery state of charge, % |
| `sensor.adria_mach_leisure_battery_voltage` | Leisure battery, V |
| `sensor.adria_mach_leisure_battery_current` | Leisure battery, A |
| `sensor.adria_mach_energy_source` | Active energy source (e.g. `el1`) |

</details>

<details>
<summary><b>Diagnostic sensors</b> (7)</summary>

| Entity | What it shows |
|---|---|
| `sensor.adria_mach_wi_fi_ssid` | Name of the MACH's Wi-Fi hotspot |
| `sensor.adria_mach_gas_sensor_status` | Gas sensor measurement status |
| `sensor.adria_mach_gas_sensor_battery` | Gas sensor battery, % |
| `sensor.adria_mach_heater_notification` | Heater notification/error text |
| `sensor.adria_mach_lte_signal` | LTE signal strength |
| `sensor.adria_mach_unit_temperature` | MACH unit temperature, °C |
| `sensor.adria_mach_firmware` | MACH firmware version |

</details>

<details>
<summary><b>Binary sensors</b> (5)</summary>

| Entity | What it shows |
|---|---|
| `binary_sensor.adria_mach_mains_supply` | Connected to mains (shore power) |
| `binary_sensor.adria_mach_alde_panel` | Alde panel powered |
| `binary_sensor.adria_mach_heater_running` | Air heater running |
| `binary_sensor.adria_mach_water_heater_running` | Water heater running |
| `binary_sensor.adria_mach_water_pump` | Water pump on |

</details>

<details>
<summary><b>Lights</b> (2)</summary>

| Entity | Controls |
|---|---|
| `light.adria_mach_internal_lights` | Internal lights, on/off |
| `light.adria_mach_external_lights` | External lights, on/off |

</details>

<details>
<summary><b>Switch</b> (1)</summary>

| Entity | Controls |
|---|---|
| `switch.adria_mach_heater` | Alde air heater on/off |

</details>

<details>
<summary><b>Numbers</b> (1 + one per light group)</summary>

| Entity | Controls |
|---|---|
| `number.adria_mach_heater_setpoint` | Heater setpoint, 5–30 °C |
| `number.adria_mach_<group name>` | Brightness of a dimmable light group, 1–99. One per group, named as in the app (for example `number.adria_mach_takspots_kok`). Groups you have named are enabled; unnamed groups are enabled when they report a level. |

The MACH has no per-group off: a group is dimmed between 1 and 99, and all internal lights
are switched together with `light.adria_mach_internal_lights`.

</details>

<details>
<summary><b>Device tracker</b> (1)</summary>

| Entity | What it shows |
|---|---|
| `device_tracker.adria_mach_position` | Vehicle GPS position, with altitude, speed and satellites as attributes |

</details>

<details>
<summary><b>Everything else the unit reports</b> (about 230 values)</summary>

Every other value the MACH reports is also created as a diagnostic sensor, named after the value,
for example `sensor.adria_mach_fridge_door_value` or `sensor.adria_mach_lte_operator_name`.

- Values that are **in use** when the integration starts are enabled automatically.
- Values that are empty (tyre sensors, Bluetooth batteries, an air conditioner that is not
  fitted) and the duplicate `_H`/`_H0`/`_H1` variants are created **disabled**. Enable any of them
  under the device → *entities not shown*.
- When a value **starts being used later** (you fit tyre sensors, say), its entity is enabled
  automatically at the next restart or reload. Entities you disabled yourself are left alone.
- Personal identifiers (SIM id, PINs, passwords) are never exposed.

</details>

### History

At startup the integration imports the MACH's own 7-day history for the water tanks, gas
bottles, leisure battery and temperatures into Home Assistant's statistics, so the week before you
installed the integration is already in the graphs. A series is skipped when the unit's chart
contradicts its live value.

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

### How do the dimmable light groups work?

Each light group is a number entity, 1–99, named as you named it in the app. The MACH rejects 0 and
100, and it has no per-group off: use `light.adria_mach_internal_lights` to switch all internal
lights. Light scenes exist in the data but are not controllable yet.

### What is the heater setpoint range?

The number entity allows 5–30 °C in whole degrees. That range is an assumption based on typical Alde
panels; the backend has only been tested with whole degrees.

### Can I change how often it polls?

Yes. Click the gear icon on the integration and set the update interval, 30–600 seconds. The default
of 60 seconds matches how often the app itself refreshes. The change applies immediately.

### An entity I want is missing

Open the Adria MACH device and look under *entities not shown*: every value the unit reports is
there, the unused ones disabled. Enable the one you want.

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
