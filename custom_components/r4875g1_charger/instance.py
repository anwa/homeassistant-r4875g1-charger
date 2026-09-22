"""Runtime access layer for one R4875G1 Charger Instance."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from collections.abc import Callable
from typing import Any

from homeassistant.components.button.const import (
    DOMAIN as BUTTON_DOMAIN,
    SERVICE_PRESS,
)
from homeassistant.components.number.const import (
    ATTR_MAX,
    ATTR_MIN,
    ATTR_STEP,
    ATTR_VALUE,
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE,
)
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_UNIT_OF_MEASUREMENT,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import Context, HomeAssistant, State
from homeassistant.helpers import entity_registry as er

from .const import CONTRACT_ROLE, SUPPORTED_CONTRACT_VERSIONS
from .control import CONTROL_SPECS, ControlAction, ControlSpec
from .models import CapabilityResolution, ChargerResolution, ResolvedRole
from .resolver import resolve_charger


class ChargerInstanceStatus(StrEnum):
    """High-level availability state of one Charger Instance."""

    OK = "ok"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    INCOMPATIBLE = "incompatible"


@dataclass(frozen=True, slots=True)
class ChargerControlError(Exception):
    """Describe a rejected semantic control request."""

    code: str
    message: str

    def __str__(self) -> str:
        """Return the human-readable control error."""
        return self.message


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

    def control_spec(self, role: str) -> ControlSpec | None:
        """Return the explicit semantic control specification for one role."""
        return CONTROL_SPECS.get(role)

    def control_available(self, role: str) -> bool:
        """Return whether one semantic control can currently be dispatched."""
        if self.status not in (
            ChargerInstanceStatus.OK,
            ChargerInstanceStatus.DEGRADED,
        ):
            return False

        spec = self.control_spec(role)
        resolved = self.role(role)
        state = self.state(role)

        return (
            spec is not None
            and resolved is not None
            and resolved.domain == spec.domain
            and state is not None
            and state.state != STATE_UNAVAILABLE
        )

    async def async_control(
        self,
        role: str,
        *,
        value: float | bool | None = None,
        context: Context | None = None,
    ) -> dict[str, object]:
        """Dispatch one allow-listed semantic control through a standard HA service."""
        if self.status not in (
            ChargerInstanceStatus.OK,
            ChargerInstanceStatus.DEGRADED,
        ):
            raise ChargerControlError(
                "instance_unavailable",
                f"Charger Instance is {self.status.value}",
            )

        spec = self.control_spec(role)
        if spec is None:
            raise ChargerControlError(
                "role_not_writable",
                f"Semantic role {role} is not writable",
            )

        resolved = self.role(role)
        if resolved is None:
            raise ChargerControlError(
                "role_unresolved",
                f"Semantic role {role} is not currently resolved",
            )

        if resolved.domain != spec.domain:
            raise ChargerControlError(
                "role_domain_mismatch",
                f"Semantic role {role} resolved to unexpected domain "
                f"{resolved.domain}",
            )

        state = self._hass.states.get(resolved.entity_id)
        if state is None or state.state == STATE_UNAVAILABLE:
            raise ChargerControlError(
                "entity_unavailable",
                f"Entity for semantic role {role} is unavailable",
            )

        if spec.action is ControlAction.PRESS:
            if value is not None:
                raise ChargerControlError(
                    "unexpected_value",
                    f"Semantic role {role} does not accept a value",
                )

            await self._hass.services.async_call(
                BUTTON_DOMAIN,
                SERVICE_PRESS,
                {ATTR_ENTITY_ID: resolved.entity_id},
                context=context,
                blocking=True,
            )
        elif spec.action is ControlAction.SET_VALUE:
            if value is None or isinstance(value, bool):
                raise ChargerControlError(
                    "value_required",
                    f"Semantic role {role} requires a numeric value",
                )

            self._validate_number_value(role, state, value)

            await self._hass.services.async_call(
                NUMBER_DOMAIN,
                SERVICE_SET_VALUE,
                {
                    ATTR_ENTITY_ID: resolved.entity_id,
                    ATTR_VALUE: value,
                },
                context=context,
                blocking=True,
            )
        else:
            if not isinstance(value, bool):
                raise ChargerControlError(
                    "value_required",
                    f"Semantic role {role} requires a boolean value",
                )

            await self._hass.services.async_call(
                SWITCH_DOMAIN,
                SERVICE_TURN_ON if value else SERVICE_TURN_OFF,
                {
                    ATTR_ENTITY_ID: resolved.entity_id,
                },
                context=context,
                blocking=True,
            )

        return {
            "role": role,
            "entity_id": resolved.entity_id,
            "action": spec.action.value,
            "service_call_completed": True,
        }

    def summary(self, config_entry_id: str) -> dict[str, Any]:
        """Return the stable API summary for this instance."""
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

    def snapshot(
        self,
        config_entry_id: str,
        *,
        can_read: Callable[[str], bool] | None = None,
    ) -> dict[str, Any]:
        """Return the semantic API snapshot for this instance."""
        data = self.summary(config_entry_id)
        data["roles"] = {
            role: self.role_snapshot(role)
            for role, resolved in sorted(self._resolution.roles.items())
            if can_read is None or can_read(resolved.entity_id)
        }
        return data

    def role_snapshot(
        self,
        role: str,
        *,
        include_mapping: bool = True,
    ) -> dict[str, object] | None:
        """Return the current frontend-safe snapshot for one semantic role."""
        resolved = self.role(role)
        if resolved is None:
            return None

        return self._role_snapshot(
            role,
            resolved,
            include_mapping=include_mapping,
        )

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
        role: str,
        resolved: ResolvedRole,
        *,
        include_mapping: bool = True,
    ) -> dict[str, object]:
        """Return one frontend-safe semantic role snapshot."""
        state = self._hass.states.get(resolved.entity_id)
        state_available = (
            state is not None
            and state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE)
        )

        data: dict[str, object] = {
            "available": state_available,
            "state": state.state if state is not None else None,
            "unit": (
                state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
                if state is not None
                else None
            ),
        }

        if include_mapping:
            data["entity_id"] = resolved.entity_id
            data["domain"] = resolved.domain

        if (spec := self.control_spec(role)) is not None:
            control: dict[str, object] = {
                "action": spec.action.value,
                "available": self.control_available(role),
            }

            if spec.action is ControlAction.SET_VALUE:
                control.update(self._number_metadata(state))

            data["control"] = control

        return data

    @staticmethod
    def _number_metadata(state: State | None) -> dict[str, object]:
        """Return frontend metadata for one Home Assistant Number entity."""
        attributes = state.attributes if state is not None else {}
        return {
            "min": attributes.get(ATTR_MIN),
            "max": attributes.get(ATTR_MAX),
            "step": attributes.get(ATTR_STEP),
            "unit": attributes.get(ATTR_UNIT_OF_MEASUREMENT),
        }

    @staticmethod
    def _validate_number_value(
        role: str,
        state: State,
        value: float,
    ) -> None:
        """Validate a numeric control value against current HA metadata."""
        if not isfinite(value):
            raise ChargerControlError(
                "invalid_value",
                f"Semantic role {role} requires a finite numeric value",
            )

        minimum = state.attributes.get(ATTR_MIN)
        maximum = state.attributes.get(ATTR_MAX)

        if isinstance(minimum, int | float) and value < minimum:
            raise ChargerControlError(
                "value_out_of_range",
                f"Value {value} is below minimum {minimum} for {role}",
            )

        if isinstance(maximum, int | float) and value > maximum:
            raise ChargerControlError(
                "value_out_of_range",
                f"Value {value} is above maximum {maximum} for {role}",
            )
