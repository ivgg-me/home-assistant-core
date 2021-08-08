"""Common constants and functions for Uptime Robot tests."""
from homeassistant import config_entries
from homeassistant.components.uptimerobot.const import DOMAIN
from homeassistant.const import CONF_API_KEY, CONF_PLATFORM
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry

MOCK_API_KEY = "1234"
MOCK_UNIQUE_ID = "1234567890"
MOCK_ENTRY_ID = "1234567890"


async def setup_uptimetobot_integration(hass: HomeAssistant) -> MockConfigEntry:
    """Set up the Uptime Robot integration."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_PLATFORM: DOMAIN, CONF_API_KEY: MOCK_API_KEY},
        unique_id=MOCK_UNIQUE_ID,
        entry_id=MOCK_ENTRY_ID,
        source=config_entries.SOURCE_USER,
    )
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    return config_entry
