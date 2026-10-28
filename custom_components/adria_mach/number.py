"""Number platform for Adria MACH (heater setpoint)."""

from __future__ import annotations

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AdriaMachConfigEntry
from .entity import AdriaMachEntity

# Range is an assumption based on typical Alde panels; the API has not been
# observed to reject values, but it has only been tested with whole degrees.
NUMBERS: tuple[NumberEntityDescription, ...] = (
    NumberEntityDescription(
        key="AIR_HEATER_TEMPERATURE",
        translation_key="heater_setpoint",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=5,
        native_max_value=30,
        native_step=1,
        mode=NumberMode.BOX,
        icon="mdi:thermostat",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdriaMachConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(AdriaMachNumber(coordinator, d) for d in NUMBERS)


class AdriaMachNumber(AdriaMachEntity, NumberEntity):
    """A numeric value controlled through setValue."""

    entity_description: NumberEntityDescription

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get(self.entity_description.key)
        try:
            return float(value) if value not in (None, "") else None
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        await self._async_set_value(int(value) if value.is_integer() else value)
