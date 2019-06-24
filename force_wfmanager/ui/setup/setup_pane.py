from pyface.tasks.api import TraitsTaskPane
from traits.api import (
    Bool, Button, Callable, Instance, Property, Unicode,
    on_trait_change
)
from traitsui.api import (
    ButtonEditor, InstanceEditor, HGroup, ModelView, UItem, View, VGroup
)

from force_bdss.api import BaseExtensionPlugin, BaseModel, Workflow
from force_wfmanager.ui.setup.new_entity_creator import NewEntityCreator
from force_wfmanager.ui.setup.workflow_info import WorkflowInfo


class SetupPane(TraitsTaskPane):
    """A TraitsTaskPane containing the factory selection and new object
    configuration editors."""

    # -------------------
    # Required Attributes
    # -------------------

    #: The Workflow currently displayed in the WorkflowTree.
    workflow_model = Instance(Workflow)

    # ------------------
    # Regular Attributes
    # ------------------

    #: An internal identifier for this pane
    id = 'force_wfmanager.setup_pane'

    #: Name displayed as the title of this pane
    name = 'Setup Pane'

    #: A Button which calls add_new_entity when pressed.
    add_new_entity_btn = Button()

    #: A Button which calls remove_entity when pressed.
    remove_entity_btn = Button()

    # ------------------
    # Derived Attributes
    # ------------------

    #: The currently selected ModelView in the WorkflowTree.
    #: Listens to: :attr:`models.workflow_tree.selected_mv
    #: <force_wfmanager.models.workflow_tree.WorkflowTree.selected_mv>`
    selected_mv = Instance(ModelView)

    #: The model from selected_mv.
    #: Listens to: :attr:`models.workflow_tree.selected_mv
    #: <force_wfmanager.models.workflow_tree.WorkflowTree.selected_mv>`
    selected_model = Instance(BaseModel)

    #: The name of the currently selected factory. If no factory is selected,
    #: this is set to 'None' (with type Unicode, not NoneType!)
    #: Listens to: :attr:`models.workflow_tree.selected_factory_name
    #: <force_wfmanager.models.workflow_tree.WorkflowTree.\
    #: selected_factory_name>`
    selected_factory_name = Unicode()

    #: A function which adds a new entity to the workflow tree, using the
    #: currently selected factory. For example, if the 'DataSources' factory
    #: is selected, this function would be ``new_data_source()``.
    #: Listens to: :attr:`models.workflow_tree.add_new_entity
    #: <force_wfmanager.models.workflow_tree.WorkflowTree.\
    #: add_new_entity>`
    add_new_entity = Callable()

    #: A function to remove the currently selected modelview from the
    #: workflow tree.
    #: Listens to: :attr:`models.workflow_tree.remove_entity
    #: <force_wfmanager.models.workflow_tree.WorkflowTree.\
    #: remove_entity>`
    remove_entity = Callable()

    #: A NewEntityModal object displaying the factories of the currently
    #: selected group.
    #: Listens to: :attr:`models.workflow_tree.entity_creator
    #: <force_wfmanager.models.workflow_tree.WorkflowTree.\
    #: entity_creator>`
    entity_creator = Instance(NewEntityCreator)

    # ----------
    # Properties
    # ----------

    #: The string displayed on the 'add new entity' button.
    add_new_entity_label = Property(
        Unicode(), depends_on='selected_factory_name'
    )

    #: A Boolean indicating whether the currently selected modelview is
    #: intended to be editable by the user. This is required to avoid
    #: displaying a default view when a model does not have a View defined for
    #: it. If a modelview has a View defining how it is represented in the UI
    #: then this is used.
    selected_mv_editable = Bool()

    #: A panel displaying extra information about the workflow: Available
    #: Plugins, non-KPI variables, current filenames and any error messages.
    #: Displayed for factories which have a lot of empty screen space.
    current_info = Property(
        Instance(WorkflowInfo),
        depends_on='selected_factory_name,selected_mv,task.current_file'
    )

    #: Determines if the add button should be active. KPI and Execution
    #: Layers can always be added, but other workflow items need a specific
    #: factory to be selected.
    enable_add_button = Property(
        Bool, depends_on='entity_creator,entity_creator.model'
    )

    #: The view when editing an existing instance within the workflow tree
    def default_traits_view(self):
        """ Sets up a TraitsUI view which displays the details
        (parameters etc.) of the currently selected modelview. This varies
        depending on what type of modelview is selected."""
        view = View(VGroup(
            # Main view with Force logo
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
            HGroup(
                # Instance View
                VGroup(
                    UItem(
                        "selected_mv", editor=InstanceEditor(),
                        style="custom", visible_when="selected_mv_editable"
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
                            "entity_creator", editor=InstanceEditor(),
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
    @on_trait_change('selected_mv')
    def get_selected_mv_editable(self):
        """ Determines if the selected modelview in the WorkflowTree has a
        default or non-default view associated. A default view should not
        be editable by the user, a non-default one should be.

        Parameters
        ----------
        self.selected_mv.trait_views(): List of View
            The list of Views associated with self.selected_mv. The default
            view is not included in this list.

        Returns
        -------
        Bool
            Returns True if selected_mv has a User Editable/Non-Default View,
            False if it only has a default View or no modelview is
            currently selected
        """
        if self.selected_mv is None or self.selected_mv.trait_views() == []:
            self.selected_mv_editable = False
        else:
            self.selected_mv_editable = True

    def _get_enable_add_button(self):
        """ Determines if the add button in the UI should be enabled.

        Parameters
        ----------
        self.entity_creator.model: BaseModel
            The result of calling `create_model()` on the selected factory.
            This occurs automatically when a factory is selected in the UI.

        Returns
        -------
        Bool
            Returns True if the selected factory can create a new instance.
            Returns False otherwise.
        """
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
            selected_factory_name=self.selected_factory_name
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
                #: FIXME - this will raise an AttributeError if
                #: self.selected_mv.model has not initialised a traits_view
                #: object
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
        """Calls add_new_entity when add_new_entity_btn is clicked"""
        self.add_new_entity()

    @on_trait_change('remove_entity_btn')
    def delete_selected_workflow_item(self, parent):
        """Calls remove_entity when remove_entity_btn is clicked"""
        self.remove_entity()
