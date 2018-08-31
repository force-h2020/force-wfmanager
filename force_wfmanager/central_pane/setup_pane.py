from pyface.tasks.api import TraitsTaskPane

from traits.api import Instance, Dict
from traits.has_traits import on_trait_change
from traits.trait_types import String, Bool
from traits.traits import Property

from traitsui.api import View, VGroup, UItem
from traitsui.editors import ShellEditor, InstanceEditor
from traitsui.handler import ModelView

from force_bdss.api import Workflow


class SetupPane(TraitsTaskPane):
    id = 'force_wfmanager.setup_pane'
    name = 'Setup Pane'

    #: The model for the Workflow
    workflow_m = Instance(Workflow)

    #: Namespace for the console
    console_ns = Dict()

    #: Does the current modelview have a non-default view
    visible_modelview = Property(Bool, depends_on='selected_mv')

    #: The currently selected ModelView in the WorkflowTree
    selected_mv = Instance(ModelView)

    #: The name of the factory group selected in the WorkflowTree
    selected_factory_group = String('Workflow')

    traits_view = View(
        VGroup(
                UItem("selected_mv", editor=InstanceEditor(), style="custom",
                      visible_when="visible_modelview"),
                UItem("console_ns", label="Console", editor=ShellEditor()),
                layout='tabbed'
                ),
            )

    def __init__(self, workflow_m, *args, **kwargs):
        super(SetupPane, self).__init__(*args, **kwargs)
        self.workflow_m = workflow_m

    def _console_ns_default(self):
        namespace = {
            "task": self.task
        }
        try:
            namespace["app"] = self.task.window.application
        except AttributeError:
            namespace["app"] = None

        return namespace

    def _get_visible_modelview(self):
        """If there is a view associated to the selected_mv, return True
        and display that view in the SetupPane"""
        if len(self.selected_mv.trait_views()) != 0:
            return True
        return False

    @on_trait_change('task.side_pane.workflow_tree.selected_factory_group')
    def set_selected_factory_group(self):
        selected = self.task.side_pane.workflow_tree.selected_factory_group
        self.selected_factory_group = selected

    @on_trait_change('task.side_pane.workflow_tree.selected_mv')
    def set_selected_mv(self):
        self.selected_mv = self.task.side_pane.workflow_tree.selected_mv
