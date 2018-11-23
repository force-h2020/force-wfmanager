from pyface.tasks.api import TraitsTaskPane
from traits.api import (
    Bool, Button, Callable, Dict, Either, Instance, Property, Unicode,
    on_trait_change
)
from traitsui.api import (
    InstanceEditor, HGroup, ModelView, UItem, View, VGroup
)

from force_bdss.api import KPISpecification, Workflow
from force_bdss.core.base_model import BaseModel
from force_wfmanager.left_side_pane.new_entity_creator import NewEntityCreator


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

    #: The name of the currently selected factory. If no factory is selected,
    #: this is set to 'None' (with type Unicode!)
    selected_factory_name = Unicode('Workflow')

    #: A function which adds a new entity to the workflow tree, using the
    # currently selected factory. For example, if the 'DataSources' factory
    #: is selected, this function would be new_data_source().
    add_new_entity_function = Callable()

    #: Function to remove the currently selected modelview
    remove_entity_function = Callable()

    #: A NewEntityModal object displaying the factories of the currently
    #: selected group
    current_modal = Instance(NewEntityCreator)

    #: A Button which calls add_new_entity_function when pressed
    add_new_entity = Button()

    #: A Button which calls remove_entity_function when pressed
    remove_entity = Button()

    #: Switch to disable adding an entity if all required properties are
    #: not set
    enable_add_button = Property(Bool, depends_on='current_modal,'
                                                  'current_modal.model')

    #: The view when editing the selected instance within the workflow tree
    traits_view = View(
        HGroup(
                # Instance View
                VGroup(
                    UItem("selected_mv", editor=InstanceEditor(),
                          style="custom",
                          visible_when="selected_mv_editable",
                          ),
                    UItem("selected_model", editor=InstanceEditor(),
                          style="custom",
                          visible_when="selected_model is not None"),
                    HGroup(
                        UItem('remove_entity', label='Delete'),
                    ),
                    label="Model Details",
                    visible_when="selected_factory_name=='None'",
                    show_border=True,
                    ),
                # Factory View
                VGroup(
                    HGroup(
                        UItem("current_modal", editor=InstanceEditor(),
                              style="custom",
                              visible_when="current_modal is not None",
                              width=825),
                        springy=True,

                    ),
                    HGroup(
                        UItem('add_new_entity', label='Add',
                              enabled_when='enable_add_button'),
                        UItem('remove_entity', label='Delete Layer',
                              visible_when="selected_factory_name == "
                                           "'DataSource'"),
                    ),
                    label="New Model Details",
                    visible_when="selected_factory_name != 'None'",
                    show_border=True,

                ),

                # TODO:
                # The console functionality will be moved to a 'Debug' menu
                # at a later stage of the UI reorganisation. It should also use
                # an envisage Task implementation if this isn't too difficult!
                # VGroup(
                # UItem("console_ns", label="Console", editor=ShellEditor()),
                # label="Console"
                # ),
            ),
        width=500,
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

    # Properties

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

    def _get_enable_add_button(self):
        """Return True if the selected factory is a generic type which can
        always be added (KPI, Execution Layer), or if a specific
        factory is selected in the Setup Pane"""
        simple_factories = ['KPI', 'ExecutionLayer']
        if self.selected_factory_name in simple_factories:
            return True
        if self.current_modal is None or self.current_modal.model is None:
            return False
        return True

    # Synchronisation with WorkflowTree

    @on_trait_change('task.side_pane.workflow_tree.add_new_entity')
    def sync_add_new_entity_function(self):
        self.add_new_entity_function = \
            self.task.side_pane.workflow_tree.add_new_entity

    @on_trait_change('task.side_pane.workflow_tree.remove_entity')
    def sync_remove_entity_function(self):
        self.remove_entity_function = \
            self.task.side_pane.workflow_tree.remove_entity

    @on_trait_change('task.side_pane.workflow_tree.selected_mv')
    def sync_selected_mv(self):
        """ Synchronise selected_mv with the selected modelview in the tree
        editor. Checks if the model held by the modelview needs to be displayed
        in the UI."""
        self.selected_mv = self.task.side_pane.workflow_tree.selected_mv
        if self.selected_mv is not None:
            if isinstance(self.selected_mv.model, BaseModel):
                self.selected_model = self.selected_mv.model
            else:
                self.selected_model = None

    @on_trait_change('task.side_pane.workflow_tree.selected_factory_name')
    def sync_selected_factory_name(self):
        self.selected_factory_name = \
            self.task.side_pane.workflow_tree.selected_factory_name

    @on_trait_change('task.side_pane.workflow_tree.current_modal')
    def sync_current_modal(self):
        self.current_modal = self.task.side_pane.workflow_tree.current_modal

    # Button handlers for creating and deleting workflow items

    @on_trait_change('add_new_entity')
    def create_new_workflow_item(self, parent):
        self.add_new_entity_function()

    @on_trait_change('remove_entity')
    def delete_selected_workflow_item(self, parent):
        self.remove_entity_function()
