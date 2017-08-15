import logging
import threading
import zmq
from pyface.api import GUI


log = logging.getLogger(__name__)


class ZMQServer(threading.Thread):
    daemon = True
    def __init__(self, analysis_model):
        super(ZMQServer, self).__init__()
        self.context = zmq.Context()
        self.analysis_model = analysis_model

    def run(self):
        # Socket to talk to server
        print("hello")
        context = self.context
        sub_socket = context.socket(zmq.SUB)
        sub_socket.bind("tcp://*:12345")
        sub_socket.setsockopt(zmq.SUBSCRIBE, "".encode("utf-8"))
        sub_socket.setsockopt(zmq.LINGER, 0)

        sync_socket = context.socket(zmq.REP)
        sync_socket.setsockopt(zmq.LINGER, 0)
        sync_socket.bind("tcp://*:12346")

        poller = zmq.Poller()
        poller.register(sub_socket)
        poller.register(sync_socket)

        WAITING = 0
        RECEIVING = 1

        state = WAITING

        while True:
            print("polling")
            events = dict(poller.poll())
            print(events)
            if sync_socket in events:
                data = sync_socket.recv_string()
                print("received ", data)
                if data.startswith("HELLO\n"):
                    sync_socket.send_string(data)
                    state = RECEIVING
                elif data.startswith("GOODBYE\n"):
                    sync_socket.send_string(data)
                    state = WAITING
                else:
                    print("unknown request", data)

            if sub_socket in events:
                if state == RECEIVING:
                    string = sub_socket.recv_string()
                    split_data = string.split("\n")
                    if split_data[2] == "MCO_PROGRESS":
                        self._deliver_info(split_data[3:])
                    elif split_data[2] == "MCO_START":
                        self._reset_info()
                else:
                    print("data while waiting. discarding")
                    string = sub_socket.recv_string()

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
