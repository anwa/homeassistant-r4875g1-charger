"""Config flow for the R4875G1 Charger integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_CHARGER_DEVICE_ID,
    CONF_CONTRACT_VERSION,
    DOMAIN,
)
from .resolver import (
    ChargerSourceError,
    resolve_charger,
    validate_resolution_for_setup,
)


class R4875G1ChargerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure one existing ESPHome Charger Controller."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial Charger Controller selection."""
        errors: dict[str, str] = {}

        if user_input is not None:
            device_id = user_input[CONF_CHARGER_DEVICE_ID]

            try:
                resolution = resolve_charger(self.hass, device_id)
            except ChargerSourceError as err:
                errors["base"] = err.code
            else:
                if error_key := validate_resolution_for_setup(resolution):
                    errors["base"] = error_key
                else:
                    await self.async_set_unique_id(
                        resolution.stable_identifier
                    )
                    self._abort_if_unique_id_configured()

                    assert resolution.contract_version is not None

                    return self.async_create_entry(
                        title=resolution.device_name,
                        data={
                            CONF_CHARGER_DEVICE_ID: device_id,
                            CONF_CONTRACT_VERSION:
                                resolution.contract_version,
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CHARGER_DEVICE_ID):
                        selector.DeviceSelector(
                            selector.DeviceSelectorConfig(
                                filter=selector.DeviceFilterSelectorConfig(
                                    integration="esphome"
                                )
                            )
                        )
                }
            ),
            errors=errors,
        )
