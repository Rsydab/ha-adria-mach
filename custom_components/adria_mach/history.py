"""Import the unit's 7-day history (getChart) into recorder statistics.

Runs once per setup in the background. Each series is imported as hourly
mean/min/max statistics on the sensor's own entity id, so the week before
the integration was installed shows up in Home Assistant's history and
statistics graphs. Hours are aligned to the top of the hour as the recorder
requires; the current, unfinished hour is left to the recorder itself.

A series is skipped when the chart's newest value contradicts the live
value, which has been observed for some values on some units.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .api import AdriaMachError
from .const import DOMAIN, HISTORY_SENSORS
from .coordinator import AdriaMachCoordinator

_LOGGER = logging.getLogger(__name__)

TOLERANCE = 1.0


async def async_import_history(
    hass: HomeAssistant, entry: ConfigEntry, coordinator: AdriaMachCoordinator
) -> None:
    if "recorder" not in hass.config.components:
        _LOGGER.debug("Recorder not loaded; skipping history import")
        return
    try:
        from homeassistant.components.recorder.models import (  # noqa: PLC0415
            StatisticData,
            StatisticMeanType,
            StatisticMetaData,
        )
        from homeassistant.components.recorder.statistics import (  # noqa: PLC0415
            async_import_statistics,
        )
    except ImportError as err:
        _LOGGER.debug("Statistics import unavailable: %s", err)
        return

    registry = er.async_get(hass)
    mach_id = coordinator.api.mach_id
    now_hour = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    imported = 0

    for key, unit, unit_class in HISTORY_SENSORS:
        entity_id = registry.async_get_entity_id("sensor", DOMAIN, f"{mach_id}_{key}")
        if not entity_id:
            continue
        try:
            points = await coordinator.api.async_get_chart(key)
        except AdriaMachError as err:
            _LOGGER.warning("History for %s not available: %s", key, err)
            continue
        if not points:
            continue

        newest_value = max(points)[1]
        live = coordinator.data.get(key)
        try:
            live_value = float(live) if live not in (None, "") else None
        except (TypeError, ValueError):
            live_value = None
        if live_value is not None and abs(newest_value - live_value) > TOLERANCE:
            _LOGGER.warning(
                "Skipping history import for %s: chart says %s but live value is %s",
                key, newest_value, live_value,
            )
            continue

        by_hour: dict[datetime, float] = {}
        for ts, value in sorted(points):
            start = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).replace(
                minute=0, second=0, microsecond=0
            )
            if start < now_hour:
                by_hour[start] = value
        if not by_hour:
            continue

        statistics = [
            StatisticData(start=start, mean=value, min=value, max=value)
            for start, value in sorted(by_hour.items())
        ]
        metadata = StatisticMetaData(
            mean_type=StatisticMeanType.ARITHMETIC,
            has_sum=False,
            name=None,
            source="recorder",
            statistic_id=entity_id,
            unit_of_measurement=unit,
            unit_class=unit_class,
        )
        try:
            async_import_statistics(hass, metadata, statistics)
            imported += 1
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Could not import history for %s: %s", key, err)

    if imported:
        _LOGGER.info("Imported 7-day history for %d Adria MACH sensors", imported)
