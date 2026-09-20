"""Runtime models for the R4875G1 Charger integration."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True, slots=True)
class RoleSpec:
    """Describe one semantic charger role."""

    role: str
    domain: str
    original_name: str
    capability: str
    required: bool = True


@dataclass(frozen=True, slots=True)
class ResolvedRole:
    """Describe one resolved Home Assistant entity."""

    role: str
    entity_id: str
    unique_id: str
    domain: str
    original_name: str
    disabled: bool

    def as_diagnostics(self) -> dict[str, object]:
        """Return diagnostics-safe role data."""
        return {
            "entity_id": self.entity_id,
            "domain": self.domain,
            "original_name": self.original_name,
            "disabled": self.disabled,
            "unique_id_sha256": _hash_unique_id(self.unique_id),
        }


@dataclass(frozen=True, slots=True)
class CapabilityResolution:
    """Describe one resolved Charger Instance capability."""

    name: str
    required: bool
    status: str
    expected_roles: int
    usable_roles: int
    missing_roles: tuple[str, ...]
    disabled_roles: tuple[str, ...]
    ambiguous_roles: dict[str, tuple[str, ...]]

    @property
    def available(self) -> bool:
        """Return whether every role required by the capability is usable."""
        return self.status == "available"

    def as_diagnostics(self) -> dict[str, object]:
        """Return diagnostics-safe capability data."""
        return {
            "required": self.required,
            "status": self.status,
            "available": self.available,
            "expected_roles": self.expected_roles,
            "usable_roles": self.usable_roles,
            "missing_roles": list(self.missing_roles),
            "disabled_roles": list(self.disabled_roles),
            "ambiguous_roles": {
                role: list(entity_ids)
                for role, entity_ids in sorted(self.ambiguous_roles.items())
            },
        }


@dataclass(frozen=True, slots=True)
class RegistryObservation:
    """Describe one registry entity observed on the selected ESPHome device."""

    entity_id: str
    unique_id: str
    domain: str
    original_name: str | None
    platform: str
    disabled: bool

    def as_diagnostics(self) -> dict[str, object]:
        """Return diagnostics-safe registry data."""
        return {
            "entity_id": self.entity_id,
            "domain": self.domain,
            "original_name": self.original_name,
            "platform": self.platform,
            "disabled": self.disabled,
            "unique_id_sha256": _hash_unique_id(self.unique_id),
        }


@dataclass(frozen=True, slots=True)
class ChargerResolution:
    """Resolved semantic view of one Charger Controller."""

    device_id: str
    device_name: str
    source_config_entry_id: str
    stable_identifier: str
    firmware_version: str | None
    contract_version: str | None
    contract_supported: bool
    roles: dict[str, ResolvedRole]
    capabilities: dict[str, CapabilityResolution]
    missing_required_roles: tuple[str, ...]
    disabled_required_roles: tuple[str, ...]
    ambiguous_required_roles: dict[str, tuple[str, ...]]
    missing_optional_roles: tuple[str, ...]
    disabled_optional_roles: tuple[str, ...]
    ambiguous_optional_roles: dict[str, tuple[str, ...]]
    registry_inventory: tuple[RegistryObservation, ...]

    @property
    def compatible(self) -> bool:
        """Return whether the Contract-1 mapping is usable."""
        return (
            self.contract_supported
            and not self.missing_required_roles
            and not self.disabled_required_roles
            and not self.ambiguous_required_roles
        )

    def as_diagnostics(self) -> dict[str, object]:
        """Return diagnostics-safe resolution data."""
        return {
            "device": {
                "device_id": self.device_id,
                "name": self.device_name,
                "source_config_entry_id": self.source_config_entry_id,
                "firmware_version": self.firmware_version,
            },
            "contract_version": self.contract_version,
            "contract_supported": self.contract_supported,
            "compatible": self.compatible,
            "resolved_role_count": len(self.roles),
            "capabilities": {
                name: capability.as_diagnostics()
                for name, capability in sorted(self.capabilities.items())
            },
            "resolved_roles": {
                role: resolved.as_diagnostics()
                for role, resolved in sorted(self.roles.items())
            },
            "missing_required_roles": list(self.missing_required_roles),
            "disabled_required_roles": list(self.disabled_required_roles),
            "ambiguous_required_roles": {
                role: list(entity_ids)
                for role, entity_ids in sorted(
                    self.ambiguous_required_roles.items()
                )
            },
            "missing_optional_roles": list(self.missing_optional_roles),
            "disabled_optional_roles": list(self.disabled_optional_roles),
            "ambiguous_optional_roles": {
                role: list(entity_ids)
                for role, entity_ids in sorted(
                    self.ambiguous_optional_roles.items()
                )
            },
            "registry_inventory": [
                observation.as_diagnostics()
                for observation in self.registry_inventory
            ],
        }


def _hash_unique_id(unique_id: str) -> str:
    """Hash an entity unique ID before exposing it through diagnostics."""
    return sha256(unique_id.encode("utf-8")).hexdigest()[:16]
