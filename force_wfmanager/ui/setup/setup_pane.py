from pyface.tasks.api import TraitsTaskPane
from traits.api import (
    Bool, Button, Instance, Property, Unicode,
    on_trait_change, cached_property
)
from traitsui.api import (
    ButtonEditor, InstanceEditor, HGroup, UItem, View, VGroup
)

from force_bdss.api import BaseModel
from force_wfmanager.ui.setup.workflow_info import WorkflowInfo
from force_wfmanager.ui.setup.system_state import SystemState


class SetupPane(TraitsTaskPane):
    """A TraitsTaskPane containing the factory selection and new object
    configuration editors."""

    # -------------------
    # Required Attributes
    # -------------------

    system_state = Instance(SystemState, allow_none=False)

    # ------------------
    # Regular Attributes
    # ------------------

    #: An internal identifier for this pane
    id = 'force_wfmanager.setup_pane'

    #: Name displayed as the title of this pane
    name = 'Setup Pane'

    # ------------------
    # Derived Attributes
    # ------------------

    #: The model from selected_view.
    #: Listens to: :attr:`models.workflow_tree.selected_view
    #: <force_wfmanager.models.workflow_tree.WorkflowTree.selected_view>`
    selected_model = Instance(BaseModel)

    #: An error message for the entire workflow
    error_message = Unicode()

    # --------------------
    # Button Attributes
    # --------------------

    #: A Button which calls add_new_entity when pressed.
    add_new_entity_btn = Button()

    #: A Button which calls remove_entity when pressed.
    remove_entity_btn = Button()

    # ----------
    # Properties
    # ----------

    #: The string displayed on the 'add new entity' button.
    add_new_entity_label = Property(
        Unicode(), depends_on='system_state:selected_factory_name'
    )

    #: A Boolean indicating whether the currently selected modelview is
    #: intended to be editable by the user. This is required to avoid
    #: displaying a default view when a model does not have a View defined for
    #: it. If a modelview has a View defining how it is represented in the UI
    #: then this is used.
    selected_view_editable = Property(
        Bool, depends_on='system_state:selected_view'
    )

    #: A Boolean indicating whether the currently selected view represents
    #: either a KPI or Parameter.
    mco_view_visible = Property(
        Bool, depends_on='system_state:[selected_view,selected_factory_name]'
    )

    #: A Boolean indicating whether the currently selected view represents
    #: a factory view.
    factory_view_visible = Property(
        Bool, depends_on='system_state:selected_factory_name'
    )

    #: A Boolean indicating whether the currently selected view represents
    #: an instance view.
    instance_view_visible = Property(
        Bool, depends_on='system_state:selected_factory_name'
    )

    #: A panel displaying extra information about the workflow: Available
    #: Plugins, non-KPI variables, current filenames and any error messages.
    #: Displayed for factories which have a lot of empty screen space.
    current_info = Property(
        Instance(WorkflowInfo),
        depends_on='system_state:[selected_factory_name,selected_view],'
                   'task.current_file'
    )

    #: Determines if the add button should be active. KPI and Execution
    #: Layers can always be added, but other workflow items need a specific
    #: factory to be selected.
    enable_add_button = Property(
        Bool, depends_on='system_state:[selected_factory_name,'
                         'entity_creator.model]'
    )

    #: The view when editing an existing instance within the workflow tree
    def default_traits_view(self):
        """ Sets up a TraitsUI view which displays the details
        (parameters etc.) of the currently selected modelview. This varies
        depending on what type of modelview is selected."""
        view = View(
            VGroup(
                # Main View with FORCE Logo
                VGroup(
                    UItem(
                        "current_info",
                        editor=InstanceEditor(),
                        style="custom",
                        ),
                    visible_when = (
                        "object.system_state.selected_factory_name == 'Workflow'"
                    )
                ),
                # MCO Parameter and KPI views
                VGroup(
                    UItem(
                        "object.system_state.selected_view",
                        editor=InstanceEditor(),
                        style="custom",
                    ),
                    visible_when="mco_view_visible"

                ),
                # Process Tree Views
                HGroup(
                    # Instance View
                    VGroup(
                        UItem(
                            "object.system_state.selected_view",
                            editor=InstanceEditor(),
                            style="custom",
                            visible_when="selected_view_editable"
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
                        visible_when="instance_view_visible",
                        show_border=True,
                    ),
                    # Factory View
                    VGroup(
                        HGroup(
                            UItem(
                                "object.system_state.entity_creator",
                                editor=InstanceEditor(),
                                style="custom",
                                visible_when="object.system_state.entity_creator "
                                             "is not None",
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
                                visible_when="object.system_state.selected_factory_name "
                                             "!= 'None'",
                                springy=True
                            ),
                            # Remove Buttons
                            UItem(
                                'remove_entity_btn',
                                label='Delete Layer',
                                visible_when=(
                                    "object.system_state.selected_factory_name "
                                    "== 'Data Source'"
                                ),
                            ),
                            label="New Item Details",
                            visible_when="factory_view_visible",
                            show_border=True,
                        ),
                    ),
                ),
            ),
            width=500,
        )

        return view

    # Property getters
    @cached_property
    def _get_selected_view_editable(self):
        """ Determines if the selected modelview in the WorkflowTree has a
        default or non-default view associated. A default view should not
        be editable by the user, a non-default one should be.

        Parameters
        ----------
        self.selected_view.trait_views(): List of View
            The list of Views associated with self.selected_view. The default
            view is not included in this list.

        Returns
        -------
        Bool
            Returns True if selected_view has a User Editable/Non-Default View,
            False if it only has a default View or no modelview is
            currently selected
        """
        if self.system_state.selected_view is None:
            return False
        elif len(self.system_state.selected_view.trait_views()) == 0:
            return False
        return True

    @cached_property
    def _get_mco_view_visible(self):
        if self.system_state.selected_view is not None:
            mco_factories = ['MCO Parameters', 'MCO KPIs']
            return (
                    self.system_state.selected_factory_name in mco_factories
            )
        return False

    @cached_property
    def _get_factory_view_visible(self):
        factories = ['None', 'Workflow', 'MCO Parameters', 'MCO KPIs']
        return (
            self.system_state.selected_factory_name not in factories
        )

    @cached_property
    def _get_instance_view_visible(self):
        return self.system_state.selected_factory_name == 'None'

    @cached_property
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
        simple_factories = ['Execution Layer', 'MCO']
        if self.system_state.selected_factory_name in simple_factories:
            return True
        if self.system_state.entity_creator is None \
                or self.system_state.entity_creator.model is None:
            return False
        return True

    @cached_property
    def _get_add_new_entity_label(self):
        """Returns the label displayed on add_new_entity_btn"""
        return 'Add New {!s}'.format(self.system_state.selected_factory_name)

    @cached_property
    def _get_current_info(self):
        return WorkflowInfo(
            workflow_filename=self.task.current_file,
            plugins=self.task.lookup_plugins(),
            selected_factory_name=self.system_state.selected_factory_name,
            error_message=self.error_message
        )

    #: Listeners
    # Synchronisation with WorkflowTree
    @on_trait_change('system_state:selected_view')
    def sync_selected_view(self):
        """ Synchronise selected_view with the selected modelview in the tree
        editor. Checks if the model held by the modelview needs to be displayed
        in the UI."""
        if self.system_state.selected_view is not None:
            if isinstance(self.system_state.selected_view.model, BaseModel):
                self.selected_model = self.system_state.selected_view.model
            else:
                self.selected_model = None


    @on_trait_change('task:side_pane:workflow_tree:error_message')
    def sync_error_message(self):
        """Synchronises entity_creator with WorkflowTree"""
        self.error_message = self.task.side_pane.workflow_tree.error_message

    #: Button actions
    # Button event handlers for creating and deleting workflow items
    def _add_new_entity_btn_fired(self):
        """Calls add_new_entity when add_new_entity_btn is clicked"""
        self.system_state.add_new_entity()

    def _remove_entity_btn_fired(self):
        """Calls remove_entity when remove_entity_btn is clicked"""
        self.system_state.remove_entity()

    #: Protected methods
    def _console_ns_default(self):
        namespace = {
            "task": self.task
        }
        try:
            namespace["app"] = self.task.window.application
        except AttributeError:
            namespace["app"] = None

        return namespace
