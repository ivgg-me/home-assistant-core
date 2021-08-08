"""Common constants and functions for Uptime Robot tests."""
from __future__ import annotations

from typing import Any
from unittest.mock import patch

from pyuptimerobot import (
    UptimeRobotAccount,
    UptimeRobotApiError,
    UptimeRobotApiResponse,
    UptimeRobotMonitor,
)

from homeassistant import config_entries
from homeassistant.components.uptimerobot.const import DOMAIN
from homeassistant.const import CONF_API_KEY, CONF_PLATFORM
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry

MOCK_UPTIMEROBOT_API_KEY = "1234"
MOCK_UPTIMEROBOT_UNIQUE_ID = "1234567890"

MOCK_UPTIMEROBOT_ACCOUNT = {"email": "test@test.test", "user_id": 1234567890}
MOCK_UPTIMEROBOT_MONITOR = {
    "id": 1234,
    "friendly_name": "Test monitor",
    "status": 2,
    "type": 1,
    "url": "http://example.com",
}


def mock_uptimerobot_api_response(
    data: dict[str, Any]
    | list[UptimeRobotAccount, UptimeRobotMonitor, UptimeRobotApiError],
    status: str = "ok",
    key: str = "monitors",
) -> UptimeRobotApiResponse:
    """Mock API response for Uptime Robot."""
    return UptimeRobotApiResponse.from_dict({"stat": status, key: data})


async def setup_uptimerobot_integration(hass: HomeAssistant) -> MockConfigEntry:
    """Set up the Uptime Robot integration."""
    mock_entry = MockConfigEntry(
        domain=DOMAIN,
        title=MOCK_UPTIMEROBOT_ACCOUNT["email"],
        data={CONF_PLATFORM: DOMAIN, CONF_API_KEY: MOCK_UPTIMEROBOT_API_KEY},
        unique_id=MOCK_UPTIMEROBOT_UNIQUE_ID,
        source=config_entries.SOURCE_USER,
    )
    mock_entry.add_to_hass(hass)

    with patch(
        "pyuptimerobot.UptimeRobot.async_get_monitors",
        return_value=mock_uptimerobot_api_response(data=[MOCK_UPTIMEROBOT_MONITOR]),
    ):

        await hass.config_entries.async_setup(mock_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_entry.state == config_entries.ConfigEntryState.LOADED

    return mock_entry
