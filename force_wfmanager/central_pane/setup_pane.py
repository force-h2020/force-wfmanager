from force_bdss.core.base_model import BaseModel
from force_bdss.core.kpi_specification import KPISpecification
from force_wfmanager.left_side_pane.new_entity_modal import NewEntityModal
from pyface.tasks.api import TraitsTaskPane

from traits.api import Instance, Dict, Callable
from traits.has_traits import on_trait_change
from traits.trait_types import String, Bool, Either, Button
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

    #: The appropriate function to add a new entity of the selected factory
    #: group to the workflow tree. For example, if the 'DataSources' group
    #: is selected, this function would be new_data_source().
    add_function = Callable()

    current_modal = Instance(NewEntityModal)



    btn = Button()

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
                    visible_when="selected_model is not None or selected_mv_editable"
                    ),
                VGroup(
                    UItem("current_modal", editor=InstanceEditor(),
                          style="custom",
                          visible_when="current_modal is not None"),
                    UItem('btn'),
                    label="New Model Details"
                ),
                VGroup(
                    UItem("console_ns", label="Console", editor=ShellEditor()),
                    label="Console"
                ),
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
        """If there is a (non-default) view associated to the selected_mv,
        return True."""
        if self.selected_mv is None:
            return False

        if len(self.selected_mv.trait_views()) != 0:
            return True
        return False

    @on_trait_change('task.side_pane.workflow_tree.add_new_entity')
    def set_add_new_entity_function(self):
        self.add_function = self.task.side_pane.workflow_tree.add_new_entity

    @on_trait_change('task.side_pane.workflow_tree.selected_mv')
    def update_selected_mv(self):
        self.selected_mv = self.task.side_pane.workflow_tree.selected_mv
        if self.selected_mv is not None:
            if isinstance(self.selected_mv.model, BaseModel):
                self.selected_model = self.selected_mv.model
            else:
                self.selected_model = None

    @on_trait_change('task.side_pane.workflow_tree.current_modal')
    def update_current_modal(self):
        self.current_modal = self.task.side_pane.workflow_tree.current_modal
        print(self.current_modal)
        if self.current_modal is not None:
            print('currentmodel:',self.current_modal, self.current_modal.current_model)

    @on_trait_change('current_modal.current_model')
    def current_model(self):
        if self.current_modal is not None:
            print(self.current_modal.current_model)

    @on_trait_change('btn')
    def create_new(self, parent):
        #self.task.side_pane.workflow_tree.workflow_mv.add_notification_listener(self.current_modal.current_model)
        self.add_function()