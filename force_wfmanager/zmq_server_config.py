from traits.api import HasStrictTraits

from force_bdss.api import ZMQSocketURL


class ZMQServerConfig(HasStrictTraits):
    #: The socket of the PubSub for the BDSS
    pub_socket_url = ZMQSocketURL("tcp://*:54537")

    #: The socket of the Request/Reply from the BDSS
    rep_socket_url = ZMQSocketURL("tcp://*:54538")
