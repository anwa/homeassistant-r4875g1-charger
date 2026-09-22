"""Semantic control definitions for the R4875G1 Charger integration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final


class ControlAction(StrEnum):
    """Supported semantic control actions."""

    PRESS = "press"
    SET_VALUE = "set_value"
    SET_SWITCH = "set_switch"


@dataclass(frozen=True, slots=True)
class ControlSpec:
    """Describe one explicitly writable semantic role."""

    action: ControlAction
    domain: str


CONTROL_SPECS: Final[dict[str, ControlSpec]] = {
    "charger.command.start": ControlSpec(ControlAction.PRESS, "button"),
    "charger.command.stop": ControlSpec(ControlAction.PRESS, "button"),
    "rectifier.1.command.start": ControlSpec(ControlAction.PRESS, "button"),
    "rectifier.1.command.stop": ControlSpec(ControlAction.PRESS, "button"),
    "rectifier.2.command.start": ControlSpec(ControlAction.PRESS, "button"),
    "rectifier.2.command.stop": ControlSpec(ControlAction.PRESS, "button"),
    "rectifier.3.command.start": ControlSpec(ControlAction.PRESS, "button"),
    "rectifier.3.command.stop": ControlSpec(ControlAction.PRESS, "button"),
    "charger.ac.current_limit": ControlSpec(ControlAction.SET_VALUE, "number"),
    "charger.dc.voltage_setpoint": ControlSpec(
        ControlAction.SET_VALUE,
        "number",
    ),
    "charger.dc.sum_power_setpoint": ControlSpec(
        ControlAction.SET_VALUE,
        "number",
    ),
    "charger.fallback.voltage_setpoint": ControlSpec(
        ControlAction.SET_VALUE,
        "number",
    ),
    "charger.fallback.current_setpoint": ControlSpec(
        ControlAction.SET_VALUE,
        "number",
    ),
    "cooling.external.automatic": ControlSpec(
        ControlAction.SET_SWITCH, "switch"
    ),
    "cooling.external.power": ControlSpec(ControlAction.SET_SWITCH, "switch"),
    "cooling.external.manual_pwm": ControlSpec(ControlAction.SET_VALUE, "number"),
}
