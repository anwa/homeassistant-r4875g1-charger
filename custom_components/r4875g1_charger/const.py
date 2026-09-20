"""Constants for the R4875G1 Charger integration."""

from typing import Final

DOMAIN: Final = "r4875g1_charger"

CONF_CHARGER_DEVICE_ID: Final = "charger_device_id"
CONF_CONTRACT_VERSION: Final = "contract_version"

ESPHOME_DOMAIN: Final = "esphome"
SUPPORTED_CONTRACT_VERSIONS: Final = frozenset({"1"})

CONTRACT_ROLE: Final = "metadata.contract_version"
CONTRACT_ENTITY_ORIGINAL_NAME: Final = "R4875G1 Charger Contract"

CAPABILITY_CONTRACT_IDENTITY: Final = "contract_identity"
CAPABILITY_CORE_CHARGER: Final = "core_charger"
CAPABILITY_RECTIFIER_DETAIL: Final = "rectifier_detail"
CAPABILITY_COOLING_ENVIRONMENT: Final = "cooling_environment"
CAPABILITY_ADVANCED_CHARGER: Final = "advanced_charger"
CAPABILITY_RECTIFIER_FAN_CONTROL: Final = "rectifier_fan_control"
CAPABILITY_EXTERNAL_COOLING: Final = "external_cooling"
CAPABILITY_CONTROLLER_DIAGNOSTICS: Final = "controller_diagnostics"
