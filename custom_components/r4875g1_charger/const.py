"""Constants for the R4875G1 Charger integration."""

from typing import Final

DOMAIN: Final = "r4875g1_charger"

CONF_CHARGER_DEVICE_ID: Final = "charger_device_id"
CONF_CONTRACT_VERSION: Final = "contract_version"

ESPHOME_DOMAIN: Final = "esphome"
SUPPORTED_CONTRACT_VERSIONS: Final = frozenset({"1"})

CONTRACT_ROLE: Final = "metadata.contract_version"
CONTRACT_ENTITY_ORIGINAL_NAME: Final = "R4875G1 Charger Contract"

CAPABILITY_CORE_CHARGER: Final = "core_charger"
