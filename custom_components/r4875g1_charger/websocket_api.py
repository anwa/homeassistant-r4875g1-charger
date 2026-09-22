"""WebSocket API for the R4875G1 Charger integration."""

from __future__ import annotations

from typing import Any, cast

import probatio

from homeassistant.auth.permissions.const import POLICY_CONTROL, POLICY_READ
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, Unauthorized

from .const import CONTRACT_ROLE, DOMAIN
from .control import CONTROL_SPECS
from .instance import ChargerControlError, ChargerInstance
from .subscription import ChargerInstanceSubscription


@callback
def async_register_websocket_api(hass: HomeAssistant) -> None:
    """Register the Charger Instance WebSocket API."""
    websocket_api.async_register_command(hass, websocket_list_instances)
    websocket_api.async_register_command(hass, websocket_get_instance)
    websocket_api.async_register_command(hass, websocket_control_instance)
    websocket_api.async_register_command(hass, websocket_subscribe_instance)


@callback
@websocket_api.websocket_command(
    {probatio.Required("type"): "r4875g1_charger/instances"}
)
def websocket_list_instances(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """List all readable loaded R4875G1 Charger Instances."""
    instances = []

    for entry in hass.config_entries.async_loaded_entries(DOMAIN):
        instance = cast(ChargerInstance, entry.runtime_data)

        if not _can_read_instance(connection, instance):
            continue

        instances.append(instance.summary(entry.entry_id))

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
    """Return one permission-filtered semantic Charger Instance snapshot."""
    entry = _loaded_entry(hass, msg["config_entry_id"])

    if entry is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Charger Instance not found",
        )
        return

    instance = cast(ChargerInstance, entry.runtime_data)
    _require_instance_read_permission(connection, instance)

    connection.send_result(
        msg["id"],
        instance.snapshot(
            entry.entry_id,
            can_read=lambda entity_id: _can_read_entity(
                connection,
                entity_id,
            ),
        ),
    )


@websocket_api.websocket_command(
    {
        probatio.Required("type"): "r4875g1_charger/control",
        probatio.Required("config_entry_id"): str,
        probatio.Required("role"): str,
        probatio.Optional("value"): probatio.Any(
            bool, probatio.Coerce(float)
        ),
    }
)
@websocket_api.async_response
async def websocket_control_instance(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Dispatch one allow-listed semantic control."""
    entry = _loaded_entry(hass, msg["config_entry_id"])

    if entry is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Charger Instance not found",
        )
        return

    role = msg["role"]

    if role not in CONTROL_SPECS:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_SUPPORTED,
            f"Semantic role {role} is not writable",
        )
        return

    instance = cast(ChargerInstance, entry.runtime_data)
    resolved = instance.role(role)

    if resolved is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            f"Semantic role {role} is not currently resolved",
        )
        return

    if not connection.user.permissions.check_entity(
        resolved.entity_id,
        POLICY_CONTROL,
    ):
        raise Unauthorized(entity_id=resolved.entity_id)

    try:
        result = await instance.async_control(
            role,
            value=msg.get("value"),
            context=connection.context(msg),
        )
    except ChargerControlError as err:
        connection.send_error(
            msg["id"],
            _websocket_error_code(err.code),
            err.message,
        )
        return
    except HomeAssistantError as err:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_HOME_ASSISTANT_ERROR,
            str(err),
        )
        return

    connection.send_result(msg["id"], result)


@callback
@websocket_api.websocket_command(
    {
        probatio.Required("type"): "r4875g1_charger/subscribe",
        probatio.Required("config_entry_id"): str,
    }
)
def websocket_subscribe_instance(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Subscribe to semantic live updates for one Charger Instance."""
    entry = _loaded_entry(hass, msg["config_entry_id"])

    if entry is None:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Charger Instance not found",
        )
        return

    instance = cast(ChargerInstance, entry.runtime_data)
    _require_instance_read_permission(connection, instance)

    subscription = ChargerInstanceSubscription(
        hass,
        instance,
        entry.entry_id,
        lambda event: connection.send_event(msg["id"], event),
        lambda entity_id: _can_read_entity(connection, entity_id),
    )

    connection.subscriptions[msg["id"]] = subscription.start()
    connection.send_result(msg["id"])
    subscription.send_initial_snapshot()


def _loaded_entry(hass: HomeAssistant, config_entry_id: str):
    """Return one loaded integration config entry by ID."""
    return next(
        (
            candidate
            for candidate in hass.config_entries.async_loaded_entries(DOMAIN)
            if candidate.entry_id == config_entry_id
        ),
        None,
    )


def _can_read_instance(
    connection: websocket_api.ActiveConnection,
    instance: ChargerInstance,
) -> bool:
    """Return whether the user may read the Contract marker for an instance."""
    entity_id = instance.entity_id(CONTRACT_ROLE)
    return (
        entity_id is not None
        and _can_read_entity(connection, entity_id)
    )


def _require_instance_read_permission(
    connection: websocket_api.ActiveConnection,
    instance: ChargerInstance,
) -> None:
    """Require read access to the Contract marker for one Charger Instance."""
    entity_id = instance.entity_id(CONTRACT_ROLE)

    if entity_id is None:
        raise Unauthorized()

    if not _can_read_entity(connection, entity_id):
        raise Unauthorized(entity_id=entity_id)


def _can_read_entity(
    connection: websocket_api.ActiveConnection,
    entity_id: str,
) -> bool:
    """Return whether the WebSocket user may read one Home Assistant entity."""
    return connection.user.permissions.check_entity(
        entity_id,
        POLICY_READ,
    )


def _websocket_error_code(control_error_code: str) -> str:
    """Map semantic control errors to Home Assistant WebSocket error codes."""
    if control_error_code == "instance_unavailable":
        return websocket_api.ERR_NOT_ALLOWED

    if control_error_code in {
        "role_not_writable",
        "role_domain_mismatch",
    }:
        return websocket_api.ERR_NOT_SUPPORTED

    if control_error_code in {
        "role_unresolved",
        "entity_unavailable",
    }:
        return websocket_api.ERR_NOT_FOUND

    return websocket_api.ERR_INVALID_FORMAT
