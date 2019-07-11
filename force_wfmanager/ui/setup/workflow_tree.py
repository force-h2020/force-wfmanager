from functools import partial, wraps

from traits.api import (
    Event, Instance, Property, Unicode, on_trait_change
)
from traitsui.api import (
    Action, Group, Menu, ModelView, TextEditor,
    TreeEditor, TreeNode, UItem, UReadonly, View, VGroup
)

from force_bdss.api import (
    ExecutionLayer, IFactoryRegistry, InputSlotInfo,
    OutputSlotInfo, Workflow, verify_workflow
)
from force_wfmanager.ui.setup.process.data_source_view \
    import DataSourceView
from force_wfmanager.ui.setup.process.execution_layer_view \
    import ExecutionLayerView
from force_wfmanager.ui.setup.process.process_view import (
    ProcessView
)
from force_wfmanager.ui.setup.mco.kpi_specification_view import (
    KPISpecificationView
)
from force_wfmanager.ui.setup.mco.mco_view import \
    MCOView
from force_wfmanager.ui.setup.mco.mco_parameter_view import (
    MCOParameterView
)
from force_wfmanager.ui.setup.new_entity_creator import NewEntityCreator
from force_wfmanager.ui.setup.communicator. \
    notification_listener_view import NotificationListenerView
from force_wfmanager.ui.setup.workflow_view import (
    WorkflowView
)
from force_wfmanager.ui.setup.communicator.communicator_view import (
    CommunicatorView
)
from force_wfmanager.ui.setup.system_state import SystemState


# VerifierError severity constants
_ERROR = "error"
_WARNING = "warning"
_INFO = "information"

# Create an empty view and menu for objects that have no data to display:
no_view = View()
no_menu = Menu()

# -------------------
# Actions!
# -------------------

# A string to be used as the enabled_when argument for the actions.
# For reference, in the enabled_when expression namespace, handler is
# the WorkflowTree instance, object is the modelview for the selected node

# MCO Actions
new_mco_action = Action(name='New MCO...', action='new_mco')
delete_mco_action = Action(name='Delete', action='delete_mco')

# Notification Listener Actions
new_notification_listener_action = Action(
    name='New Notification Listener...',
    action='new_notification_listener'
)
delete_notification_listener_action = Action(
    name='Delete',
    action='delete_notification_listener'
)

# Execution Layer Actions
new_layer_action = Action(name="New Layer...", action='new_layer')
delete_layer_action = Action(name='Delete', action='delete_layer')

# DataSource Actions
new_data_source_action = Action(
    name='New DataSource...',
    action='new_data_source'
)
delete_data_source_action = Action(name='Delete', action='delete_data_source')


