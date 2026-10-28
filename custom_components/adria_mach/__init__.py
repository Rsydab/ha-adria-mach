"""The Adria MACH integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AdriaMachApi
from .const import CONF_MACH_ID, DEFAULT_SCAN_INTERVAL, is_variant, value_in_use
from .coordinator import AdriaMachCoordinator
from .history import async_import_history

_LOGGER = logging.getLogger(__name__)

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

    _async_enable_values_now_in_use(hass, entry, coordinator)

    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_create_background_task(
        hass, async_import_history(hass, entry, coordinator), "adria_mach_history"
    )
    return True


@callback
def _async_enable_values_now_in_use(
    hass: HomeAssistant, entry: ConfigEntry, coordinator: AdriaMachCoordinator
) -> None:
    """Enable entities this integration created disabled, if their value is now in use.

    Entities the user disabled themselves are left alone. Home Assistant reloads
    the entry shortly after entities are enabled, which sets them up.
    """
    registry = er.async_get(hass)
    prefix = f"{coordinator.api.mach_id}_"
    enabled = 0
    for reg_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        if reg_entry.disabled_by is not er.RegistryEntryDisabler.INTEGRATION:
            continue
        key = reg_entry.unique_id.removeprefix(prefix)
        if is_variant(key) or not value_in_use(coordinator.data.get(key)):
            continue
        registry.async_update_entity(reg_entry.entity_id, disabled_by=None)
        enabled += 1
    if enabled:
        _LOGGER.info("Enabled %d Adria MACH entities whose values are now in use", enabled)


async def _async_options_updated(hass: HomeAssistant, entry: AdriaMachConfigEntry) -> None:
    """Apply a changed poll interval without reloading."""
    entry.runtime_data.update_interval = timedelta(seconds=_scan_interval(entry))


async def async_unload_entry(hass: HomeAssistant, entry: AdriaMachConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
