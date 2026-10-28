"""Config flow for Adria MACH."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AdriaMachApi, AdriaMachAuthError, AdriaMachConnectionError
from .const import CONF_MACH_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_MACH_ID): str,
    }
)


class AdriaMachConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the user step."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            mach_id = user_input[CONF_MACH_ID].strip().upper()
            await self.async_set_unique_id(mach_id)
            self._abort_if_unique_id_configured()

            api = AdriaMachApi(
                async_get_clientsession(self.hass),
                user_input[CONF_USERNAME].strip(),
                user_input[CONF_PASSWORD],
                mach_id,
            )
            try:
                await api.async_authenticate()
                info = await api.async_get_mach_info()
            except AdriaMachAuthError:
                errors["base"] = "invalid_auth"
            except AdriaMachConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error validating Adria MACH")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"Adria MACH {mach_id}",
                    data={**user_input, CONF_MACH_ID: mach_id},
                    description_placeholders={"version": str(info.get("version", ""))},
                )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
