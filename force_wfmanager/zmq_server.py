import logging
import threading
import pickle

import zmq

from pyface.api import GUI
from force_bdss.api import MCOProgressEvent, MCOStartEvent, MCOFinishEvent


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
        self._sync_socket = None

    def run(self):
        if self.state != ZMQServer.STATE_STOPPED:
            return

        # Socket to talk to server
        log.info("Server started")

        self._pub_socket, self._sync_socket = self._setup_sockets()

        poller = zmq.Poller()
        poller.register(self._pub_socket)
        poller.register(self._sync_socket)

        self.state = ZMQServer.STATE_WAITING

        while True:
            events = dict(poller.poll())

            if self._sync_socket in events:
                sync_data = self._sync_socket.recv_multipart()
                try:
                    handle = getattr(self, "_handle_"+self.state+"_sync")
                except AttributeError:
                    log.error("State {} cannot handle sync data. "
                              "Discarding.".format(self.state))
                else:
                    handle(sync_data)

            if self._pub_socket in events:
                pub_data = self._pub_socket.recv_multipart()
                try:
                    handle = getattr(self, "_handle_"+self.state+"_pub")
                except AttributeError:
                    log.error("State {} cannot handle pub data. "
                              "Discarding.".format(self.state))
                else:
                    handle(pub_data)

    def _setup_sockets(self):
        context = self._context
        pub_socket = context.socket(zmq.SUB)
        pub_socket.bind(self.config.pub_url)
        pub_socket.setsockopt(zmq.SUBSCRIBE, "".encode("utf-8"))
        pub_socket.setsockopt(zmq.LINGER, 0)

        sync_socket = context.socket(zmq.REP)
        sync_socket.setsockopt(zmq.LINGER, 0)
        sync_socket.bind(self.config.sync_url)

        return pub_socket, sync_socket

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
            log.error("Unknown msg received {}".format(msg))
            return

        self._sync_socket.send_multipart(data)
        self.state = ZMQServer.STATE_WAITING

    def _handle_RECEIVING_pub(self, data):
        if len(data) != 3:
            log.error("Unknown request received {}".format(data))
            return

        msg, identifier, pickle_data = data

        if msg != "MESSAGE":
            log.error("Unknown msg received {}".format(msg))
            return


        try:
            event = pickle.loads(pickle_data)
        except Exception as e:
            log.error("Received pickle data. Discarding")

        if isinstance(event, MCOProgressEvent):
            self._deliver_info(event.input + event.output)
        elif isinstance(event, MCOStartEvent):
            self._reset_info()
        elif isinstance(event, MCOFinishEvent):
            pass
        else:
            log.error("Received unrecognized type data while waiting. Discarding")

    def _deliver_info(self, data):
        def _add_data():
            if len(self.analysis_model.value_names) == 0:
                self.analysis_model.value_names = ["x", "y"]

            data_float = tuple(map(float, data))
            self.analysis_model.evaluation_steps.append(data_float)

        GUI.invoke_later(_add_data)

    def _reset_info(self):
        def _add_data():
            self.analysis_model.value_names = []
            self.analysis_model.evaluation_steps[:] = []

        GUI.invoke_later(_add_data)
