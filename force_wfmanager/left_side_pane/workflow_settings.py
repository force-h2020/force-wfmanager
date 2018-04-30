from traits.api import (Instance, List, Property, HasStrictTraits,
                        on_trait_change)

from traitsui.api import (TreeEditor, TreeNode, UItem, View, Menu, Action,
                          Handler)

from force_bdss.api import (
    BaseMCOFactory,
    BaseDataSourceFactory,
    BaseMCOParameterFactory)
from force_bdss.core.workflow import Workflow
from force_wfmanager.left_side_pane.execution_layer_model_view import \
    ExecutionLayerModelView

from .new_entity_modal import NewEntityModal
from .workflow_model_view import WorkflowModelView
from .mco_model_view import MCOModelView
from .mco_parameter_model_view import MCOParameterModelView
from .data_source_model_view import DataSourceModelView

# Create an empty view and menu for objects that have no data to display:
no_view = View()
no_menu = Menu()


class WorkflowHandler(Handler):
    """ Handler for the Workflow editor, this handler will take care of events
    on the tree editor (e.g. right click on a tree element) """
    def new_mco(self, editor, object):
        """ Opens a dialog for creating a MCO """
        workflow_mv = editor.object.workflow_mv

        modal = NewEntityModal(factories=workflow_mv.mco_factories)
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            workflow_mv.set_mco(modal.current_model)

    def delete_mco(self, editor, object):
        workflow_mv = editor.object.workflow_mv
        workflow_mv.set_mco(None)

    def new_parameter(self, editor, object):
        modal = NewEntityModal(
            factories=editor.object.mco_parameter_factories
        )
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            object.add_parameter(result)

    def delete_parameter(self, editor, object):
        object.remove_parameter(object.model)

    def new_data_source(self, editor, object):
        """ Opens a dialog for creating a Data Source """
        modal = NewEntityModal(
            factories=editor.object.data_source_factories)
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            object.add_data_source(result)

    def edit_entity_handler(self, editor, object):
        """ Opens a dialog for configuring the workflow element """
        # This is a live dialog, workaround for issue #58
        object.model.edit_traits(kind="livemodal")

    def new_layer(self, editor, object):
        editor.object.workflow_mv.add_execution_layer()

    def delete_layer(self, editor, object):
        """ Delete an element from the workflow """
        editor.object.remove_layer(object.model)


new_mco_action = Action(
    name='New MCO...',
    action='handler.new_mco(editor, object)')

delete_mco_action = Action(
    name='Delete',
    action='handler.delete_mco(editor, object)')

new_parameter_action = Action(
    name='New parameter...',
    action='handler.new_parameter(editor, object)')

delete_parameter_action = Action(
    name='Delete',
    action='handler.delete_parameter(editor, object)')

new_layer_action = Action(
    name="New Layer...",
    action='handler.new_layer(editor, object)'
)

new_data_source_action = Action(
    name='New DataSource...',
    action='handler.new_data_source(editor, object)')

edit_entity_action = Action(
    name='Edit...',
    action='handler.edit_entity(editor, object)'
)

delete_layer_action = Action(
    name='Delete',
    action='handler.delete_layer(editor, object)'
)


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
            menu=Menu(edit_entity_action,
                      delete_mco_action),
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
            menu=Menu(edit_entity_action, delete_parameter_action),
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
             menu=no_menu,
         ),
    ],
    orientation="vertical"
)


class WorkflowSettings(HasStrictTraits):
    """ Part of the GUI containing the tree editor displaying the Workflow """
    #: Available MCO factories
    mco_factories = List(Instance(BaseMCOFactory))

    #: Available parameters factories
    mco_parameter_factories = Property(
        List(Instance(BaseMCOParameterFactory)),
        depends_on='workflow_m.mco')

    #: Available data source factories
    data_source_factories = List(Instance(BaseDataSourceFactory))

    #: The workflow model view
    workflow_mv = Instance(WorkflowModelView, allow_none=False)

    #: The workflow model
    workflow_m = Instance(Workflow, allow_none=False)

    traits_view = View(
        UItem(name='workflow_mv',
              editor=tree_editor,
              show_label=False),
        width=800,
        height=600,
        resizable=True,
        handler=WorkflowHandler())

    def _workflow_mv_default(self):
        return WorkflowModelView(
            model=self.workflow_m
        )

    @on_trait_change('workflow_m', post_init=True)
    def update_model_view(self):
        self.workflow_mv.model = self.workflow_m

    def _get_mco_parameter_factories(self):
        mco_factory = self.workflow_m.mco.factory
        return mco_factory.parameter_factories()
