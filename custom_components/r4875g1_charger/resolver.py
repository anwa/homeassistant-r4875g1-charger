"""Resolve an ESPHome Charger Controller into semantic Home Assistant roles."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .const import (
    CONTRACT_ROLE,
    ESPHOME_DOMAIN,
    SUPPORTED_CONTRACT_VERSIONS,
)
from .models import (
    CapabilityResolution,
    ChargerResolution,
    RegistryObservation,
    ResolvedRole,
)
from .role_specs import CAPABILITY_REQUIREMENTS, CONTRACT_ROLE_SPECS


@dataclass(frozen=True, slots=True)
class ChargerSourceError(Exception):
    """Raised when the selected source device cannot represent a charger."""

    code: str

    def __str__(self) -> str:
        """Return the error code."""
        return self.code


def resolve_charger(
    hass: HomeAssistant,
    device_id: str,
    *,
    configured_contract_version: str | None = None,
) -> ChargerResolution:
    """Resolve one existing ESPHome device into a semantic Charger Instance."""
    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    device = device_registry.async_get(device_id)
    if device is None or not isinstance(device, dr.DeviceEntry):
        raise ChargerSourceError("device_not_found")

    source_config_entry_id = device.config_entry_id
    if source_config_entry_id is None:
        raise ChargerSourceError("missing_source_config_entry")

    source_entry = hass.config_entries.async_get_entry(source_config_entry_id)
    if source_entry is None or source_entry.domain != ESPHOME_DOMAIN:
        raise ChargerSourceError("not_esphome_device")

    stable_identifier = _stable_esphome_identifier(device)

    entries = [
        entry
        for entry in er.async_entries_for_device(
            entity_registry,
            device_id,
            include_disabled_entities=True,
        )
        if entry.config_entry_id == source_config_entry_id
        and entry.platform == ESPHOME_DOMAIN
    ]

    inventory = tuple(
        RegistryObservation(
            entity_id=entry.entity_id,
            unique_id=entry.unique_id,
            domain=_entity_domain(entry.entity_id),
            original_name=entry.original_name,
            platform=entry.platform,
            disabled=entry.disabled_by is not None,
        )
        for entry in sorted(entries, key=lambda item: item.entity_id)
    )

    entries_by_identity: dict[tuple[str, str | None], list[er.RegistryEntry]] = {}
    for entry in entries:
        key = (_entity_domain(entry.entity_id), entry.original_name)
        entries_by_identity.setdefault(key, []).append(entry)

    resolved_roles: dict[str, ResolvedRole] = {}
    missing_roles: set[str] = set()
    disabled_roles: set[str] = set()
    ambiguous_roles: dict[str, tuple[str, ...]] = {}

    for spec in CONTRACT_ROLE_SPECS:
        candidates = entries_by_identity.get(
            (spec.domain, spec.original_name),
            [],
        )

        if not candidates:
            missing_roles.add(spec.role)
            continue

        if len(candidates) > 1:
            ambiguous_roles[spec.role] = tuple(
                sorted(entry.entity_id for entry in candidates)
            )
            continue

        entry = candidates[0]
        disabled = entry.disabled_by is not None

        resolved_roles[spec.role] = ResolvedRole(
            role=spec.role,
            entity_id=entry.entity_id,
            unique_id=entry.unique_id,
            domain=spec.domain,
            original_name=spec.original_name,
            disabled=disabled,
        )

        if disabled:
            disabled_roles.add(spec.role)

    required_roles = {
        spec.role for spec in CONTRACT_ROLE_SPECS if spec.required
    }
    optional_roles = {
        spec.role for spec in CONTRACT_ROLE_SPECS if not spec.required
    }

    missing_required = tuple(sorted(missing_roles & required_roles))
    disabled_required = tuple(sorted(disabled_roles & required_roles))
    ambiguous_required = {
        role: entity_ids
        for role, entity_ids in sorted(ambiguous_roles.items())
        if role in required_roles
    }

    missing_optional = tuple(sorted(missing_roles & optional_roles))
    disabled_optional = tuple(sorted(disabled_roles & optional_roles))
    ambiguous_optional = {
        role: entity_ids
        for role, entity_ids in sorted(ambiguous_roles.items())
        if role in optional_roles
    }

    capabilities = _resolve_capabilities(
        resolved_roles,
        missing_roles,
        disabled_roles,
        ambiguous_roles,
    )

    contract_version = configured_contract_version
    contract_role = resolved_roles.get(CONTRACT_ROLE)

    if contract_role is not None:
        state = hass.states.get(contract_role.entity_id)
        if state is not None and state.state not in (
            STATE_UNKNOWN,
            STATE_UNAVAILABLE,
            "",
        ):
            contract_version = state.state

    contract_supported = contract_version in SUPPORTED_CONTRACT_VERSIONS

    device_name = (
        device.name_by_user
        or device.name
        or source_entry.title
        or "R4875G1 Charger"
    )

    return ChargerResolution(
        device_id=device_id,
        device_name=device_name,
        source_config_entry_id=source_config_entry_id,
        stable_identifier=stable_identifier,
        firmware_version=device.sw_version,
        contract_version=contract_version,
        contract_supported=contract_supported,
        roles=resolved_roles,
        capabilities=capabilities,
        missing_required_roles=missing_required,
        disabled_required_roles=disabled_required,
        ambiguous_required_roles=ambiguous_required,
        missing_optional_roles=missing_optional,
        disabled_optional_roles=disabled_optional,
        ambiguous_optional_roles=ambiguous_optional,
        registry_inventory=inventory,
    )


def validate_resolution_for_setup(resolution: ChargerResolution) -> str | None:
    """Return a config-flow error key when a resolution cannot be configured."""
    if resolution.contract_version is None:
        return "contract_unavailable"

    if not resolution.contract_supported:
        return "unsupported_contract"

    if resolution.ambiguous_required_roles:
        return "ambiguous_required_roles"

    if resolution.disabled_required_roles:
        return "disabled_required_roles"

    if resolution.missing_required_roles:
        return "missing_required_roles"

    return None


def _resolve_capabilities(
    resolved_roles: dict[str, ResolvedRole],
    missing_roles: set[str],
    disabled_roles: set[str],
    ambiguous_roles: dict[str, tuple[str, ...]],
) -> dict[str, CapabilityResolution]:
    """Build explicit capability state from the semantic role map."""
    capabilities: dict[str, CapabilityResolution] = {}

    for capability_name, capability_required in CAPABILITY_REQUIREMENTS.items():
        specs = tuple(
            spec
            for spec in CONTRACT_ROLE_SPECS
            if spec.capability == capability_name
        )

        capability_roles = {spec.role for spec in specs}
        capability_missing = tuple(
            sorted(capability_roles & missing_roles)
        )
        capability_disabled = tuple(
            sorted(capability_roles & disabled_roles)
        )
        capability_ambiguous = {
            role: entity_ids
            for role, entity_ids in sorted(ambiguous_roles.items())
            if role in capability_roles
        }

        usable_roles = sum(
            1
            for spec in specs
            if spec.role in resolved_roles
            and spec.role not in disabled_roles
        )

        if usable_roles == len(specs):
            status = "available"
        elif usable_roles == 0:
            status = "unavailable"
        else:
            status = "partial"

        capabilities[capability_name] = CapabilityResolution(
            name=capability_name,
            required=capability_required,
            status=status,
            expected_roles=len(specs),
            usable_roles=usable_roles,
            missing_roles=capability_missing,
            disabled_roles=capability_disabled,
            ambiguous_roles=capability_ambiguous,
        )

    return capabilities


def _stable_esphome_identifier(device: dr.DeviceEntry) -> str:
    """Return a stable identifier for one ESPHome main device."""
    for connection_type, value in device.connections:
        if connection_type == dr.CONNECTION_NETWORK_MAC:
            return f"{ESPHOME_DOMAIN}:{dr.format_mac(value)}"

    raise ChargerSourceError("missing_stable_identifier")


def _entity_domain(entity_id: str) -> str:
    """Return the domain portion of an entity ID."""
    return entity_id.partition(".")[0]
