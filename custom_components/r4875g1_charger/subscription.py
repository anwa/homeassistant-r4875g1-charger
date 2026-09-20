"""Semantic live subscription support for one Charger Instance."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.core import (
    CALLBACK_TYPE,
    Event,
    EventStateChangedData,
    HomeAssistant,
    callback,
)
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONTRACT_ROLE
from .instance import ChargerInstance
from .resolver import ChargerSourceError


class ChargerInstanceSubscription:
    """Translate Home Assistant state changes into semantic Charger events."""

    def __init__(
        self,
        hass: HomeAssistant,
        instance: ChargerInstance,
        config_entry_id: str,
        send_event: Callable[[dict[str, Any]], None],
        can_read: Callable[[str], bool],
    ) -> None:
        """Initialize one semantic Charger Instance subscription."""
        self._hass = hass
        self._instance = instance
        self._config_entry_id = config_entry_id
        self._send_event = send_event
        self._can_read = can_read
        self._entity_to_role: dict[str, str] = {}
        self._state_unsub: CALLBACK_TYPE | None = None
        self._registry_unsub: CALLBACK_TYPE | None = None

    @callback
    def start(self) -> CALLBACK_TYPE:
        """Start state and registry tracking and return the unsubscribe callback."""
        self._replace_state_listener()
        self._registry_unsub = self._hass.bus.async_listen(
            er.EVENT_ENTITY_REGISTRY_UPDATED,
            self._async_entity_registry_updated,
        )
        return self.unsubscribe

    @callback
    def send_initial_snapshot(self) -> None:
        """Send the initial semantic snapshot after the subscription is accepted."""
        self._send_event(
            {
                "event": "snapshot",
                "data": self._instance.snapshot(
                    self._config_entry_id,
                    can_read=self._can_read,
                ),
            }
        )

    @callback
    def unsubscribe(self) -> None:
        """Stop all listeners owned by this subscription."""
        if self._state_unsub is not None:
            self._state_unsub()
            self._state_unsub = None

        if self._registry_unsub is not None:
            self._registry_unsub()
            self._registry_unsub = None

        self._entity_to_role.clear()

    @callback
    def _replace_state_listener(self) -> None:
        """Bind state tracking to the current resolved and readable entities."""
        if self._state_unsub is not None:
            self._state_unsub()
            self._state_unsub = None

        self._entity_to_role = {
            resolved.entity_id: role
            for role, resolved in self._instance.resolution.roles.items()
            if self._can_read(resolved.entity_id)
        }

        if self._entity_to_role:
            self._state_unsub = async_track_state_change_event(
                self._hass,
                self._entity_to_role,
                self._async_state_changed,
            )

    @callback
    def _async_state_changed(
        self,
        event: Event[EventStateChangedData],
    ) -> None:
        """Forward one Home Assistant entity change as a semantic role event."""
        entity_id = event.data["entity_id"]
        role = self._entity_to_role.get(entity_id)

        if role is None or not self._can_read(entity_id):
            return

        role_data = self._instance.role_snapshot(
            role,
            include_mapping=False,
        )
        if role_data is None:
            return

        payload: dict[str, Any] = {
            "event": "role_state",
            "role": role,
            "data": role_data,
        }

        if role == CONTRACT_ROLE:
            payload["instance"] = self._instance.summary(
                self._config_entry_id
            )

        self._send_event(payload)

    @callback
    def _async_entity_registry_updated(
        self,
        event: Event[er.EventEntityRegistryUpdatedData],
    ) -> None:
        """Refresh mappings and listeners after relevant registry changes."""
        if not self._instance.registry_event_affects(event.data):
            return

        try:
            self._instance.refresh()
        except ChargerSourceError as err:
            self._send_event(
                {
                    "event": "mapping_error",
                    "error": err.code,
                }
            )
            return

        self._replace_state_listener()
        self._send_event(
            {
                "event": "mapping_changed",
                "data": self._instance.snapshot(
                    self._config_entry_id,
                    can_read=self._can_read,
                ),
            }
        )
