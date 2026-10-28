"""Config flow for Adria MACH.

Only email and password are asked for. The MACH unit is discovered from the
account; if the account has several units, the user picks one.
"""

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

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class AdriaMachConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the user and device-selection steps."""

    VERSION = 1

    def __init__(self) -> None:
        self._username: str = ""
        self._password: str = ""
        self._devices: list[dict[str, str]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            self._username = user_input[CONF_USERNAME].strip()
            self._password = user_input[CONF_PASSWORD]
            api = AdriaMachApi(
                async_get_clientsession(self.hass), self._username, self._password
            )
            try:
                await api.async_authenticate()
                self._devices = await api.async_discover_devices()
            except AdriaMachAuthError:
                errors["base"] = "invalid_auth"
            except AdriaMachConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error validating Adria MACH")
                errors["base"] = "unknown"
            else:
                if not self._devices:
                    errors["base"] = "no_devices"
                elif len(self._devices) == 1:
                    return await self._async_create(self._devices[0]["mach_id"])
                else:
                    return await self.async_step_device()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors
        )

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return await self._async_create(user_input[CONF_MACH_ID])

        options = {
            d["mach_id"]: f"{d['name'] or 'MACH'} ({d['mach_id']})" for d in self._devices
        }
        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema({vol.Required(CONF_MACH_ID): vol.In(options)}),
        )

    async def _async_create(self, mach_id: str) -> ConfigFlowResult:
        await self.async_set_unique_id(mach_id)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=f"Adria MACH {mach_id}",
            data={
                CONF_USERNAME: self._username,
                CONF_PASSWORD: self._password,
                CONF_MACH_ID: mach_id,
            },
        )
