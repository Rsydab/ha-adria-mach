"""Sensor platform for Adria MACH.

Two kinds of sensors:
- curated ones with proper names, units and device classes (SENSORS below)
- one generic sensor per remaining device value the unit reports. Those are
  enabled automatically when the value is in use at setup time, and created
  disabled otherwise (empty values, and the _H/_H0/_H1 duplicate variants),
  so every value is available without cluttering the device.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AdriaMachConfigEntry
from .const import (
    KEY_NOTIFICATION_COUNT,
    KEY_WIFI_SSID,
    LIGHT_GROUP_KEYS,
    SENSITIVE_KEY_PARTS,
    is_variant,
    value_in_use,
)
from .entity import AdriaMachEntity

SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="LIVING_MEASURED_TEMPERATURE",
        translation_key="inside_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="OUTSIDE_MEASURED_TEMPERATURE",
        translation_key="outside_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="OUTSIDE_MEASURED_HUMIDITY",
        translation_key="outside_humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="MEASURED_PRESSURE",
        translation_key="air_pressure",
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        native_unit_of_measurement=UnitOfPressure.HPA,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="FRESH_WATER_LEVEL",
        translation_key="fresh_water",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water",
    ),
    SensorEntityDescription(
        key="WASTE_WATER_LEVEL",
        translation_key="waste_water",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-off",
    ),
    SensorEntityDescription(
        key="GAS_BOTTLE_LEVEL_P",
        translation_key="gas_bottle_1",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon="mdi:gas-cylinder",
    ),
    SensorEntityDescription(
        key="GAS_BOTTLE_LEVEL_BACKUP_P",
        translation_key="gas_bottle_2",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon="mdi:gas-cylinder",
    ),
    SensorEntityDescription(
        key="GAS_SENSOR_MEASUREMENT_STATUS",
        translation_key="gas_sensor_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:gas-cylinder",
    ),
    SensorEntityDescription(
        key="GAS_SENSOR_BATTERY_LEVEL",
        translation_key="gas_sensor_battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="LIVING_BATTERY_SOC",
        translation_key="battery_soc",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="LIVING_BATTERY_VOLTAGE",
        translation_key="battery_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="LIVING_BATTERY_CURRENT",
        translation_key="battery_current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="ENERGY_SOURCE",
        translation_key="energy_source",
        icon="mdi:power-plug",
    ),
    SensorEntityDescription(
        key="HEATER_NOTIFICATION",
        translation_key="heater_notification",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:radiator",
    ),
    SensorEntityDescription(
        key="LTE_SIGNAL_STRENGTH",
        translation_key="lte_signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:signal",
    ),
    SensorEntityDescription(
        key="MACH_TEMPERATURE",
        translation_key="unit_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="SYSTEM_IO_FIRMWARE_VERSION",
        translation_key="firmware",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:chip",
    ),
    SensorEntityDescription(
        key=KEY_NOTIFICATION_COUNT,
        translation_key="notifications",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:bell",
    ),
    SensorEntityDescription(
        key=KEY_WIFI_SSID,
        translation_key="wifi_ssid",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:wifi",
    ),
)

NUMERIC_CLASSES = {
    SensorDeviceClass.TEMPERATURE,
    SensorDeviceClass.HUMIDITY,
    SensorDeviceClass.ATMOSPHERIC_PRESSURE,
    SensorDeviceClass.BATTERY,
    SensorDeviceClass.VOLTAGE,
    SensorDeviceClass.CURRENT,
}

# Keys already represented by another platform (binary_sensor, light, switch,
# number, device_tracker) and therefore not duplicated as generic sensors.
COVERED_BY_OTHER_PLATFORMS = {
    "MAINS_SUPPLY_VALUE",
    "ALDE_PANEL_VALUE",
    "AIR_HEATER_WORKING",
    "WATER_HEATER_WORKING",
    "WATER_PUMP_VALUE",
    "INTERNAL_LIGHT_VALUE",
    "EXTERNAL_LIGHT_VALUE",
    "AIR_HEATER_VALUE",
    "AIR_HEATER_TEMPERATURE",
    "GPS_LATITUDE",
    "GPS_LONGITUDE",
    *LIGHT_GROUP_KEYS,
}

NO_STATS_PARTS = ("TIME", "UTC", "VERSION")


def _is_sensitive(key: str) -> bool:
    return any(part in key for part in SENSITIVE_KEY_PARTS)


def _unit_and_class(key: str) -> tuple[str | None, SensorDeviceClass | None]:
    if "TEMPERATURE" in key:
        return UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE
    if "HUMIDITY" in key:
        return PERCENTAGE, SensorDeviceClass.HUMIDITY
    if key.endswith(("_P", "_SOC", "_SOH")) or "BATTERY_LEVEL" in key:
        return PERCENTAGE, None
    if "VOLTAGE" in key:
        return UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE
    if "CURRENT" in key:
        return UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT
    return None, None


def _generic_description(key: str, value: Any) -> SensorEntityDescription:
    numeric = isinstance(value, (int, float)) and not isinstance(value, bool)
    unit, device_class = _unit_and_class(key) if numeric else (None, None)
    state_class = (
        SensorStateClass.MEASUREMENT
        if numeric and not any(p in key for p in NO_STATS_PARTS)
        else None
    )
    return SensorEntityDescription(
        key=key,
        name=key.replace("_", " ").capitalize(),
        native_unit_of_measurement=unit,
        device_class=device_class,
        state_class=state_class,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=value_in_use(value) and not is_variant(key),
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdriaMachConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities: list[AdriaMachSensor] = [AdriaMachSensor(coordinator, d) for d in SENSORS]

    curated = {d.key for d in SENSORS} | COVERED_BY_OTHER_PLATFORMS
    for key in sorted(coordinator.data or {}):
        if key in curated or _is_sensitive(key):
            continue
        entities.append(
            AdriaMachSensor(coordinator, _generic_description(key, coordinator.data[key]))
        )
    async_add_entities(entities)


class AdriaMachSensor(AdriaMachEntity, SensorEntity):
    """One value from getValuesAll."""

    entity_description: SensorEntityDescription

    @property
    def native_value(self):
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None or value == "":
            return None
        numeric = (
            self.entity_description.device_class in NUMERIC_CLASSES
            or self.entity_description.state_class is not None
        )
        if numeric and isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
        if not numeric and not isinstance(value, str):
            return str(value)
        return value
