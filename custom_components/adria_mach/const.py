"""Constants for the Adria MACH integration."""

DOMAIN = "adria_mach"

CONF_MACH_ID = "mach_id"

BASE_URL = "https://mach-backend.solvesall.com"
USER_AGENT = "home-assistant-adria-mach/0.1"

DEFAULT_SCAN_INTERVAL = 60  # seconds

# Value the backend uses for "not set"
NOT_SET = -9007199254740991

# Safety margin before token expiry (seconds)
TOKEN_MARGIN = 120
