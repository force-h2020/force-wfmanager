from traits.api import (
    Instance, on_trait_change, Unicode, Event, Property, Callable, Button,
    Int
)
from functools import partial

from traits.has_traits import cached_property
from traitsui.api import (
    TreeEditor, TreeNode, UItem, View, Menu, Action, ModelView, UReadonly,
    VGroup, HGroup, InstanceEditor, Group, OKButton, TextEditor, Spring
)

from force_bdss.api import (KPISpecification, Workflow, IFactoryRegistryPlugin,
                            ExecutionLayer, verify_workflow)

from force_wfmanager.left_side_pane.data_source_model_view import \
    DataSourceModelView
from force_wfmanager.left_side_pane.execution_layer_model_view import \
    ExecutionLayerModelView

# Create an empty view and menu for objects that have no data to display:
from force_wfmanager.left_side_pane.kpi_specification_model_view import \
    KPISpecificationModelView
from force_wfmanager.left_side_pane.mco_model_view import MCOModelView
from force_wfmanager.left_side_pane.mco_parameter_model_view import \
    MCOParameterModelView
from force_wfmanager.left_side_pane.new_entity_modal import NewEntityModal
from force_wfmanager.left_side_pane.notification_listener_model_view import \
    NotificationListenerModelView
from force_wfmanager.left_side_pane.workflow_model_view import \
    WorkflowModelView
from force_wfmanager.left_side_pane.view_utils import model_info

ERROR_TEMPLATE = """
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
        <style type="text/css">
            .container{{
                width: 100%;
                display: block;
            }}
        </style>
    </head>
    <body>
    <h4>{title} {error_no}</h4>
        <p>{desc}<\p>
    </body>
    </html>
"""

no_view = View()
no_menu = Menu()

# Actions!

new_kpi_action = Action(name='New KPI...', action='new_kpi')
new_layer_action = Action(name="New Layer...", action='new_layer')

delete_mco_action = Action(name='Delete MCO', action='delete_mco')
delete_notification_listener_action = Action(
    name='Delete Notification Listener',
    action='delete_notification_listener'
)
delete_parameter_action = Action(
    name='Delete Parameter', action='delete_parameter'
)
delete_kpi_action = Action(name="Delete KPI", action='delete_kpi')
delete_layer_action = Action(name='Delete Layer', action='delete_layer')
delete_data_source_action = Action(
    name='Delete Data Source', action='delete_data_source'
)


