import logging
import threading
import zmq
from pyface.api import GUI


log = logging.getLogger(__name__)


class ZMQServer(threading.Thread):

    (STATE_STOPPED,
     STATE_WAITING,
     STATE_RECEIVING) = range(3)

    def __init__(self, config, analysis_model):
        super(ZMQServer, self).__init__()
        self.daemon = True
        self.config = config
        self._context = zmq.Context()
        self.analysis_model = analysis_model
        self.state = ZMQServer.STATE_STOPPED

    def run(self):
        if self.state != ZMQServer.STATE_STOPPED:
            return

        # Socket to talk to server
        log.info("Server started")

        pub_socket, rep_socket = self._setup_sockets()

        poller = zmq.Poller()
        poller.register(pub_socket)
        poller.register(rep_socket)

        state = ZMQServer.STATE_WAITING

        while True:
            events = dict(poller.poll())
            if rep_socket in events:
                data = rep_socket.recv_string()
                if data.startswith("HELLO\n"):
                    rep_socket.send_string(data)
                    state = ZMQServer.STATE_RECEIVING
                elif data.startswith("GOODBYE\n"):
                    rep_socket.send_string(data)
                    state = ZMQServer.STATE_WAITING
                else:
                    log.error("Unknown request received {}".format(data))

            if pub_socket in events:
                if state == ZMQServer.STATE_RECEIVING:
                    string = pub_socket.recv_string()
                    split_data = string.split("\n")
                    if split_data[2] == "MCO_PROGRESS":
                        self._deliver_info(split_data[3:])
                    elif split_data[2] == "MCO_START":
                        self._reset_info()
                else:
                    log.error("Received data while waiting. Discarding")
                    string = pub_socket.recv_string()

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
