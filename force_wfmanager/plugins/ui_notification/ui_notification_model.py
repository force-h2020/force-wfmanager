from traits.api import Unicode
from force_bdss.api import (
    BaseNotificationListenerModel)


class UINotificationModel(BaseNotificationListenerModel):
    #: The socket URL where the UI will be found. Synchronization port.
    sync_url = Unicode()

    #: The socket URL where the UI will be found. PubSub port.
    pub_url = Unicode()

    #: Unique identifier assigned by the UI to recognize the connection.
    identifier = Unicode()
