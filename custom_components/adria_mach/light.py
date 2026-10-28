"""Light platform for Adria MACH (on/off lights)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.light import ColorMode, LightEntity, LightEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AdriaMachConfigEntry
from .entity import AdriaMachEntity

LIGHTS: tuple[LightEntityDescription, ...] = (
    LightEntityDescription(key="INTERNAL_LIGHT_VALUE", translation_key="internal_lights"),
    LightEntityDescription(key="EXTERNAL_LIGHT_VALUE", translation_key="external_lights"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdriaMachConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(AdriaMachLight(coordinator, d) for d in LIGHTS)


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
