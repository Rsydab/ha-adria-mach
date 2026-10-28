"""Button platform for Adria MACH: save the current lights into a scene slot.

Pressing sends "save" to the scene slot (observed from the app).
"""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AdriaMachConfigEntry
from .const import SCENE_KEYS
from .entity import AdriaMachEntity
from .scene import scene_name


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdriaMachConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities = []
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
    async_add_entities(entities)


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
            from homeassistant.exceptions import HomeAssistantError  # noqa: PLC0415

            raise HomeAssistantError(f"MACH did not save scene {self.name}")
