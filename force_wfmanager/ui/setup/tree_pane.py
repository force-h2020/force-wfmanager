from pyface.tasks.api import TraitsDockPane

from traits.api import (
    Instance, Button, on_trait_change, Bool, Property, Unicode
)
from traitsui.api import View, UItem, VGroup, UReadonly, TextEditor, Group

from force_bdss.api import IFactoryRegistry, Workflow

from force_wfmanager.ui.setup.workflow_tree import WorkflowTree


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
    factory_registry = Instance(IFactoryRegistry)

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

    #: Tree editor for the Model Workflow
    workflow_tree = Instance(WorkflowTree)

    #: Enables or disables the workflow tree.
    ui_enabled = Bool(True)

    #: MCO button for bringin up the MCO options
    mco_button = Button('MCO')

    #: MCO button for bringin up the Notification options
    notification_button = Button('Notifications')

    #: The error message currently displayed in the UI.
    setup_error = Unicode('')

    # ----
    # View
    # ----

    traits_view = View(
        Group(
            VGroup(
                UItem('workflow_tree',
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

    def _workflow_tree_default(self):
        wf_tree = WorkflowTree(
            _factory_registry=self.factory_registry,
            model=self.workflow_model
        )
        self.run_enabled = wf_tree.workflow_mv.valid
        return wf_tree

    @on_trait_change("workflow_tree.selected_error")
    def _sync_setup_error(self):
        self.setup_error = self.workflow_tree.selected_error

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
