"""Runtime access layer for one R4875G1 Charger Instance."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er

from .const import CONTRACT_ROLE, SUPPORTED_CONTRACT_VERSIONS
from .models import CapabilityResolution, ChargerResolution, ResolvedRole
from .resolver import resolve_charger


class ChargerInstanceStatus(StrEnum):
    """High-level availability state of one Charger Instance."""

    OK = "ok"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    INCOMPATIBLE = "incompatible"


class ChargerInstance:
    """Stable runtime interface over one resolved Charger Controller."""

    def __init__(
        self,
        hass: HomeAssistant,
        device_id: str,
        configured_contract_version: str,
    ) -> None:
        """Initialize and resolve one Charger Instance."""
        self._hass = hass
        self._device_id = device_id
        self._configured_contract_version = configured_contract_version
        self._resolution = resolve_charger(
            hass,
            device_id,
            configured_contract_version=configured_contract_version,
        )

    @property
    def resolution(self) -> ChargerResolution:
        """Return the current semantic resolution."""
        return self._resolution

    @property
    def device_id(self) -> str:
        """Return the selected Home Assistant device ID."""
        return self._device_id

    @property
    def name(self) -> str:
        """Return the current Charger Instance name."""
        return self._resolution.device_name

    @property
    def firmware_version(self) -> str | None:
        """Return the Controller firmware version reported by Home Assistant."""
        return self._resolution.firmware_version

    @property
    def contract_version(self) -> str | None:
        """Return the live contract version when the Controller is online."""
        state = self.state(CONTRACT_ROLE)
        if state is not None and state.state not in (
            STATE_UNKNOWN,
            STATE_UNAVAILABLE,
            "",
        ):
            return state.state
        return self._resolution.contract_version

    @property
    def contract_supported(self) -> bool:
        """Return whether the live or last-known contract version is supported."""
        return self.contract_version in SUPPORTED_CONTRACT_VERSIONS

    @property
    def compatible(self) -> bool:
        """Return whether the semantic contract is structurally compatible."""
        return (
            self.contract_supported
            and not self._resolution.missing_required_roles
            and not self._resolution.disabled_required_roles
            and not self._resolution.ambiguous_required_roles
        )

    @property
    def online(self) -> bool:
        """Return whether the Contract marker currently has a usable HA state."""
        state = self.state(CONTRACT_ROLE)
        return (
            state is not None
            and state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE, "")
        )

    @property
    def status(self) -> ChargerInstanceStatus:
        """Return the high-level runtime status."""
        if not self.compatible:
            return ChargerInstanceStatus.INCOMPATIBLE

        if not self.online:
            return ChargerInstanceStatus.OFFLINE

        if any(
            not capability.required and capability.status == "partial"
            for capability in self._resolution.capabilities.values()
        ):
            return ChargerInstanceStatus.DEGRADED

        return ChargerInstanceStatus.OK

    def refresh(self) -> None:
        """Refresh semantic role mappings from the Home Assistant registries."""
        self._resolution = resolve_charger(
            self._hass,
            self._device_id,
            configured_contract_version=self._configured_contract_version,
        )

    def role(self, role: str) -> ResolvedRole | None:
        """Return one resolved semantic role."""
        return self._resolution.roles.get(role)

    def entity_id(self, role: str) -> str | None:
        """Return the current Home Assistant entity ID for a semantic role."""
        resolved = self.role(role)
        return resolved.entity_id if resolved is not None else None

    def state(self, role: str) -> State | None:
        """Return the current Home Assistant state for a semantic role."""
        entity_id = self.entity_id(role)
        if entity_id is None:
            return None
        return self._hass.states.get(entity_id)

    def state_value(self, role: str) -> str | None:
        """Return the current raw Home Assistant state value for a role."""
        state = self.state(role)
        return state.state if state is not None else None

    def capability(self, name: str) -> CapabilityResolution | None:
        """Return one resolved capability."""
        return self._resolution.capabilities.get(name)

    def capability_available(self, name: str) -> bool:
        """Return whether a capability is completely usable."""
        capability = self.capability(name)
        return capability is not None and capability.available

    def registry_event_affects(
        self,
        event_data: er.EventEntityRegistryUpdatedData,
    ) -> bool:
        """Return whether an entity-registry update affects this instance."""
        known_entity_ids = {
            observation.entity_id
            for observation in self._resolution.registry_inventory
        }

        entity_id = event_data["entity_id"]
        old_entity_id = event_data.get("old_entity_id")

        if entity_id in known_entity_ids or old_entity_id in known_entity_ids:
            return True

        registry_entry = er.async_get(self._hass).async_get(entity_id)
        return (
            registry_entry is not None
            and registry_entry.device_id == self._device_id
        )

    def summary(self, config_entry_id: str) -> dict[str, Any]:
        """Return the stable read-only API summary for this instance."""
        return {
            "config_entry_id": config_entry_id,
            "name": self.name,
            "status": self.status.value,
            "online": self.online,
            "compatible": self.compatible,
            "contract_version": self.contract_version,
            "firmware_version": self.firmware_version,
            "capabilities": {
                name: {
                    "required": capability.required,
                    "status": capability.status,
                    "available": capability.available,
                }
                for name, capability in sorted(
                    self._resolution.capabilities.items()
                )
            },
        }

    def snapshot(self, config_entry_id: str) -> dict[str, Any]:
        """Return the semantic read-only API snapshot for this instance."""
        data = self.summary(config_entry_id)
        data["roles"] = {
            role: self._role_snapshot(resolved)
            for role, resolved in sorted(self._resolution.roles.items())
        }
        return data

    def as_diagnostics(self) -> dict[str, object]:
        """Return diagnostics for the active runtime instance."""
        data = self._resolution.as_diagnostics()
        data["instance_status"] = self.status.value
        data["online"] = self.online
        data["contract_version"] = self.contract_version
        data["contract_supported"] = self.contract_supported
        data["compatible"] = self.compatible
        return data

    def _role_snapshot(
        self,
        resolved: ResolvedRole,
    ) -> dict[str, object]:
        """Return one frontend-safe semantic role snapshot."""
        state = self._hass.states.get(resolved.entity_id)
        state_available = (
            state is not None
            and state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE)
        )

        return {
            "entity_id": resolved.entity_id,
            "domain": resolved.domain,
            "available": state_available,
            "state": state.state if state is not None else None,
        }
