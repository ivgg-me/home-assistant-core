"""Support for PlayStation 4 consoles."""
import logging

import voluptuous as vol
from pyps4_homeassistant.ddp import async_create_ddp_endpoint
from pyps4_homeassistant.media_art import COUNTRIES

from homeassistant.const import (
    ATTR_COMMAND, ATTR_ENTITY_ID, CONF_REGION, CONF_TOKEN)
from homeassistant.core import split_entity_id
from homeassistant.helpers import entity_registry, config_validation as cv
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.util import location
from homeassistant.util.json import load_json, save_json

from .config_flow import PlayStation4FlowHandler  # noqa: pylint: disable=unused-import
from .const import COMMANDS, DOMAIN, GAMES_FILE, PS4_DATA

_LOGGER = logging.getLogger(__name__)

SERVICE_COMMAND = 'send_command'

PS4_COMMAND_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required(ATTR_COMMAND): vol.In(list(COMMANDS))
})


class PS4Data():
    """Init Data Class."""

    def __init__(self):
        """Init Class."""
        self.devices = []
        self.protocol = None


async def async_setup(hass, config):
    """Set up the PS4 Component."""
    hass.data[PS4_DATA] = PS4Data()

    transport, protocol = await async_create_ddp_endpoint()
    hass.data[PS4_DATA].protocol = protocol
    _LOGGER.debug("PS4 DDP endpoint created: %s, %s", transport, protocol)
    service_handle(hass)
    return True


async def async_setup_entry(hass, config_entry):
    """Set up PS4 from a config entry."""
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(
        config_entry, 'media_player'))
    return True


async def async_unload_entry(hass, entry):
    """Unload a PS4 config entry."""
    await hass.config_entries.async_forward_entry_unload(
        entry, 'media_player')
    return True


async def async_migrate_entry(hass, entry):
    """Migrate old entry."""
    config_entries = hass.config_entries
    data = entry.data
    version = entry.version

    _LOGGER.debug("Migrating PS4 entry from Version %s", version)

    reason = {
        1: "Region codes have changed",
        2: "Format for Unique ID for entity registry has changed"
    }

    # Migrate Version 1 -> Version 2: New region codes.
    if version == 1:
        loc = await location.async_detect_location_info(
            hass.helpers.aiohttp_client.async_get_clientsession()
        )
        if loc:
            country = loc.country_name
            if country in COUNTRIES:
                for device in data['devices']:
                    device[CONF_REGION] = country
                version = entry.version = 2
                config_entries.async_update_entry(entry, data=data)
                _LOGGER.info(
                    "PlayStation 4 Config Updated: \
                    Region changed to: %s", country)

    # Migrate Version 2 -> Version 3: Update identifier format.
    if version == 2:
        # Prevent changing entity_id. Updates entity registry.
        registry = await entity_registry.async_get_registry(hass)

        for entity_id, e_entry in registry.entities.items():
            if e_entry.config_entry_id == entry.entry_id:
                unique_id = e_entry.unique_id

                # Remove old entity entry.
                registry.async_remove(entity_id)

                # Format old unique_id.
                unique_id = format_unique_id(entry.data[CONF_TOKEN], unique_id)

                # Create new entry with old entity_id.
                new_id = split_entity_id(entity_id)[1]
                registry.async_get_or_create(
                    'media_player', DOMAIN, unique_id,
                    suggested_object_id=new_id,
                    config_entry_id=e_entry.config_entry_id,
                    device_id=e_entry.device_id
                )
                entry.version = 3
                _LOGGER.info(
                    "PlayStation 4 identifier for entity: %s \
                    has changed", entity_id)
                config_entries.async_update_entry(entry)
                return True

    msg = """{} for the PlayStation 4 Integration.
            Please remove the PS4 Integration and re-configure
            [here](/config/integrations).""".format(reason[version])

    hass.components.persistent_notification.async_create(
        title="PlayStation 4 Integration Configuration Requires Update",
        message=msg,
        notification_id='config_entry_migration'
    )
    return False


def format_unique_id(creds, mac_address):
    """Use last 4 Chars of credential as suffix. Unique ID per PSN user."""
    suffix = creds[-4:]
    return "{}_{}".format(mac_address, suffix)


def load_games(hass: HomeAssistantType) -> dict:
    """Load games for sources."""
    g_file = hass.config.path(GAMES_FILE)
    try:
        games = load_json(g_file)

    # If file does not exist, create empty file.
    except FileNotFoundError:
        games = {}
        save_games(hass, games)
    return games


def save_games(hass: HomeAssistantType, games: dict):
    """Save games to file."""
    g_file = hass.config.path(GAMES_FILE)
    try:
        save_json(g_file, games)
    except OSError as error:
        _LOGGER.error("Could not save game list, %s", error)

    # Retry loading file
    if games is None:
        load_games(hass)


def service_handle(hass: HomeAssistantType):
    """Handle for services."""
    async def async_service_command(call):
        """Service for sending commands."""
        entity_ids = call.data[ATTR_ENTITY_ID]
        command = call.data[ATTR_COMMAND]
        for device in hass.data[PS4_DATA].devices:
            if device.entity_id in entity_ids:
                await device.async_send_command(command)

    hass.services.async_register(
        DOMAIN, SERVICE_COMMAND, async_service_command,
        schema=PS4_COMMAND_SCHEMA)
