"""Read-only WebSocket API for the R4875G1 Charger integration."""

from __future__ import annotations

from typing import Any, cast

import probatio

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .instance import ChargerInstance


@callback
def async_register_websocket_api(hass: HomeAssistant) -> None:
    """Register the read-only Charger Instance WebSocket API."""
    websocket_api.async_register_command(hass, websocket_list_instances)
    websocket_api.async_register_command(hass, websocket_get_instance)


@callback
@websocket_api.websocket_command(
    {probatio.Required("type"): "r4875g1_charger/instances"}
)
def websocket_list_instances(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """List all loaded R4875G1 Charger Instances."""
    instances = [
        cast(ChargerInstance, entry.runtime_data).summary(entry.entry_id)
        for entry in hass.config_entries.async_loaded_entries(DOMAIN)
    ]
    connection.send_result(msg["id"], {"instances": instances})


@callback
@websocket_api.websocket_command(
    {
        probatio.Required("type"): "r4875g1_charger/instance",
        probatio.Required("config_entry_id"): str,
    }
)
def websocket_get_instance(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return one semantic Charger Instance snapshot."""
    config_entry_id = msg["config_entry_id"]

    entry = next(
        (
            candidate
            for candidate in hass.config_entries.async_loaded_entries(DOMAIN)
            if candidate.entry_id == config_entry_id
        ),
        None,
    )

    if entry is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Charger Instance not found",
        )
        return

    instance = cast(ChargerInstance, entry.runtime_data)
    connection.send_result(
        msg["id"],
        instance.snapshot(entry.entry_id),
    )
