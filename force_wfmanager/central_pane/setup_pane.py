from force_bdss.api import Workflow
from force_bdss.core.base_model import BaseModel
from force_bdss.core.kpi_specification import KPISpecification
from pyface.tasks.api import TraitsTaskPane
from traits.api import (
    Bool, Dict, Either, Instance, String, Property, on_trait_change
)
from traitsui.api import (
    InstanceEditor, ModelView, ShellEditor, UItem, View, VGroup
)


class SetupPane(TraitsTaskPane):
    id = 'force_wfmanager.setup_pane'
    name = 'Setup Pane'

    #: The model for the Workflow
    workflow_model = Instance(Workflow)

    #: Namespace for the console
    console_ns = Dict()

    #: The model from the selected modelview (selected_mv.model)
    selected_model = Either(Instance(BaseModel), Instance(KPISpecification))

    #: A Bool indicating whether the modelview is intended to be editable by
    #: the user. Workaround to avoid displaying a default view.
    #: If a modelview has a View defining how it is represented in the UI
    #: then this is used. However, if a modelview does not have this the
    #: default view displays everything and does not look too nice!
    selected_mv_editable = Property(Bool, depends_on='selected_mv')

    #: The currently selected ModelView in the WorkflowTree
    selected_mv = Instance(ModelView)

    #: The name of the factory group selected in the WorkflowTree
    selected_factory_group = String('Workflow')

    #: The view when editing the selected instance within the workflow tree
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
        """Determine if the selected modelview in the WorkflowTree has a
        default or non-default view associated. A default view should not
        be editable by the user, a non-default one should be.

        Parameters
        ----------
        self.selected_mv - Currently selected modelview, synchronised to
        selected_mv in the WorkflowTree class.

        self.selected_mv.trait_views() - The list of Views associated with
        this Traits object. The default view is not included.

        Returns
        -------
        True - User Editable/Non-Default View
        False - Default View or No modelview currently selected

        """
        if self.selected_mv is None or self.selected_mv.trait_views() == []:
            return False
        return True

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
