"""Home Assistant Contract-1 semantic role definitions."""

from __future__ import annotations

from .const import (
    CAPABILITY_ADVANCED_CHARGER,
    CAPABILITY_CONTRACT_IDENTITY,
    CAPABILITY_CONTROLLER_DIAGNOSTICS,
    CAPABILITY_COOLING_ENVIRONMENT,
    CAPABILITY_CORE_CHARGER,
    CAPABILITY_EXTERNAL_COOLING,
    CAPABILITY_RECTIFIER_DETAIL,
    CAPABILITY_RECTIFIER_FAN_CONTROL,
    CONTRACT_ENTITY_ORIGINAL_NAME,
    CONTRACT_ROLE,
)
from .models import RoleSpec

CAPABILITY_REQUIREMENTS: dict[str, bool] = {
    CAPABILITY_CONTRACT_IDENTITY: True,
    CAPABILITY_CORE_CHARGER: True,
    CAPABILITY_RECTIFIER_DETAIL: True,
    CAPABILITY_COOLING_ENVIRONMENT: True,
    CAPABILITY_ADVANCED_CHARGER: False,
    CAPABILITY_RECTIFIER_FAN_CONTROL: False,
    CAPABILITY_EXTERNAL_COOLING: False,
    CAPABILITY_CONTROLLER_DIAGNOSTICS: False,
}

_METADATA_ROLE_SPECS: tuple[RoleSpec, ...] = (
    RoleSpec(
        role=CONTRACT_ROLE,
        domain="sensor",
        original_name=CONTRACT_ENTITY_ORIGINAL_NAME,
        capability=CAPABILITY_CONTRACT_IDENTITY,
    ),
)

_CORE_CHARGER_ROLE_SPECS: tuple[RoleSpec, ...] = (
    RoleSpec("charger.ac.power", "sensor", "Combined AC Power All Units", CAPABILITY_CORE_CHARGER),
    RoleSpec("charger.ac.voltage", "sensor", "Average AC Voltage All Units", CAPABILITY_CORE_CHARGER),
    RoleSpec("charger.ac.current", "sensor", "Average AC Current All Units", CAPABILITY_CORE_CHARGER),
    RoleSpec("charger.ac.current_limit", "number", "Set AC Current Limit", CAPABILITY_CORE_CHARGER),
    RoleSpec("charger.dc.power", "sensor", "Combined DC Power All Units", CAPABILITY_CORE_CHARGER),
    RoleSpec("charger.dc.voltage", "sensor", "Average DC Voltage All Units", CAPABILITY_CORE_CHARGER),
    RoleSpec("charger.dc.current", "sensor", "Combined DC Current All Units", CAPABILITY_CORE_CHARGER),
    RoleSpec("charger.dc.voltage_setpoint", "number", "Set DC Voltage Limit", CAPABILITY_CORE_CHARGER),
    RoleSpec("charger.dc.sum_power_setpoint", "number", "Set DC Sum Power", CAPABILITY_CORE_CHARGER),
    RoleSpec("charger.fallback.voltage_setpoint", "number", "Set DC Voltage Limit Fallback", CAPABILITY_CORE_CHARGER),
    RoleSpec("charger.fallback.current_setpoint", "number", "Set DC Current Limit Fallback", CAPABILITY_CORE_CHARGER),
    RoleSpec("charger.available_units", "sensor", "Available Units", CAPABILITY_CORE_CHARGER),
    RoleSpec("charger.running_units", "sensor", "Running Units", CAPABILITY_CORE_CHARGER),
    RoleSpec(
        "charger.highest_output_temperature",
        "sensor",
        "Highest Output Temperature All Units",
        CAPABILITY_CORE_CHARGER,
    ),
    RoleSpec(
        "charger.conversion_efficiency",
        "sensor",
        "Conversion Efficiency All Units",
        CAPABILITY_CORE_CHARGER,
    ),
    RoleSpec("charger.command.start", "button", "Turn On All Units", CAPABILITY_CORE_CHARGER),
    RoleSpec("charger.command.stop", "button", "Turn Off All Units", CAPABILITY_CORE_CHARGER),
)

