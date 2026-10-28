"""Device tracker (GPS position of the vehicle) for Adria MACH."""

from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AdriaMachConfigEntry
from .entity import AdriaMachEntity

DESCRIPTION = EntityDescription(key="GPS_LATITUDE", translation_key="position")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdriaMachConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([AdriaMachTracker(entry.runtime_data, DESCRIPTION)])


def _float(value) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


class AdriaMachTracker(AdriaMachEntity, TrackerEntity):
    """Vehicle position from the MACH unit's GPS."""

    _attr_source_type = SourceType.GPS
    _attr_icon = "mdi:caravan"

    @property
    def latitude(self) -> float | None:
        return _float(self.coordinator.data.get("GPS_LATITUDE"))

    @property
    def longitude(self) -> float | None:
        return _float(self.coordinator.data.get("GPS_LONGITUDE"))

    @property
    def extra_state_attributes(self) -> dict:
        d = self.coordinator.data
        return {
            "altitude": _float(d.get("GPS_ALTITUDE")),
            "velocity": _float(d.get("GPS_VELOCITY")),
            "satellites": d.get("GPS_VISIBLE_SATELLITES"),
        }