#: Wrapper to perform workflow verification after a method or function call
def triggers_verify(func):
    """Decorator for functions which make changes requiring the workflow to
    be verified"""

    @wraps(func)
    def wrap(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self.verify_workflow_event = True

    return wrap


def selection(func):
    """ Decorator for functions called on selecting something in the tree
    editor. Clears the `selected_factory_name`, `entity_creator`,
    `add_new_entity` and `remove_entity` attributes before they are set
    based on the selection choice
    """

    @wraps(func)
    def wrap(self, *args, **kwargs):
        self.system_state.selected_factory_name = 'None'
        self.system_state.entity_creator = None
        self.system_state.add_new_entity = None
        self.system_state.remove_entity = None
        func(self, *args, **kwargs)

    return wrap


class TreeNodeWithStatus(TreeNode):
    """ Custom TreeNode class for workflow elements. Allows setting a
    workflow element's icon depending on whether it has an error or not.
    """

    def get_icon(self, object, is_expanded):
        """ Overrides get_icon method of TreeNode.

        Parameters
        ----------
        object: HasTraits
            The view assigned to this TreeNode
        is_expanded: bool
            True if the TreeNode is expanded, i.e. child nodes of this
            TreeNode are also visible in the UI.
        """
        return 'icons/valid.png' if object.valid else 'icons/invalid.png'

    def when_label_changed(self, object, listener, remove):
        """ Overrides/Extends when_label_change method of TreeNode.
        This method sets up the listener as normal, where it responds to
        changes in the TreeNode label. Additionally, it sets the listener
        to respond to changes in the 'valid' attribute of a ModelView.

        Parameters
        ----------
        object: HasTraits
            The view assigned to this TreeNode
        listener: method
            The _label_updated method from TreeEditor
        remove: bool
            Whether to remove the listener from object

        Notes
        -----
        This is done as the method label_updated in tree_editor.py is one of
        the few handler methods to call update_icon. Since we also want to
        update the icon in response to a property change, this is a logical
        place to add the extra functionality.
        Unfortunately, the calls take place at the toolkit (qt, wx) level
        rather than at traitsUI level so this can't be done more directly.
        """
        super(TreeNodeWithStatus, self).when_label_changed(
            object, listener, remove
        )
        object.on_trait_change(listener, 'valid')


class WorkflowTree(ModelView):
    """ Part of the GUI containing the tree editor displaying the Workflow."""

    # -------------------
    # Required Attributes
    # -------------------

    #: The BDSS Workflow displayed in the WorkflowTree. Updated when
    #: ``TreePane.workflow_model`` changes
    model = Instance(Workflow, allow_none=False)

    #: A registry of the available factories
    _factory_registry = Instance(IFactoryRegistry, allow_none=False)

    #: Holds information about current selected objects
    system_state = Instance(SystemState, allow_none=False)

    # ------------------
    # Regular Attributes
    # ------------------

    #: The ModelView for the BDSS Workflow
    workflow_view = Instance(WorkflowView, allow_none=False)

    # ------------------
    # Derived Attributes
    # ------------------

    #: An event which runs a verification check on the current workflow when
    #: triggered.
    #: Listens to: :func:`~workflow_view.verify_workflow_event`
    verify_workflow_event = Event

    # ----------
    # Properties
    # ----------

    #: The error message currently displayed in the UI.
    selected_error = Property(
        Unicode(),
        depends_on="system_state.selected_view.[error_message,label]"
    )

    def default_traits_view(self):
        """The layout of the View for the WorkflowTree"""

        tree_editor = TreeEditor(
            nodes=[
                # Root node "Workflow"
                TreeNodeWithStatus(
                    node_for=[WorkflowView],
                    auto_open=True,
                    children='',
                    name='Workflow',
                    label='=Workflow',
                    view=no_view,
                    menu=no_menu,
                    on_select=self.workflow_selected
                ),
                # Node representing the Process"
                TreeNode(
                    node_for=[WorkflowView],
                    auto_open=True,
                    children='process_view',
                    name='Process',
                    label='=Process',
                    view=no_view,
                    menu=no_menu,
                    on_select=self.workflow_selected
                ),
                #: Node representing the Execution layers
                TreeNode(
                    node_for=[ProcessView],
                    auto_open=True,
                    children='execution_layer_views',
                    label='=Execution Layers',
                    name='Execution Layers',
                    view=no_view,
                    menu=Menu(new_layer_action),
                    on_select=self.process_selected
                ),
                TreeNodeWithStatus(
                    node_for=[ExecutionLayerView],
                    auto_open=True,
                    children='data_source_views',
                    label='label',
                    name='DataSources',
                    view=no_view,
                    menu=Menu(delete_layer_action),
                    on_select=self.execution_layer_selected
                ),
                TreeNodeWithStatus(
                    node_for=[DataSourceView],
                    auto_open=True,
                    children='',
                    label='label',
                    name='DataSources',
                    menu=Menu(delete_data_source_action),
                    on_select=self.data_source_selected
                ),
                # Folder node "MCO" containing the MCO
                TreeNode(
                    node_for=[WorkflowView],
                    auto_open=True,
                    children='mco_view',
                    label='=MCO',
                    name='MCO',
                    view=no_view,
                    menu=no_menu,
                    on_select=self.mco_selected,
                ),
                # Node representing the MCO
                TreeNodeWithStatus(
                    node_for=[MCOView],
                    auto_open=True,
                    children='mco_options',
                    label='label',
                    name='MCO',
                    view=no_view,
                    menu=Menu(delete_mco_action),
                    on_select=self.mco_optimizer_selected
                ),
                # Node representing the MCO Parameters
                TreeNodeWithStatus(
                    node_for=[MCOParameterView],
                    auto_open=True,
                    children='',
                    label='=Parameters',
                    name='Parameters',
                    view=no_view,
                    menu=no_menu,
                    on_select=self.mco_parameters_selected
                ),
                # Node representing the MCO KPIs
                TreeNodeWithStatus(
                    node_for=[KPISpecificationView],
                    auto_open=True,
                    children='',
                    label='=KPIs',
                    name='KPIs',
                    view=no_view,
                    menu=no_menu,
                    on_select=self.mco_kpis_selected
                ),
                TreeNode(
                    node_for=[WorkflowView],
                    auto_open=True,
                    children='communicator_view',
                    name='Communicator',
                    label='=Communicator',
                    view=no_view,
                    menu=no_menu,
                    on_select=self.workflow_selected
                ),
                TreeNode(
                    node_for=[CommunicatorView],
                    auto_open=True,
                    children='notification_listener_views',
                    label='=Notification Listeners',
                    name='Notification Listeners',
                    view=no_view,
                    menu=no_menu,
                    on_select=self.communicator_selected
                ),
                # Node representing the Notification Listener
                TreeNodeWithStatus(
                    node_for=[NotificationListenerView],
                    auto_open=True,
                    children='',
                    label='label',
                    name='Notification Listeners',
                    view=no_view,
                    menu=Menu(delete_notification_listener_action),
                    on_select=self.notification_listener_selected
                )
            ],
            orientation="horizontal",
            editable=False,
            selected="object.system_state.selected_view",
        )

        view = View(
            Group(
                VGroup(
                    UItem(name='workflow_view',
                          editor=tree_editor,
                          show_label=False
                          ),
                ),
                VGroup(
                    UReadonly(
                        name='selected_error',
                        editor=TextEditor(),
                    ),
                    label='Workflow Errors',
                    show_border=True
                ),
            ),
            width=500,
            resizable=True,
        )

        return view

    #: Defaults
    def _workflow_view_default(self):
        """A default WorkflowModelView"""
        return WorkflowView(model=self.model)

    #: Property getters
    def _get_selected_error(self):
        """Returns the error messages for the currently selected modelview"""
        if self.system_state.selected_view is None:
            return ERROR_TEMPLATE.format("No Item Selected", "")

        if self.system_state.selected_view.error_message == '':
            mv_label = self.system_state.selected_view.label
            return ERROR_TEMPLATE.format(
                "No errors for {}".format(mv_label), "")
        else:
            mv_label = self.system_state.selected_view.label
            error_list = (self.system_state.selected_view
                          .error_message.split('\n'))
            body_strings = ''.join([SINGLE_ERROR.format(error)
                                    for error in error_list])
            return ERROR_TEMPLATE.format(
                "Errors for {}:".format(mv_label), body_strings)

    #: Listeners
    @on_trait_change('model')
    def update_model_view(self):
        """Update the workflow modelview's model and verify, on either loading
        a new workflow, or an internal change to the workflow.
        """
        self.workflow_view = WorkflowView(model=self.model)
        self.verify_workflow_event = True

    # Workflow Verification
    @on_trait_change("workflow_view.verify_workflow_event")
    def received_verify_request(self):
        """Checks if the root node of workflow tree is requesting a
        verification of the workflow"""
        self.verify_workflow_event = True

    @on_trait_change("verify_workflow_event")
    def perform_verify_workflow_event(self):
        """Verify the workflow and update error_message traits of
        every ModelView in the workflow"""
        errors = verify_workflow(self.model)

        # Communicate the verification errors to each level of the
        # workflow tree
        self.verify_tree(errors)

    # Item Selection Actions - create an appropriate NewEntityModal,
    # set add_new_entity to be for the right object type and provide a way to
    # add things by double clicking

    @selection
    def workflow_selected(self, workflow_view):
        """Called on selecting the top node in the WorkflowTree

        Parameters
        ----------
        workflow_view: WorkflowView
            Unused, automatically passed by TreeEditor on selection
        """
        self.system_state.selected_factory_name = 'Workflow'

    @selection
    def process_selected(self, process_view):
        """Called on selecting a ProcessView node in the WorkflowTree

        Parameters
        ----------
        process_view: ProcessView
            Selected ProcessView node in the TreeEditor
        """

        self.system_state.selected_factory_name = 'Execution Layer'
        self.system_state.add_new_entity = partial(
            self.new_layer,
            ui_info=None,
            object=process_view
        )

    @selection
    def execution_layer_selected(self, execution_layer_view):
        """Called on selecting an ExecutionLayerView node in
        the WorkflowTree

        Parameters
        ----------
        execution_layer_view: ExecutionLayerView
            Selected ExecutionLayerView node in the TreeEditor
        """

        add_new_entity = partial(
            self.new_data_source,
            ui_info=None,
            object=execution_layer_view,
        )

        factories = self._factory_registry.data_source_factories

        if factories is not None:

            visible_factories = [f for f in factories if f.ui_visible]

            self.system_state.entity_creator = NewEntityCreator(
                factories=visible_factories,
                dclick_function=add_new_entity
            )

        self.system_state.add_new_entity = partial(
            add_new_entity,
            ui_info=None,
        )

        self.system_state.remove_entity = partial(
            self.delete_layer,
            ui_info=None,
            object=execution_layer_view
        )

        self.system_state.selected_factory_name = 'Data Source'

    @selection
    def data_source_selected(self, data_source_view):
        """Called on selecting a DataSourceView node in the
        WorkflowTree

        Parameters
        ----------
        data_source_view: DataSourceView
            Selected DataSourceView node in the TreeEditor
        """
        self.system_state.remove_entity = partial(
            self.delete_data_source,
            ui_info=None,
            object=data_source_view)

    @selection
    def mco_selected(self, workflow_view):
        """Called on selecting the MCO node in the WorkflowTree

        Parameters
        ----------
        workflow_view: WorkflowView
            Selected WorkflowView in the TreeEditor containing the MCO
        """

        add_new_entity = partial(
            self.new_mco,
            object=workflow_view
        )

        factories = self._factory_registry.mco_factories

        if factories is not None:
            visible_factories = [f for f in factories if f.ui_visible]

            self.system_state.entity_creator = NewEntityCreator(
                factories=visible_factories,
                dclick_function=add_new_entity
            )

        self.system_state.add_new_entity = partial(
            add_new_entity,
            ui_info=None
        )

        self.system_state.selected_factory_name = 'MCO'

    @selection
    def mco_optimizer_selected(self, mco_view):
        """Called on selecting a MCOView node in the WorkflowTree

        Parameters
        ----------
        mco_view: MCOView
            Selected MCOView in the TreeEditor
        """

        self.system_state.remove_entity = partial(
            self.delete_mco,
            ui_info=None,
            object=mco_view
        )

    @selection
    def mco_parameters_selected(self, parameter_view):
        """Called on selecting the ParameterView node in the WorkflowTree

        Parameters
        ----------
        parameter_view: MCOParameterView
            Unused, automatically passed by TreeEditor on selection
        """
        self.system_state.selected_factory_name = 'MCO Parameters'

    @selection
    def mco_kpis_selected(self, kpi_view):
        """Called on selecting the KPISpecificationView node in the
        WorkflowTree

        Parameters
        ----------
        kpi_view: KPISpecificationView
            Unused, automatically passed by TreeEditor on selection
        """
        self.system_state.selected_factory_name = 'MCO KPIs'

    @selection
    def communicator_selected(self, communicator_view):
        """Called on selecting the Communication node in the WorkflowTree

        Parameters
        ----------
        communicator_view: CommunicatorView
            Selected CommunicationView in the TreeEditor
        """
        add_new_entity = partial(
            self.new_notification_listener,
            object=communicator_view
        )

        factories = self._factory_registry.notification_listener_factories

        if factories is not None:
            visible_factories = [f for f in factories if f.ui_visible]

            self.system_state.entity_creator = NewEntityCreator(
                factories=visible_factories,
                dclick_function=add_new_entity
            )

        self.system_state.add_new_entity = partial(
            add_new_entity,
            ui_info=None
        )

        self.system_state.selected_factory_name = 'Notification Listener'

    @selection
    def notification_listener_selected(self, notification_listener_view):
        """Called on selecting a NotificationListenerView node in the
        WorkflowTree

        Parameters
        ----------
        notification_listener_view: NotificationListenerView
            Selected NotificationListenerView in the TreeEditor
        """

        self.system_state.remove_entity = partial(
            self.delete_notification_listener,
            ui_info=None,
            object=notification_listener_view
        )

    # Methods for new entity creation - The args ui_info and object
    # (the selected view) are passed by the WorkflowTree on selection.
    # Additional (unused) args are passed when calling dclick_function by
    # double-clicking a specific factory in the NewEntityCreator

    @triggers_verify
    def new_data_source(self, object, ui_info=None):
        """Adds a new datasource to the workflow."""
        object.add_data_source(self.system_state.entity_creator.model)
        self.system_state.entity_creator.reset_model()

    @triggers_verify
    def new_layer(self, ui_info, object):
        """Adds a new execution layer to the workflow"""
        object.add_execution_layer(ExecutionLayer())

    @triggers_verify
    def new_mco(self, ui_info, object):
        """Adds a new mco to the workflow"""
        object.set_mco(self.system_state.entity_creator.model)
        self.system_state.entity_creator.reset_model()

    @triggers_verify
    def new_notification_listener(self, ui_info, object):
        """"Adds a new notification listener to the workflow"""
        print(ui_info, object, self.system_state.entity_creator)
        object.add_notification_listener(self.system_state.entity_creator
                                         .model)
        self.system_state.entity_creator.reset_model()

    # Methods for deleting entities from the workflow - object is the
    # modelview being deleted.
    # E.g. for delete_data_source the object is a DataSourceModelView

    @triggers_verify
    def delete_data_source(self, ui_info, object):
        """Delete a data source from the workflow"""
        self.workflow_view.remove_data_source(object.model)

    @triggers_verify
    def delete_layer(self, ui_info, object):
        """Delete a execution layer from the workflow"""
        self.workflow_view.remove_execution_layer(object.model)

    @triggers_verify
    def delete_mco(self, ui_info, object):
        """Delete a mco from the workflow"""
        self.workflow_view.set_mco(None)

    @triggers_verify
    def delete_notification_listener(self, ui_info, object):
        """Delete a notification listener from the workflow"""
        self.workflow_view.remove_notification_listener(object.model)

    def verify_tree(self, errors, start_view=None):
        """ Assign the errors generated by verifier.py to the appropriate
        ModelView. This is done recursively, so parent ModelViews also have
        error messages from their child ModelViews.
        Parameters
        ----------
        errors: List(VerifierError)
            A list of the current workflow errors
        start_view: ModelView
        """
        # A dictionary with the mappings between modelview lists
        mappings = {
            'WorkflowView': ['mco_view', 'process_view',
                             'communicator_view'],
            'MCOModelView': ['mco_options'],
            'MCOParameterView': ['parameter_model_views'],
            'KPISpecificationView': ['kpi_model_views'],
            'ProcessView': ['execution_layer_views'],
            'ExecutionLayerView': ['data_source_views'],
            'CommunicatorView': ['notification_listener_views']
        }

        # Begin from top-level WorkflowModelView if nothing specified already
        if start_view is None:
            start_view = self.workflow_view

        # Get the current modelview's class
        current_view_type = start_view.__class__.__name__

        # A list of error messages to be displayed in the UI
        message_list = []

        # If the current ModelView has any child modelviews
        # retrieve their error messages by calling self.verify_tree
        if current_view_type in mappings:

            for child_view_list_name in mappings[current_view_type]:
                child_view_list = getattr(
                    start_view, child_view_list_name
                )

                for child_view in child_view_list:
                    child_view_errors = self.verify_tree(
                        errors, start_view=child_view
                    )

                    # Add any unique error messages to the list
                    for message in child_view_errors:
                        if message not in message_list:
                            message_list.append(message)

        # A list of messages to pass to the parent ModelView
        send_to_parent = message_list[:]

        start_view.valid = True

        for verifier_error in errors:
            # Check whether this model is the subject of an error. 'warning'
            # or 'information' level messages are only displayed locally and
            # don't invalidate that modelview
            if start_view.model == verifier_error.subject:
                message_list.append(verifier_error.local_error)
                # If there are any 'error' level entries, set the modelview
                # as invalid, and communicate these to the parent modelview.
                if verifier_error.severity == _ERROR:
                    send_to_parent.append(verifier_error.global_error)
                    start_view.valid = False

            # For errors where the subject is an Input/OutputSlotInfo object,
            # check if this is an attribute of the (DataSource) model
            err_subject_type = type(verifier_error.subject)
            if err_subject_type in [InputSlotInfo, OutputSlotInfo]:
                slots = []
                slots.extend(
                    getattr(start_view.model, 'input_slot_info', [])
                )
                slots.extend(
                    getattr(start_view.model, 'output_slot_info', [])
                )
                if verifier_error.subject in slots:
                    if verifier_error.local_error not in message_list:
                        message_list.append(verifier_error.local_error)
                    if verifier_error.severity == _ERROR:
                        send_to_parent.append(verifier_error.global_error)
                        start_view.valid = False

        # Display message so that errors relevant to this ModelView come first
        start_view.error_message = '\n'.join(reversed(message_list))

        # Pass relevant error messages to parent
        return send_to_parent


# HTML Formatting Templates
ERROR_TEMPLATE = """
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
        <style type="text/css">
            .container{{
                width: 100%;
                font-family: sans-serif;
                display: block;
            }}
        </style>
    </head>
    <body>
    <h4>{}</h4>
        {}
    </body>
    </html>
"""

SINGLE_ERROR = r"""<p>{}<\p>"""
