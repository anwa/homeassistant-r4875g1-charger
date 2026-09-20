"""Diagnostics for the R4875G1 Charger integration."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import R4875G1ChargerConfigEntry
from .const import CONF_CHARGER_DEVICE_ID, CONF_CONTRACT_VERSION
from .resolver import ChargerSourceError, resolve_charger


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: R4875G1ChargerConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for one configured Charger Instance."""
    try:
        resolution = resolve_charger(
            hass,
            entry.data[CONF_CHARGER_DEVICE_ID],
            configured_contract_version=entry.data[
                CONF_CONTRACT_VERSION
            ],
        )
    except ChargerSourceError as err:
        return {
            "configured_device_id": entry.data[
                CONF_CHARGER_DEVICE_ID
            ],
            "configured_contract_version": entry.data[
                CONF_CONTRACT_VERSION
            ],
            "resolver_error": err.code,
        }

    return resolution.as_diagnostics()
