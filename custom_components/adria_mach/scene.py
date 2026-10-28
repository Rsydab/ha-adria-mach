"""Scene platform for Adria MACH: the unit's light scenes, named as in the app.

Activating a scene sends "restore" to the scene slot (observed from the app).
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.scene import Scene
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AdriaMachConfigEntry
from .const import SCENE_KEYS
from .entity import AdriaMachEntity


def scene_name(coordinator, key: str) -> tuple[str, bool]:
    """(name, custom) for a scene slot: the app's name if set, else a generic one."""
    custom = coordinator.user_settings.get(f"{key}_name", "")
    number = key.rsplit("_", 1)[1]
    return (custom or f"Light scene {number}", bool(custom))


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
            AdriaMachScene(
                coordinator,
                EntityDescription(key=key, name=name, entity_registry_enabled_default=custom),
            )
        )
    async_add_entities(entities)


class AdriaMachScene(AdriaMachEntity, Scene):
    """Activate a stored light scene."""

    _attr_icon = "mdi:lightbulb-group"

    async def async_activate(self, **kwargs: Any) -> None:
        await self._async_set_value("restore")
