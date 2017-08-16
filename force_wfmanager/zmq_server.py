import logging
import threading
import zmq
from pyface.api import GUI


log = logging.getLogger(__name__)


class ZMQServer(threading.Thread):

    STATE_STOPPED = "STOPPED"
    STATE_WAITING = "WAITING"
    STATE_RECEIVING = "RECEIVING"

    def __init__(self, config, analysis_model):
        super(ZMQServer, self).__init__()
        self.daemon = True
        self.config = config
        self.state = ZMQServer.STATE_STOPPED
        self.analysis_model = analysis_model

        self._context = zmq.Context()
        self._pub_socket = None
        self._rep_socket = None

    def run(self):
        if self.state != ZMQServer.STATE_STOPPED:
            return

        # Socket to talk to server
        log.info("Server started")

        self._pub_socket, self._rep_socket = self._setup_sockets()

        poller = zmq.Poller()
        poller.register(self._pub_socket)
        poller.register(self._rep_socket)

        self.state = ZMQServer.STATE_WAITING

        while True:
            events = dict(poller.poll())
            pub_data = None
            rep_data = None

            if self._pub_socket in events:
                pub_data = self._pub_socket.recv_string()

            if self._rep_socket in events:
                rep_data = self._rep_socket.recv_string()

            handle = getattr(self, "_handle_"+self.state)
            handle(events, pub_data, rep_data)

    def _setup_sockets(self):
        context = self._context
        pub_socket = context.socket(zmq.SUB)
        pub_socket.bind(self.config.pub_socket_url)
        pub_socket.setsockopt(zmq.SUBSCRIBE, "".encode("utf-8"))
        pub_socket.setsockopt(zmq.LINGER, 0)

        rep_socket = context.socket(zmq.REP)
        rep_socket.setsockopt(zmq.LINGER, 0)
        rep_socket.bind(self.config.rep_socket_url)

        return pub_socket, rep_socket

    def _handle_WAITING(self, pub_data, rep_data):
        if rep_data is not None:
            if rep_data.startswith("HELLO\n"):
                self._rep_socket.send_string(rep_data)
                self.state = ZMQServer.STATE_RECEIVING
                return
            else:
                log.error("Unknown request received {}".format(rep_data))

    def _handle_RECEIVING(self, pub_data, rep_data):
        if rep_data is not None:
            if rep_data.startswith("GOODBYE\n"):
                self._rep_socket.send_string(rep_data)
                self.state = ZMQServer.STATE_WAITING
                return
            else:
                log.error("Unknown request received {}".format(rep_data))
                return

        if pub_data is not None:
            if pub_data.startswith("EVENT"):
                split_data = pub_data.split("\n")
                if split_data[2] == "MCO_PROGRESS":
                    self._deliver_info(split_data[3:])
                elif split_data[2] == "MCO_START":
                    self._reset_info()
                else:
                    log.error("Received data while waiting. Discarding")
            else:
                log.error("Unrecognized message received. Discarding")


    def _deliver_info(self, data):
        def _add_data():
            if len(self.analysis_model.value_names) == 0:
                self.analysis_model.value_names = ["x", "y"]

            data_float = map(float, data)
            self.analysis_model.evaluation_steps.append(data_float)

        GUI.invoke_later(_add_data)

    def _reset_info(self):
        def _add_data():
            self.analysis_model.value_names = []
            self.analysis_model.evaluation_steps[:] = []

        GUI.invoke_later(_add_data)
