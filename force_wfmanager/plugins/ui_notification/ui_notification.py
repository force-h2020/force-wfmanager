import logging

import zmq
from traits.api import Instance, String

from force_bdss.api import (
    BaseNotificationListener,
    BaseDriverEvent,
)
from .event_serializer import EventSerializer

log = logging.getLogger(__name__)


class UINotification(BaseNotificationListener):
    """
    Notification engine for the UI. Uses zeromq for the traffic handling.
    """
    #: The ZMQ context. If None, it means that the service is unavailable.
    _context = Instance(zmq.Context)

    #: The pubsub socket.
    _pub_socket = Instance(zmq.Socket)

    #: The synchronization socket to communicate with the server (UI)
    _sync_socket = Instance(zmq.Socket)

    #: Unique identifier from the UI. To be returned in the protocol.
    _identifier = String()

    #: The protocol version that this plugin delivers
    _proto_version = "1"

    #: The serializer for the event.
    _serializer = Instance(EventSerializer)

    def initialize(self, model):
        self._identifier = model.identifier
        self._context = self._create_context()

        self._pub_socket = self._context.socket(zmq.PUB)
        self._pub_socket.setsockopt(zmq.LINGER, 0)
        self._pub_socket.connect(model.pub_url)

        self._sync_socket = self._context.socket(zmq.REQ)
        self._sync_socket.setsockopt(zmq.LINGER, 0)
        self._sync_socket.connect(model.sync_url)

        msg = ["HELLO",
               str(self._identifier),
               str(self._proto_version)]
        self._sync_socket.send_multipart(msg)
        events = self._sync_socket.poll(1000, zmq.POLLIN)

        if events == 0:
            log.info("Could not connect to UI server after 1000 ms. "
                     "Continuing without UI notification.")
            self._close_and_clear_sockets()
            return

        recv = self._sync_socket.recv_multipart()

        if recv != msg:
            log.error(
                ("Unexpected reply in sync"
                 " negotiation with UI server. '{}'".format(recv)))
            self._close_and_clear_sockets()
            return

    def deliver(self, event):
        if not self._context:
            return

        if not isinstance(event, BaseDriverEvent):
            raise TypeError("Event is not a BaseDriverEvent")

        data = self._serializer.serialize(event)
        self._pub_socket.send_multipart(
            ["MESSAGE", self._identifier, data])

    def finalize(self):
        if not self._context:
            return

        msg = ["GOODBYE", str(self._identifier)]
        self._sync_socket.send_multipart(msg)
        events = self._sync_socket.poll(1000, zmq.POLLIN)
        if events == 0:
            log.error("Could not close connection to UI server after "
                      "1000 ms.")
            self._close_and_clear_sockets()
            return

        recv = self._sync_socket.recv_multipart()

        if recv != msg:
            log.error(
                ("Unexpected reply in goodbye sync"
                 " negotiation with UI server. '{}'".format(recv)))

        self._close_and_clear_sockets()

    def _close_and_clear_sockets(self):
        if self._pub_socket:
            self._pub_socket.close()

        if self._sync_socket:
            self._sync_socket.close()

        if self._context:
            self._context.term()

        self._pub_socket = None
        self._sync_socket = None
        self._context = None

    def _create_context(self):
        return zmq.Context()

    def __serializer_default(self):
        return EventSerializer()
