from functools import partial, wraps

from traits.api import (
    Callable, Event, Instance, Property, Unicode, on_trait_change
)
from traitsui.api import (
    Action, Group, Menu, ModelView, TextEditor,
    TreeEditor, TreeNode, UItem, UReadonly, View, VGroup
)

from force_bdss.api import (
    ExecutionLayer, IFactoryRegistry, InputSlotInfo, KPISpecification,
    OutputSlotInfo, Workflow, verify_workflow
)
from force_wfmanager.ui.setup.execution_layers.data_source_model_view \
    import DataSourceModelView
from force_wfmanager.ui.setup.execution_layers.execution_layer_model_view \
    import ExecutionLayerModelView

from force_wfmanager.ui.setup.mco.kpi_specification_model_view import (
    KPISpecificationModelView
)
from force_wfmanager.ui.setup.mco.mco_model_view import MCOModelView
from force_wfmanager.ui.setup.mco.mco_parameter_model_view import (
    MCOParameterModelView
)
from force_wfmanager.ui.setup.new_entity_creator import NewEntityCreator
from force_wfmanager.ui.setup.notification_listeners.\
    notification_listener_model_view import NotificationListenerModelView
from force_wfmanager.ui.setup.workflow_model_view import (
    WorkflowModelView
)
from force_wfmanager.ui.ui_utils import model_info

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
call_modelview_editable = 'handler.modelview_editable(object)'

# MCO Actions
new_mco_action = Action(name='New MCO...', action='new_mco')
delete_mco_action = Action(name='Delete', action='delete_mco')
edit_mco_action = Action(name='Edit...', action='edit_mco',
                         enabled_when=call_modelview_editable)

# Notification Listener Actions
new_notification_listener_action = Action(
    name='New Notification Listener...',
    action='new_notification_listener'
)
delete_notification_listener_action = Action(
    name='Delete',
    action='delete_notification_listener'
)
edit_notification_listener_action = Action(
    name='Edit...',
    action='edit_notification_listener',
    enabled_when=call_modelview_editable
)

# Parameter Actions
new_parameter_action = Action(name='New Parameter...', action='new_parameter')
edit_parameter_action = Action(
    name='Edit...', action='edit_parameter',
    enabled_when=call_modelview_editable
)
delete_parameter_action = Action(name='Delete', action='delete_parameter')

# KPI Actions
new_kpi_action = Action(name='New KPI...', action='new_kpi')
delete_kpi_action = Action(name="Delete", action='delete_kpi')

# Execution Layer Actions
new_layer_action = Action(name="New Layer...", action='new_layer')
delete_layer_action = Action(name='Delete', action='delete_layer')

