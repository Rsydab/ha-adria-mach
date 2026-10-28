"""Constants for the Adria MACH integration."""

DOMAIN = "adria_mach"

CONF_MACH_ID = "mach_id"

BASE_URL = "https://mach-backend.solvesall.com"
USER_AGENT = "home-assistant-adria-mach/0.1"

DEFAULT_SCAN_INTERVAL = 60  # seconds
SCAN_INTERVAL_MIN = 30
SCAN_INTERVAL_MAX = 600

# Device keys that are never exposed as entities (personal identifiers / secrets)
SENSITIVE_KEY_PARTS = ("SIM_ID", "PASSWORD", "_PIN", "USERNAME", "APN", "SMS_FORWARDING", "SHARED")

# _H/_H0/_H1 are duplicate variants of other values; never enabled automatically
VARIANT_SUFFIXES = ("_H", "_H0", "_H1")


def is_variant(key: str) -> bool:
    return any(key.endswith(s) for s in VARIANT_SUFFIXES)


def value_in_use(value) -> bool:
    return value is not None and value != ""


# Light groups. Observed from the app: 0-100 % in the app maps to 1..50 on the
# unit (52 % -> 26, 100 % -> 50), and a group is switched off by sending the
# NOT_SET sentinel. On/off-only groups reject every level except 50 (= on);
# they are learned automatically and listed in this option.
LIGHT_GROUP_KEYS = tuple(f"LIGHT_GROUP_{n}_BRIGHTNESS" for n in range(1, 11))
LIGHT_GROUP_DEVICE_MAX = 50
CONF_ONOFF_LIGHT_GROUPS = "onoff_light_groups"

# Light scenes: "restore" activates, "save" stores the current lights
SCENE_KEYS = tuple(f"LIGHT_SYSTEM_MEMORY_{n}" for n in range(1, 5))

# Synthetic keys added to coordinator data from other calls / computations
KEY_NOTIFICATION_COUNT = "NOTIFICATION_COUNT"
KEY_WIFI_SSID = "WIFI_SSID"
KEY_TILT_FRONT_BACK = "TILT_FRONT_BACK"
KEY_TILT_SIDE = "TILT_SIDE"

# Levelling: the unit's gravity vector when the vehicle was level, stored in
# entry options by the "Calibrate level" button. Without it the unit's X axis
# is assumed vertical (how the unit is mounted on this vehicle).
CONF_LEVEL_REFERENCE = "level_reference"
ACCEL_KEYS = ("ACCELERATION_X", "ACCELERATION_Y", "ACCELERATION_Z")

# User settings are re-read every N polls (names and SSID rarely change)
SETTINGS_REFRESH_POLLS = 60

# Firmware update check (the app's own update service), once per N polls
UPDATES_URL = "https://adria-mach-updates.solvesall.com/api/updates/updatesAvailable"
UPDATES_REFRESH_POLLS = 60
KEY_FIRMWARE_UPDATE = "FIRMWARE_UPDATE_AVAILABLE"
KEY_FIRMWARE_UPDATE_INFO = "FIRMWARE_UPDATE_INFO"

# "All lights off" button in the unit; the app sends "press"
KEY_ALL_LIGHTS_OFF = "LIGHT_SYSTEM_SWITCH_OFF_BUTTON"

# Light group 10 has no name in the app's settings on the vehicle this was
# built on, but is its outdoor light dimmer.
LIGHT_GROUP_DEFAULT_NAMES = {"LIGHT_GROUP_10_BRIGHTNESS": "Outdoor lights"}

# 7-day history (getChart) imported into recorder statistics: key, unit, unit class
HISTORY_SENSORS = (
    ("FRESH_WATER_LEVEL", "%", "unitless"),
    ("WASTE_WATER_LEVEL", "%", "unitless"),
    ("GAS_BOTTLE_LEVEL_P", "%", "unitless"),
    ("GAS_BOTTLE_LEVEL_BACKUP_P", "%", "unitless"),
    ("LIVING_BATTERY_SOC", "%", "unitless"),
    ("LIVING_BATTERY_VOLTAGE", "V", "voltage"),
    ("LIVING_MEASURED_TEMPERATURE", "°C", "temperature"),
    ("OUTSIDE_MEASURED_TEMPERATURE", "°C", "temperature"),
)

# Value the backend uses for "not set"
NOT_SET = -9007199254740991

# Safety margin before token expiry (seconds)
TOKEN_MARGIN = 120
