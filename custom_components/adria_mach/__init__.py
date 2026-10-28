"""The Adria MACH integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AdriaMachApi
from .const import CONF_MACH_ID, DEFAULT_SCAN_INTERVAL
from .coordinator import AdriaMachCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.LIGHT,
    Platform.SWITCH,
    Platform.NUMBER,
]

type AdriaMachConfigEntry = ConfigEntry[AdriaMachCoordinator]


def _scan_interval(entry: ConfigEntry) -> int:
    return int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))


async def async_setup_entry(hass: HomeAssistant, entry: AdriaMachConfigEntry) -> bool:
    """Set up Adria MACH from a config entry."""
    api = AdriaMachApi(
        async_get_clientsession(hass),
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        entry.data[CONF_MACH_ID],
    )
    coordinator = AdriaMachCoordinator(hass, api, _scan_interval(entry))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_options_updated(hass: HomeAssistant, entry: AdriaMachConfigEntry) -> None:
    """Apply a changed poll interval without reloading."""
    entry.runtime_data.update_interval = timedelta(seconds=_scan_interval(entry))


async def async_unload_entry(hass: HomeAssistant, entry: AdriaMachConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
