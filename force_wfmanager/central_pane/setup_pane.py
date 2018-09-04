from force_bdss.core.base_model import BaseModel
from force_bdss.core.kpi_specification import KPISpecification
from pyface.tasks.api import TraitsTaskPane

from traits.api import Instance, Dict
from traits.has_traits import on_trait_change
from traits.trait_types import String, Bool, Either
from traits.traits import Property

from traitsui.api import View, VGroup, UItem
from traitsui.editors import ShellEditor, InstanceEditor
from traitsui.handler import ModelView

from force_bdss.api import Workflow


class SetupPane(TraitsTaskPane):
    id = 'force_wfmanager.setup_pane'
    name = 'Setup Pane'

    #: The model for the Workflow
    workflow_model = Instance(Workflow)

    #: Namespace for the console
    console_ns = Dict()

    #: The model from selected_mv
    selected_model = Either(Instance(BaseModel),
                            Instance(KPISpecification))

    #: Does the current model have anything the user could edit
    selected_mv_editable = Property(Bool, depends_on='selected_mv')

    #: The currently selected ModelView in the WorkflowTree
    selected_mv = Instance(ModelView)

    #: The name of the factory group selected in the WorkflowTree
    selected_factory_group = String('Workflow')

    #: The view when editing an existing instance within the workflow tree
    traits_view = View(
        VGroup(
                VGroup(
                    UItem("selected_mv", editor=InstanceEditor(),
                          style="custom",
                          visible_when="selected_mv_editable"),
                    UItem("selected_model", editor=InstanceEditor(),
                          style="custom",
                          visible_when="selected_model is not None"),
                    label="Model Details",
                    ),
                VGroup(
                    UItem("console_ns", label="Console", editor=ShellEditor()),
                    label="Console"
                    ),
                layout='tabbed'
            )
        )

    def _console_ns_default(self):
        namespace = {
            "task": self.task
        }
        try:
            namespace["app"] = self.task.window.application
        except AttributeError:
            namespace["app"] = None

        return namespace

    def _get_selected_mv_editable(self):
        """If there is a view associated to the selected_mv, return True
        and display that view in the SetupPane."""
        if self.selected_mv is None:
            return False

        if len(self.selected_mv.trait_views()) != 0:
            return True
        return False

    @on_trait_change('task.side_pane.workflow_tree.selected_factory_group')
    def set_selected_factory_group(self):
        selected = self.task.side_pane.workflow_tree.selected_factory_group
        self.selected_factory_group = selected

    @on_trait_change('task.side_pane.workflow_tree.selected_mv')
    def update_selected_mv(self):
        self.selected_mv = self.task.side_pane.workflow_tree.selected_mv
        if self.selected_mv is not None:
            if isinstance(self.selected_mv.model, BaseModel):
                self.selected_model = self.selected_mv.model
            else:
                self.selected_model = None
