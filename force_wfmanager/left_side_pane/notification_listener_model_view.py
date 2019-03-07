from traits.api import Instance, Unicode, Bool, Event
from traitsui.api import ModelView

from force_bdss.api import BaseNotificationListenerModel
from force_wfmanager.left_side_pane.variable_names_registry import (
    VariableNamesRegistry
)
from force_wfmanager.left_side_pane.view_utils import get_factory_name


class NotificationListenerModelView(ModelView):

    # -------------------
    # Required Attributes
    # -------------------

    #: The model object this MV wraps
    model = Instance(BaseNotificationListenerModel)

    #: Registry of the available variables
    variable_names_registry = Instance(VariableNamesRegistry)

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
    #: <force_wfmanager.left_side_pane.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    #: Event to request a verification check on the workflow.
    verify_workflow_event = Event

    #: Defines if the Notification listener is valid or not. Updated by
    #: :func:`workflow_tree.WorkflowTree.verify_tree
    #: <force_wfmanager.left_side_pane.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    def _label_default(self):
        return get_factory_name(self.model.factory)
