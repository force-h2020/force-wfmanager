from pyface.tasks.api import TraitsTaskPane
from traits.api import (
    Bool, Button, Callable, Instance, Property, Unicode,
    on_trait_change
)
from traitsui.api import (
    ButtonEditor, InstanceEditor, HGroup, ModelView, UItem, View, VGroup
)

from force_bdss.api import BaseExtensionPlugin, BaseModel, Workflow
from force_wfmanager.left_side_pane.new_entity_creator import NewEntityCreator
from force_wfmanager.left_side_pane.workflow_info import WorkflowInfo


class SetupPane(TraitsTaskPane):
    """A TraitsTaskPane containing the factory selection and new object
    configuration editors.

    Attributes
    ----------
    id: String
    name: String
    workflow_model: Workflow
        The model for the Workflow
    selected_mv: ModelView
        The currently selected ModelView in the WorkflowTree
        Affected by: task.side_pane.workflow_tree.selected_mv
    selected_model: BaseModel
        The model from selected_mv
    selected_mv_editable: Bool
        A Bool indicating whether the modelview is intended to be editable by
        the user. Workaround to avoid displaying a default view.
        If a modelview has a View defining how it is represented in the UI
        then this is used. However, if a modelview does not have this the
        default view displays everything and does not look too nice!
        Affected by: selected_mv
    selected_factory_name: Unicode
        The name of the currently selected factory. If no factory is selected,
        this is set to 'None' (with type Unicode, not NoneType!)
        Affected by: task.side_pane.workflow_tree.selected_factory_name
    add_new_entity: Callable
        A function which adds a new entity to the workflow tree, using the
        currently selected factory. For example, if the 'DataSources' factory
        is selected, this function would be new_data_source().
        Affected by: task.side_pane.workflow_tree.add_new_entity
    add_new_entity_label: Unicode
        The string displayed on the 'add new entity' button
        Affected by: selected_factory_name
    remove_entity: Callable
        Function to remove the currently selected modelview from the
        workflow tree
        Affected by: task.side_pane.workflow_tree.remove_entity
    entity_creator: NewEntityCreator
        A NewEntityModal object displaying the factories of the currently
        selected group
        Affected by: task.side_pane.workflow_tree.entity_creator
    current_info: WorkflowInfo
        A panel displaying extra information about the workflow in general.
        Displayed for factories which have a lot of empty screen space.
        Affected by: selected_factory_name, selected_mv, task.current_file
    add_new_entity_btn: Button
        A Button which calls add_new_entity when pressed
    remove_entity_btn: Button
        A Button which calls remove_entity when pressed
    enable_add_button: Bool
        Determines if the add button should be active. KPI and Execution
        Layers can always be added, but other workflow items need a specific
        factory to be selected
        Affected by: entity_creator, entity_creator.model
    """
    id = 'force_wfmanager.setup_pane'

    name = 'Setup Pane'

    workflow_model = Instance(Workflow)

    selected_mv = Instance(ModelView)

    selected_model = Instance(BaseModel)

    selected_mv_editable = Property(Bool, depends_on='selected_mv')

    selected_factory_name = Unicode('Workflow')

    add_new_entity = Callable()

    add_new_entity_label = Property(
        Unicode(), depends_on='selected_factory_name'
    )

    remove_entity = Callable()

    entity_creator = Instance(NewEntityCreator)

    current_info = Property(
        Instance(WorkflowInfo),
        depends_on='selected_factory_name,selected_mv,task.current_file'
    )

    add_new_entity_btn = Button()

    remove_entity_btn = Button()

    enable_add_button = Property(Bool, depends_on='entity_creator,'
                                                  'entity_creator.model')

    #: The view when editing an existing instance within the workflow tree
    def default_traits_view(self):
        view = View(VGroup(
            HGroup(
                # Instance View
                VGroup(
                    UItem(
                        "selected_mv", editor=InstanceEditor(),
                        style="custom",
                        visible_when="selected_mv_editable"
                    ),
                    UItem(
                        "selected_model", editor=InstanceEditor(),
                        style="custom",
                        visible_when="selected_model is not None"
                    ),
                    # Remove Buttons
                    HGroup(
                        UItem('remove_entity_btn', label='Delete'),
                        ),
                    label="Item Details",
                    visible_when="selected_factory_name=='None'",
                    show_border=True,
                    ),
                # Factory View
                VGroup(
                    HGroup(
                        UItem(
                            "entity_creator",
                            editor=InstanceEditor(),
                            style="custom",
                            visible_when="entity_creator is not None",
                            width=825
                        ),
                        springy=True,
                    ),
                    HGroup(
                        UItem(
                            'add_new_entity_btn',
                            editor=ButtonEditor(
                                label_value='add_new_entity_label'
                            ),
                            enabled_when='enable_add_button',
                            visible_when="selected_factory_name != 'None'",
                            springy=True
                        ),
                        # Remove Buttons
                        UItem(
                            'remove_entity_btn',
                            label='Delete Layer',
                            visible_when=(
                                "selected_factory_name == 'Data Source'"
                            ),
                        ),
                        label="New Item Details",
                        visible_when="selected_factory_name not in "
                                     "['None', 'Workflow']",
                        show_border=True,
                    ),
                ),
            ),
            VGroup(
                UItem(
                    "current_info",
                    editor=InstanceEditor(),
                    style="custom",
                    visible_when=(
                        "selected_factory_name in ['Workflow', 'KPI',"
                        "'Execution Layer']"
                    )
                )
            ),
        ),
            width=500,
        )

        return view

    def _console_ns_default(self):
        namespace = {
            "task": self.task
        }
        try:
            namespace["app"] = self.task.window.application
        except AttributeError:
            namespace["app"] = None

        return namespace

    # Property getters

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
        factory is selected in the Setup Pane. Returns False otherwise."""
        simple_factories = ['KPI', 'Execution Layer']
        if self.selected_factory_name in simple_factories:
            return True
        if self.entity_creator is None or self.entity_creator.model is None:
            return False
        return True

    def _get_current_info(self):
        """Returns a WorkflowInfo object, which displays general information
        about the workflow and plugins installed. This is displayed when
        nodes with less visual content are selected."""
        workflow_mv = self.task.side_pane.workflow_tree.workflow_mv
        plugins = [
            plugin for plugin in self.task.window.application.plugin_manager
            if isinstance(plugin, BaseExtensionPlugin)
        ]

        # Plugins guaranteed to have an id, so sort by that if name is not set
        plugins.sort(
            key=lambda s: s.name if s.name not in ('', None) else s.id
        )

        return WorkflowInfo(
            plugins=plugins, workflow_mv=workflow_mv,
            workflow_filename=self.task.current_file,
            selected_factory=self.selected_factory_name
        )

    def _get_add_new_entity_label(self):
        """Returns the label displayed on add_new_entity_btn"""
        return 'Add New {!s}'.format(self.selected_factory_name)

    # Synchronisation with WorkflowTree

    @on_trait_change('task.side_pane.workflow_tree.add_new_entity')
    def sync_add_new_entity(self):
        """Synchronises add_new_entity with WorkflowTree"""
        self.add_new_entity = (
            self.task.side_pane.workflow_tree.add_new_entity
        )

    @on_trait_change('task.side_pane.workflow_tree.remove_entity')
    def sync_remove_entity(self):
        """Synchronises remove_entity with WorkflowTree"""
        self.remove_entity = (
            self.task.side_pane.workflow_tree.remove_entity
        )

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
        """Synchronises selected_factory_name with WorkflowTree"""
        self.selected_factory_name = (
            self.task.side_pane.workflow_tree.selected_factory_name
        )

    @on_trait_change('task.side_pane.workflow_tree.entity_creator')
    def sync_entity_creator(self):
        """Synchronises entity_creator with WorkflowTree"""
        self.entity_creator = self.task.side_pane.workflow_tree.entity_creator

    # Button event handlers for creating and deleting workflow items
    @on_trait_change('add_new_entity_btn')
    def create_new_workflow_item(self, parent):
        """Calls add_new_entity when add_new_entity_btn clicked"""
        self.add_new_entity()

    @on_trait_change('remove_entity_btn')
    def delete_selected_workflow_item(self, parent):
        """Calls remove_entity when remove_entity_btn clicked"""
        self.remove_entity()
