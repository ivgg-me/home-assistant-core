"""deCONZ cover platform tests."""
from copy import deepcopy

from homeassistant.components import deconz
import homeassistant.components.cover as cover
from homeassistant.setup import async_setup_component

from .test_gateway import DECONZ_WEB_REQUEST, setup_deconz_integration

from tests.async_mock import patch

COVERS = {
    "1": {
        "id": "Level controllable cover id",
        "name": "Level controllable cover",
        "type": "Level controllable output",
        "state": {"bri": 254, "on": False, "reachable": True},
        "modelid": "Not zigbee spec",
        "uniqueid": "00:00:00:00:00:00:00:00-00",
    },
    "2": {
        "id": "Window covering device id",
        "name": "Window covering device",
        "type": "Window covering device",
        "state": {"bri": 254, "on": True, "reachable": True},
        "modelid": "lumi.curtain",
        "uniqueid": "00:00:00:00:00:00:00:01-00",
    },
    "3": {
        "id": "Unsupported cover id",
        "name": "Unsupported cover",
        "type": "Not a cover",
        "state": {"reachable": True},
        "uniqueid": "00:00:00:00:00:00:00:02-00",
    },
    "4": {
        "id": "deconz old brightness cover id",
        "name": "deconz old brightness cover",
        "type": "Level controllable output",
        "state": {"bri": 255, "on": False, "reachable": True},
        "modelid": "Not zigbee spec",
        "uniqueid": "00:00:00:00:00:00:00:03-00",
    },
    "5": {
        "id": "Window covering controller id",
        "name": "Window covering controller",
        "type": "Window covering controller",
        "state": {"bri": 254, "on": True, "reachable": True},
        "modelid": "Motor controller",
        "uniqueid": "00:00:00:00:00:00:00:04-00",
    },
}


async def test_platform_manually_configured(hass):
    """Test that we do not discover anything or try to set up a gateway."""
    assert (
        await async_setup_component(
            hass, cover.DOMAIN, {"cover": {"platform": deconz.DOMAIN}}
        )
        is True
    )
    assert deconz.DOMAIN not in hass.data


async def test_no_covers(hass):
    """Test that no cover entities are created."""
    await setup_deconz_integration(hass)
    assert len(hass.states.async_all()) == 0


async def test_cover(hass):
    """Test that all supported cover entities are created."""
    data = deepcopy(DECONZ_WEB_REQUEST)
    data["lights"] = deepcopy(COVERS)
    gateway = await setup_deconz_integration(hass, get_state_response=data)

    assert len(hass.states.async_all()) == 5
    assert hass.states.get("cover.level_controllable_cover").state == "open"
    assert hass.states.get("cover.window_covering_device").state == "closed"
    assert hass.states.get("cover.unsupported_cover") is None
    assert hass.states.get("cover.deconz_old_brightness_cover").state == "open"
    assert hass.states.get("cover.window_covering_controller").state == "closed"

    # Event signals cover is closed

    state_changed_event = {
        "t": "event",
        "e": "changed",
        "r": "lights",
        "id": "1",
        "state": {"on": True},
    }
    gateway.api.event_handler(state_changed_event)
    await hass.async_block_till_done()

    assert hass.states.get("cover.level_controllable_cover").state == "closed"

    # Verify service calls

    level_controllable_cover_device = gateway.api.lights["1"]

    # Service open cover

    with patch.object(
        level_controllable_cover_device, "_request", return_value=True
    ) as set_callback:
        await hass.services.async_call(
            cover.DOMAIN,
            cover.SERVICE_OPEN_COVER,
            {"entity_id": "cover.level_controllable_cover"},
            blocking=True,
        )
        await hass.async_block_till_done()
        set_callback.assert_called_with("put", "/lights/1/state", json={"on": False})

    # Service close cover

    with patch.object(
        level_controllable_cover_device, "_request", return_value=True
    ) as set_callback:
        await hass.services.async_call(
            cover.DOMAIN,
            cover.SERVICE_CLOSE_COVER,
            {"entity_id": "cover.level_controllable_cover"},
            blocking=True,
        )
        await hass.async_block_till_done()
        set_callback.assert_called_with(
            "put", "/lights/1/state", json={"on": True, "bri": 254}
        )

    # Service stop cover movement

    with patch.object(
        level_controllable_cover_device, "_request", return_value=True
    ) as set_callback:
        await hass.services.async_call(
            cover.DOMAIN,
            cover.SERVICE_STOP_COVER,
            {"entity_id": "cover.level_controllable_cover"},
            blocking=True,
        )
        await hass.async_block_till_done()
        set_callback.assert_called_with("put", "/lights/1/state", json={"bri_inc": 0})

    # Test that a reported cover position of 255 (deconz-rest-api < 2.05.73) is interpreted correctly.
    assert hass.states.get("cover.deconz_old_brightness_cover").state == "open"

    state_changed_event = {
        "t": "event",
        "e": "changed",
        "r": "lights",
        "id": "4",
        "state": {"on": True},
    }
    gateway.api.event_handler(state_changed_event)
    await hass.async_block_till_done()

    deconz_old_brightness_cover = hass.states.get("cover.deconz_old_brightness_cover")
    assert deconz_old_brightness_cover.state == "closed"
    assert deconz_old_brightness_cover.attributes["current_position"] == 0

    await gateway.async_reset()

    assert len(hass.states.async_all()) == 0
