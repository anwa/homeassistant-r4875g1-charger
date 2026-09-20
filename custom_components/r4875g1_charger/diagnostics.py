"""Diagnostics for the R4875G1 Charger integration."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import R4875G1ChargerConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: R4875G1ChargerConfigEntry,
) -> dict[str, Any]:
    """Return the active runtime resolution for one Charger Instance."""
    return entry.runtime_data.as_diagnostics()
