from pyface.tasks.api import TraitsDockPane

from traits.api import Instance, Button, on_trait_change, Bool

from traitsui.api import View, UItem, VGroup

from force_bdss.api import IFactoryRegistryPlugin, Workflow

from .workflow_tree import WorkflowTree


class TreePane(TraitsDockPane):
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
    #:
    workflow_model = Instance(Workflow)

    # -------------------
    # Required Attributes
    # -------------------

    #: The factory registry containing all the factories
    factory_registry = Instance(IFactoryRegistryPlugin)

    # ------------------
    # Regular Attributes
    # ------------------

    #: An internal identifier for this pane
    id = 'force_wfmanager.tree_pane'

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

    #: Tree editor for the Workflow
    workflow_tree = Instance(WorkflowTree)

    #: Run button for running the computation
    run_button = Button('Run')

    #: Enables or disables the workflow tree.
    ui_enabled = Bool(True)

    #: Enable or disable the run button.
    run_enabled = Bool(True)

    # ----
    # View
    # ----

    traits_view = View(VGroup(
        UItem('workflow_tree', style='custom', enabled_when="ui_enabled"),
        UItem('run_button', enabled_when="run_enabled")
    ))

    def _workflow_tree_default(self):
        wf_tree = WorkflowTree(
            _factory_registry=self.factory_registry,
            model=self.workflow_model
        )
        self.run_enabled = wf_tree.workflow_mv.valid
        return wf_tree

    @on_trait_change('workflow_tree.workflow_mv.valid')
    def update_run_btn_status(self):
        """Enables/Disables the run button if the workflow is valid/invalid"""
        self.run_enabled = (
                self.workflow_tree.workflow_mv.valid and self.ui_enabled
        )

    @on_trait_change('workflow_model', post_init=True)
    def update_workflow_tree(self, *args, **kwargs):
        """Synchronises :attr:`workflow_tree.model <workflow_tree>`
        with :attr:`workflow_model`"""
        self.workflow_tree.model = self.workflow_model
