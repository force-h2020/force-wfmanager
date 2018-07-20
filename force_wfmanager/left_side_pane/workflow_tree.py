from traits.api import Instance, on_trait_change, Str, Event, Property

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

call_modelview_editable = 'handler.modelview_editable(object)'

# For reference, in the enabled_when expression namespace, handler is
# the WorkflowTree instance, object is the modelview for a particular node -
# in this case an MCOModelView

new_mco_action = Action(name='New MCO...', action='new_mco')
delete_mco_action = Action(name='Delete', action='delete_mco')
edit_mco_action = Action(name='Edit...', action='edit_mco',
                         enabled_when=call_modelview_editable)

new_notification_listener_action = Action(
    name='New Notification Listener...',
    action='new_notification_listener')
delete_notification_listener_action = Action(
    name='Delete',
    action='delete_notification_listener')
edit_notification_listener_action = Action(
    name='Edit...',
    action='edit_notification_listener',
    enabled_when=call_modelview_editable)
new_parameter_action = Action(name='New Parameter...', action='new_parameter')
edit_parameter_action = Action(name='Edit...', action='edit_parameter',
                               enabled_when=call_modelview_editable)
delete_parameter_action = Action(name='Delete', action='delete_parameter')
new_kpi_action = Action(name='New KPI...', action='new_kpi')
delete_kpi_action = Action(name="Delete", action='delete_kpi')
new_layer_action = Action(name="New Layer...", action='new_layer')
delete_layer_action = Action(name='Delete', action='delete_layer')
new_data_source_action = Action(name='New DataSource...',
                                action='new_data_source')
delete_data_source_action = Action(name='Delete', action='delete_data_source')
edit_data_source_action = Action(name='Edit...', action='edit_data_source',
                                 enabled_when=call_modelview_editable)


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
        width=800,
        height=600,
        resizable=True,
        kind="livemodal",
        buttons=[OKButton]
        )


