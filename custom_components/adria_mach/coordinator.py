"""Data update coordinator for Adria MACH."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AdriaMachApi, AdriaMachAuthError, AdriaMachConnectionError, AdriaMachError
from .const import (
    CONF_LEVEL_REFERENCE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    KEY_NOTIFICATION_COUNT,
    KEY_TILT_FRONT_BACK,
    KEY_TILT_SIDE,
    KEY_WIFI_SSID,
    SETTINGS_REFRESH_POLLS,
)
from .levelling import accel_vector, tilt_angles

_LOGGER = logging.getLogger(__name__)


class AdriaMachCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls getValuesAll (plus notification count) on a fixed interval."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: AdriaMachApi,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api
        self.mach_info: dict[str, Any] = {}
        self.user_settings: dict[str, str] = {}
        self._polls = 0

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            if not self.mach_info:
                self.mach_info = await self.api.async_get_mach_info()
            data = await self.api.async_get_all_values()
            if not self.user_settings or self._polls % SETTINGS_REFRESH_POLLS == 0:
                self.user_settings = await self.api.async_get_user_settings()
            self._polls += 1
        except AdriaMachAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except AdriaMachConnectionError as err:
            raise UpdateFailed(f"Connection failed: {err}") from err

        # Secondary values: a failure here must not fail the whole update.
        try:
            data[KEY_NOTIFICATION_COUNT] = await self.api.async_count_notifications()
        except AdriaMachError as err:
            _LOGGER.debug("Notification count unavailable: %s", err)
        if ssid := self.user_settings.get("wifiSsid"):
            data[KEY_WIFI_SSID] = ssid

        # Levelling from the unit's accelerometer, relative to the stored reference.
        if (acc := accel_vector(data)) is not None:
            reference = (self.config_entry.options or {}).get(CONF_LEVEL_REFERENCE)
            if (angles := tilt_angles(acc, reference)) is not None:
                data[KEY_TILT_FRONT_BACK], data[KEY_TILT_SIDE] = angles
        return data