# DataSource Actions
new_data_source_action = Action(
    name='New DataSource...',
    action='new_data_source'
)
delete_data_source_action = Action(name='Delete', action='delete_data_source')
edit_data_source_action = Action(
    name='Edit...', action='edit_data_source',
    enabled_when=call_modelview_editable
)


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
        self.selected_factory_name = 'None'
        self.entity_creator = None
        self.add_new_entity = None
        self.remove_entity = None
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
        object: ModelView
            The ModelView assigned to this TreeNode
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
        object: ModelView
            The ModelView assigned to this TreeNode
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
    _factory_registry = Instance(IFactoryRegistry)

    # ------------------
    # Regular Attributes
    # ------------------

    #: A View containing the UI elements for this class
    traits_view = View()

    #: The ModelView for the BDSS Workflow
    workflow_mv = Instance(WorkflowModelView, allow_none=False)

    #: The ModelView currently selected in the WorkflowTree. Updated
    #: automatically when a new ModelView is selected by the user
    selected_mv = Instance(ModelView)

    # ------------------
    # Derived Attributes
    # ------------------

    #: The name of the currently selected factory group. This will be None
    #: if a non-factory or nothing is selected, or (for example) "MCO" if the
    #: MCO folder is selected.
    #: Listens to: :func:`~selected_mv`
    selected_factory_name = Unicode()

    #: Creates new instances of DataSource, MCO, Notification Listener or
    #: MCO Parameters - depending on the plugins currently installed.
    #: Listens to: :func:`~selected_mv`
    entity_creator = Instance(NewEntityCreator)

    #: A method which adds the new instance from entity_creator to the
    #: appropriate place in the Workflow.
    #: Listens to: :func:`~selected_mv`
    add_new_entity = Callable()

    #: A method which removes the currently selected instance from the
    #: Workflow.
    #: Listens to: :func:`~selected_mv`
    remove_entity = Callable()

    #: An event which runs a verification check on the current workflow when
    #: triggered.
    #: Listens to: :func:`~workflow_mv.verify_workflow_event`
    verify_workflow_event = Event

    # ----------
    # Properties
    # ----------

    #: The error message currently displayed in the UI.
    selected_error = Property(
        Unicode(),
        depends_on="selected_mv,selected_mv.error_message,selected_mv.label"
    )

    def default_traits_view(self):
        """The layout of the View for the WorkflowTree"""
        tree_editor = TreeEditor(
            nodes=[
                # Root node "Workflow"
                TreeNodeWithStatus(
                    node_for=[WorkflowModelView],
                    auto_open=True,
                    children='',
                    name='Workflow',
                    label='=Workflow',
                    view=no_view,
                    menu=no_menu,
                    on_select=self.workflow_selected
                ),

                #: Node representing the Execution layers
                TreeNode(
                    node_for=[WorkflowModelView],
                    auto_open=True,
                    children='execution_layers_mv',
                    label='=Execution Layers',
                    name='Execution Layers',
                    view=no_view,
                    menu=Menu(new_layer_action),
                    on_select=partial(
                        self.factory,
                        None,
                        self.new_layer,
                        'Execution Layer'
                    )
                ),
                TreeNodeWithStatus(
                    node_for=[ExecutionLayerModelView],
                    auto_open=True,
                    children='data_sources_mv',
                    label='label',
                    name='DataSources',
                    view=no_view,
                    menu=Menu(delete_layer_action),
                    on_select=partial(
                        self.factory_instance,
                        self._factory_registry.data_source_factories,
                        self.new_data_source,
                        'Data Source',
                        self.delete_layer
                    )
                ),
                TreeNodeWithStatus(
                    node_for=[DataSourceModelView],
                    auto_open=True,
                    children='',
                    label='label',
                    name='DataSources',
                    menu=Menu(delete_data_source_action),
                    on_select=partial(self.instance, self.delete_data_source)
                ),
                # Folder node "MCO" containing the MCO
                TreeNode(
                    node_for=[WorkflowModelView],
                    auto_open=True,
                    children='mco_mv',
                    label='=MCO',
                    name='MCO',
                    view=no_view,
                    menu=no_menu,
                    on_select=partial(
                        self.factory,
                        self._factory_registry.mco_factories,
                        self.new_mco,
                        'MCO'
                    )
                ),
                # Node representing the MCO
                TreeNodeWithStatus(
                    node_for=[MCOModelView],
                    auto_open=True,
                    children='',
                    label='label',
                    name='MCO',
                    view=no_view,
                    menu=Menu(delete_mco_action),
                    on_select=partial(self.instance, self.delete_mco)
                ),
                # Folder node "Parameters" containing the MCO parameters
                TreeNode(
                    node_for=[MCOModelView],
                    auto_open=True,
                    children='mco_parameters_mv',
                    label='=Parameters',
                    name='Parameters',
                    view=no_view,
                    menu=no_menu,
                    on_select=partial(
                        self.factory,
                        self.parameter_factories,
                        self.new_parameter,
                        'Parameter'
                    )
                ),
                #: Node representing an MCO parameter
                TreeNodeWithStatus(
                    node_for=[MCOParameterModelView],
                    auto_open=True,
                    children='',
                    name='Parameters',
                    label='label',
                    menu=Menu(delete_parameter_action),
                    on_select=partial(self.instance, self.delete_parameter)
                ),
                TreeNode(
                    node_for=[MCOModelView],
                    auto_open=True,
                    children='kpis_mv',
                    label='=KPIs',
                    name='KPIs',
                    view=no_view,
                    menu=Menu(new_kpi_action),
                    on_select=partial(
                        self.factory,
                        None,
                        self.new_kpi,
                        'KPI'
                    )
                ),
                TreeNodeWithStatus(
                    node_for=[KPISpecificationModelView],
                    auto_open=True,
                    children='',
                    label='label',
                    name='KPIs',
                    view=no_view,
                    menu=Menu(delete_kpi_action),
                    on_select=partial(self.instance, self.delete_kpi)
                ),
                # Folder node "Notification" containing the
                # Notification listeners
                TreeNode(
                    node_for=[WorkflowModelView],
                    auto_open=True,
                    children='notification_listeners_mv',
                    name='Notification Listeners',
                    label='=Notification Listeners',
                    view=no_view,
                    menu=no_menu,
                    on_select=partial(
                        self.factory,
                        self._factory_registry.notification_listener_factories,
                        self.new_notification_listener,
                        'Notification Listener',
                    )
                ),
                # Node representing the Notification Listener
                TreeNodeWithStatus(
                    node_for=[NotificationListenerModelView],
                    auto_open=True,
                    children='',
                    label='label',
                    name='Notification Listeners',
                    view=no_view,
                    menu=Menu(delete_notification_listener_action),
                    on_select=partial(
                        self.instance,
                        self.delete_notification_listener
                    )
                ),
            ],
            orientation="horizontal",
            editable=False,
            selected="selected_mv",
        )

        view = View(
            Group(
                VGroup(
                    UItem(name='workflow_mv',
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

    def _workflow_mv_default(self):
        """A default WorkflowModelView"""
        return WorkflowModelView(model=self.model)

    @on_trait_change('model')
    def update_model_view(self):
        """Update the workflow modelview's model and verify, on either loading
        a new workflow, or an internal change to the workflow.
        """
        self.workflow_mv = WorkflowModelView(model=self.model)
        self.verify_workflow_event = True

    # Item Selection Actions - create an appropriate NewEntityModal,
    # set add_new_entity to be for the right object type and provide a way to
    # add things by double clicking

    @selection
    def factory_instance(self, from_registry, create_fn, factory_group_name,
                         delete_fn, modelview):
        """Called on selecting a node in the TreeEditor which represents an
        instance in the workflow, but also represents a factory for creating
        new instances.
        For example an ExecutionLayerModelView represents an ExecutionLayer
        object, but is also a factory for new DataSources.

        Parameters
        ----------
        from_registry: List(BaseFactory) or Callable
            A list of factories available for this node
        create_fn: function
            A function which adds a newly created instance to the Workflow
        factory_group_name: String
            A name showing which group (MCO, Datasource etc.) the factory
            belongs to
        delete_fn: function
            A function which removes the object from the workflow
        modelview: ModelView
            The modelview of the currently selected node
        """

        self.factory.__wrapped__(self, from_registry, create_fn,
                                 factory_group_name, modelview)
        self.instance.__wrapped__(self, delete_fn, modelview)

    @selection
    def factory(self, from_registry, create_fn, factory_group_name, modelview):
        """Called on selecting a node in the TreeEditor which represents a
        factory.

        Parameters
        ----------
        from_registry: List(BaseFactory) or Callable
            A list of factories available for this node
        create_fn: function
            A function which adds a newly created instance to the Workflow
        factory_group_name: String
            A name showing which group (MCO, Datasource etc.) the factory
            belongs to
        modelview: ModelView
            The modelview of the currently selected node
        """
        self.add_new_entity = partial(create_fn, None, modelview)
        if from_registry is not None:
            try:
                # For a non-constant factory list (parameter factories)
                visible_factories = [
                    f for f in from_registry() if f.ui_visible
                ]
            except TypeError:
                visible_factories = [f for f in from_registry if f.ui_visible]
            entity_creator = NewEntityCreator(
                factories=visible_factories,
                dclick_function=self.add_new_entity
            )
            self.entity_creator = entity_creator
        else:
            self.entity_creator = None
        self.selected_factory_name = factory_group_name

    @selection
    def instance(self, delete_fn, modelview):
        """Called on selecting a a node in the TreeEditor which represents an
        object in the workflow

        Parameters
        ----------
        delete_fn: function
            A function which removes the object from the workflow
        modelview: ModelView
            The modelview of the currently selected node
        """

        self.remove_entity = partial(delete_fn, None, modelview)

    @selection
    def workflow_selected(self, workflow_mv):
        """Called on selecting the top node in the WorkflowTree

        Parameters
        ----------
        workflow_mv: WorkflowModelView
            Unused, automatically passed by TreeEditor on selection
        """
        self.selected_factory_name = 'Workflow'

    def parameter_factories(self):
        """Returns the list of parameter factories for the current MCO."""
        if self.model.mco is not None:
            parameter_factories = (
                self.model.mco.factory.parameter_factories
            )
            return parameter_factories
        return None

    # Methods for new entity creation - The args ui_info and object
    # (the selected modelview) are passed by the WorkflowTree on selection.
    # Additional (unused) args are passed when calling dclick_function by
    # double-clicking a specific factory in the NewEntityCreator

    @triggers_verify
    def new_data_source(self, ui_info, object, *args):
        """Adds a new datasource to the workflow."""
        object.add_data_source(self.entity_creator.model)
        self.entity_creator.reset_model()

    @triggers_verify
    def new_kpi(self, ui_info, object):
        """Adds a new KPI to the workflow"""
        object.add_kpi(KPISpecification())

    @triggers_verify
    def new_layer(self, ui_info, object):
        """Adds a new execution layer to the workflow"""
        object.add_execution_layer(ExecutionLayer())

    @triggers_verify
    def new_mco(self, ui_info, object, *args):
        """Adds a new mco to the workflow"""
        object.set_mco(self.entity_creator.model)
        self.entity_creator.reset_model()

    @triggers_verify
    def new_notification_listener(self, ui_info, object, *args):
        """"Adds a new notification listener to the workflow"""
        object.add_notification_listener(self.entity_creator.model)
        self.entity_creator.reset_model()

    @triggers_verify
    def new_parameter(self, ui_info, object, *args):
        """Adds a new mco parameter to the workflow"""
        object.add_parameter(self.entity_creator.model)
        self.entity_creator.reset_model()

    # Methods for deleting entities from the workflow - object is the
    # modelview being deleted.
    # E.g. for delete_data_source the object is a DataSourceModelView

    @triggers_verify
    def delete_data_source(self, ui_info, object):
        """Delete a data source from the workflow"""
        self.workflow_mv.remove_data_source(object.model)

    @triggers_verify
    def delete_kpi(self, ui_info, object):
        """Delete a kpi from the workflow"""
        if len(self.workflow_mv.mco_mv) > 0:
            mco_mv = self.workflow_mv.mco_mv[0]
            mco_mv.remove_kpi(object.model)

    @triggers_verify
    def delete_layer(self, ui_info, object):
        """Delete a execution layer from the workflow"""
        self.workflow_mv.remove_execution_layer(object.model)

    @triggers_verify
    def delete_mco(self, ui_info, object):
        """Delete a mco from the workflow"""
        self.workflow_mv.set_mco(None)

    @triggers_verify
    def delete_notification_listener(self, ui_info, object):
        """Delete a notification listener from the workflow"""
        self.workflow_mv.remove_notification_listener(object.model)

    @triggers_verify
    def delete_parameter(self, ui_info, object):
        """Delete a mco parameter from the workflow"""
        if len(self.workflow_mv.mco_mv) > 0:
            mco_mv = self.workflow_mv.mco_mv[0]
            mco_mv.remove_parameter(object.model)

    # Workflow Verification

    @on_trait_change("workflow_mv.verify_workflow_event")
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

    def verify_tree(self, errors, start_modelview=None):
        """ Assign the errors generated by verifier.py to the appropriate
        ModelView. This is done recursively, so parent ModelViews also have
        error messages from their child ModelViews.

        Parameters
        ----------
        errors: List(VerifierError)
            A list of the current workflow errors
        start_modelview: ModelView
        """
        # A dictionary with the mappings between modelview lists
        mappings = {
            'WorkflowModelView':
                ['mco_mv', 'notification_listeners_mv', 'execution_layers_mv'],
            'MCOModelView': ['mco_parameters_mv', 'kpis_mv'],
            'ExecutionLayerModelView': ['data_sources_mv']
        }

        # Begin from top-level WorkflowModelView if nothing specified already
        if start_modelview is None:
            start_modelview = self.workflow_mv

        # Get the current modelview's class
        current_modelview_type = start_modelview.__class__.__name__

        # A list of error messages to be displayed in the UI
        message_list = []

        # If the current ModelView has any child modelviews
        # retrieve their error messages by calling self.verify_tree
        if current_modelview_type in mappings:

            for child_modelview_list_name in mappings[current_modelview_type]:
                child_modelview_list = getattr(
                    start_modelview, child_modelview_list_name
                )

                for child_modelview in child_modelview_list:
                    child_modelview_errors = self.verify_tree(
                        errors, start_modelview=child_modelview
                    )

                    # Add any unique error messages to the list
                    for message in child_modelview_errors:
                        if message not in message_list:
                            message_list.append(message)

        # A list of messages to pass to the parent ModelView
        send_to_parent = message_list[:]

        start_modelview.valid = True

        for verifier_error in errors:
            # Check whether this model is the subject of an error. 'warning'
            # or 'information' level messages are only displayed locally and
            # don't invalidate that modelview
            if start_modelview.model == verifier_error.subject:
                message_list.append(verifier_error.local_error)
                # If there are any 'error' level entries, set the modelview
                # as invalid, and communicate these to the parent modelview.
                if verifier_error.severity == _ERROR:
                    send_to_parent.append(verifier_error.global_error)
                    start_modelview.valid = False

            # For errors where the subject is an Input/OutputSlotInfo object,
            # check if this is an attribute of the (DataSource) model
            err_subject_type = type(verifier_error.subject)
            if err_subject_type in [InputSlotInfo, OutputSlotInfo]:
                slots = []
                slots.extend(
                    getattr(start_modelview.model, 'input_slot_info', [])
                )
                slots.extend(
                    getattr(start_modelview.model, 'output_slot_info', [])
                )
                if verifier_error.subject in slots:
                    if verifier_error.local_error not in message_list:
                        message_list.append(verifier_error.local_error)
                    if verifier_error.severity == _ERROR:
                        send_to_parent.append(verifier_error.global_error)
                        start_modelview.valid = False

        # Display message so that errors relevant to this ModelView come first
        start_modelview.error_message = '\n'.join(reversed(message_list))

        # Pass relevant error messages to parent
        return send_to_parent

    def modelview_editable(self, modelview):
        """Checks if the model associated to a ModelView instance
        has a non-empty, editable view

        Parameters
        ----------
        modelview: ModelView
            A ModelView
        """

        return model_info(modelview.model) != []

    def _get_selected_error(self):
        """Returns the error messages for the currently selected modelview"""
        if self.selected_mv is None:
            return ERROR_TEMPLATE.format("No Item Selected", "")

        if self.selected_mv.error_message == '':
            mv_label = self.selected_mv.label
            return ERROR_TEMPLATE.format(
                "No errors for {}".format(mv_label), "")
        else:
            mv_label = self.selected_mv.label
            error_list = self.selected_mv.error_message.split('\n')
            body_strings = ''.join([SINGLE_ERROR.format(error)
                                    for error in error_list])
            return ERROR_TEMPLATE.format(
                "Errors for {}:".format(mv_label), body_strings)


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

SINGLE_ERROR = """<p>{}<\p>"""
