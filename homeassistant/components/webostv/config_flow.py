"""Config flow for LG webOS Smart TV integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiopylgtv.webos_client import PyLGTVCmdException, PyLGTVPairException
from async_timeout import timeout
import voluptuous as vol
from websockets.exceptions import ConnectionClosed

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.exceptions import HomeAssistantError

from . import NoStoreClient, convert_client_keys
from .const import CONF_CLIENT_KEY, DEFAULT_NAME, DOMAIN, WEBOSTV_CONFIG_FILE

_LOGGER = logging.getLogger(__name__)

PAIR_TIMEOUT = 60
STEP_USER_DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_HOST): str, vol.Optional(CONF_NAME, default=DEFAULT_NAME): str}
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LG webOS Smart TV."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH
    data: dict | None = None
    errors: dict | None = None
    pair_task: asyncio.Task | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step."""
        if user_input is None:
            # Reset pair task to allow a new pair after errors.
            self.pair_task = None
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=self.errors
            )

        if not self.pair_task and (not self.client or self.errors):
            host = user_input[CONF_HOST]
            self.client = NoStoreClient(host)

        if not self.pair_task:
            self.pair_task = self.hass.async_create_task(
                self.validate_input(user_input)
            )
            return self.async_show_progress(
                step_id="user",
                progress_action="pair",
            )

        self.errors = {}

        try:
            info = await self.pair_task
        except CannotConnect:
            self.errors["base"] = "cannot_connect"
        except InvalidAuth:
            self.errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            self.errors["base"] = "unknown"

        if self.errors:
            return self.async_show_progress_done(next_step_id="pair_failed")

        self.data = info
        return self.async_show_progress_done(next_step_id="finish")

    async def validate_input(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate the user input allows us to connect.

        Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
        """
        try:
            async with timeout(PAIR_TIMEOUT):
                await self.client.connect()
                await self.client.disconnect()
        except PyLGTVPairException:
            _LOGGER.warning(
                "Connected to LG webOS TV %s but not paired", self.client.ip
            )
            raise InvalidAuth
        except (
            OSError,
            ConnectionClosed,
            ConnectionRefusedError,
            asyncio.TimeoutError,
            PyLGTVCmdException,
        ):
            _LOGGER.error("Unable to connect to host %s", self.client.ip)
            raise CannotConnect
        finally:
            # Continue the flow after show progress when the task is done.
            self.hass.async_create_task(
                self.hass.config_entries.flow.async_configure(
                    flow_id=self.flow_id, user_input={}
                )
            )

        # Return info that you want to store in the config entry.
        return {
            **data,
            CONF_CLIENT_KEY: self.client.client_key,
        }

    async def async_step_pair_failed(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Pairing the tv failed."""
        return await self.async_step_user()

    async def async_step_finish(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Finish the config flow."""
        return self.async_create_entry(title=self.data[CONF_NAME], data=self.data)

    async def async_step_import(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Import legacy configuration."""
        host = user_input[CONF_HOST]
        config_file = self.hass.config.path(WEBOSTV_CONFIG_FILE)

        await self.hass.async_add_executor_job(convert_client_keys, config_file)

        self.client = NoStoreClient(host, key_file_path=config_file)
        await self.client.async_init()

        return await self.async_step_user(
            user_input={
                CONF_HOST: host,
                CONF_NAME: user_input[CONF_NAME],
            }
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
