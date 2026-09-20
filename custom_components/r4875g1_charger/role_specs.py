"""Bootstrap semantic role definitions for the R4875G1 Charger integration.

This is intentionally not yet the complete Contract-1 role table. The first
development milestone verifies how the real ESPHome Charger Controller appears
in Home Assistant's device and entity registries before the full contract is
frozen into the backend.
"""

from __future__ import annotations

from .const import CONTRACT_ENTITY_ORIGINAL_NAME, CONTRACT_ROLE
from .models import RoleSpec

BOOTSTRAP_ROLE_SPECS: tuple[RoleSpec, ...] = (
    RoleSpec(
        role=CONTRACT_ROLE,
        domain="sensor",
        original_name=CONTRACT_ENTITY_ORIGINAL_NAME,
    ),
    RoleSpec(
        role="charger.ac.power",
        domain="sensor",
        original_name="Combined AC Power All Units",
    ),
    RoleSpec(
        role="charger.dc.power",
        domain="sensor",
        original_name="Combined DC Power All Units",
    ),
    RoleSpec(
        role="charger.dc.voltage",
        domain="sensor",
        original_name="Average DC Voltage All Units",
    ),
    RoleSpec(
        role="charger.dc.current",
        domain="sensor",
        original_name="Combined DC Current All Units",
    ),
    RoleSpec(
        role="charger.dc.voltage_setpoint",
        domain="number",
        original_name="Set DC Voltage Limit",
    ),
    RoleSpec(
        role="charger.available_units",
        domain="sensor",
        original_name="Available Units",
    ),
    RoleSpec(
        role="charger.running_units",
        domain="sensor",
        original_name="Running Units",
    ),
    RoleSpec(
        role="charger.command.start",
        domain="button",
        original_name="Turn On All Units",
    ),
    RoleSpec(
        role="charger.command.stop",
        domain="button",
        original_name="Turn Off All Units",
    ),
)
