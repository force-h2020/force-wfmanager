from pyface.tasks.api import TraitsDockPane

from traits.api import Bool, Button, Instance, on_trait_change
from traitsui.api import UItem, VGroup, View

from force_bdss.api import IFactoryRegistry, Workflow

from force_wfmanager.ui.setup.system_state import SystemState
from force_wfmanager.ui.setup.workflow_tree import WorkflowTree


class SidePane(TraitsDockPane):
    """ Side pane which contains a visualisation of the workflow (via a
    TraitsUI TreeEditor) along with a button to run the workflow.
    """

    # -----------------------------
    #    Required Attributes
    # -----------------------------

    #: The Workflow model. Updated when
    #: :attr:`WfManagerSetupTask.workflow_model <force_wfmanager.\
    # wfmanager_setup_task.WfManagerSetupTask.workflow_model>` changes.
    #: Listens to: :attr:`WfManagerSetupTask.workflow_model <force_wfmanager.\
    #: wfmanager_setup_task.WfManagerSetupTask.workflow_model>`
    workflow_model = Instance(Workflow, allow_none=False)

    #: Holds information about current selected objects
    system_state = Instance(SystemState, allow_none=False)

    #: The factory registry containing all the factories
    factory_registry = Instance(IFactoryRegistry, allow_none=False)

    # --------------------
    # Dependent Attributes
    # --------------------

    #: Tree editor for the Process Model Workflow
    workflow_tree = Instance(WorkflowTree)

    # ----------------------
    #   Regular Attributes
    # ----------------------

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

    # -------------------
    #     Buttons
    # -------------------

    #: Run button for running the computation
    run_button = Button('Run')

    #: Enables or disables the workflow tree.
    ui_enabled = Bool(True)

    #: Enable or disable the run button.
    run_enabled = Bool(True)

    # -------------------
    #        View
    # -------------------

    traits_view = View(
        VGroup(
            UItem('workflow_tree', style='custom', enabled_when="ui_enabled"),
            UItem('run_button', enabled_when="run_enabled")
        )
    )

    # -------------------
    #     Defaults
    # -------------------

    def _workflow_tree_default(self):
        workflow_tree = WorkflowTree(
            model=self.workflow_model,
            _factory_registry=self.factory_registry,
            system_state=self.system_state
        )
        self.run_enabled = workflow_tree.workflow_view.valid
        return workflow_tree

    # -------------------
    #      Listeners
    # -------------------

    @on_trait_change('workflow_tree.workflow_view.valid')
    def update_run_btn_status(self):
        """Enables/Disables the run button if the workflow is valid/invalid"""
        self.run_enabled = (
                self.workflow_tree.workflow_view.valid and self.ui_enabled
        )

    @on_trait_change('workflow_model', post_init=True)
    def update_workflow_tree(self, *args, **kwargs):
        """Synchronises :attr:`workflow_tree.model <workflow_tree>`
        with :attr:`workflow_model`"""
        self.workflow_tree.model = self.workflow_model
