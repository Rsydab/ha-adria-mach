"""Light platform for Adria MACH.

- Internal/external light circuits: on/off.
- Light groups: on/off with brightness, named as in the app. The unit does not
  report a group's level while it is on (only briefly after it is set), so the
  group lights keep the last commanded state (assumed state). A group is
  switched off by sending the unit's "not set" sentinel; 0-100 % maps to 1..50.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AdriaMachConfigEntry
from .api import AdriaMachError
from .const import LIGHT_GROUP_DEVICE_MAX, LIGHT_GROUP_KEYS, NOT_SET, value_in_use
from .entity import AdriaMachEntity

_LOGGER = logging.getLogger(__name__)

LIGHTS: tuple[LightEntityDescription, ...] = (
    LightEntityDescription(key="INTERNAL_LIGHT_VALUE", translation_key="internal_lights"),
    LightEntityDescription(key="EXTERNAL_LIGHT_VALUE", translation_key="external_lights"),
)


def _ha_to_device(brightness: int) -> int:
    """HA 1..255 -> unit 1..50."""
    return max(1, min(LIGHT_GROUP_DEVICE_MAX, round(brightness / 255 * LIGHT_GROUP_DEVICE_MAX)))


def _device_to_ha(value: float) -> int:
    """Unit 1..50 -> HA 1..255."""
    return max(1, min(255, round(float(value) / LIGHT_GROUP_DEVICE_MAX * 255)))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdriaMachConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities: list[LightEntity] = [AdriaMachLight(coordinator, d) for d in LIGHTS]
    for key in LIGHT_GROUP_KEYS:
        if key not in coordinator.data:
            continue
        custom_name = coordinator.user_settings.get(f"{key}_name", "")
        number = key.split("_")[2]
        entities.append(
            AdriaMachGroupLight(
                coordinator,
                LightEntityDescription(
                    key=key,
                    name=custom_name or f"Light group {number}",
                    entity_registry_enabled_default=bool(custom_name)
                    or value_in_use(coordinator.data[key]),
                ),
            )
        )
    async_add_entities(entities)


class AdriaMachLight(AdriaMachEntity, LightEntity):
    """An on/off light controlled through setValue."""

    entity_description: LightEntityDescription
    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get(self.entity_description.key)
        return None if value is None else str(value).lower() == "on"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_set_value("on")

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_set_value("off")


class AdriaMachGroupLight(AdriaMachEntity, LightEntity):
    """A light group with brightness. State is assumed from the last command."""

    entity_description: LightEntityDescription
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_assumed_state = True

    def __init__(self, coordinator, description: LightEntityDescription) -> None:
        super().__init__(coordinator, description)
        self._is_on = False
        self._brightness = 255
        self._sync_from_data()

    def _sync_from_data(self) -> None:
        """A reported level means the group is on at that level; 'not set' says nothing."""
        value = self.coordinator.data.get(self.entity_description.key)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0:
            self._is_on = True
            self._brightness = _device_to_ha(value)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._sync_from_data()
        super()._handle_coordinator_update()

    @property
    def is_on(self) -> bool:
        return self._is_on

    @property
    def brightness(self) -> int:
        return self._brightness

    async def _send(self, value: Any) -> bool:
        try:
            return await self.coordinator.api.async_set_value(self.entity_description.key, value)
        except AdriaMachError as err:
            raise HomeAssistantError(f"Could not control {self.name}: {err}") from err

    async def async_turn_on(self, **kwargs: Any) -> None:
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = int(kwargs[ATTR_BRIGHTNESS])
        level = _ha_to_device(self._brightness)
        ok = await self._send(level)
        if not ok and level != LIGHT_GROUP_DEVICE_MAX:
            # On/off-only groups reject levels; full is the best fallback.
            ok = await self._send(LIGHT_GROUP_DEVICE_MAX)
            if ok:
                self._brightness = 255
        if not ok:
            raise HomeAssistantError(
                f"{self.name} did not accept a level; it may be an on/off-only group"
            )
        self._is_on = True
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        if not await self._send(NOT_SET):
            raise HomeAssistantError(f"{self.name} did not switch off")
        self._is_on = False
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
