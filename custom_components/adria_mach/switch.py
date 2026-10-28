"""Switch platform for Adria MACH (heater on/off)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AdriaMachConfigEntry
from .entity import AdriaMachEntity

SWITCHES: tuple[SwitchEntityDescription, ...] = (
    SwitchEntityDescription(
        key="AIR_HEATER_VALUE",
        translation_key="heater",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:radiator",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdriaMachConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(AdriaMachSwitch(coordinator, d) for d in SWITCHES)


class AdriaMachSwitch(AdriaMachEntity, SwitchEntity):
    """An on/off value controlled through setValue."""

    entity_description: SwitchEntityDescription

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get(self.entity_description.key)
        return None if value is None else str(value).lower() == "on"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_set_value("on")

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_set_value("off")
