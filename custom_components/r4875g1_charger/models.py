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
    roles: dict[str, ResolvedRole]
    missing_required_roles: tuple[str, ...]
    disabled_required_roles: tuple[str, ...]
    ambiguous_required_roles: dict[str, tuple[str, ...]]
    registry_inventory: tuple[RegistryObservation, ...]

    @property
    def compatible(self) -> bool:
        """Return whether the bootstrap Contract-1 mapping is usable."""
        return (
            self.contract_version is not None
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
            "compatible": self.compatible,
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
            "registry_inventory": [
                observation.as_diagnostics()
                for observation in self.registry_inventory
            ],
        }


def _hash_unique_id(unique_id: str) -> str:
    """Hash an entity unique ID before exposing it through diagnostics."""
    return sha256(unique_id.encode("utf-8")).hexdigest()[:16]
