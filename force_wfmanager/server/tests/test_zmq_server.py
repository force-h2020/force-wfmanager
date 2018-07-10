import json
import logging
import unittest
import contextlib
import random

import six
from testfixtures import LogCapture

from force_wfmanager.tests.utils import wait_condition

try:
    import mock
except ImportError:
    from unittest import mock

import time

from force_bdss.api import MCOStartEvent
from force_wfmanager.server.zmq_server import ZMQServer


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

    def bind_to_random_port(self, address):
        return random.randint(40000, 65535)

    def connect(self, where):
        pass

    def setsockopt(self, opt, val):
        pass

    def close(self):
        pass


class TestZMQServer(unittest.TestCase):
    def test_start_and_stop(self):
        received = []

        def cb(event):
            received.append(event)

        def err_cb(error_type, error_msg):
            pass

        server = ZMQServer(cb, err_cb)

        self.assertEqual(server.state, ZMQServer.STATE_STOPPED)
        server.start()

        wait_condition(lambda: server.state == ZMQServer.STATE_WAITING)
        server.stop()

        wait_condition(lambda: server.state == ZMQServer.STATE_STOPPED)

    @contextlib.contextmanager
    def mock_started_server(self, events_received, errors_received):
            with self.mock_server(events_received, errors_received) as server:
                server.start()
                wait_condition(lambda: server.state == ZMQServer.STATE_WAITING)

                yield server

                server._inproc_socket.data = ''.encode('utf-8')
                wait_condition(lambda: server.state == ZMQServer.STATE_STOPPED)

    @contextlib.contextmanager
    def mock_server(self, events_received, errors_received):
        mock_pub_socket = MockSocket()
        mock_sync_socket = MockSocket()
        mock_inproc_socket = MockSocket()

        def cb(event):
            events_received.append(event)

        def err_cb(err_type, err_msg):
            errors_received.append((err_type, err_msg))

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

            server = ZMQServer(cb, err_cb)

            yield server

    def test_receive_info(self):
        events = []
        errors = []

        with self.mock_started_server(events, errors) as server:
            server._sync_socket.data = [x.encode('utf-8')
                                        for x in ["HELLO", "xxx", "1"]]
            wait_condition(lambda: server.state == ZMQServer.STATE_RECEIVING)

            server._sync_socket.data = [x.encode('utf-8')
                                        for x in ["GOODBYE", "xxx"]]
            wait_condition(lambda: server.state == ZMQServer.STATE_WAITING)

            server._sync_socket.data = [x.encode('utf-8')
                                        for x in ["HELLO", "xxx", "1"]]
            wait_condition(lambda: server.state == ZMQServer.STATE_RECEIVING)

            server._pub_socket.data = [
                x.encode('utf-8')
                for x in ["MESSAGE", "xxx", json.dumps(
                    {
                        'type': 'MCOStartEvent',
                        'model_data': {}
                    })]]

            wait_condition(lambda: len(events) == 1)
            self.assertIsInstance(events[0], MCOStartEvent)

            server._sync_socket.data = [x.encode('utf-8')
                                        for x in ["GOODBYE", "xxx"]]
            wait_condition(lambda: server.state == ZMQServer.STATE_WAITING)

    def test_error_conditions_waiting_sync(self):
        events = []
        errors = []
        with LogCapture(level=logging.ERROR) as capture:
            with self.mock_started_server(events, errors) as server:
                server._sync_socket.data = ["HELLO".encode('utf-8')]
                wait_condition(lambda: len(capture.records) == 1)
                server._sync_socket.data = [x.encode('utf-8')
                                            for x in ["WHATEVER", 'xxx', '3']]
                wait_condition(lambda: len(capture.records) == 2)
                server._sync_socket.data = [x.encode('utf-8')
                                            for x in ["HELLO", 'xxx', '3']]
                wait_condition(lambda: len(capture.records) == 3)

            if six.PY2:
                capture.check(
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     "Unknown request received [u'HELLO']"),
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     "Unknown msg request received WHATEVER"),
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     "Unknown protocol received 3")
                )
            else:
                capture.check(
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     "Unknown request received ['HELLO']"),
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     "Unknown msg request received WHATEVER"),
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     "Unknown protocol received 3")
                )

    def test_error_conditions_receiving_sync(self):
        events = []
        errors = []
        with LogCapture(level=logging.ERROR) as capture:
            with self.mock_started_server(events, errors) as server:
                server._sync_socket.data = [x.encode('utf-8')
                                            for x in ["HELLO", "xxx", "1"]]
                wait_condition(
                    lambda: server.state == ZMQServer.STATE_RECEIVING)

                server._sync_socket.data = [x.encode('utf-8')
                                            for x in ["HELLO", 'xxx', '1']]
                wait_condition(lambda: len(capture.records) == 1)

                server._sync_socket.data = [x.encode('utf-8')
                                            for x in ["HELLO", 'xxx']]
                wait_condition(lambda: len(capture.records) == 2)

            if six.PY2:
                capture.check(
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     "Unknown request received [u'HELLO', u'xxx', u'1']"),
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     "Unknown msg request received HELLO"),
                )
            else:
                capture.check(
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     "Unknown request received ['HELLO', 'xxx', '1']"),
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     "Unknown msg request received HELLO"),
                )

    def test_error_conditions_waiting_pub(self):
        events = []
        errors = []
        with LogCapture(level=logging.ERROR) as capture:
            with self.mock_started_server(events, errors) as server:
                server._pub_socket.data = [x.encode('utf-8')
                                           for x in ["HELLO", "xxx", "1"]]
                wait_condition(lambda: len(capture.records) == 1)

            capture.check(
                ('force_wfmanager.server.zmq_server', 'ERROR',
                 "State WAITING cannot handle pub data. Discarding."),
            )

    def test_socket_ordering(self):
        events = []
        errors = []
        with self.mock_started_server(events, errors) as server:
            server._sync_socket.data = [x.encode('utf-8')
                                        for x in ["HELLO", "xxx", "1"]]
            wait_condition(lambda: server.state == ZMQServer.STATE_RECEIVING)

            server._pub_socket.data = [
                x.encode('utf-8')
                for x in ["MESSAGE", "xxx", json.dumps(
                    {
                        'type': 'MCOStartEvent',
                        'model_data': {}
                    })]]
            server._sync_socket.data = [x.encode('utf-8')
                                        for x in ["GOODBYE", "xxx"]]

            wait_condition(lambda: len(events) == 1)
            wait_condition(lambda: server.state == ZMQServer.STATE_WAITING)

    def test_error_conditions_receiving_pub(self):
        events = []
        errors = []
        with LogCapture(level=logging.ERROR) as capture:
            with self.mock_started_server(events, errors) as server:
                server._sync_socket.data = [x.encode('utf-8')
                                            for x in ["HELLO", "xxx", "1"]]
                wait_condition(
                    lambda: server.state == ZMQServer.STATE_RECEIVING)

                server._pub_socket.data = [x.encode('utf-8')
                                           for x in ["MESSAGE", "xxx"]]
                wait_condition(lambda: len(capture.records) == 1)

                server._pub_socket.data = [x.encode('utf-8')
                                           for x in ["WHATEVER", "xxx", ""]]
                wait_condition(lambda: len(capture.records) == 2)

                server._pub_socket.data = [x.encode('utf-8')
                                           for x in ["MESSAGE",
                                                     "xxx",
                                                     "bonkers"]]
                wait_condition(lambda: len(capture.records) == 3)

            if six.PY2:
                capture.check(
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     "Unknown request received [u'MESSAGE', u'xxx']"),
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     "Unknown msg request received WHATEVER"),
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     'Received invalid data. Discarding'),
                )
            else:
                capture.check(
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     "Unknown request received ['MESSAGE', 'xxx']"),
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     "Unknown msg request received WHATEVER"),
                    ('force_wfmanager.server.zmq_server', 'ERROR',
                     'Received invalid data. Discarding'),
                )

    def test_server_error_on_connect(self):
        events = []
        errors = []
        with self.mock_server(events, errors) as server:
            with mock.patch.object(MockSocket,
                                   'bind_to_random_port') as rp:
                rp.side_effect = Exception("Boom")

                server.start()
                wait_condition(lambda: len(errors) != 0)

        self.assertEqual(errors, [(ZMQServer.ERROR_TYPE_CRITICAL,
                                   "Unable to setup server sockets: Boom.\n"
                                   "The server is now stopped. You will be "
                                   "unable to receive progress information "
                                   "from the BDSS.")])
        self.assertEqual(server.state, ZMQServer.STATE_STOPPED)

    def test_server_error_on_poller_register(self):
        events = []
        errors = []
        with self.mock_server(events, errors) as server:
            with mock.patch.object(MockPoller, 'register') as register:
                register.side_effect = Exception("Boom")

                server.start()
                wait_condition(lambda: len(errors) != 0)

        self.assertEqual(errors, [(ZMQServer.ERROR_TYPE_CRITICAL,
                                   "Unable to register sockets to poller: "
                                   "Boom.\n"
                                   "The server is now stopped. You will be "
                                   "unable to receive progress information "
                                   "from the BDSS.")])
        self.assertEqual(server.state, ZMQServer.STATE_STOPPED)

    def test_server_error_unable_to_poll(self):
        events = []
        errors = []
        with LogCapture(level=logging.ERROR) as capture:
            with self.mock_server(events, errors) as server:
                with mock.patch.object(MockPoller, 'poll') as poll:
                    poll.side_effect = Exception("Boom")

                    server.start()
                    wait_condition(lambda: len(errors) != 0)

        self.assertEqual(errors, [(ZMQServer.ERROR_TYPE_CRITICAL,
                                   "Unable to poll sockets: "
                                   "Boom.\n"
                                   "The server is now stopped. You will be "
                                   "unable to receive progress information "
                                   "from the BDSS.")])
        self.assertEqual(server.state, ZMQServer.STATE_STOPPED)

    def test_server_error_handler_failure(self):
        events = []
        errors = []
        with LogCapture(level=logging.ERROR) as capture:
            with self.mock_server(events, errors) as server:
                with mock.patch.object(MockSocket, 'send_multipart') as send:
                    send.side_effect = Exception("Boom")

                    server.start()
                    wait_condition(
                        lambda: server.state == ZMQServer.STATE_WAITING)

                    server._sync_socket.data = [x.encode('utf-8')
                                                for x in ["HELLO", "xxx", "1"]]
                    wait_condition(
                        lambda: server.state != ZMQServer.STATE_WAITING)

        self.assertEqual(errors[0][0], ZMQServer.ERROR_TYPE_CRITICAL)
        self.assertIn("Handler", errors[0][1])
        self.assertEqual(server.state, ZMQServer.STATE_STOPPED)
