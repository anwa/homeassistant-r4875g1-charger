"""R4875G1 Charger Home Assistant integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

from .const import CONF_CHARGER_DEVICE_ID, CONF_CONTRACT_VERSION
from .models import ChargerResolution
from .resolver import ChargerSourceError, resolve_charger

type R4875G1ChargerConfigEntry = ConfigEntry[ChargerResolution]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: R4875G1ChargerConfigEntry,
) -> bool:
    """Set up one configured Charger Instance."""
    try:
        entry.runtime_data = _resolve_entry(hass, entry)
    except ChargerSourceError:
        return False

    @callback
    def _async_entity_registry_updated(_: Event) -> None:
        """Refresh semantic mappings after entity-registry changes."""
        try:
            entry.runtime_data = _resolve_entry(hass, entry)
        except ChargerSourceError as err:
            _LOGGER.warning(
                "Could not refresh Charger Instance after registry update: %s",
                err.code,
            )

    entry.async_on_unload(
        hass.bus.async_listen(
            er.EVENT_ENTITY_REGISTRY_UPDATED,
            _async_entity_registry_updated,
        )
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: R4875G1ChargerConfigEntry,
) -> bool:
    """Unload one configured Charger Instance."""
    return True


def _resolve_entry(
    hass: HomeAssistant,
    entry: R4875G1ChargerConfigEntry,
) -> ChargerResolution:
    """Resolve the current semantic mapping for one config entry."""
    return resolve_charger(
        hass,
        entry.data[CONF_CHARGER_DEVICE_ID],
        configured_contract_version=entry.data[CONF_CONTRACT_VERSION],
    )
