from traits.api import (Instance, List, Property, on_trait_change)

from traitsui.api import (
    TreeEditor, TreeNode, UItem, View, Menu, Action,
)
from traitsui.handler import ModelView

from force_bdss.api import (
    BaseMCOFactory,
    BaseDataSourceFactory,
    BaseMCOParameterFactory)
from force_bdss.core.workflow import Workflow
from force_wfmanager.left_side_pane.execution_layer_model_view import \
    ExecutionLayerModelView

from force_bdss.core.execution_layer import ExecutionLayer
from .new_entity_modal import NewEntityModal
from .workflow_model_view import WorkflowModelView
from .mco_model_view import MCOModelView
from .mco_parameter_model_view import MCOParameterModelView
from .data_source_model_view import DataSourceModelView

# Create an empty view and menu for objects that have no data to display:
no_view = View()
no_menu = Menu()

# Actions!
new_mco_action = Action(name='New MCO...', action='new_mco')
delete_mco_action = Action(name='Delete', action='delete_mco')
edit_mco_action = Action(name='Edit...', action='edit_mco')
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
    """ Custom TreeNode class for worklow elements """
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


class WorkflowSettings(ModelView):
    """ Part of the GUI containing the tree editor displaying the Workflow """
    #: Available MCO factories
    mco_factories = List(Instance(BaseMCOFactory))

    #: Available parameters factories
    mco_parameter_factories = Property(
        List(Instance(BaseMCOParameterFactory)),
        depends_on='mco')

    #: Available data source factories
    data_source_factories = List(Instance(BaseDataSourceFactory))

    #: The workflow model view
    workflow_mv = Instance(WorkflowModelView, allow_none=False)

    #: The workflow model
    model = Instance(Workflow, allow_none=False)

    traits_view = View(
        UItem(name='workflow_mv',
              editor=tree_editor,
              show_label=False),
        width=800,
        height=600,
        resizable=True)

    def _workflow_mv_default(self):
        return WorkflowModelView(model=self.model)

    @on_trait_change('model')
    def update_model_view(self):
        self.workflow_mv.model = self.model

    def _get_mco_parameter_factories(self):
        if self.model.mco is not None:
            return self.model.mco.factory.parameter_factories()
        return []

    def new_mco(self, ui_info, object):
        """ Opens a dialog for creating a MCO """
        workflow_mv = self.workflow_mv

        modal = NewEntityModal(factories=self.mco_factories)
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            workflow_mv.set_mco(result)

    def edit_mco(self, ui_info, object):
        object.model.edit_traits(kind="livemodal")

    def delete_mco(self, ui_info, object):
        """Deletes the MCO"""
        self.workflow_mv.set_mco(None)

    def new_parameter(self, ui_info, object):
        modal = NewEntityModal(factories=self.mco_parameter_factories)
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            object.add_parameter(result)

    def edit_parameter(self, ui_info, object):
        object.model.edit_traits(kind="livemodal")

    def delete_parameter(self, ui_info, object):
        if len(self.workflow_mv.mco_mv) > 0:
            mco_mv = self.workflow_mv.mco_mv[0]
            mco_mv.remove_parameter(object.model)

    def new_data_source(self, ui_info, object):
        """ Opens a dialog for creating a Data Source """
        modal = NewEntityModal(factories=self.data_source_factories)
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            object.add_data_source(result)

    def delete_data_source(self, ui_info, object):
        self.workflow_mv.remove_data_source(object.model)

    def edit_data_source(self, ui_info, object):
        # This is a live dialog, workaround for issue #58
        object.model.edit_traits(kind="livemodal")

    def new_layer(self, ui_info, object):
        self.workflow_mv.add_execution_layer(ExecutionLayer())

    def delete_layer(self, ui_info, object):
        """ Delete an element from the workflow """
        self.workflow_mv.remove_execution_layer(object.model)

