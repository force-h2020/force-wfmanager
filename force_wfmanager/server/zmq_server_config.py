from traits.api import HasStrictTraits

from force_wfmanager.local_traits import ZMQSocketURL


class ZMQServerConfig(HasStrictTraits):
    #: The socket of the PubSub for the BDSS
    pub_url = ZMQSocketURL("tcp://*:54537")

    #: The socket of the Request/Reply from the BDSS
    sync_url = ZMQSocketURL("tcp://*:54538")
