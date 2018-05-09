from traits.api import Instance, Str, Bool
from traitsui.api import ModelView

from force_bdss.notification_listeners.base_notification_listener_model \
    import BaseNotificationListenerModel
from force_wfmanager.left_side_pane.view_utils import get_factory_name


class NotificationListenerModelView(ModelView):
    #: The model object this MV wraps
    model = Instance(BaseNotificationListenerModel)

    #: Label to be used in the TreeEditor
    label = Str()

    #: Defines if the Notification listener is valid or not
    valid = Bool(True)

    def _label_default(self):
        return get_factory_name(self.model.factory)