class WorkflowTree(ModelView):
    """ Part of the GUI containing the tree editor displaying the Workflow """

    tree_editor = TreeEditor(
        nodes=[
            # Root node "Workflow"
            TreeNodeWithStatus(
                node_for=[WorkflowModelView],
                auto_open=True,
                children='',
                label='=Workflow',
                view=no_view,
                menu=no_menu,
            ),
            # Folder node "Notification" containing the Notification listeners
            TreeNode(
                node_for=[WorkflowModelView],
                auto_open=True,
                children='notification_listeners_mv',
                label='=Notification Listeners',
                view=no_view,
                menu=Menu(new_notification_listener_action),
            ),
            # Node representing the Notification Listener
            TreeNodeWithStatus(
                node_for=[NotificationListenerModelView],
                auto_open=True,
                children='',
                label='label',
                view=no_view,
                menu=Menu(edit_notification_listener_action,
                          delete_notification_listener_action),
            ),
            # Folder node "MCO" containing the MCO
            TreeNode(
                node_for=[WorkflowModelView],
                auto_open=True,
                children='mco_mv',
                label='=MCO',
                view=no_view,
                menu=Menu(new_mco_action),
            ),
            # Node representing the MCO
            TreeNodeWithStatus(
                node_for=[MCOModelView],
                auto_open=True,
                children='',
                label='label',
                view=no_view,
                menu=Menu(edit_mco_action, delete_mco_action),
            ),
            # Folder node "Parameters" containing the MCO parameters
            TreeNode(
                node_for=[MCOModelView],
                auto_open=True,
                children='mco_parameters_mv',
                label='=Parameters',
                view=no_view,
                menu=Menu(new_parameter_action),
            ),
            #: Node representing an MCO parameter
            TreeNodeWithStatus(
                node_for=[MCOParameterModelView],
                auto_open=True,
                children='',
                label='label',
                menu=Menu(edit_parameter_action, delete_parameter_action),
            ),
            TreeNode(
                node_for=[MCOModelView],
                auto_open=True,
                children='kpis_mv',
                label='=KPIs',
                view=no_view,
                menu=Menu(new_kpi_action),
            ),
            TreeNodeWithStatus(
                node_for=[KPISpecificationModelView],
                auto_open=True,
                children='',
                label='label',
                menu=Menu(delete_kpi_action),
            ),
            #: Node representing the layers
            TreeNode(
                node_for=[WorkflowModelView],
                auto_open=True,
                children='execution_layers_mv',
                label='=Execution Layers',
                view=no_view,
                menu=Menu(new_layer_action),
            ),
            TreeNodeWithStatus(
                node_for=[ExecutionLayerModelView],
                auto_open=True,
                children='data_sources_mv',
                label='label',
                view=no_view,
                menu=Menu(new_data_source_action, delete_layer_action),
            ),
            TreeNodeWithStatus(
                node_for=[DataSourceModelView],
                auto_open=True,
                children='',
                label='label',
                menu=Menu(edit_data_source_action, delete_data_source_action),
            ),
        ],
        orientation="vertical",
        selected="selected_mv",
    )

    #: The workflow model
    model = Instance(Workflow, allow_none=False)

    #: The workflow model view
    workflow_mv = Instance(WorkflowModelView, allow_none=False)

    #: Available MCO factories
    _factory_registry = Instance(IFactoryRegistryPlugin)

    #: The currently selected modelview
    selected_mv = Instance(ModelView)

    #: The error message relating to selected_mv
    selected_error = Property(Str, depends_on="selected_mv,"
                                              "selected_mv.error_message,"
                                              "selected_mv.label")

    #: An event which runs a verification check on the current workflow
    verify_workflow_event = Event

    traits_view = View(
        VGroup(
            UItem(name='workflow_mv',
                  editor=tree_editor,
                  show_label=False
                  ),
            UReadonly(
                name='selected_error',
                editor=TextEditor(),
                ),
            ),
        width=800,
        height=600,
        resizable=True
        )

    def __init__(self, model, factory_registry, *args, **kwargs):
        super(WorkflowTree, self).__init__(*args, **kwargs)
        self.model = model
        self._factory_registry = factory_registry

    def _workflow_mv_default(self):
        return WorkflowModelView(model=self.model)

    @on_trait_change('model')
    def update_model_view(self):
        """Update the workflow modelview's model and verify, on either loading
        a new workflow, or an internal change to the workflow"""
        self.workflow_mv = WorkflowModelView(model=self.model)
        self.verify_workflow_event = True

    @triggers_verify
    def new_mco(self, ui_info, object):
        """ Opens a dialog for creating a MCO """
        workflow_mv = self.workflow_mv

        modal = NewEntityModal(factories=self._factory_registry.mco_factories)
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            workflow_mv.set_mco(result)

    @triggers_verify
    def edit_mco(self, ui_info, object):
        ModelEditDialog(model=object.model).edit_traits()

    @triggers_verify
    def delete_mco(self, ui_info, object):
        """Deletes the MCO"""
        self.workflow_mv.set_mco(None)

    @triggers_verify
    def new_notification_listener(self, ui_info, object):
        """ Opens a dialog for creating a notification listener"""
        workflow_mv = self.workflow_mv

        visible_factories = [
            f for f in self._factory_registry.notification_listener_factories
            if f.ui_visible
        ]
        modal = NewEntityModal(
            factories=visible_factories
        )
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            workflow_mv.add_notification_listener(result)

    @triggers_verify
    def edit_notification_listener(self, ui_info, object):
        ModelEditDialog(model=object.model).edit_traits()

    @triggers_verify
    def delete_notification_listener(self, ui_info, object):
        """Deletes the notification listener"""
        self.workflow_mv.remove_notification_listener(object.model)

    @triggers_verify
    def new_parameter(self, ui_info, object):
        parameter_factories = []
        if self.model.mco is not None:
            parameter_factories = self.model.mco.factory.parameter_factories()

        modal = NewEntityModal(factories=parameter_factories)
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            object.add_parameter(result)

    @triggers_verify
    def edit_parameter(self, ui_info, object):
        ModelEditDialog(model=object.model).edit_traits()

    @triggers_verify
    def delete_parameter(self, ui_info, object):
        if len(self.workflow_mv.mco_mv) > 0:
            mco_mv = self.workflow_mv.mco_mv[0]
            mco_mv.remove_parameter(object.model)

    @triggers_verify
    def new_kpi(self, ui_info, object):
        object.add_kpi(KPISpecification())

    @triggers_verify
    def delete_kpi(self, ui_info, object):
        if len(self.workflow_mv.mco_mv) > 0:
            mco_mv = self.workflow_mv.mco_mv[0]
            mco_mv.remove_kpi(object.model)

    @triggers_verify
    def new_data_source(self, ui_info, object):
        """ Opens a dialog for creating a Data Source """
        modal = NewEntityModal(
            factories=self._factory_registry.data_source_factories
        )
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            object.add_data_source(result)

    @triggers_verify
    def delete_data_source(self, ui_info, object):
        self.workflow_mv.remove_data_source(object.model)

    @triggers_verify
    def edit_data_source(self, ui_info, object):
        # This is a live dialog, workaround for issue #58
        ModelEditDialog(model=object.model).edit_traits()

    @triggers_verify
    def new_layer(self, ui_info, object):
        self.workflow_mv.add_execution_layer(ExecutionLayer())

    @triggers_verify
    def delete_layer(self, ui_info, object):
        """ Delete an element from the workflow """
        self.workflow_mv.remove_execution_layer(object.model)

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
