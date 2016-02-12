"""
homeassistant.components.notify.command_line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
command_line notification service.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/notify.command_line/
"""
import logging
import subprocess
import shlex
from homeassistant.helpers import validate_config
from homeassistant.components.notify import (
    DOMAIN, BaseNotificationService)

_LOGGER = logging.getLogger(__name__)


def get_service(hass, config):
    """ Get the Command Line notification service. """

    if not validate_config({DOMAIN: config},
                           {DOMAIN: ['command']},
                           _LOGGER):
        return None

    command = config['command']

    return CommandLineNotificationService(command)


# pylint: disable=too-few-public-methods
class CommandLineNotificationService(BaseNotificationService):
    """ Implements notification service for the Command Line service. """

    def __init__(self, command):
        self.command = command

    def send_message(self, message="", **kwargs):
        """ Send a message to a command_line. """
        try:
            subprocess.check_call(
                "{} {}".format(self.command,
                               shlex.quote(message)),
                shell=True)
        except subprocess.CalledProcessError:
            _LOGGER.error('Command failed: %s', self.command)