_ADVANCED_CHARGER_ROLE_SPECS: tuple[RoleSpec, ...] = (
    RoleSpec(
        "charger.dc.current_setpoint",
        "number",
        "Set DC Current Limit",
        CAPABILITY_ADVANCED_CHARGER,
        required=False,
    ),
    RoleSpec(
        "charger.dc.current_limit_effective",
        "sensor",
        "Effective DC Current Limit",
        CAPABILITY_ADVANCED_CHARGER,
        required=False,
    ),
    RoleSpec(
        "charger.dc.current_limit_thermal",
        "sensor",
        "Thermal DC Current Limit",
        CAPABILITY_ADVANCED_CHARGER,
        required=False,
    ),
    RoleSpec(
        "charger.dc.current_limit_applied",
        "sensor",
        "Applied DC Current Limit",
        CAPABILITY_ADVANCED_CHARGER,
        required=False,
    ),
    RoleSpec(
        "charger.internal_fan.minimum_duty_setpoint",
        "number",
        "Set Fan Minimum Speed",
        CAPABILITY_ADVANCED_CHARGER,
        required=False,
    ),
    RoleSpec(
        "charger.internal_fan.command.auto_all",
        "button",
        "Set Fan Auto Mode All Units",
        CAPABILITY_ADVANCED_CHARGER,
        required=False,
    ),
    RoleSpec(
        "charger.internal_fan.command.full_all",
        "button",
        "Set Fan Full Speed All Units",
        CAPABILITY_ADVANCED_CHARGER,
        required=False,
    ),
    RoleSpec(
        "charger.command.discover_rectifiers",
        "button",
        "Discover Rectifier Units",
        CAPABILITY_ADVANCED_CHARGER,
        required=False,
    ),
    RoleSpec(
        "charger.energy.ac_today",
        "sensor",
        "AC Energy Today",
        CAPABILITY_ADVANCED_CHARGER,
        required=False,
    ),
    RoleSpec(
        "charger.energy.dc_today",
        "sensor",
        "DC Energy Today",
        CAPABILITY_ADVANCED_CHARGER,
        required=False,
    ),
    RoleSpec(
        "charger.capability_mismatch",
        "binary_sensor",
        "Rectifier Capability Mismatch",
        CAPABILITY_ADVANCED_CHARGER,
        required=False,
    ),
)


def _rectifier_required_role_specs(unit: int) -> tuple[RoleSpec, ...]:
    """Return required Contract-1 roles for one rectifier."""
    suffix = f"Unit {unit}"
    prefix = f"rectifier.{unit}"

    return (
        RoleSpec(f"{prefix}.connected", "binary_sensor", f"CAN Communication {suffix}", CAPABILITY_RECTIFIER_DETAIL),
        RoleSpec(f"{prefix}.lifecycle", "sensor", f"Control State {suffix}", CAPABILITY_RECTIFIER_DETAIL),
        RoleSpec(f"{prefix}.power_state", "sensor", f"Power State {suffix}", CAPABILITY_RECTIFIER_DETAIL),
        RoleSpec(f"{prefix}.thermal_state", "sensor", f"Thermal State {suffix}", CAPABILITY_RECTIFIER_DETAIL),
        RoleSpec(f"{prefix}.ac.voltage", "sensor", f"AC Voltage {suffix}", CAPABILITY_RECTIFIER_DETAIL),
        RoleSpec(f"{prefix}.ac.current", "sensor", f"AC Current {suffix}", CAPABILITY_RECTIFIER_DETAIL),
        RoleSpec(f"{prefix}.ac.power", "sensor", f"AC Power {suffix}", CAPABILITY_RECTIFIER_DETAIL),
        RoleSpec(f"{prefix}.ac.frequency", "sensor", f"AC Frequency {suffix}", CAPABILITY_RECTIFIER_DETAIL),
        RoleSpec(f"{prefix}.dc.voltage", "sensor", f"DC Voltage {suffix}", CAPABILITY_RECTIFIER_DETAIL),
        RoleSpec(f"{prefix}.dc.current", "sensor", f"DC Current {suffix}", CAPABILITY_RECTIFIER_DETAIL),
        RoleSpec(f"{prefix}.dc.power", "sensor", f"DC Power {suffix}", CAPABILITY_RECTIFIER_DETAIL),
        RoleSpec(
            f"{prefix}.dc.current_setpoint_reported",
            "sensor",
            f"Max DC Current Setpoint {suffix}",
            CAPABILITY_RECTIFIER_DETAIL,
        ),
        RoleSpec(
            f"{prefix}.temperature.input",
            "sensor",
            f"Input Temperature {suffix}",
            CAPABILITY_RECTIFIER_DETAIL,
        ),
        RoleSpec(
            f"{prefix}.temperature.output",
            "sensor",
            f"Output Temperature {suffix}",
            CAPABILITY_RECTIFIER_DETAIL,
        ),
        RoleSpec(f"{prefix}.fan.rpm", "sensor", f"Fan RPM {suffix}", CAPABILITY_RECTIFIER_DETAIL),
        RoleSpec(
            f"{prefix}.fan.minimum_duty",
            "sensor",
            f"Fan Minimum Duty {suffix}",
            CAPABILITY_RECTIFIER_DETAIL,
        ),
        RoleSpec(
            f"{prefix}.fan.target_duty",
            "sensor",
            f"Fan Duty Target {suffix}",
            CAPABILITY_RECTIFIER_DETAIL,
        ),
        RoleSpec(
            f"{prefix}.max_current_capability",
            "sensor",
            f"Max Current Capability {suffix}",
            CAPABILITY_RECTIFIER_DETAIL,
        ),
        RoleSpec(
            f"{prefix}.operating_hours",
            "sensor",
            f"Operating Hours {suffix}",
            CAPABILITY_RECTIFIER_DETAIL,
        ),
        RoleSpec(f"{prefix}.command.start", "button", f"Turn On {suffix}", CAPABILITY_RECTIFIER_DETAIL),
        RoleSpec(f"{prefix}.command.stop", "button", f"Turn Off {suffix}", CAPABILITY_RECTIFIER_DETAIL),
    )


