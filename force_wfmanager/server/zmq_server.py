import logging
import threading

import zmq

from force_wfmanager.server.event_deserializer import (
    EventDeserializer, DeserializerError)

log = logging.getLogger(__name__)


class ZMQServer(threading.Thread):
    """ZeroMQ based server. It is a state machine with different
    handlers. New behavior is added by adding or modifying the current
    handle methods.

    Handler methods have the form

    _handle_[STATE]_[socket].

    where [STATE] is the string associated to the state (see STATE_* enum
    in class) and [socket] is "pub" for handling data from the pubsub socket,
    "sync" for handling data from the synchronization (req/rep) socket.
    """

    STATE_STOPPED = "STOPPED"
    STATE_WAITING = "WAITING"
    STATE_RECEIVING = "RECEIVING"

    def __init__(self, config, on_event_callback):
        """Sets up the server with the appropriate configuration.
        When the event is detected, on_event_callback will be called
        _in_the_secondary_thread_.

        Parameters
        ----------
        config: ZMQServerConfig
            The configuration options of the server
        on_event_callback: function
            A function or method to call when a new event is received.
            This function will be called by the secondary thread
            (this thread).
        """
        super(ZMQServer, self).__init__(name="ZMQServer")
        self.daemon = True
        self.config = config
        self.state = ZMQServer.STATE_STOPPED
        self._on_event_callback = on_event_callback

        self._context = self._get_context()
        self._pub_socket = None
        self._sync_socket = None
        self._inproc_socket = None
        self._deserializer = EventDeserializer()

    def run(self):
        if self.state != ZMQServer.STATE_STOPPED:
            return

        # Socket to talk to server
        log.info("Server started")

        (self._pub_socket,
         self._sync_socket,
         self._inproc_socket) = self._setup_sockets()

        poller = self._get_poller()
        poller.register(self._pub_socket)
        poller.register(self._sync_socket)
        poller.register(self._inproc_socket)

        self.state = ZMQServer.STATE_WAITING

        while True:
            events = dict(poller.poll())

            for socket_name, socket in [
                    ("sync", self._sync_socket),
                    ("pub", self._pub_socket),
                    ]:

                if socket not in events:
                    continue

                data = [x.decode('utf-8') for x in socket.recv_multipart()]

                try:
                    handle = getattr(
                        self,
                        "_handle_"+self.state+"_"+socket_name)
                except AttributeError:
                    log.error("State {} cannot handle {} data. "
                              "Discarding.".format(self.state,
                                                   socket_name))
                else:
                    handle(data)

            if self._inproc_socket in events:
                self._inproc_socket.recv()
                self._pub_socket.close()
                self._sync_socket.close()
                self.state = ZMQServer.STATE_STOPPED
                self._inproc_socket.send(''.encode('utf-8'))
                self._inproc_socket.close()
                return

    def stop(self):
        """Stops the server. This method is synchronous.
        It stops until the server acknowledges that it
        stopped. If you want to timeout, wrap this call in
        a future and timeout the future."""
        try:
            socket = self._context.socket(zmq.PAIR)
            socket.setsockopt(zmq.RCVTIMEO, 1000)
            socket.setsockopt(zmq.SNDTIMEO, 1000)
            socket.setsockopt(zmq.LINGER, 0)
            socket.connect("inproc://stop")
            socket.send("".encode("utf-8"))
            socket.recv()
        except Exception:
            # If anything goes wrong at this stage, just log it and
            # ignore
            log.exception("Error while attempting to stop server")
        finally:
            socket.close()

    def _setup_sockets(self):
        """Sets up the sockets."""
        context = self._context
        pub_socket = context.socket(zmq.SUB)
        pub_socket.setsockopt(zmq.SUBSCRIBE, "".encode("utf-8"))
        pub_socket.setsockopt(zmq.LINGER, 0)
        pub_socket.bind(self.config.pub_url)

        sync_socket = context.socket(zmq.REP)
        sync_socket.setsockopt(zmq.LINGER, 0)
        sync_socket.bind(self.config.sync_url)

        inproc_socket = context.socket(zmq.PAIR)
        inproc_socket.bind("inproc://stop")
        return pub_socket, sync_socket, inproc_socket

    def _get_context(self):
        return zmq.Context()

    def _get_poller(self):
        return zmq.Poller()

    # Handlers. Check format in class docstring.

    def _handle_WAITING_sync(self, data):
        if len(data) != 3:
            log.error("Unknown request received {}".format(data))
            return

        msg, identifier, protocol = data
        if msg != "HELLO":
            log.error("Unknown msg request received {}".format(msg))
            return

        if protocol != "1":
            log.error("Unknown protocol received {}".format(protocol))
            return

        self._sync_socket.send_multipart(data)
        self.state = ZMQServer.STATE_RECEIVING

    def _handle_RECEIVING_sync(self, data):
        if len(data) != 2:
            log.error("Unknown request received {}".format(data))
            return

        msg, identifier = data

        if msg != "GOODBYE":
            log.error("Unknown msg request received {}".format(msg))
            return

        self._sync_socket.send_multipart(data)
        self.state = ZMQServer.STATE_WAITING

    def _handle_RECEIVING_pub(self, data):
        if len(data) != 3:
            log.error("Unknown request received {}".format(data))
            return

        msg, identifier, serialized_data = data

        if msg != "MESSAGE":
            log.error("Unknown msg request received {}".format(msg))
            return

        try:
            event = self._deserializer.deserialize(serialized_data)
        except DeserializerError:
            log.error("Received invalid data. Discarding")
            return

        self._on_event_callback(event)
