"""R4875G1 Charger Home Assistant integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.typing import ConfigType

from .const import CONF_CHARGER_DEVICE_ID, CONF_CONTRACT_VERSION
from .instance import ChargerInstance
from .resolver import ChargerSourceError
from .websocket_api import async_register_websocket_api

type R4875G1ChargerConfigEntry = ConfigEntry[ChargerInstance]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the R4875G1 Charger integration."""
    async_register_websocket_api(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: R4875G1ChargerConfigEntry,
) -> bool:
    """Set up one configured Charger Instance."""
    try:
        instance = ChargerInstance(
            hass,
            entry.data[CONF_CHARGER_DEVICE_ID],
            entry.data[CONF_CONTRACT_VERSION],
        )
    except ChargerSourceError:
        return False

    entry.runtime_data = instance

    @callback
    def _async_entity_registry_updated(
        event: Event[er.EventEntityRegistryUpdatedData],
    ) -> None:
        """Refresh semantic mappings after relevant registry changes."""
        if not instance.registry_event_affects(event.data):
            return

        try:
            instance.refresh()
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
