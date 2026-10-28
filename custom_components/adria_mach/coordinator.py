"""Data update coordinator for Adria MACH."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AdriaMachApi, AdriaMachAuthError, AdriaMachConnectionError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class AdriaMachCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls getValuesAll on a fixed interval."""

    def __init__(self, hass: HomeAssistant, api: AdriaMachApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api
        self.mach_info: dict[str, Any] = {}

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            if not self.mach_info:
                self.mach_info = await self.api.async_get_mach_info()
            return await self.api.async_get_all_values()
        except AdriaMachAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except AdriaMachConnectionError as err:
            raise UpdateFailed(f"Connection failed: {err}") from err
