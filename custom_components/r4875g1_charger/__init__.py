"""R4875G1 Charger Home Assistant integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_CHARGER_DEVICE_ID, CONF_CONTRACT_VERSION
from .models import ChargerResolution
from .resolver import ChargerSourceError, resolve_charger

type R4875G1ChargerConfigEntry = ConfigEntry[ChargerResolution]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: R4875G1ChargerConfigEntry,
) -> bool:
    """Set up one configured Charger Instance."""
    try:
        resolution = resolve_charger(
            hass,
            entry.data[CONF_CHARGER_DEVICE_ID],
            configured_contract_version=entry.data[
                CONF_CONTRACT_VERSION
            ],
        )
    except ChargerSourceError:
        return False

    entry.runtime_data = resolution
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: R4875G1ChargerConfigEntry,
) -> bool:
    """Unload one configured Charger Instance."""
    return True
