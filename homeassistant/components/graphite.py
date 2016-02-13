"""
homeassistant.components.graphite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Component that records all events and state changes and feeds the data to
a graphite installation.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/graphite/
"""
import logging
import queue
import socket
import threading
import time

from homeassistant.const import (
    EVENT_STATE_CHANGED,
    EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STOP)
from homeassistant.helpers import state

DOMAIN = "graphite"
_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """ Setup graphite feeder. """
    graphite_config = config.get('graphite', {})
    host = graphite_config.get('host', 'localhost')
    prefix = graphite_config.get('prefix', 'ha')
    try:
        port = int(graphite_config.get('port', 2003))
    except ValueError:
        _LOGGER.error('Invalid port specified')
        return False

    GraphiteFeeder(hass, host, port, prefix)
    return True


class GraphiteFeeder(threading.Thread):
    """ Feeds data to graphite. """
    def __init__(self, hass, host, port, prefix):
        super(GraphiteFeeder, self).__init__(daemon=True)
        self._hass = hass
        self._host = host
        self._port = port
        # rstrip any trailing dots in case they think they
        # need it
        self._prefix = prefix.rstrip('.')
        self._queue = queue.Queue()
        self._quit_object = object()

        hass.bus.listen_once(EVENT_HOMEASSISTANT_START,
                             self.start_listen)
        hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP,
                             self.shutdown)
        hass.bus.listen(EVENT_STATE_CHANGED, self.event_listener)

    def start_listen(self, event):
        """ Start event-processing thread. """
        self.start()

    def shutdown(self, event):
        """ Tell the thread that we are done.

        This does not block because there is nothing to
        clean up (and no penalty for killing in-process
        connections to graphite.
        """
        self._queue.put(self._quit_object)

    def event_listener(self, event):
        """ Queue an event for processing. """
        self._queue.put(event)

    def _send_to_graphite(self, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((self._host, self._port))
        sock.sendall(data.encode('ascii'))
        sock.send('\n'.encode('ascii'))
        sock.close()

    def _report_attributes(self, entity_id, new_state):
        now = time.time()
        things = dict(new_state.attributes)
        try:
            things['state'] = state.state_as_number(new_state)
        except ValueError:
            pass
        lines = ['%s.%s.%s %f %i' % (self._prefix,
                                     entity_id, key.replace(' ', '_'),
                                     value, now)
                 for key, value in things.items()
                 if isinstance(value, (float, int))]
        if not lines:
            return
        _LOGGER.debug('Sending to graphite: %s', lines)
        try:
            self._send_to_graphite('\n'.join(lines))
        except socket.error:
            _LOGGER.exception('Failed to send data to graphite')

    def run(self):
        while True:
            event = self._queue.get()
            if event == self._quit_object:
                self._queue.task_done()
                return
            elif (event.event_type == EVENT_STATE_CHANGED and
                  'new_state' in event.data):
                self._report_attributes(event.data['entity_id'],
                                        event.data['new_state'])
            self._queue.task_done()
