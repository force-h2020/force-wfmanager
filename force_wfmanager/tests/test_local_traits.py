import unittest
from traits.api import HasStrictTraits, TraitError

from force_wfmanager.local_traits import ZMQSocketURL


class Traited(HasStrictTraits):
    socket_url = ZMQSocketURL()


class TestLocalTraits(unittest.TestCase):
    def test_zmq_socket_url(self):
        c = Traited()

        for working in ["tcp://127.0.0.1:12345",
                        "tcp://255.255.255.255:65535",
                        "tcp://1.1.1.1:65535"]:
            c.socket_url = working
            self.assertEqual(c.socket_url, working)

        for broken in ["tcp://270.0.0.1:12345",
                       "tcp://0.270.0.1:12345",
                       "tcp://0.0.270.1:12345",
                       "tcp://0.0.0.270:12345",
                       "url://255.255.255.255:65535",
                       "whatever",
                       "tcp://1.1.1.1:100000"]:
            with self.assertRaises(TraitError):
                c.socket_url = broken
