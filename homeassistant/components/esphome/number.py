"""Support for esphome numbers."""
from __future__ import annotations

import math

from aioesphomeapi import NumberInfo, NumberState

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EsphomeEntity, esphome_state_property, platform_async_setup_entry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up esphome numbers based on a config entry."""
    await platform_async_setup_entry(
        hass,
        entry,
        async_add_entities,
        component_key="number",
        info_type=NumberInfo,
        entity_type=EsphomeNumber,
        state_type=NumberState,
    )


# https://github.com/PyCQA/pylint/issues/3150 for all @esphome_state_property
# pylint: disable=invalid-overridden-method


class EsphomeNumber(EsphomeEntity[NumberInfo, NumberState], NumberEntity):
    """A number implementation for esphome."""

    @property
    def min_value(self) -> float:
        """Return the minimum value."""
        return super()._static_info.min_value

    @property
    def max_value(self) -> float:
        """Return the maximum value."""
        return super()._static_info.max_value

    @property
    def step(self) -> float:
        """Return the increment/decrement step."""
        return super()._static_info.step

    @property
    def unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return super()._static_info.unit_of_measurement

    @esphome_state_property
    def value(self) -> float | None:
        """Return the state of the entity."""
        if math.isnan(self._state.state):
            return None
        if self._state.missing_state:
            return None
        return self._state.state

    async def async_set_value(self, value: float) -> None:
        """Update the current value."""
        await self._client.number_command(self._static_info.key, value)
