"""Support for by a Remootio device controlled garage door or gate."""
from __future__ import annotations

import logging
from typing import Any

from aioremootio import (
    ConnectionOptions,
    Event,
    EventType,
    Listener,
    RemootioClient,
    State,
    StateChange,
)

from homeassistant.components import cover
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_CLASS, CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_API_AUTH_KEY,
    CONF_API_SECRET_KEY,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    ED_ENTITY_ID,
    ED_NAME,
    ED_SERIAL_NUMBER,
)
from .utils import create_client

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up an ``RemootioCover`` entity based on the given configuration entry."""

    _LOGGER.debug("config_entry [%s]" % config_entry.as_dict())

    connection_options: ConnectionOptions = ConnectionOptions(
        config_entry.data[CONF_IP_ADDRESS],
        config_entry.data[CONF_API_SECRET_KEY],
        config_entry.data[CONF_API_AUTH_KEY],
    )
    serial_number: str = config_entry.data[CONF_SERIAL_NUMBER]
    device_class: str = config_entry.data[CONF_DEVICE_CLASS]

    remootio_client: RemootioClient = await create_client(
        hass, connection_options, _LOGGER, serial_number
    )

    async_add_entities(
        [
            RemootioCover(
                serial_number, config_entry.title, device_class, remootio_client
            )
        ]
    )


class RemootioCover(cover.CoverEntity):
    """Cover entity which represents an Remootio device controlled garage door or gate."""

    __name: str
    __unique_id: str
    __device_class: str
    __remootio_client: RemootioClient
    __device_info: DeviceInfo

    def __init__(
        self,
        unique_id: str,
        name: str,
        device_class: str,
        remootio_client: RemootioClient,
    ) -> None:
        """Initialize this cover entity."""
        super().__init__()
        self.__name = name
        self.__unique_id = unique_id
        self.__device_class = device_class
        self.__remootio_client = remootio_client
        self.__device_info = DeviceInfo(
            name="Remootio",
            manufacturer="Assemblabs Ltd",
            suggested_area="The first end-to-end encrypted Wi-Fi and Bluetooth enabled smart remote controller, "
            "that lets you control and monitor your gates and garage doors using your smartphone.",
        )

    async def async_added_to_hass(self) -> None:
        """Register listeners to the used Remootio client to be notified on state changes and events."""
        await self.__remootio_client.add_state_change_listener(
            RemootioCoverStateChangeListener(self)
        )

        await self.__remootio_client.add_event_listener(
            RemootioCoverEventListener(self)
        )

        self.async_schedule_update_ha_state(force_refresh=True)

    async def async_will_remove_from_hass(self) -> None:
        """Terminate the used Remootio client."""
        await self.__remootio_client.terminate()

    async def async_update(self) -> None:
        """Trigger state update of the used Remootio client."""
        await self.__remootio_client.trigger_state_update()

    @property
    def should_poll(self) -> bool:
        """Home Assistant shouldn't check this entity for an updated state because it notifies Home Assistant about state changes, therefore this method always returns False."""
        return False

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of this entity. Serial number of the connected Remmotio device."""
        return self.__unique_id

    @property
    def name(self) -> str | None:
        """Return the name of this entity."""
        return self.__name

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return information about the Remootio device."""
        return self.__device_info

    @property
    def device_class(self) -> str | None:
        """Return the device class of the represented device."""
        return self.__device_class

    @property
    def supported_features(self) -> int:
        """Return the features supported by the represented device."""
        return cover.SUPPORT_OPEN | cover.SUPPORT_CLOSE

    @property
    def is_opening(self):
        """Return True when the Remootio controlled garage door or gate is currently opening."""
        result: bool = self.__remootio_client.state == State.OPENING
        _LOGGER.debug(f"is_opening [{result}]")
        return result

    @property
    def is_closing(self):
        """Return True when the Remootio controlled garage door or gate is currently closing."""
        result: bool = self.__remootio_client.state == State.CLOSING
        _LOGGER.debug(f"is_closing [{result}]")
        return result

    @property
    def is_closed(self):
        """Return True when the Remootio controlled garage door or gate is currently closed."""
        result: bool = self.__remootio_client.state == State.CLOSED
        _LOGGER.debug(f"is_closed [{result}]")
        return result

    def open_cover(self, **kwargs: Any) -> None:
        """Open the Remootio controlled garage door or gate."""
        self.hass.async_create_task(self.async_open_cover())

    async def async_open_cover(self, **kwargs):
        """Open the Remootio controlled garage door or gate."""
        await self.__remootio_client.trigger_open()

    def close_cover(self, **kwargs: Any) -> None:
        """Close the Remootio controlled garage door or gate."""
        self.hass.async_create_task(self.async_close_cover())

    async def async_close_cover(self, **kwargs):
        """Close the Remootio controlled garage door or gate."""
        await self.__remootio_client.trigger_close()


class RemootioCoverStateChangeListener(Listener[StateChange]):
    """Listener to be invoked when Remootio controlled garage door or gate changes its state."""

    __owner: RemootioCover

    def __init__(self, owner: RemootioCover) -> None:
        """Initialize an instance of this class."""
        super().__init__()
        self.__owner = owner

    async def execute(self, client: RemootioClient, subject: StateChange) -> None:
        """Execute this listener. Tell Home Assistant that the Remootio controlled garage door or gate has changed its state."""
        _LOGGER.debug(
            f"Telling Home Assistant that the Remootio controlled garage door or gate has changed its state. RemootioClientState [{client.state}] RemootioCoverEntityId [{self.__owner.entity_id}] RemootioCoverUniqueId [{self.__owner.unique_id}] RemootioCoverState [{self.__owner.state}]"
        )
        self.__owner.async_schedule_update_ha_state()


class RemootioCoverEventListener(Listener[Event]):
    """Listener to be invoked on an event sent by the Remmotio device."""

    __owner: RemootioCover

    def __init__(self, owner: RemootioCover) -> None:
        """Initialize an instance of this class."""
        super().__init__()
        self.__owner = owner

    async def execute(self, client: RemootioClient, subject: Event) -> None:
        """Execute this listener. Fire events in Home Assistant based on events sent by the Remootio device.

        Fires the event remootio_left_open in Home Assistant when the Remootio controlled garage door or gate has been left open.
        As event data the serial number of the Remootio device (also the id of the entity which represents it in Home Assistant) and
        the name of the entity which represents the Remootio device in Home Assistant will be passed to the fired event.
        """
        if subject.type == EventType.LEFT_OPEN:
            event_type = f"{DOMAIN.lower()}_{subject.type.name.lower()}"

            _LOGGER.debug(
                f"Firing event. EvenType [{event_type}] RemootioCoverEntityId [{self.__owner.entity_id}] RemootioCoverUniqueId [{self.__owner.unique_id}]"
            )

            self.__owner.hass.bus.async_fire(
                event_type,
                {
                    ED_ENTITY_ID: self.__owner.entity_id,
                    ED_SERIAL_NUMBER: self.__owner.unique_id,
                    ED_NAME: self.__owner.name,
                },
            )
