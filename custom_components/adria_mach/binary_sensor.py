"""Binary sensor platform for Adria MACH (on/off values, read-only)."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AdriaMachConfigEntry
from .entity import AdriaMachEntity

BINARY_SENSORS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="MAINS_SUPPLY_VALUE",
        translation_key="mains_supply",
        device_class=BinarySensorDeviceClass.PLUG,
    ),
    BinarySensorEntityDescription(
        key="ALDE_PANEL_VALUE",
        translation_key="alde_panel",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    BinarySensorEntityDescription(
        key="AIR_HEATER_WORKING",
        translation_key="heater_working",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    BinarySensorEntityDescription(
        key="WATER_HEATER_WORKING",
        translation_key="water_heater_working",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    BinarySensorEntityDescription(
        key="WATER_PUMP_VALUE",
        translation_key="water_pump",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdriaMachConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(AdriaMachBinarySensor(coordinator, d) for d in BINARY_SENSORS)


class AdriaMachBinarySensor(AdriaMachEntity, BinarySensorEntity):
    """An on/off value from getValuesAll."""

    entity_description: BinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None
        return str(value).lower() in ("on", "true", "1", "yes")
