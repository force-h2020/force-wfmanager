from traits.api import Str

from force_bdss.api import BaseNotificationListenerModel

from force_wfmanager.utils.local_traits import ZMQSocketURL


class UINotificationModel(BaseNotificationListenerModel):
    """This is a data model for :class:`UINotification
    <.ui_notification.UINotification>`, which contains the
    sync and pub sockets, along with an identifier.
    """
    #: The socket URL where the UI will be found. Synchronization port.
    sync_url = ZMQSocketURL()

    #: The socket URL where the UI will be found. PubSub port.
    pub_url = ZMQSocketURL()

    #: Unique identifier assigned by the UI to recognize the connection.
    identifier = Str()

    pub2_url = ZMQSocketURL()
