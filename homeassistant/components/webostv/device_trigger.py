"""Provides device automations for control of LG webOS Smart TV."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.components.automation import AutomationActionType
from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.device_automation.exceptions import (
    InvalidDeviceAutomationConfig,
)
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_PLATFORM, CONF_TYPE
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers.device_registry import (
    DeviceRegistry,
    async_get as get_dev_reg,
)
from homeassistant.helpers.typing import ConfigType

from . import WebOsClientWrapper
from .const import DATA_CONFIG_ENTRY, DOMAIN

TRIGGER_TYPE_TURN_ON = "turn_on"

TRIGGER_TYPES = {TRIGGER_TYPE_TURN_ON}
TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES),
    }
)


async def async_get_triggers(
    _hass: HomeAssistant, device_id: str
) -> list[dict[str, str]]:
    """List device triggers for device."""
    triggers = []
    triggers.append(
        {
            CONF_PLATFORM: "device",
            CONF_DEVICE_ID: device_id,
            CONF_DOMAIN: DOMAIN,
            CONF_TYPE: TRIGGER_TYPE_TURN_ON,
        }
    )

    return triggers


async def async_validate_trigger_config(
    hass: HomeAssistant, config: ConfigType
) -> ConfigType:
    """Validate config."""
    config = TRIGGER_SCHEMA(config)

    device_reg: DeviceRegistry = get_dev_reg(hass)
    device_id = config[CONF_DEVICE_ID]
    device = device_reg.async_get(device_id)

    if not device:
        raise InvalidDeviceAutomationConfig(f"Device not found: {device_id}")

    return config


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: AutomationActionType,
    automation_info: dict,
) -> CALLBACK_TYPE | None:
    """Attach a trigger."""
    trigger_data = automation_info.get("trigger_data", {}) if automation_info else {}
    device_reg: DeviceRegistry = get_dev_reg(hass)
    if config[CONF_TYPE] == TRIGGER_TYPE_TURN_ON:
        variables = {
            "trigger": {
                **trigger_data,
                "platform": "device",
                "domain": DOMAIN,
                "device_id": config[CONF_DEVICE_ID],
                "description": f"webostv '{config[CONF_TYPE]}' event",
            }
        }

        device = device_reg.async_get(config[CONF_DEVICE_ID])
        wrapper: WebOsClientWrapper | None
        for config_entry_id in device.config_entries:
            if wrapper := hass.data[DOMAIN][DATA_CONFIG_ENTRY].get(config_entry_id):
                return wrapper.turn_on.async_attach(action, variables)

    return None
