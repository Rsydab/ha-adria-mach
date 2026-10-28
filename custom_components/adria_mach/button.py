"""Button platform for Adria MACH.

- Save the current lights into a scene slot (sends "save", observed from the app).
- Calibrate level: store the current gravity vector as the levelling reference.
"""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AdriaMachConfigEntry
from .const import CONF_LEVEL_REFERENCE, KEY_ALL_LIGHTS_OFF, SCENE_KEYS
from .entity import AdriaMachEntity
from .levelling import accel_vector
from .scene import scene_name

CALIBRATE = ButtonEntityDescription(
    key="ACCELERATION_X",
    translation_key="calibrate_level",
    icon="mdi:axis-z-rotate-clockwise",
    entity_category=EntityCategory.CONFIG,
)

ALL_LIGHTS_OFF = ButtonEntityDescription(
    key=KEY_ALL_LIGHTS_OFF,
    translation_key="all_lights_off",
    icon="mdi:lightbulb-group-off",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdriaMachConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities: list[ButtonEntity] = []
    for key in SCENE_KEYS:
        if key not in coordinator.data:
            continue
        name, custom = scene_name(coordinator, key)
        entities.append(
            AdriaMachSaveSceneButton(
                coordinator,
                ButtonEntityDescription(
                    key=f"{key}_save",
                    name=f"Save scene {name}",
                    icon="mdi:content-save",
                    entity_category=EntityCategory.CONFIG,
                    entity_registry_enabled_default=custom,
                ),
            )
        )
    if accel_vector(coordinator.data) is not None:
        entities.append(AdriaMachCalibrateButton(coordinator, CALIBRATE))
    if KEY_ALL_LIGHTS_OFF in coordinator.data:
        entities.append(AdriaMachPressButton(coordinator, ALL_LIGHTS_OFF))
    async_add_entities(entities)


class AdriaMachPressButton(AdriaMachEntity, ButtonEntity):
    """A button in the unit; the app sends 'press'."""

    async def async_press(self) -> None:
        ok = await self.coordinator.api.async_set_value(self.entity_description.key, "press")
        if not ok:
            raise HomeAssistantError(f"MACH did not accept {self.name}")
        await self.coordinator.async_request_refresh()


class AdriaMachSaveSceneButton(AdriaMachEntity, ButtonEntity):
    """Store the current light state into a scene slot."""

    @property
    def available(self) -> bool:
        key = self.entity_description.key.removesuffix("_save")
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and key in self.coordinator.data
        )

    async def async_press(self) -> None:
        key = self.entity_description.key.removesuffix("_save")
        ok = await self.coordinator.api.async_set_value(key, "save")
        if not ok:
            raise HomeAssistantError(f"MACH did not save scene {self.name}")


class AdriaMachCalibrateButton(AdriaMachEntity, ButtonEntity):
    """Store the current gravity vector as 'level'."""

    async def async_press(self) -> None:
        acc = accel_vector(self.coordinator.data)
        if acc is None:
            raise HomeAssistantError("No accelerometer reading available")
        entry = self.coordinator.config_entry
        self.hass.config_entries.async_update_entry(
            entry, options={**entry.options, CONF_LEVEL_REFERENCE: list(acc)}
        )
