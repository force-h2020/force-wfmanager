import json
import logging
import unittest
import contextlib

from testfixtures import LogCapture

from force_wfmanager.tests.utils import wait_condition

try:
    import mock
except ImportError:
    from unittest import mock

import time

from force_bdss.api import MCOStartEvent
from force_wfmanager.server.zmq_server import ZMQServer
from force_wfmanager.server.zmq_server_config import ZMQServerConfig


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

        wait_condition(lambda: server.state == ZMQServer.STATE_WAITING)
        server.stop()

        wait_condition(lambda: server.state == ZMQServer.STATE_STOPPED)

    def test_double_start(self):
        config = ZMQServerConfig()
        server = ZMQServer(config, lambda: None)

        server.start()
        wait_condition(lambda: server.state == ZMQServer.STATE_WAITING)

        # This should have no effect and leave the state as waiting.
        server.start()
        wait_condition(lambda: server.state == ZMQServer.STATE_WAITING)

        server.stop()
        wait_condition(lambda: server.state == ZMQServer.STATE_STOPPED)

    @contextlib.contextmanager
    def mock_server(self, events_received):
        mock_pub_socket = MockSocket()
        mock_sync_socket = MockSocket()
        mock_inproc_socket = MockSocket()

        def cb(event):
            events_received.append(event)

        with mock.patch.object(
                ZMQServer, "_get_poller") as mock_get_poller, \
                mock.patch.object(
                    ZMQServer, "_get_context") as mock_get_context:

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

            yield server

            mock_inproc_socket.data = ''
            wait_condition(lambda: server.state == ZMQServer.STATE_STOPPED)

    def test_receive_info(self):
        received = []

        with self.mock_server(received) as server:
            server._sync_socket.data = ["HELLO", "xxx", "1"]
            wait_condition(lambda: server.state == ZMQServer.STATE_RECEIVING)

            server._sync_socket.data = ["GOODBYE", "xxx"]
            wait_condition(lambda: server.state == ZMQServer.STATE_WAITING)

            server._sync_socket.data = ["HELLO", "xxx", "1"]
            wait_condition(lambda: server.state == ZMQServer.STATE_RECEIVING)

            server._pub_socket.data = ["MESSAGE", "xxx",
                                       json.dumps({
                                          'type': 'MCOStartEvent',
                                          'model_data': {}
                                                 })]

            wait_condition(lambda: len(received) == 1)
            self.assertIsInstance(received[0], MCOStartEvent)

            server._sync_socket.data = ["GOODBYE", "xxx"]
            wait_condition(lambda: server.state == ZMQServer.STATE_WAITING)

    def test_error_conditions_waiting_sync(self):
        received = []
        with LogCapture(level=logging.ERROR) as capture:
            with self.mock_server(received) as server:
                server._sync_socket.data = ["HELLO"]
                wait_condition(lambda: len(capture.records) == 1)
                server._sync_socket.data = ["WHATEVER", 'xxx', '3']
                wait_condition(lambda: len(capture.records) == 2)
                server._sync_socket.data = ["HELLO", 'xxx', '3']
                wait_condition(lambda: len(capture.records) == 3)

            capture.check(
                ('force_wfmanager.server.zmq_server', 'ERROR',
                 "Unknown request received ['HELLO']"),
                ('force_wfmanager.server.zmq_server', 'ERROR',
                 'Unknown msg request received WHATEVER'),
                ('force_wfmanager.server.zmq_server', 'ERROR',
                 'Unknown protocol received 3')
            )

    def test_error_conditions_receiving_sync(self):
        received = []
        with LogCapture(level=logging.ERROR) as capture:
            with self.mock_server(received) as server:
                server._sync_socket.data = ["HELLO", "xxx", "1"]
                wait_condition(
                    lambda: server.state == ZMQServer.STATE_RECEIVING)

                server._sync_socket.data = ["HELLO", 'xxx', '1']
                wait_condition(lambda: len(capture.records) == 1)

                server._sync_socket.data = ["HELLO", 'xxx']
                wait_condition(lambda: len(capture.records) == 2)

            capture.check(
                ('force_wfmanager.server.zmq_server', 'ERROR',
                 "Unknown request received ['HELLO', 'xxx', '1']"),
                ('force_wfmanager.server.zmq_server', 'ERROR',
                 'Unknown msg request received HELLO'),
            )

    def test_error_conditions_waiting_pub(self):
        received = []
        with LogCapture(level=logging.ERROR) as capture:
            with self.mock_server(received) as server:
                server._pub_socket.data = ["HELLO", "xxx", "1"]
                wait_condition(lambda: len(capture.records) == 1)

            capture.check(
                ('force_wfmanager.server.zmq_server', 'ERROR',
                 "State WAITING cannot handle pub data. Discarding."),
            )

    def test_error_conditions_receiving_pub(self):
        received = []
        with LogCapture(level=logging.ERROR) as capture:
            with self.mock_server(received) as server:
                server._sync_socket.data = ["HELLO", "xxx", "1"]
                wait_condition(
                    lambda: server.state == ZMQServer.STATE_RECEIVING)

                server._pub_socket.data = ["MESSAGE", "xxx"]
                wait_condition(lambda: len(capture.records) == 1)

                server._pub_socket.data = ["WHATEVER", "xxx", ""]
                wait_condition(lambda: len(capture.records) == 2)

                server._pub_socket.data = ["MESSAGE", "xxx", "bonkers"]
                wait_condition(lambda: len(capture.records) == 3)

            capture.check(
                ('force_wfmanager.server.zmq_server', 'ERROR',
                 "Unknown request received ['MESSAGE', 'xxx']"),
                ('force_wfmanager.server.zmq_server', 'ERROR',
                 'Unknown msg request received WHATEVER'),
                ('force_wfmanager.server.zmq_server', 'ERROR',
                 'Received invalid data. Discarding'),
            )
