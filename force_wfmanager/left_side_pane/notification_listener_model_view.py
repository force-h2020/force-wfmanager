from traits.api import  Bool, Event, Instance, TraitError, Unicode
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

    #: A registry of currently avaliable variable names
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

    #: Event to request a verification check on the workflow
    verify_workflow_event = Event

    #: Defines if the Notification listener is valid or not. Updated by
    #: :func:`workflow_tree.WorkflowTree.verify_tree
    #: <force_wfmanager.left_side_pane.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    def _label_default(self):
        return get_factory_name(self.model.factory)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        passed_traits = self.model.trait_get(from_mv=True)
        for name in passed_traits:
            try:
                self.sync_trait(name, self.model)
            except AttributeError as e:
                extra_message = (
                    "The trait '{}' in the model class '{}' has the metadata "
                    "'from_mv=True', but there is no corresponding trait in "
                    "the modelview. Available traits are: {}".format(
                        name, self.model.__class__.__name__,
                        ', '.join(self.class_visible_traits())
                    )
                )
                raise TraitError(extra_message).with_traceback(e.__traceback__)