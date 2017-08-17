import json
import unittest

try:
    import mock
except ImportError:
    from unittest import mock

import time

from force_bdss.api import MCOStartEvent
from force_wfmanager.server.zmq_server import ZMQServer
from force_wfmanager.server.zmq_server_config import ZMQServerConfig


class TimeoutError(Exception):
    pass


def wait_condition(condition, seconds=5):
    count = 0
    while True:
        if condition():
            break
        time.sleep(1)
        count += 1
        if count == seconds:
            raise TimeoutError("timeout")


class MockPoller(object):
    def __init__(self):
        self.sockets = []

    def poll(self):
        while True:
            sockets_with_data = [
                (s, "whatever event") for s in self.sockets
                if s.data is not None]

            if len(sockets_with_data) != 0:
                return sockets_with_data

            time.sleep(0.1)

    def register(self, socket):
        self.sockets.append(socket)


class MockSocket(object):
    def __init__(self):
        self.data = None
        self.received = None

    def recv_multipart(self):
        data = self.data
        self.data = None
        return data

    def send_multipart(self, data):
        self.received = data

    def recv(self):
        data = self.data
        self.data = None
        return data

    def send(self, data):
        self.received = data

    def bind(self, where):
        pass

    def connect(self, where):
        pass

    def setsockopt(self, opt, val):
        pass

    def close(self):
        pass


class TestZMQServer(unittest.TestCase):
    def test_start_and_stop(self):
        config = ZMQServerConfig()
        received = []
        def cb(event):
            received.append(event)

        server = ZMQServer(config, cb)

        self.assertEqual(server.state, ZMQServer.STATE_STOPPED)
        server.start()

        self.assertEqual(server.state, ZMQServer.STATE_WAITING)
        server.stop()

        self.assertEqual(server.state, ZMQServer.STATE_STOPPED)

    def test_receive_info(self):
        mock_pub_socket = MockSocket()
        mock_sync_socket = MockSocket()
        mock_inproc_socket = MockSocket()

        received = []
        def cb(event):
            received.append(event)

        with mock.patch.object(ZMQServer, "_get_poller") as mock_get_poller, \
                mock.patch.object(ZMQServer, "_get_context") as mock_get_context:

            mock_get_poller.return_value = MockPoller()
            mock_context = mock.Mock()
            mock_context.socket.side_effect = [mock_pub_socket,
                                               mock_sync_socket,
                                               mock_inproc_socket]
            mock_get_context.return_value = mock_context

            config = ZMQServerConfig()
            server = ZMQServer(config, cb)
            server.start()

            wait_condition(lambda: server.state == ZMQServer.STATE_WAITING)
            mock_sync_socket.data = ["HELLO", "xxx", "1"]
            wait_condition(lambda: server.state == ZMQServer.STATE_RECEIVING)

            mock_sync_socket.data = ["GOODBYE", "xxx"]
            wait_condition(lambda: server.state == ZMQServer.STATE_WAITING)

            mock_sync_socket.data = ["HELLO", "xxx", "1"]
            wait_condition(lambda: server.state == ZMQServer.STATE_RECEIVING)

            mock_pub_socket.data = ["MESSAGE", "xxx",
                                    json.dumps({
                                        'type': 'MCOStartEvent',
                                        'model_data': {}
                                                })]

            wait_condition(lambda: len(received) == 1)
            self.assertIsInstance(received[0], MCOStartEvent)

            mock_sync_socket.data = ["GOODBYE", "xxx"]
            wait_condition(lambda: server.state == ZMQServer.STATE_WAITING)

            mock_inproc_socket.data = ''
            wait_condition(lambda: server.state == ZMQServer.STATE_STOPPED)


