"""Switch platform for Adria MACH: everything the unit exposes as plain on/off."""

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
    SwitchEntityDescription(
        key="WATER_PUMP_VALUE",
        translation_key="water_pump",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:water-pump",
    ),
    SwitchEntityDescription(
        key="AUTOMATIC_CLIMATE_CONTROL_SETTING",
        translation_key="climate_auto",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:thermostat-auto",
    ),
    SwitchEntityDescription(
        key="FRIDGE_VALUE",
        translation_key="fridge",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:fridge",
    ),
    SwitchEntityDescription(
        key="FRIDGE_AUTOMATIC_MODE",
        translation_key="fridge_auto",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:fridge-outline",
    ),
    SwitchEntityDescription(
        key="FRIDGE_FRAME_HEATER_VALUE",
        translation_key="fridge_frame_heater",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:fridge-alert",
    ),
    SwitchEntityDescription(
        key="AUX_VALUE",
        translation_key="aux",
        device_class=SwitchDeviceClass.OUTLET,
        icon="mdi:power-socket-eu",
    ),
    SwitchEntityDescription(
        key="AIR_CONDITION_VALUE",
        translation_key="air_condition",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:air-conditioner",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdriaMachConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        AdriaMachSwitch(coordinator, d) for d in SWITCHES if d.key in coordinator.data
    )


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
