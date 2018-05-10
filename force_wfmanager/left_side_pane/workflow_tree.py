from traits.api import (
    Instance,
    on_trait_change)

from traitsui.api import (
    TreeEditor, TreeNode, UItem, View, Menu, Action, ModelView,
    InstanceEditor, Group, OKButton
)

from force_bdss.core.workflow import Workflow
from force_bdss.factory_registry_plugin import IFactoryRegistryPlugin
from force_wfmanager.left_side_pane.data_source_model_view import \
    DataSourceModelView
from force_wfmanager.left_side_pane.execution_layer_model_view import \
    ExecutionLayerModelView

from force_bdss.core.execution_layer import ExecutionLayer

# Create an empty view and menu for objects that have no data to display:
from force_wfmanager.left_side_pane.mco_model_view import MCOModelView
from force_wfmanager.left_side_pane.mco_parameter_model_view import \
    MCOParameterModelView
from force_wfmanager.left_side_pane.new_entity_modal import NewEntityModal
from force_wfmanager.left_side_pane.notification_listener_model_view import \
    NotificationListenerModelView
from force_wfmanager.left_side_pane.workflow_model_view import \
    WorkflowModelView

no_view = View()
no_menu = Menu()

# Actions!
new_mco_action = Action(name='New MCO...', action='new_mco')
delete_mco_action = Action(name='Delete', action='delete_mco')
edit_mco_action = Action(name='Edit...', action='edit_mco')

new_notification_listener_action = Action(
    name='New Notification Listener...',
    action='new_notification_listener')
delete_notification_listener_action = Action(
    name='Delete',
    action='delete_notification_listener')
edit_notification_listener_action = Action(
    name='Edit...',
    action='edit_notification_listener')
new_parameter_action = Action(name='New Parameter...', action='new_parameter')
edit_parameter_action = Action(name='Edit...', action='edit_parameter')
delete_parameter_action = Action(name='Delete', action='delete_parameter')
new_layer_action = Action(name="New Layer...", action='new_layer')
delete_layer_action = Action(name='Delete', action='delete_layer')
new_data_source_action = Action(name='New DataSource...',
                                action='new_data_source')
delete_data_source_action = Action(name='Delete', action='delete_data_source')
edit_data_source_action = Action(name='Edit...', action='edit_data_source')


class TreeNodeWithStatus(TreeNode):
    """ Custom TreeNode class for workflow elements """
    def get_icon(self, object, is_expanded):
        return 'icons/valid.png' if object.valid else 'icons/invalid.png'


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
             menu=Menu(new_data_source_action, delete_layer_action)
         ),
        TreeNodeWithStatus(
             node_for=[DataSourceModelView],
             auto_open=True,
             children='',
             label='label',
             menu=Menu(edit_data_source_action, delete_data_source_action),
         ),
    ],
    orientation="vertical"
)


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
    #: The workflow model
    model = Instance(Workflow, allow_none=False)

    #: The workflow model view
    workflow_mv = Instance(WorkflowModelView, allow_none=False)

    #: Available MCO factories
    _factory_registry = Instance(IFactoryRegistryPlugin)

    traits_view = View(
        UItem(name='workflow_mv',
              editor=tree_editor,
              show_label=False),
        width=800,
        height=600,
        resizable=True)

    def __init__(self, model, factory_registry, *args, **kwargs):
        super(WorkflowTree, self).__init__(*args, **kwargs)
        self.model = model
        self._factory_registry = factory_registry

    def _workflow_mv_default(self):
        return WorkflowModelView(model=self.model)

    @on_trait_change('model')
    def update_model_view(self):
        self.workflow_mv.model = self.model

    def new_mco(self, ui_info, object):
        """ Opens a dialog for creating a MCO """
        workflow_mv = self.workflow_mv

        modal = NewEntityModal(factories=self._factory_registry.mco_factories)
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            workflow_mv.set_mco(result)

    def edit_mco(self, ui_info, object):
        ModelEditDialog(model=object.model).edit_traits()

    def delete_mco(self, ui_info, object):
        """Deletes the MCO"""
        self.workflow_mv.set_mco(None)

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

    def edit_notification_listener(self, ui_info, object):
        ModelEditDialog(model=object.model).edit_traits()

    def delete_notification_listener(self, ui_info, object):
        """Deletes the notification listener"""
        self.workflow_mv.remove_notification_listener(object.model)

    def new_parameter(self, ui_info, object):
        parameter_factories = []
        if self.model.mco is not None:
            parameter_factories = self.model.mco.factory.parameter_factories()

        modal = NewEntityModal(factories=parameter_factories)
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            object.add_parameter(result)

    def edit_parameter(self, ui_info, object):
        ModelEditDialog(model=object.model).edit_traits()

    def delete_parameter(self, ui_info, object):
        if len(self.workflow_mv.mco_mv) > 0:
            mco_mv = self.workflow_mv.mco_mv[0]
            mco_mv.remove_parameter(object.model)

    def new_data_source(self, ui_info, object):
        """ Opens a dialog for creating a Data Source """
        modal = NewEntityModal(
            factories=self._factory_registry.data_source_factories
        )
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            object.add_data_source(result)

    def delete_data_source(self, ui_info, object):
        self.workflow_mv.remove_data_source(object.model)

    def edit_data_source(self, ui_info, object):
        # This is a live dialog, workaround for issue #58
        ModelEditDialog(model=object.model).edit_traits()

    def new_layer(self, ui_info, object):
        self.workflow_mv.add_execution_layer(ExecutionLayer())

    def delete_layer(self, ui_info, object):
        """ Delete an element from the workflow """
        self.workflow_mv.remove_execution_layer(object.model)
