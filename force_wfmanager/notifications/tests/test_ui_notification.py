import unittest
from testfixtures import LogCapture
from threading import Event

from force_bdss.api import (
    MCOStartEvent,
    MCOProgressEvent,
    MCOFinishEvent,
    DataValue,
)
from force_wfmanager.notifications.ui_notification import UINotification
from force_wfmanager.notifications.ui_notification_factory import (
    UINotificationFactory,
)
from force_wfmanager.notifications.ui_notification_model import (
    UINotificationModel,
)

try:
    import mock
except ImportError:
    from unittest import mock

import zmq


UI_MIXIN = (
    "force_bdss.ui_hooks.ui_notification_mixins.UIEventNotificationMixin."
)


class TestUINotification(unittest.TestCase):
    def setUp(self):
        factory = mock.Mock(spec=UINotificationFactory)
        self.model = UINotificationModel(factory)
        self.model.identifier = "an_id"

        listener = UINotification(factory)
        self.sync_socket = mock.Mock(spec=zmq.Socket)
        self.sync_socket.recv_multipart = mock.Mock()
        self.sync_socket.recv_multipart.side_effect = [
            [x.encode("utf-8") for x in ["HELLO", "an_id", "1"]],
            [x.encode("utf-8") for x in ["GOODBYE", "an_id"]],
        ]

        self.pub_socket = mock.Mock(spec=zmq.Socket)
        self.sub_socket = mock.Mock(spec=zmq.Socket)
        self.sub_socket.recv_multipart.side_effect = [
            [x.encode("utf-8") for x in ["MSG", "an_id", "1"]],
            [x.encode("utf-8") for x in ["MGS", "PAUSE_BDSS", "1"]],
            [x.encode("utf-8") for x in ["MGS", "PAUSE_BDSS", "1"]],
            [x.encode("utf-8") for x in ["MGS", "RESUME_BDSS", "1"]],
            [x.encode("utf-8") for x in ["MGS", "STOP_BDSS", "1"]],
        ]

        self.context = mock.Mock(spec=zmq.Context)
        self.context.socket.side_effect = [
            self.pub_socket,
            self.sub_socket,
            self.sync_socket,
        ]
        listener.__class__._create_context = mock.Mock(
            return_value=self.context
        )

        self.listener = listener

    def test_deliver(self):
        listener = self.listener
        listener.initialize(self.model)
        self.assertEqual(
            self.sync_socket.send_multipart.call_args[0][0],
            [x.encode("utf-8") for x in ["HELLO", "an_id", "1"]],
        )

        listener.deliver(MCOStartEvent())
        self.assertEqual(
            self.pub_socket.send_multipart.call_args[0][0][0:2],
            [x.encode("utf-8") for x in ["MESSAGE", "an_id"]],
        )

        listener.deliver(
            MCOProgressEvent(
                optimal_point=[
                    DataValue(value=1),
                    DataValue(value=2),
                    DataValue(value=3),
                ],
                optimal_kpis=[DataValue(value=4), DataValue(value=5)],
            )
        )
        self.assertEqual(
            self.pub_socket.send_multipart.call_args[0][0][0:2],
            [x.encode("utf-8") for x in ["MESSAGE", "an_id"]],
        )

        listener.deliver(MCOFinishEvent())
        self.assertEqual(
            self.pub_socket.send_multipart.call_args[0][0][0:2],
            [x.encode("utf-8") for x in ["MESSAGE", "an_id"]],
        )

        with self.assertRaisesRegex(
            TypeError, "Event is not a BaseDriverEvent"
        ):
            listener.deliver("not an event")

    def test_finalize(self):
        self.listener.initialize(self.model)
        self.assertTrue(self.listener._poller_running)
        self.listener.finalize()
        self.assertTrue(self.context.term.called)
        self.assertTrue(self.sync_socket.close.called)
        self.assertTrue(self.pub_socket.close.called)
        self.assertIsNone(self.listener._context)
        self.assertIsNone(self.listener._sync_socket)
        self.assertIsNone(self.listener._pub_socket)
        self.assertFalse(self.listener._poller_running)

    def test_initialize(self):
        listener = self.listener
        listener.initialize(self.model)
        self.assertEqual(
            self.sync_socket.send_multipart.call_args[0][0],
            [x.encode("utf-8") for x in ["HELLO", "an_id", "1"]],
        )

    def test_polling(self):
        self.sync_socket.poll.return_value = 0
        listener = self.listener
        with LogCapture() as capture:
            listener.initialize(self.model)
            capture.check(
                (
                    "force_wfmanager.notifications.ui_notification",
                    "INFO",
                    "Could not connect to UI server after 1000 ms. "
                    "Continuing without UI notification.",
                )
            )

        self.assertIsNone(listener._context)

    def test_wrong_init_recv(self):
        listener = self.listener

        self.sync_socket.recv_multipart.side_effect = [
            [x.encode("utf-8") for x in ["HELLO", "not_the_right_id", "1"]],
            [x.encode("utf-8") for x in ["GOODBYE", "an_id"]],
        ]

        with LogCapture() as capture:
            listener.initialize(self.model)
            capture.check(
                (
                    "force_wfmanager.notifications.ui_notification",
                    "ERROR",
                    "Unexpected reply in sync negotiation with UI server. "
                    "'['HELLO', 'not_the_right_id', '1']'",
                )
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
                (
                    "force_wfmanager.notifications.ui_notification",
                    "ERROR",
                    "Could not close connection to UI server "
                    "after 1000 ms.",
                )
            )

        self.assertIsNone(listener._context)

    def test_wrong_finalize_recv(self):
        listener = self.listener
        self.sync_socket.poll.side_effect = [1, 1]
        self.sync_socket.recv_multipart.side_effect = [
            [x.encode("utf-8") for x in ["HELLO", "an_id", "1"]],
            [x.encode("utf-8") for x in ["GOODBYE", "not_the_right_id"]],
        ]

        listener.initialize(self.model)

        with LogCapture() as capture:
            listener.finalize()
            capture.check(
                (
                    "force_wfmanager.notifications.ui_notification",
                    "ERROR",
                    "Unexpected reply in goodbye sync "
                    "negotiation with UI server. "
                    "'['GOODBYE', 'not_the_right_id']'",
                )
            )

        self.assertIsNone(listener._context)

    def test_double_clear_sockets(self):
        listener = self.listener

        listener._close_and_clear_sockets()
        self.assertIsNone(listener._context)

        listener._close_and_clear_sockets()
        self.assertIsNone(listener._context)

    def test_run_poller(self):
        stop_event = Event()
        pause_event = Event()

        with mock.patch(
            "zmq.Poller.poll", return_value={self.sub_socket: None}
        ):
            with mock.patch(UI_MIXIN + "send_stop") as mock_stop, mock.patch(
                UI_MIXIN + "send_pause"
            ) as mock_pause, mock.patch(
                UI_MIXIN + "send_resume"
            ) as mock_resume:
                self.listener.set_stop_event(stop_event)
                self.listener.set_pause_event(pause_event)
                self.listener.run_poller(self.sub_socket)
                self.assertEqual(1, mock_stop.call_count)
                self.assertEqual(2, mock_pause.call_count)
                self.assertEqual(1, mock_resume.call_count)
                self.assertFalse(self.listener._poller_running)

        # Test for different socket poll
        pub_socket = self.pub_socket
        sub_socket = self.sub_socket

        class DummyPoller:
            def __init__(self):
                self.counter = 5

            def poll(self):
                self.counter -= 1
                if self.counter != 0:
                    return {pub_socket: None}
                return {sub_socket: None}

            def register(self, socket):
                self.socket = socket

        self.sub_socket.recv_multipart.side_effect = [
            [x.encode("utf-8") for x in ["MGS", "STOP_BDSS", "1"]]
        ]
        with mock.patch("zmq.Poller", return_value=DummyPoller()):
            with mock.patch(UI_MIXIN + "send_stop") as mock_stop, mock.patch(
                UI_MIXIN + "send_pause"
            ) as mock_pause, mock.patch(
                UI_MIXIN + "send_resume"
            ) as mock_resume:
                self.listener.set_stop_event(stop_event)
                self.listener.set_pause_event(pause_event)
                self.listener.run_poller(self.sub_socket)
                self.assertEqual(1, mock_stop.call_count)
                self.assertEqual(0, mock_pause.call_count)
                self.assertEqual(0, mock_resume.call_count)
                self.assertFalse(self.listener._poller_running)

        self.sub_socket.recv_multipart.side_effect = [
            [x.encode("utf-8") for x in ["MGS", "STOP_BDSS"]],
            [x.encode("utf-8") for x in ["MGS", "STOP_BDSS", "1"]],
        ]
        with mock.patch(
            "zmq.Poller.poll", return_value={self.sub_socket: None}
        ):
            with LogCapture() as capture:
                self.listener.run_poller(self.sub_socket)
            capture.check(
                (
                    "force_wfmanager.notifications.ui_notification",
                    "ERROR",
                    "Incompatible data received: expected (msg, identifier, data), "
                    "but got ['MGS', 'STOP_BDSS'] instead.",
                )
            )
