"""Test Uptime Robot binary_sensor."""

import datetime
from unittest.mock import patch

from pyuptimerobot.exceptions import UptimeRobotAuthenticationException

from homeassistant.components.binary_sensor import DEVICE_CLASS_CONNECTIVITY
from homeassistant.components.uptimerobot.const import ATTRIBUTION
from homeassistant.const import STATE_ON, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.util import dt

from .common import MOCK_UPTIMEROBOT_MONITOR, setup_uptimerobot_integration

from tests.common import async_fire_time_changed


async def test_presentation(hass: HomeAssistant):
    """Test the presenstation of Uptime Robot binary_sensors."""
    await setup_uptimerobot_integration(hass)

    entity = hass.states.get("binary_sensor.test_monitor")

    assert entity.state == STATE_ON
    assert entity.attributes["device_class"] == DEVICE_CLASS_CONNECTIVITY
    assert entity.attributes["attribution"] == ATTRIBUTION
    assert entity.attributes["target"] == MOCK_UPTIMEROBOT_MONITOR["url"]


async def test_unaviable_on_update_failure(hass: HomeAssistant):
    """Test entity unaviable on update failure."""
    await setup_uptimerobot_integration(hass)

    entity = hass.states.get("binary_sensor.test_monitor")
    assert entity.state == STATE_ON

    with patch(
        "pyuptimerobot.UptimeRobot.async_get_monitors",
        side_effect=UptimeRobotAuthenticationException,
    ):
        async_fire_time_changed(hass, dt.utcnow() + datetime.timedelta(seconds=10))
        await hass.async_block_till_done()

    entity = hass.states.get("binary_sensor.test_monitor")
    assert entity.state == STATE_UNAVAILABLE
