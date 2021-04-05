"""The LG webOS Smart TV integration."""
from __future__ import annotations

import asyncio
from contextlib import suppress
import json
import logging
import os

from aiopylgtv import PyLGTVCmdException, PyLGTVPairException, WebOsClient
from sqlitedict import SqliteDict
import voluptuous as vol
from websockets.exceptions import ConnectionClosed

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    ATTR_COMMAND,
    ATTR_ENTITY_ID,
    CONF_CUSTOMIZE,
    CONF_HOST,
    CONF_ICON,
    CONF_NAME,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    ATTR_BUTTON,
    ATTR_PAYLOAD,
    ATTR_SOUND_OUTPUT,
    CONF_CLIENT_KEY,
    CONF_ON_ACTION,
    CONF_SOURCES,
    DEFAULT_NAME,
    DOMAIN,
    SERVICE_BUTTON,
    SERVICE_COMMAND,
    SERVICE_SELECT_SOUND_OUTPUT,
)

CUSTOMIZE_SCHEMA = vol.Schema(
    {vol.Optional(CONF_SOURCES, default=[]): vol.All(cv.ensure_list, [cv.string])}
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Optional(CONF_CUSTOMIZE, default={}): CUSTOMIZE_SCHEMA,
                        vol.Required(CONF_HOST): cv.string,
                        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                        vol.Optional(CONF_ON_ACTION): cv.SCRIPT_SCHEMA,
                        vol.Optional(CONF_ICON): cv.string,
                    }
                )
            ],
        )
    },
    extra=vol.ALLOW_EXTRA,
)

CALL_SCHEMA = vol.Schema({vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids})

BUTTON_SCHEMA = CALL_SCHEMA.extend({vol.Required(ATTR_BUTTON): cv.string})

COMMAND_SCHEMA = CALL_SCHEMA.extend(
    {vol.Required(ATTR_COMMAND): cv.string, vol.Optional(ATTR_PAYLOAD): dict}
)

SOUND_OUTPUT_SCHEMA = CALL_SCHEMA.extend({vol.Required(ATTR_SOUND_OUTPUT): cv.string})

SERVICE_TO_METHOD = {
    SERVICE_BUTTON: {"method": "async_button", "schema": BUTTON_SCHEMA},
    SERVICE_COMMAND: {"method": "async_command", "schema": COMMAND_SCHEMA},
    SERVICE_SELECT_SOUND_OUTPUT: {
        "method": "async_select_sound_output",
        "schema": SOUND_OUTPUT_SCHEMA,
    },
}

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["media_player"]
DATA_HASS_CONFIG = f"{DOMAIN}_hass_config"


async def async_setup(hass, config):
    """Set up the LG WebOS TV platform."""
    hass.data[DATA_HASS_CONFIG] = config

    if DOMAIN not in config:
        return True

    for conf in config[DOMAIN]:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=conf,
            )
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up LG webOS Smart TV from a config entry."""
    if DOMAIN not in hass.data:

        async def async_service_handler(service):
            method = SERVICE_TO_METHOD.get(service.service)
            data = service.data.copy()
            data["method"] = method["method"]
            async_dispatcher_send(hass, DOMAIN, data)

        for service in SERVICE_TO_METHOD:
            schema = SERVICE_TO_METHOD[service]["schema"]
            hass.services.async_register(
                DOMAIN, service, async_service_handler, schema=schema
            )

    host = entry.data[CONF_HOST]
    client_key = entry.data[CONF_CLIENT_KEY]

    client = NoStoreClient(host, client_key=client_key)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client

    async def async_on_stop(event):
        """Unregister callbacks and disconnect."""
        client.clear_state_update_callbacks()
        await client.disconnect()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, async_on_stop)

    await async_connect(client)

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    # set up notify platform, no entry support for notify component yet,
    # have to use discovery to load platform.
    hass.async_create_task(
        async_load_platform(
            hass,
            "notify",
            DOMAIN,
            {
                CONF_ICON: entry.data.get(CONF_ICON),
                CONF_NAME: entry.data.get(CONF_NAME, DEFAULT_NAME),
                "entry_id": entry.entry_id,
            },
            hass.data[DATA_HASS_CONFIG],
        )
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if len(hass.data[DOMAIN]) == 0:
            hass.data.pop(DOMAIN)
            for service in SERVICE_TO_METHOD:
                hass.services.async_remove(DOMAIN, service)

    return unload_ok


def convert_client_keys(config_file):
    """In case the config file contains JSON, convert it to a Sqlite config file."""
    # Return early if config file is non-existing
    if not os.path.isfile(config_file):
        return

    # Try to parse the file as being JSON
    with open(config_file) as json_file:
        try:
            json_conf = json.load(json_file)
        except (json.JSONDecodeError, UnicodeDecodeError):
            json_conf = None

    # If the file contains JSON, convert it to an Sqlite DB
    if json_conf:
        _LOGGER.warning("LG webOS TV client-key file is being migrated to Sqlite!")

        # Clean the JSON file
        os.remove(config_file)

        # Write the data to the Sqlite DB
        with SqliteDict(config_file) as conf:
            for host, key in json_conf.items():
                conf[host] = key
            conf.commit()


async def async_connect(client):
    """Attempt a connection, but fail gracefully if tv is off for example."""
    with suppress(
        OSError,
        ConnectionClosed,
        ConnectionRefusedError,
        asyncio.TimeoutError,
        asyncio.CancelledError,
        PyLGTVPairException,
        PyLGTVCmdException,
    ):
        await client.connect()


class NoStoreClient(WebOsClient):
    """Remove the client key sqlite client storage."""

    def write_client_key(self) -> None:
        """Do not save the current client key."""
