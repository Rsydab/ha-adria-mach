"""Base entity for Adria MACH."""

from __future__ import annotations

from typing import Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import AdriaMachError
from .const import DOMAIN
from .coordinator import AdriaMachCoordinator


class AdriaMachEntity(CoordinatorEntity[AdriaMachCoordinator]):
    """Common device info and unique id handling."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: AdriaMachCoordinator, description: EntityDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        mach_id = coordinator.api.mach_id
        self._attr_unique_id = f"{mach_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mach_id)},
            name="Adria MACH",
            manufacturer="Adria Mobil / Solvesall",
            model=coordinator.mach_info.get("type") or "MACH",
            sw_version=coordinator.data.get("SYSTEM_IO_FIRMWARE_VERSION")
            if coordinator.data
            else None,
            serial_number=mach_id,
        )

    @property
    def available(self) -> bool:
        return (
            super().available
            and self.coordinator.data is not None
            and self.entity_description.key in self.coordinator.data
        )

    async def _async_set_value(self, value: Any) -> None:
        """Write one value to the unit, update state optimistically, then refresh."""
        key = self.entity_description.key
        try:
            ok = await self.coordinator.api.async_set_value(key, value)
        except AdriaMachError as err:
            raise HomeAssistantError(f"Could not set {key}: {err}") from err
        if not ok:
            raise HomeAssistantError(f"MACH rejected setting {key} to {value!r}")
        if self.coordinator.data is not None:
            self.coordinator.data[key] = value
            self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