def _rectifier_optional_role_specs(unit: int) -> tuple[RoleSpec, ...]:
    """Return optional fan-control roles for one rectifier."""
    suffix = f"Unit {unit}"
    prefix = f"rectifier.{unit}"

    return (
        RoleSpec(
            f"{prefix}.fan.command.auto",
            "button",
            f"Set Fan Auto Mode {suffix}",
            CAPABILITY_RECTIFIER_FAN_CONTROL,
            required=False,
        ),
        RoleSpec(
            f"{prefix}.fan.command.full",
            "button",
            f"Set Fan Full Speed {suffix}",
            CAPABILITY_RECTIFIER_FAN_CONTROL,
            required=False,
        ),
    )


_RECTIFIER_REQUIRED_ROLE_SPECS = tuple(
    role
    for unit in range(1, 4)
    for role in _rectifier_required_role_specs(unit)
)

_RECTIFIER_OPTIONAL_ROLE_SPECS = tuple(
    role
    for unit in range(1, 4)
    for role in _rectifier_optional_role_specs(unit)
)

_COOLING_ENVIRONMENT_ROLE_SPECS: tuple[RoleSpec, ...] = (
    RoleSpec(
        "cooling.compartment.temperature",
        "sensor",
        "Rectifier Compartment Temperature",
        CAPABILITY_COOLING_ENVIRONMENT,
    ),
    RoleSpec(
        "cooling.compartment.humidity",
        "sensor",
        "Rectifier Compartment Humidity",
        CAPABILITY_COOLING_ENVIRONMENT,
    ),
    RoleSpec(
        "cooling.compartment.sea_level_pressure",
        "sensor",
        "Rectifier Compartment Sea-Level Pressure",
        CAPABILITY_COOLING_ENVIRONMENT,
    ),
)

