from concurrent.futures import ThreadPoolExecutor
import logging
import zmq

from traits.api import Instance, String, Bool

from force_bdss.api import (
    BaseNotificationListener,
    BaseDriverEvent,
    UIEventNotificationMixin,
)

log = logging.getLogger(__name__)


class UINotification(BaseNotificationListener, UIEventNotificationMixin):
    """
    Notification engine for the UI. Uses zeromq for the traffic handling.
    """

    #: The ZMQ context. If None, it means that the service is unavailable.
    _context = Instance(zmq.Context)

    #: The Publisher pubsub socket.
    _pub_socket = Instance(zmq.Socket)

    #: The Subscriber pubsub socket.
    _sub_socket = Instance(zmq.Socket)

    #: The synchronization socket to communicate with the server (UI)
    _sync_socket = Instance(zmq.Socket)

    #: zmq.Poller state. If not `_poller_running`, then the Listener
    #: doesn't poll the Publishing socket on the WfManager side.
    _poller_running = Bool(False)

    #: Unique identifier from the UI. To be returned in the protocol.
    _identifier = String()

    #: The protocol version that this plugin delivers
    _proto_version = "1"

    # ----------------
    #  Private Methods
    # ----------------

    def _close_and_clear_sockets(self):
        if self._pub_socket:
            self._pub_socket.close()

        if self._sync_socket:
            self._sync_socket.close()

        if self._sub_socket:
            self._sub_socket.close()

        if self._context:
            self._context.term()

        self._pub_socket = None
        self._sync_socket = None
        self._sub_socket = None
        self._context = None

    def _create_context(self):
        return zmq.Context()

    # ----------------
    #  Public Methods
    # ----------------

    def initialize(self, model):
        """ Sets up the zmq sockets and context to connects to the Workflow
        Manager server. Called when the notification
        listeners are set up in :mod:`force_bdss.core_mco_driver`. Sends a
        'HELLO' message to the ZMQ Server in
        :mod:`force_wfmanager.wfmanager_setup_task`.
        """
        self._identifier = model.identifier
        self._context = self._create_context()

        self._pub_socket = self._context.socket(zmq.PUB)
        self._pub_socket.setsockopt(zmq.LINGER, 0)
        self._pub_socket.connect(model.pub_url)

        self._sub_socket = self._context.socket(zmq.SUB)
        self._sub_socket.setsockopt(zmq.SUBSCRIBE, "".encode("utf-8"))
        self._sub_socket.setsockopt(zmq.LINGER, 0)
        self._sub_socket.connect(model.sub_url)

        self._sync_socket = self._context.socket(zmq.REQ)
        self._sync_socket.setsockopt(zmq.LINGER, 0)
        self._sync_socket.connect(model.sync_url)

        msg = [
            x.encode("utf-8")
            for x in ["HELLO", self._identifier, self._proto_version]
        ]

        # Send a special "HELLO" message to the zmq server. This is sent to the
        # 'sync' socket and should be handled by the '_handle_WAITING_sync'
        # method in ZMQServer
        self._sync_socket.send_multipart(msg)
        events = self._sync_socket.poll(1000, zmq.POLLIN)

        if events == 0:
            log.info(
                "Could not connect to UI server after 1000 ms. "
                "Continuing without UI notification."
            )
            self._close_and_clear_sockets()
            return

        # The server should send back an identical response
        recv = self._sync_socket.recv_multipart()
        if recv != msg:
            log.error(
                (
                    "Unexpected reply in sync"
                    " negotiation with UI server. '{}'".format(
                        [x.decode("utf-8") for x in recv]
                    )
                )
            )
            self._close_and_clear_sockets()
            return

        poll_executor = ThreadPoolExecutor(max_workers=1)
        poll_executor.submit(self.run_poller, self._sub_socket)

    def run_poller(self, sub_socket):
        """ Instantiates a zmq.Poller bound to the `sub_socket` until the
        self._poller_running is not set to False. The self._poller_running is
        set to false either when a `STOP_BDSS` message is received, or when the
        Listener is finalized.
        """
        poller = zmq.Poller()
        poller.register(sub_socket)
        self._poller_running = True

        while self._poller_running:
            events = dict(poller.poll())
            if sub_socket not in events:
                continue

            data = [x.decode("utf-8") for x in sub_socket.recv_multipart()]
            try:
                msg, identifier, serialized_data = data
                if identifier == "STOP_BDSS":
                    self._poller_running = False
                    self.send_stop()
                if identifier == "PAUSE_BDSS":
                    self.send_pause()
                if identifier == "RESUME_BDSS":
                    self.send_resume()
            except Exception as e:
                log.warning(f"Poller exception {e}")

    def deliver(self, event):
        """ Serializes as JSON and sends a BaseDriverEvent (see
        :class:`force_bdss.events.base_driver_event.BaseDriverEvent`)
        as a message to the ZMQServer.

        Parameters
        ----------
        event: BaseDriverEvent
            The event to send to the server

        Raises
        ------
        TypeError:
            Raises if `event` is not a `BaseDriverEvent`
        """
        if not self._context:
            return

        if not isinstance(event, BaseDriverEvent):
            raise TypeError("Event is not a BaseDriverEvent")

        data = event.dumps_json()

        self._pub_socket.send_multipart(
            [x.encode("utf-8") for x in ["MESSAGE", self._identifier, data]]
        )

    def finalize(self):
        """ Disconnects from the ZMQServer."""
        if not self._context:
            return
        self._poller_running = False

        msg = [x.encode("utf-8") for x in ["GOODBYE", self._identifier]]
        self._sync_socket.send_multipart(msg)
        events = self._sync_socket.poll(1000, zmq.POLLIN)
        if events == 0:
            log.error(
                "Could not close connection to UI server after " "1000 ms."
            )
            self._close_and_clear_sockets()
            return

        recv = self._sync_socket.recv_multipart()

        if recv != msg:
            log.error(
                (
                    "Unexpected reply in goodbye sync"
                    " negotiation with UI server. '{}'".format(
                        [x.decode("utf-8") for x in recv]
                    )
                )
            )

        self._close_and_clear_sockets()
