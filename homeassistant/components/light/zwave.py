"""
Support for Z-Wave lights.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/light.zwave/
"""
import logging

# Because we do not compile openzwave on CI
# pylint: disable=import-error
from threading import Timer
from homeassistant.components.light import ATTR_BRIGHTNESS, ATTR_COLOR_TEMP, \
    ATTR_RGB_COLOR, DOMAIN, Light
from homeassistant.components import zwave
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.util.color import HASS_COLOR_MAX, HASS_COLOR_MIN, \
    color_temperature_mired_to_kelvin, color_temperature_to_rgb

_LOGGER = logging.getLogger(__name__)

COLOR_CHANNEL_WARM_WHITE = 0x01
COLOR_CHANNEL_COLD_WHITE = 0x02
COLOR_CHANNEL_RED = 0x04
COLOR_CHANNEL_GREEN = 0x08
COLOR_CHANNEL_BLUE = 0x10

# Generate midpoint color temperatures for bulbs that have limited
# support for white light colors
TEMP_MID_HASS = (HASS_COLOR_MAX - HASS_COLOR_MIN) / 2 + HASS_COLOR_MIN
TEMP_WARM_HASS = (HASS_COLOR_MAX - HASS_COLOR_MIN) / 3 * 2 + HASS_COLOR_MIN
TEMP_COLD_HASS = (HASS_COLOR_MAX - HASS_COLOR_MIN) / 3 + HASS_COLOR_MIN


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Find and add Z-Wave lights."""
    if discovery_info is None or zwave.NETWORK is None:
        return

    node = zwave.NETWORK.nodes[discovery_info[zwave.ATTR_NODE_ID]]
    value = node.values[discovery_info[zwave.ATTR_VALUE_ID]]

    if value.command_class != zwave.COMMAND_CLASS_SWITCH_MULTILEVEL:
        return
    if value.type != zwave.TYPE_BYTE:
        return
    if value.genre != zwave.GENRE_USER:
        return

    value.set_change_verified(False)

    if node.has_command_class(zwave.COMMAND_CLASS_COLOR):
        try:
            add_devices([ZwaveColorLight(value)])
        except ValueError as exception:
            _LOGGER.warning(
                "Error initializing as color bulb: %s "
                "Initializing as standard dimmer.", exception)
            add_devices([ZwaveDimmer(value)])
    else:
        add_devices([ZwaveDimmer(value)])


def brightness_state(value):
    """Return the brightness and state."""
    if value.data > 0:
        return (value.data / 99) * 255, STATE_ON
    else:
        return 255, STATE_OFF


class ZwaveDimmer(zwave.ZWaveDeviceEntity, Light):
    """Representation of a Z-Wave dimmer."""

    # pylint: disable=too-many-arguments
    def __init__(self, value):
        """Initialize the light."""
        from openzwave.network import ZWaveNetwork
        from pydispatch import dispatcher

        zwave.ZWaveDeviceEntity.__init__(self, value, DOMAIN)
        self._brightness = None
        self._state = None
        self.update_properties()

        # Used for value change event handling
        self._refreshing = False
        self._timer = None

        dispatcher.connect(
            self._value_changed, ZWaveNetwork.SIGNAL_VALUE_CHANGED)

    def update_properties(self):
        """Update internal properties based on zwave values."""
        # Brightness
        self._brightness, self._state = brightness_state(self._value)

    def _value_changed(self, value):
        """Called when a value has changed on the network."""
        if self._value.value_id != value.value_id:
            return

        if self._refreshing:
            self._refreshing = False
            self.update_properties()
        else:
            def _refresh_value():
                """Used timer callback for delayed value refresh."""
                self._refreshing = True
                self._value.refresh()

            if self._timer is not None and self._timer.isAlive():
                self._timer.cancel()

            self._timer = Timer(2, _refresh_value)
            self._timer.start()

        self.update_ha_state()

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        return self._brightness

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state == STATE_ON

    def turn_on(self, **kwargs):
        """Turn the device on."""
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]

        # Zwave multilevel switches use a range of [0, 99] to control
        # brightness.
        brightness = int((self._brightness / 255) * 99)

        if self._value.node.set_dimmer(self._value.value_id, brightness):
            self._state = STATE_ON

    def turn_off(self, **kwargs):
        """Turn the device off."""
        if self._value.node.set_dimmer(self._value.value_id, 0):
            self._state = STATE_OFF


def ct_to_rgb(temp):
    """Convert color temperature (mireds) to RGB."""
    colorlist = list(
        color_temperature_to_rgb(color_temperature_mired_to_kelvin(temp)))
    return [int(val) for val in colorlist]


class ZwaveColorLight(ZwaveDimmer):
    """Representation of a Z-Wave color changing light."""

    def __init__(self, value):
        """Initialize the light."""
        self._value_color = None
        self._value_color_channels = None
        self._color_channels = None
        self._rgb = None
        self._ct = None

        # Here we attempt to find a zwave color value with the same instance
        # id as the dimmer value. Currently zwave nodes that change colors
        # only include one dimmer and one color command, but this will
        # hopefully provide some forward compatibility for new devices that
        # have multiple color changing elements.
        for value_color in value.node.get_rgbbulbs().values():
            if value.instance == value_color.instance:
                self._value_color = value_color

        if self._value_color is None:
            raise ValueError("No matching color command found.")

        for value_color_channels in value.node.get_values(
                class_id=zwave.COMMAND_CLASS_COLOR, genre='System',
                type="Int").values():
            self._value_color_channels = value_color_channels

        if self._value_color_channels is None:
            raise ValueError("Color Channels not found.")

        super().__init__(value)

    def update_properties(self):
        """Update internal properties based on zwave values."""
        super().update_properties()

        # Color Channels
        self._color_channels = self._value_color_channels.data

        # Color Data String
        data = self._value_color.data

        # RGB is always present in the openzwave color data string.
        self._rgb = [
            int(data[1:3], 16),
            int(data[3:5], 16),
            int(data[5:7], 16)]

        # Parse remaining color channels. Openzwave appends white channels
        # that are present.
        index = 7

        # Warm white
        if self._color_channels & COLOR_CHANNEL_WARM_WHITE:
            warm_white = int(data[index:index+2], 16)
            index += 2
        else:
            warm_white = 0

        # Cold white
        if self._color_channels & COLOR_CHANNEL_COLD_WHITE:
            cold_white = int(data[index:index+2], 16)
            index += 2
        else:
            cold_white = 0

        # Color temperature. With two white channels, only two color
        # temperatures are supported for the bulb. The channel values
        # indicate brightness for warm/cold color temperature.
        if (self._color_channels & COLOR_CHANNEL_WARM_WHITE and
                self._color_channels & COLOR_CHANNEL_COLD_WHITE):
            if warm_white > 0:
                self._ct = TEMP_WARM_HASS
                self._rgb = ct_to_rgb(self._ct)
            elif cold_white > 0:
                self._ct = TEMP_COLD_HASS
                self._rgb = ct_to_rgb(self._ct)
            else:
                # RGB color is being used. Just report midpoint.
                self._ct = TEMP_MID_HASS

        # If only warm white is reported 0-255 is color temperature.
        elif self._color_channels & COLOR_CHANNEL_WARM_WHITE:
            self._ct = HASS_COLOR_MIN + (HASS_COLOR_MAX - HASS_COLOR_MIN) * (
                warm_white / 255)
            self._rgb = ct_to_rgb(self._ct)

        # If only cold white is reported 0-255 is negative color temperature.
        elif self._color_channels & COLOR_CHANNEL_COLD_WHITE:
            self._ct = HASS_COLOR_MIN + (HASS_COLOR_MAX - HASS_COLOR_MIN) * (
                (255 - cold_white) / 255)
            self._rgb = ct_to_rgb(self._ct)

        # If no rgb channels supported, report None.
        if not (self._color_channels & COLOR_CHANNEL_RED or
                self._color_channels & COLOR_CHANNEL_GREEN or
                self._color_channels & COLOR_CHANNEL_BLUE):
            self._rgb = None

    @property
    def rgb_color(self):
        """Return the rgb color."""
        return self._rgb

    @property
    def color_temp(self):
        """Return the color temperature."""
        return self._ct

    def turn_on(self, **kwargs):
        """Turn the device on."""
        rgbw = None

        if ATTR_COLOR_TEMP in kwargs:
            # With two white channels, only two color temperatures are
            # supported for the bulb.
            if (self._color_channels & COLOR_CHANNEL_WARM_WHITE and
                    self._color_channels & COLOR_CHANNEL_COLD_WHITE):
                if kwargs[ATTR_COLOR_TEMP] > TEMP_MID_HASS:
                    self._ct = TEMP_WARM_HASS
                    rgbw = b'#000000FF00'
                else:
                    self._ct = TEMP_COLD_HASS
                    rgbw = b'#00000000FF'

            # If only warm white is reported 0-255 is color temperature
            elif self._color_channels & COLOR_CHANNEL_WARM_WHITE:
                rgbw = b'#000000'
                temp = (
                    (kwargs[ATTR_COLOR_TEMP] - HASS_COLOR_MIN) /
                    (HASS_COLOR_MAX - HASS_COLOR_MIN) * 255)
                rgbw += format(int(temp)).encode('utf-8')

            # If only cold white is reported 0-255 is negative color temp
            elif self._color_channels & COLOR_CHANNEL_COLD_WHITE:
                rgbw = b'#000000'
                temp = (
                    255 - (kwargs[ATTR_COLOR_TEMP] - HASS_COLOR_MIN) /
                    (HASS_COLOR_MAX - HASS_COLOR_MIN) * 255)
                rgbw += format(int(temp)).encode('utf-8')

        elif ATTR_RGB_COLOR in kwargs:
            self._rgb = kwargs[ATTR_RGB_COLOR]

            rgbw = b'#'
            for colorval in self._rgb:
                rgbw += format(colorval, '02x').encode('utf-8')
            rgbw += b'0000'

        if rgbw is None:
            _LOGGER.warning("rgbw string was not generated for turn_on")
        else:
            self._value_color.node.set_rgbw(self._value_color.value_id, rgbw)

        super().turn_on(**kwargs)