_EXTERNAL_COOLING_ROLE_SPECS: tuple[RoleSpec, ...] = (
    RoleSpec(
        "cooling.external.automatic",
        "switch",
        "Cooling Fan Automatic",
        CAPABILITY_EXTERNAL_COOLING,
        required=False,
    ),
    RoleSpec(
        "cooling.external.power",
        "switch",
        "Cooling Fan Power",
        CAPABILITY_EXTERNAL_COOLING,
        required=False,
    ),
    RoleSpec(
        "cooling.external.manual_pwm",
        "number",
        "Cooling Fan Manual PWM",
        CAPABILITY_EXTERNAL_COOLING,
        required=False,
    ),
    RoleSpec(
        "cooling.external.actual_pwm",
        "sensor",
        "Cooling Fan PWM Actual",
        CAPABILITY_EXTERNAL_COOLING,
        required=False,
    ),
    RoleSpec(
        "cooling.external.controller_temperature",
        "sensor",
        "Cooling Fan Controller Temperature",
        CAPABILITY_EXTERNAL_COOLING,
        required=False,
    ),
    RoleSpec(
        "cooling.external.fan.1.rpm",
        "sensor",
        "Cooling Fan 1 RPM",
        CAPABILITY_EXTERNAL_COOLING,
        required=False,
    ),
    RoleSpec(
        "cooling.external.fan.2.rpm",
        "sensor",
        "Cooling Fan 2 RPM",
        CAPABILITY_EXTERNAL_COOLING,
        required=False,
    ),
    RoleSpec(
        "cooling.external.fan.3.rpm",
        "sensor",
        "Cooling Fan 3 RPM",
        CAPABILITY_EXTERNAL_COOLING,
        required=False,
    ),
)

_CONTROLLER_DIAGNOSTIC_ROLE_SPECS: tuple[RoleSpec, ...] = (
    RoleSpec(
        "system.controller_battery.voltage",
        "sensor",
        "Controller Battery Voltage",
        CAPABILITY_CONTROLLER_DIAGNOSTICS,
        required=False,
    ),
    RoleSpec(
        "system.controller_battery.soc",
        "sensor",
        "Controller Battery State of Charge",
        CAPABILITY_CONTROLLER_DIAGNOSTICS,
        required=False,
    ),
    RoleSpec("system.heap.free", "sensor", "Heap Free", CAPABILITY_CONTROLLER_DIAGNOSTICS, required=False),
    RoleSpec(
        "system.heap.max_block",
        "sensor",
        "Heap Max Block",
        CAPABILITY_CONTROLLER_DIAGNOSTICS,
        required=False,
    ),
    RoleSpec("system.psram.free", "sensor", "Free PSRAM", CAPABILITY_CONTROLLER_DIAGNOSTICS, required=False),
    RoleSpec("system.loop_time", "sensor", "Loop Time", CAPABILITY_CONTROLLER_DIAGNOSTICS, required=False),
    RoleSpec("system.cpu.frequency", "sensor", "CPU Frequency", CAPABILITY_CONTROLLER_DIAGNOSTICS, required=False),
    RoleSpec(
        "system.cpu.temperature",
        "sensor",
        "Controller CPU Temperature",
        CAPABILITY_CONTROLLER_DIAGNOSTICS,
        required=False,
    ),
    RoleSpec("system.uptime", "sensor", "Uptime", CAPABILITY_CONTROLLER_DIAGNOSTICS, required=False),
    RoleSpec("system.wifi.rssi", "sensor", "WiFi RSSI", CAPABILITY_CONTROLLER_DIAGNOSTICS, required=False),
    RoleSpec(
        "system.esphome_version",
        "sensor",
        "ESPHome Version",
        CAPABILITY_CONTROLLER_DIAGNOSTICS,
        required=False,
    ),
    RoleSpec(
        "system.device_info",
        "sensor",
        "Device Info",
        CAPABILITY_CONTROLLER_DIAGNOSTICS,
        required=False,
    ),
    RoleSpec(
        "system.reset_reason",
        "sensor",
        "Reset Reason",
        CAPABILITY_CONTROLLER_DIAGNOSTICS,
        required=False,
    ),
)

CONTRACT_ROLE_SPECS: tuple[RoleSpec, ...] = (
    _METADATA_ROLE_SPECS
    + _CORE_CHARGER_ROLE_SPECS
    + _ADVANCED_CHARGER_ROLE_SPECS
    + _RECTIFIER_REQUIRED_ROLE_SPECS
    + _RECTIFIER_OPTIONAL_ROLE_SPECS
    + _COOLING_ENVIRONMENT_ROLE_SPECS
    + _EXTERNAL_COOLING_ROLE_SPECS
    + _CONTROLLER_DIAGNOSTIC_ROLE_SPECS
)
