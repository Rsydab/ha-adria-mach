"""Number platform for Adria MACH: heater setpoint and dimmable light groups."""

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
from .const import LIGHT_GROUP_KEYS, LIGHT_GROUP_MAX, LIGHT_GROUP_MIN, value_in_use
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


def _dimmer_description(key: str, name: str, custom_named: bool, value) -> NumberEntityDescription:
    """One dimmable light group. The unit accepts 1..99; there is no per-group off.

    Groups the owner has named in the app are enabled; unnamed groups are enabled
    only when they currently report a level.
    """
    return NumberEntityDescription(
        key=key,
        name=name,
        native_min_value=LIGHT_GROUP_MIN,
        native_max_value=LIGHT_GROUP_MAX,
        native_step=1,
        mode=NumberMode.SLIDER,
        icon="mdi:brightness-6",
        entity_registry_enabled_default=custom_named or value_in_use(value),
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdriaMachConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities = [AdriaMachNumber(coordinator, d) for d in NUMBERS]
    for key in LIGHT_GROUP_KEYS:
        if key not in coordinator.data:
            continue
        custom_name = coordinator.user_settings.get(f"{key}_name", "")
        number = key.split("_")[2]
        name = custom_name or f"Light group {number}"
        entities.append(
            AdriaMachNumber(
                coordinator,
                _dimmer_description(key, name, bool(custom_name), coordinator.data[key]),
            )
        )
    async_add_entities(entities)


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
