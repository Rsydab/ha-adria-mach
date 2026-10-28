"""Binary sensor platform for Adria MACH (read-only on/off and open/closed values)."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AdriaMachConfigEntry
from .const import KEY_FIRMWARE_UPDATE, KEY_FIRMWARE_UPDATE_INFO
from .entity import AdriaMachEntity


@dataclass(frozen=True, kw_only=True)
class AdriaMachBinarySensorDescription(BinarySensorEntityDescription):
    """Adds the values that mean 'on'."""

    on_values: tuple[str, ...] = ("on", "true", "1", "yes")


BINARY_SENSORS: tuple[AdriaMachBinarySensorDescription, ...] = (
    AdriaMachBinarySensorDescription(
        key="MAINS_SUPPLY_VALUE",
        translation_key="mains_supply",
        device_class=BinarySensorDeviceClass.PLUG,
    ),
    AdriaMachBinarySensorDescription(
        key="ALDE_PANEL_VALUE",
        translation_key="alde_panel",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    AdriaMachBinarySensorDescription(
        key="AIR_HEATER_WORKING",
        translation_key="heater_working",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AdriaMachBinarySensorDescription(
        key="WATER_HEATER_WORKING",
        translation_key="water_heater_working",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AdriaMachBinarySensorDescription(
        key="FRIDGE_DOOR_VALUE",
        translation_key="fridge_door",
        device_class=BinarySensorDeviceClass.DOOR,
        on_values=("open",),
    ),
    AdriaMachBinarySensorDescription(
        key=KEY_FIRMWARE_UPDATE,
        translation_key="firmware_update",
        device_class=BinarySensorDeviceClass.UPDATE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdriaMachConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        AdriaMachBinarySensor(coordinator, d) for d in BINARY_SENSORS if d.key in coordinator.data
    )


class AdriaMachBinarySensor(AdriaMachEntity, BinarySensorEntity):
    """A read-only two-state value."""

    entity_description: AdriaMachBinarySensorDescription

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        return str(value).lower() in self.entity_description.on_values

    @property
    def extra_state_attributes(self) -> dict | None:
        if self.entity_description.key == KEY_FIRMWARE_UPDATE:
            info = self.coordinator.data.get(KEY_FIRMWARE_UPDATE_INFO) or {}
            return {"update": info} if info else None
        return None
