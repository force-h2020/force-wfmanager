from pyface.tasks.api import TraitsDockPane

from traits.api import (
    Instance, Button, on_trait_change, Bool, Unicode
)
from traitsui.api import View, UItem, VGroup, UReadonly, TextEditor, Group

from force_bdss.api import IFactoryRegistry
from force_wfmanager.ui.setup.process_tree import ProcessTree
from force_bdss.api import Workflow
from force_wfmanager.ui.setup.workflow_model_view import WorkflowModelView


class SidePane(TraitsDockPane):
    """ Side pane which contains a visualisation of the workflow (via a
    TraitsUI TreeEditor) along with a button to run the workflow.
    """

    # -----------------------------
    # Required/Dependent Attributes
    # -----------------------------

    #: The Workflow model. Updated when
    #: :attr:`WfManagerSetupTask.workflow_model <force_wfmanager.\
    # wfmanager_setup_task.WfManagerSetupTask.workflow_model>` changes.
    #: Listens to: :attr:`WfManagerSetupTask.workflow_model <force_wfmanager.\
    #: wfmanager_setup_task.WfManagerSetupTask.workflow_model>`
    workflow_model = Instance(Workflow, allow_none=False)

    # -------------------
    # Required Attributes
    # -------------------

    #: The factory registry containing all the factories
    factory_registry = Instance(IFactoryRegistry)

    # ------------------
    # Regular Attributes
    # ------------------

    #: An internal identifier for this pane
    id = 'force_wfmanager.side_pane'

    #: Name displayed as the title of this pane
    name = 'Workflow'

    #: Remove the possibility to close the pane
    closable = False

    #: Remove the possibility to detach the pane from the GUI
    floatable = False

    #: Remove the possibility to move the pane in the GUI
    movable = False

    #: Make the pane visible by default
    visible = True

    #: Collated information about the total workflow
    workflow_model_view = Instance(WorkflowModelView)

    #: Tree editor for the Process Model Workflow
    process_tree = Instance(ProcessTree)

    #: Enables or disables the workflow tree.
    ui_enabled = Bool(True)

    #: MCO button for bringing up the MCO options
    mco_button = Button('MCO')

    #: MCO button for bringing up the Notification options
    notification_button = Button('Notifications')

    #: The error message currently displayed in the UI.
    setup_error = Unicode('')

    # ----
    # View
    # ----

    traits_view = View(
        Group(
            VGroup(
                UItem('process_tree',
                      style='custom',
                      enabled_when="ui_enabled"),
                UItem('mco_button'),
                UItem('notification_button')
            ),
            VGroup(
                UReadonly(
                    name='setup_error',
                    editor=TextEditor()
                ),
                label='Workflow Errors',
                show_border=True,
            )
        )
    )

    def _workflow_model_view_default(self):
        return WorkflowModelView(
            model=self.workflow_model
        )

    def _process_tree_default(self):
        return ProcessTree(
            process_model_view=self.workflow_model_view.process_model_view,
            _factory_registry=self.factory_registry,
        )

    @on_trait_change("process_tree:selected_error")
    def _sync_setup_error(self):
        print('side_pane _sync_setup_error called')
        self.setup_error = self.process_tree.selected_error

    def _mco_button_fired(self):
        self.process_tree.selected_mv = self.workflow_model_view.mco_model_view
        self.process_tree.selected_factory_name = 'MCO'

    def _notification_button_fired(self):
        self.process_tree.selected_mv = self.workflow_model_view.notification_listener_info
        self.process_tree.selected_factory_name = 'Notification Listeners'
