from pyface.tasks.api import TraitsDockPane

from traits.api import Instance, Button, on_trait_change, Bool

from traitsui.api import View, UItem, VGroup

from force_bdss.factory_registry_plugin import IFactoryRegistryPlugin
from force_bdss.core.workflow import Workflow

from .workflow_tree import WorkflowTree


class SidePane(TraitsDockPane):
    """ Side pane which contains the WorkflowSettings (Tree editor for the
    Workflow) and the Run button """
    id = 'force_wfmanager.side_pane'
    name = 'Workflow'

    #: Remove the possibility to close the pane
    closable = False

    #: Remove the possibility to detach the pane from the GUI
    floatable = False

    #: Remove the possibility to move the pane in the GUI
    movable = False

    #: Make the pane visible by default
    visible = True

    #: The factory registry containing all the factories
    factory_registry = Instance(IFactoryRegistryPlugin)

    #: The Workflow model
    workflow_m = Instance(Workflow)

    #: Tree editor for the Workflow
    workflow_tree = Instance(WorkflowTree)

    #: Run button for running the computation
    run_button = Button('Run')

    #: Enable or disable the contained entities.
    #: Used when the computation is running
    enabled = Bool(True)

    run_btn_enabled = Bool(True)

    traits_view = View(VGroup(
        UItem('workflow_tree',
              style='custom',
              enabled_when="enabled"
              ),
        UItem('run_button',
              enabled_when="enabled and run_btn_enabled"
              )
    ))

    def _workflow_tree_default(self):
        return WorkflowTree(
            factory_registry=self.factory_registry,
            model=self.workflow_m
        )

    @on_trait_change('workflow_tree.workflow_mv.valid')
    def update_run_btn_status(self):
        self.run_btn_enabled = self.workflow_tree.workflow_mv.valid

    @on_trait_change('workflow_m', post_init=True)
    def update_workflow_tree(self, *args, **kwargs):
        self.workflow_tree.model = self.workflow_m
