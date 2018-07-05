from traits.api import Instance, Str, Bool, Event
from traitsui.api import ModelView

from force_bdss.api import BaseNotificationListenerModel
from force_wfmanager.left_side_pane.view_utils import get_factory_name


class NotificationListenerModelView(ModelView):
    #: The model object this MV wraps
    model = Instance(BaseNotificationListenerModel)

    #: Label to be used in the TreeEditor
    label = Str()

    #: An error message for issues in this modelview
    error_message = Str()

    #: Event to request a verification check on the workflow
    verify_workflow_event = Event

    #: Defines if the Notification listener is valid or not
    valid = Bool(True)

    def _label_default(self):
        return get_factory_name(self.model.factory)