#: Wrapper to call workflow verification after each method
def triggers_verify(func):
    def wrap(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self.verify_workflow_event = True
    return wrap


class TreeNodeWithStatus(TreeNode):
    """ Custom TreeNode class for workflow elements """

    def get_icon(self, object, is_expanded):
        return 'icons/valid.png' if object.valid else 'icons/invalid.png'

    def when_label_changed(self, object, listener, remove):
        super(TreeNodeWithStatus, self).when_label_changed(
            object, listener, remove
        )
        object.on_trait_change(listener, 'valid')


class ModelEditDialog(ModelView):
    """Editing modelview to show the model in a nice box."""

    traits_view = View(
        Group(
            UItem('model',
                  style='custom',
                  editor=InstanceEditor(),
                  ),
            style="custom",
            label="Configuration Options",
            show_border=True
            ),
        title='Edit Element',
        width=400,
        height=900,
        resizable=True,
        kind="livemodal",
        buttons=[OKButton]
        )


class WorkflowTree(ModelView):
    """ Part of the GUI containing the tree editor displaying the Workflow """

    #: The workflow model
    model = Instance(Workflow, allow_none=False)

    #: The workflow model view
    workflow_mv = Instance(WorkflowModelView, allow_none=False)

    #: Available MCO factories
    _factory_registry = Instance(IFactoryRegistryPlugin)

    #: The currently selected modelview
    selected_mv = Instance(ModelView)

    #: The name of the currently selected factory group. This will be None
    #: if an actual modelview is selected, or (for example) 'MCO' if the
    #: MCO folder is selected
    selected_factory_name = Unicode()

    #: The NewEntityModal for the selected factory group
    current_modal = Instance(NewEntityModal)

    #: A function to add the new instance from current_modal to the Workflow
    add_new_entity = Callable()

    #: A function to remove the selected object from the workflow
    remove_entity = Callable()

    #: The error message relating to selected_mv
    error_list = Property(
        Unicode(), depends_on="selected_mv,selected_mv.error_message,"
                              "selected_mv.label")

    #: The single error currently displayed, plus navigation buttons to view
    #: the other errors
    selected_error = Property(
        Unicode(), depends_on='error_list,selected_error_index')

    selected_error_index = Int(0)

    last_error_btn = Button('>>')
    next_error_btn = Button(' > ')
    prev_error_btn = Button(' < ')
    first_error_btn = Button('<<')

    #: An event which runs a verification check on the current workflow
    verify_workflow_event = Event

    traits_view = View()

    def default_traits_view(self):

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
                    on_select=self.notification_factory_selected
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
                    on_select=self.notification_instance_selected
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
                    on_select=self.mco_factory_selected

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
                    on_select=self.mco_instance_selected
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
                    on_select=self.parameter_factory_selected
                ),
                #: Node representing an MCO parameter
                TreeNodeWithStatus(
                    node_for=[MCOParameterModelView],
                    auto_open=True,
                    children='',
                    name='Parameters',
                    label='label',
                    menu=Menu(delete_parameter_action),
                    on_select=self.parameter_instance_selected
                ),
                TreeNode(
                    node_for=[MCOModelView],
                    auto_open=True,
                    children='kpis_mv',
                    label='=KPIs',
                    name='KPIs',
                    view=no_view,
                    menu=Menu(new_kpi_action),
                    on_select=self.kpi_factory_selected
                ),
                TreeNodeWithStatus(
                    node_for=[KPISpecificationModelView],
                    auto_open=True,
                    children='',
                    label='label',
                    name='KPIs',
                    menu=Menu(delete_kpi_action),
                    on_select=self.kpi_instance_selected
                ),
                #: Node representing the layers
                TreeNode(
                    node_for=[WorkflowModelView],
                    auto_open=True,
                    children='execution_layers_mv',
                    label='=Execution Layers',
                    name='Execution Layers',
                    view=no_view,
                    menu=Menu(new_layer_action),
                    on_select=self.execution_layer_factory_selected
                ),
                TreeNodeWithStatus(
                    node_for=[ExecutionLayerModelView],
                    auto_open=True,
                    children='data_sources_mv',
                    label='label',
                    name='DataSources',
                    view=no_view,
                    menu=Menu(delete_layer_action),
                    on_select=self.datasource_factory_exec_instance_selected
                ),
                TreeNodeWithStatus(
                    node_for=[DataSourceModelView],
                    auto_open=True,
                    children='',
                    label='label',
                    name='DataSources',
                    menu=Menu(delete_data_source_action),
                    on_select=self.datasource_instance_selected
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
                    HGroup(
                        Spring(),
                        UItem('first_error_btn'),
                        UItem('prev_error_btn'),
                        UItem('next_error_btn'),
                        UItem('last_error_btn'),
                        Spring(),
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
        return WorkflowModelView(model=self.model)

    def workflow_selected(self, name):
        self.selected_factory_name = 'Workflow'

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

    def _no_factory_selected(self):
        self.selected_factory_name = 'None'
        self.current_modal = None
        self.add_new_entity = None

    def _no_instance_selected(self):
        self.remove_entity = None

    def datasource_factory_exec_instance_selected(self, ds_factory):
        self.add_new_entity = partial(self.new_data_source, None, ds_factory)
        modal = NewEntityModal(
            factories=self._factory_registry.data_source_factories,
            dclick_function=partial(self.new_data_source, None, ds_factory)
        )
        self.current_modal = modal
        self.selected_factory_name = 'DataSource'
        self.remove_entity = partial(self.delete_layer, None, ds_factory)

    def execution_layer_factory_selected(self, exec_factory):
        self.add_new_entity = partial(self.new_layer, None, exec_factory)
        self.current_modal = None
        self.selected_factory_name = 'ExecutionLayer'
        self._no_instance_selected()

    def kpi_factory_selected(self, kpi_factory):
        self.add_new_entity = partial(self.new_kpi, None, kpi_factory)
        self.current_modal = None
        self.selected_factory_name = 'KPI'
        self._no_instance_selected()

    def mco_factory_selected(self, mco_factory):
        self.add_new_entity = partial(self.new_mco, None, mco_factory)
        modal = NewEntityModal(
            factories=self._factory_registry.mco_factories,
            dclick_function=partial(self.new_mco, None, mco_factory)
        )
        self.current_modal = modal
        self.selected_factory_name = 'MCO'
        self._no_instance_selected()

    def notification_factory_selected(self, notif_factory):
        visible_factories = [
            f for f in self._factory_registry.notification_listener_factories
            if f.ui_visible
        ]

        self.add_new_entity = partial(self.new_notification_listener,
                                      None, notif_factory)
        modal = NewEntityModal(
            factories=visible_factories,
            dclick_function=partial(self.new_notification_listener,
                                    None, notif_factory)
        )
        self.current_modal = modal
        self.selected_factory_name = 'NotificationListener'
        self._no_instance_selected()

    def parameter_factory_selected(self, param_factory):
        parameter_factories = []
        self.add_new_entity = partial(self.new_parameter, None,
                                      param_factory)
        if self.model.mco is not None:
            parameter_factories = self.model.mco.factory.parameter_factories

        modal = NewEntityModal(
            factories=parameter_factories,
            dclick_function=partial(self.new_parameter, None,
                                    param_factory)
        )
        self.current_modal = modal
        self.selected_factory_name = 'Parameter'
        self._no_instance_selected()

    def mco_instance_selected(self, mco_instance):
        self.remove_entity = partial(self.delete_mco, None,
                                     mco_instance)
        self._no_factory_selected()

    def notification_instance_selected(self, notification_instance):
        self.remove_entity = partial(self.delete_notification_listener,
                                     None, notification_instance)
        self._no_factory_selected()

    def kpi_instance_selected(self, kpi_instance):
        self.remove_entity = partial(self.delete_kpi, None, kpi_instance)
        self._no_factory_selected()

    def parameter_instance_selected(self, parameter_instance):
        self.remove_entity = partial(self.delete_parameter, None,
                                     parameter_instance)
        self._no_factory_selected()

    def datasource_instance_selected(self, datasource_instance):
        self.remove_entity = partial(self.delete_data_source, None,
                                     datasource_instance)
        self._no_factory_selected()

    #: Functions for new entity creation - The args ui_info and object are
    #: passed by the WorkflowTree on selection. The additional factory arg
    #: is passed on double-clicking a specific factory in the ModalDialog

    @triggers_verify
    def new_data_source(self, ui_info, object, factory=None):
        """Adds a new datasource to the workflow."""
        object.add_data_source(self.current_modal.model)
        self.current_modal.reset_model()

    @triggers_verify
    def new_kpi(self, ui_info, object):
        object.add_kpi(KPISpecification())

    @triggers_verify
    def new_layer(self, ui_info, object):
        object.add_execution_layer(ExecutionLayer())

    @triggers_verify
    def new_mco(self, ui_info, object, factory=None):
        object.set_mco(self.current_modal.model)
        self.current_modal.reset_model()

    @triggers_verify
    def new_notification_listener(self, ui_info, object, factory=None):
        object.add_notification_listener(self.current_modal.model)
        self.current_modal.reset_model()

    @triggers_verify
    def new_parameter(self, ui_info, object, factory=None):
        object.add_parameter(self.current_modal.model)
        self.current_modal.reset_model()

    # Delete entities - object is the modelview being deleted.
    # E.g. for delete_data_source the object is a DataSourceModelView

    @triggers_verify
    def delete_data_source(self, ui_info, object):
        self.workflow_mv.remove_data_source(object.model)

    @triggers_verify
    def delete_kpi(self, ui_info, object):
        if len(self.workflow_mv.mco_mv) > 0:
            mco_mv = self.workflow_mv.mco_mv[0]
            mco_mv.remove_kpi(object.model)

    @triggers_verify
    def delete_layer(self, ui_info, object):
        self.workflow_mv.remove_execution_layer(object.model)

    @triggers_verify
    def delete_mco(self, ui_info, object):
        self.workflow_mv.set_mco(None)

    @triggers_verify
    def delete_notification_listener(self, ui_info, object):
        self.workflow_mv.remove_notification_listener(object.model)

    @triggers_verify
    def delete_parameter(self, ui_info, object):
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

        # A (currently hardcoded) dictionary with the mappings between
        # modelview lists
        parent_child = {'WorkflowModelView': ['mco_mv',
                                              'notification_listeners_mv',
                                              'execution_layers_mv'],
                        'MCOModelView': ['mco_parameters_mv', 'kpis_mv'],
                        'ExecutionLayerModelView': ['data_sources_mv']}

        # Communicate the verification errors to each level of the
        # workflow tree
        self.verify_tree(parent_child, errors)

    def verify_tree(self, mappings, errors, current_modelview=None):
        """ Assign the errors generated by verifier.py to the appropriate
        ModelView. Parent ModelViews also have error messages from
        their child ModelViews"""

        # Begin from top-level WorkflowModelView if nothing specified already
        if current_modelview is None:
            current_modelview = self.workflow_mv

        # Get the current modelview's class
        current_modelview_type = current_modelview.__class__.__name__

        # A list of error messages
        message_list = []

        # If the current ModelView has any child modelviews..
        if current_modelview_type in mappings:
            # ..retrieve their error messages by calling self.verify_tree
            for child_modelview_list_name in mappings[current_modelview_type]:

                child_modelview_list = getattr(current_modelview,
                                               child_modelview_list_name)

                for child_modelview in child_modelview_list:
                    child_modelview_errors = self.verify_tree(mappings, errors,
                                                              child_modelview)

                    # Add any unique error messages to the list
                    for message in child_modelview_errors:
                        if message not in message_list:
                            message_list.append(message)

        # A list of messages to pass to the parent ModelView
        send_to_parent = message_list[:]

        for verifier_error in errors:
            if current_modelview.model == verifier_error.subject:
                # Add the local error messages to the list
                message_list.append(verifier_error.local_error)
                # If there are any errors to be communicated up the tree,
                # add them to send_to_parent
                if verifier_error.global_error != '':
                    send_to_parent.append(verifier_error.global_error)

        if len(message_list) != 0:
            current_modelview.valid = False
        else:
            current_modelview.valid = True

        # Display message so that errors relevant to this ModelView come first
        current_modelview.error_message = '\n'.join(reversed(message_list))

        # Pass relevant error messages to parent
        return send_to_parent

    def modelview_editable(self, modelview):
        """Checks if the model associated to a ModelView instance
        has a non-empty, editable view """

        return model_info(modelview.model) != []

    @on_trait_change('next_error_btn')
    def next_error(self):
        self.selected_error_index = (self.selected_error_index + 1) % len(
            self.error_list)

    @on_trait_change('prev_error_btn')
    def prev_error(self):
        self.selected_error_index = (self.selected_error_index - 1) % len(
            self.error_list)

    @on_trait_change('first_error_btn')
    def first_error(self):
        self.selected_error_index = 0

    @on_trait_change('last_error_btn')
    def last_error(self):
        self.selected_error_index = len(self.error_list) - 1

    @cached_property
    def _get_error_list(self):

        self.selected_error_index = 0

        if self.selected_mv is None or self.selected_mv.error_message == '':
            return []
        else:
            error_list = self.selected_mv.error_message.split('\n')
            return error_list

    def _get_selected_error(self):

        if self.selected_mv is None:
            return ERROR_TEMPLATE.format(title='No Item Selected', error_no="",
                                         desc="")
        elif len(self.error_list) == 0:
            return ERROR_TEMPLATE.format(
                title='No Errors in {}'.format(self.selected_mv.label),
                error_no="", desc="")
        else:
            return ERROR_TEMPLATE.format(
                title='Error in {}'.format(self.selected_mv.label),
                error_no='({}/{})'.format(self.selected_error_index + 1,
                                          len(self.error_list)),
                desc=self.error_list[self.selected_error_index])
