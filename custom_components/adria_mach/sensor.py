"""Sensor platform for Adria MACH."""

from __future__ import annotations

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
        key="AIR_HEATER_TEMPERATURE",
        translation_key="heater_setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermostat",
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
)

NUMERIC_CLASSES = {
    SensorDeviceClass.TEMPERATURE,
    SensorDeviceClass.HUMIDITY,
    SensorDeviceClass.ATMOSPHERIC_PRESSURE,
    SensorDeviceClass.BATTERY,
    SensorDeviceClass.VOLTAGE,
    SensorDeviceClass.CURRENT,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdriaMachConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(AdriaMachSensor(coordinator, d) for d in SENSORS)


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
        return value
