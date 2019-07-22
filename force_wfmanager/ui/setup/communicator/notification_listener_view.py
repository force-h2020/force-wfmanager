from traits.api import (
    Instance, Unicode, Bool, Event, HasTraits
)
from force_bdss.api import BaseNotificationListenerModel
from force_wfmanager.ui.ui_utils import get_factory_name


class NotificationListenerView(HasTraits):

    # -------------------
    # Required Attributes
    # -------------------

    #: The model object this MV wraps
    model = Instance(BaseNotificationListenerModel)

    # ------------------
    # Regular Attributes
    # ------------------

    #: Label to be used in the TreeEditor
    label = Unicode()

    # --------------------
    # Dependent Attributes
    # --------------------

    #: An error message for issues in this modelview. Updated by
    #: :func:`workflow_tree.WorkflowTree.verify_tree
    #: <force_wfmanager.models.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    #: Event to request a verification check on the workflow.
    verify_workflow_event = Event

    #: Defines if the Notification listener is valid or not. Updated by
    #: :func:`workflow_tree.WorkflowTree.verify_tree
    #: <force_wfmanager.models.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    # -------------------
    #       Defaults
    # -------------------

    def _label_default(self):
        return get_factory_name(self.model.factory)
