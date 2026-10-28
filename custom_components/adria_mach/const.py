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

# Value the backend uses for "not set"
NOT_SET = -9007199254740991

# Safety margin before token expiry (seconds)
TOKEN_MARGIN = 120
