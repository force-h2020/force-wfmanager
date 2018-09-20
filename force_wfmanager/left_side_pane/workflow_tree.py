from traits.api import (
    Instance, on_trait_change, Unicode, Event, Property, Callable
)
from functools import partial

from traitsui.api import (
    TreeEditor, TreeNode, UItem, View, Menu, Action, ModelView, UReadonly,
    VGroup, InstanceEditor, Group, OKButton, TextEditor
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
    selected_error = Property(
        Unicode(), depends_on="selected_mv,selected_mv.error_message,"
                              "selected_mv.label")

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
                    on_select=self.show_workflow_status
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
                    on_select=partial(self.selection,
                                      'Notification Listeners', None)
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
                    on_select=partial(self.selection,
                                      None, 'Notification Listeners')
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
                    on_select=partial(self.selection,
                                      'MCO', None)

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
                    on_select=partial(self.selection,
                                      None, 'MCO')
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
                    on_select=partial(self.selection,
                                      'Parameters', None)
                ),
                #: Node representing an MCO parameter
                TreeNodeWithStatus(
                    node_for=[MCOParameterModelView],
                    auto_open=True,
                    children='',
                    name='Parameters',
                    label='label',
                    menu=Menu(delete_parameter_action),
                    on_select=partial(self.selection,
                                      None, 'Parameters')
                ),
                TreeNode(
                    node_for=[MCOModelView],
                    auto_open=True,
                    children='kpis_mv',
                    label='=KPIs',
                    name='KPIs',
                    view=no_view,
                    menu=Menu(new_kpi_action),
                    on_select=partial(self.selection,
                                      'KPIs', None)
                ),
                TreeNodeWithStatus(
                    node_for=[KPISpecificationModelView],
                    auto_open=True,
                    children='',
                    label='label',
                    name='KPIs',
                    menu=Menu(delete_kpi_action),
                    on_select=partial(self.selection,
                                      None, 'KPIs')
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
                    on_select=partial(self.selection,
                                      'Execution Layers', None)
                ),
                TreeNodeWithStatus(
                    node_for=[ExecutionLayerModelView],
                    auto_open=True,
                    children='data_sources_mv',
                    label='label',
                    name='DataSources',
                    view=no_view,
                    menu=Menu(delete_layer_action),
                    on_select=partial(self.selection,
                                      'DataSources', 'Execution Layers')
                ),
                TreeNodeWithStatus(
                    node_for=[DataSourceModelView],
                    auto_open=True,
                    children='',
                    label='label',
                    name='DataSources',
                    menu=Menu(delete_data_source_action),
                    on_select=partial(self.selection,
                                      None, 'DataSources')
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
        return WorkflowModelView(model=self.model)

    # TODO: Add in workflow status screen
    def show_workflow_status(self, name):
        pass

    @on_trait_change('model')
    def update_model_view(self):
        """Update the workflow modelview's model and verify, on either loading
        a new workflow, or an internal change to the workflow.
        """
        self.workflow_mv = WorkflowModelView(model=self.model)
        self.verify_workflow_event = True

    def selection(self, factory_name, instance_name, object):
        """Assigns the correct add/remove entity functions based on which
        object is selected in the workflow tree"""
        instance_select_function = {
            'Notification Listeners': self.delete_notification_listener,
            'MCO': self.delete_mco, 'KPIs': self.delete_kpi,
            'Execution Layers': self.delete_layer,
            'DataSources': self.delete_data_source,
            'Parameters': self.delete_parameter
        }
        factory_select_function = {
            'Notification Listeners': self.notification_factory_selected,
            'MCO': self.mco_factory_selected,
            'KPIs': self.kpi_factory_selected,
            'Execution Layers': self.execution_layer_factory_selected,
            'DataSources': self.datasource_factory_selected,
            'Parameters': self.parameter_factory_selected
        }
        if instance_name is not None and factory_name is not None:
            self.selected_factory_name = factory_name
            on_select = factory_select_function[factory_name]
            on_select(object)
            self.remove_entity = partial(
                instance_select_function[instance_name], None,
                object)

        elif instance_name is not None:

            self.current_modal = None
            self.selected_factory_name = 'None'
            self.add_new_entity = None
            self.remove_entity = partial(
                instance_select_function[instance_name], None, object
            )
        elif factory_name is not None:

            self.selected_factory_name = factory_name
            on_select = factory_select_function[factory_name]
            on_select(object)

    # Item Selection Actions - create an appropriate NewEntityModal

    def datasource_factory_selected(self, object):
        self.add_new_entity = partial(self.new_data_source, None, object)
        modal = NewEntityModal(
            factories=self._factory_registry.data_source_factories,
            dclick_function=self.add_new_entity
        )
        self.current_modal = modal


    def execution_layer_factory_selected(self, object):
        self.current_modal = None
        self.add_new_entity = partial(self.new_layer, None, object)

    def kpi_factory_selected(self, object):
        self.current_modal = None
        self.add_new_entity = partial(self.new_kpi, None, object)

    def mco_factory_selected(self, object):
        self.add_new_entity = partial(self.new_mco, None, object)
        modal = NewEntityModal(
            factories=self._factory_registry.mco_factories,
            dclick_function=self.add_new_entity
        )
        self.current_modal = modal


    def notification_factory_selected(self, object):

        visible_factories = [
            f for f in self._factory_registry.notification_listener_factories
            if f.ui_visible
        ]
        modal = NewEntityModal(factories=visible_factories,
                               dclick_function=self.add_new_entity)
        self.current_modal = modal
        self.add_new_entity = partial(self.new_notification_listener, None,
                                      object)

    def parameter_factory_selected(self, object):
        parameter_factories = []
        if self.model.mco is not None:
            parameter_factories = self.model.mco.factory.parameter_factories
        modal = NewEntityModal(factories=parameter_factories,
                               dclick_function=self.add_new_entity)
        self.current_modal = modal
        self.add_new_entity = partial(self.new_parameter, None, object)

    # New entity creation - object is containing ModelView.
    # E.g. for new_parameter the object is the MCOModelView

    @triggers_verify
    def new_data_source(self, ui_info, object, factory=None):
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

    def _get_selected_error(self):

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
        <h4>{}</h4>
            {}
        </body>
        </html>
"""
SINGLE_ERROR = """<p>{}<\p>"""
