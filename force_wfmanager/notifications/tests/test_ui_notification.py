import unittest
from testfixtures import LogCapture

from force_bdss.api import MCOStartEvent, MCOProgressEvent, \
    MCOFinishEvent, DataValue
from force_wfmanager.notifications.ui_notification import \
    UINotification
from force_wfmanager.notifications.ui_notification_factory import \
    UINotificationFactory
from force_wfmanager.notifications.ui_notification_model import \
    UINotificationModel

try:
    import mock
except ImportError:
    from unittest import mock

import zmq


class TestUINotification(unittest.TestCase):
    def setUp(self):
        factory = mock.Mock(spec=UINotificationFactory)
        self.model = UINotificationModel(factory)
        self.model.identifier = "an_id"

        listener = UINotification(factory)
        self.sync_socket = mock.Mock(spec=zmq.Socket)
        self.sync_socket.recv_multipart = mock.Mock()
        self.sync_socket.recv_multipart.side_effect = [
            [x.encode('utf-8') for x in ["HELLO", "an_id", "1"]],
            [x.encode('utf-8') for x in ["GOODBYE", "an_id"]]
        ]

        self.pub_socket = mock.Mock(spec=zmq.Socket)
        self.context = mock.Mock(spec=zmq.Context)
        self.context.socket.side_effect = [self.pub_socket,
                                           self.sync_socket]
        listener.__class__._create_context = mock.Mock(
            return_value=self.context)

        self.listener = listener

    def test_deliver(self):
        listener = self.listener
        listener.initialize(self.model)
        self.assertEqual(
            self.sync_socket.send_multipart.call_args[0][0],
            [x.encode('utf-8') for x in ['HELLO', 'an_id', '1']])

        listener.deliver(MCOStartEvent())
        self.assertEqual(
            self.pub_socket.send_multipart.call_args[0][0][0:2],
            [x.encode('utf-8') for x in ['MESSAGE', 'an_id']])

        listener.deliver(MCOProgressEvent(
            optimal_point=[DataValue(value=1),
                           DataValue(value=2),
                           DataValue(value=3)],
            optimal_kpis=[DataValue(value=4), DataValue(value=5)]))
        self.assertEqual(
            self.pub_socket.send_multipart.call_args[0][0][0:2],
            [x.encode('utf-8') for x in ['MESSAGE', 'an_id']])

        listener.deliver(MCOFinishEvent())
        self.assertEqual(
            self.pub_socket.send_multipart.call_args[0][0][0:2],
            [x.encode('utf-8') for x in ['MESSAGE', 'an_id']])

    def test_finalize(self):
        listener = self.listener
        listener.initialize(self.model)
        listener.finalize()
        self.assertTrue(self.context.term.called)
        self.assertTrue(self.sync_socket.close.called)
        self.assertTrue(self.pub_socket.close.called)
        self.assertIsNone(listener._context)
        self.assertIsNone(listener._sync_socket)
        self.assertIsNone(listener._pub_socket)

    def test_initialize(self):
        listener = self.listener
        listener.initialize(self.model)
        self.assertEqual(
            self.sync_socket.send_multipart.call_args[0][0],
            [x.encode('utf-8') for x in ['HELLO', 'an_id', '1']])

    def test_polling(self):
        self.sync_socket.poll.return_value = 0
        listener = self.listener
        with LogCapture() as capture:
            listener.initialize(self.model)
            capture.check(
                ("force_wfmanager.notifications.ui_notification",  # noqa
                 "INFO",
                 "Could not connect to UI server after 1000 ms. Continuing without UI notification."  # noqa
                 ),
            )

        self.assertIsNone(listener._context)

    def test_wrong_init_recv(self):
        listener = self.listener

        self.sync_socket.recv_multipart.side_effect = [
            [x.encode('utf-8') for x in ["HELLO", "not_the_right_id", "1"]],
            [x.encode('utf-8') for x in ["GOODBYE", "an_id"]]
        ]

        with LogCapture() as capture:
            listener.initialize(self.model)
            capture.check(
                ("force_wfmanager.notifications.ui_notification",  # noqa
                 "ERROR",
                 "Unexpected reply in sync negotiation with UI server. "
                 "'['HELLO', 'not_the_right_id', '1']'"  # noqa
                 ),
            )

        self.assertIsNone(listener._context)

    def test_deliver_without_context(self):
        self.listener.deliver(MCOStartEvent())
        self.assertFalse(self.pub_socket.send_multipart.called)

    def test_finalize_without_context(self):
        self.listener.finalize()
        self.assertFalse(self.sync_socket.send_multipart.called)

    def test_finalize_no_response(self):
        self.sync_socket.poll.side_effect = [1, 0]
        listener = self.listener
        listener.initialize(self.model)
        with LogCapture() as capture:
            listener.finalize()
            capture.check(
                ("force_wfmanager.notifications.ui_notification",  # noqa
                 "ERROR",
                 "Could not close connection to UI server after 1000 ms."  # noqa
                 ),
            )

        self.assertIsNone(listener._context)

    def test_wrong_finalize_recv(self):
        listener = self.listener
        self.sync_socket.poll.side_effect = [1, 1]
        self.sync_socket.recv_multipart.side_effect = [
            [x.encode('utf-8') for x in ["HELLO", "an_id", "1"]],
            [x.encode('utf-8') for x in ["GOODBYE", "not_the_right_id"]]
        ]

        listener.initialize(self.model)

        with LogCapture() as capture:
            listener.finalize()
            capture.check(
                ("force_wfmanager.notifications.ui_notification",  # noqa
                 "ERROR",
                 "Unexpected reply in goodbye sync negotiation with UI server. "  # noqa
                 "'['GOODBYE', 'not_the_right_id']'"  # noqa
                 ),
            )

        self.assertIsNone(listener._context)

    def test_double_clear_sockets(self):
        listener = self.listener

        listener._close_and_clear_sockets()
        self.assertIsNone(listener._context)

        listener._close_and_clear_sockets()
        self.assertIsNone(listener._context)
