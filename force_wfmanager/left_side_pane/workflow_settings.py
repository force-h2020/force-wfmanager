from traits.api import (Instance, List, Property, HasStrictTraits,
                        on_trait_change)

from traitsui.api import (TreeEditor, TreeNode, UItem, View, Menu, Action,
                          Handler)

from force_bdss.api import (
    BaseMCOFactory,
    BaseDataSourceFactory,
    BaseKPICalculatorFactory,
    BaseMCOParameterFactory)
from force_bdss.core.workflow import Workflow

from .new_entity_modal import NewEntityModal
from .workflow_model_view import WorkflowModelView
from .mco_model_view import MCOModelView
from .mco_parameter_model_view import MCOParameterModelView
from .data_source_model_view import DataSourceModelView
from .kpi_calculator_model_view import KPICalculatorModelView

# Create an empty view and menu for objects that have no data to display:
no_view = View()
no_menu = Menu()


class WorkflowHandler(Handler):
    """ Handler for the Workflow editor, this handler will take care of events
    on the tree editor (e.g. right click on a tree element) """
    def new_mco_handler(self, editor, object):
        """ Opens a dialog for creating a MCO """
        modal = NewEntityModal(
            workflow_mv=editor.object.workflow_mv,
            factories=editor.object.mco_factories)
        modal.edit_traits()

    def new_parameter_handler(self, editor, object):
        """ Opens a dialog for creating a parameter """
        modal = NewEntityModal(
            workflow_mv=editor.object.workflow_mv,
            factories=editor.object.mco_parameter_factories
        )
        modal.edit_traits()

    def new_data_source_handler(self, editor, object):
        """ Opens a dialog for creating a Data Source """
        modal = NewEntityModal(
            workflow_mv=editor.object.workflow_mv,
            factories=editor.object.data_source_factories)
        modal.edit_traits()

    def new_kpi_calculator_handler(self, editor, object):
        """ Opens a dialog for creating a KPI Calculator """
        modal = NewEntityModal(
            workflow_mv=editor.object.workflow_mv,
            factories=editor.object.kpi_calculator_factories)
        modal.edit_traits()

    def edit_entity_handler(self, editor, object):
        """ Opens a dialog for configuring the workflow element """
        object.model.edit_traits(kind="modal")

    def delete_entity_handler(self, editor, object):
        """ Delete an element from the workflow """
        editor.object.workflow_mv.remove_entity(object.model)


new_mco_action = Action(
    name='New MCO...',
    action='handler.new_mco_handler(editor, object)')

new_parameter_action = Action(
    name='New parameter...',
    action='handler.new_parameter_handler(editor, object)')

new_data_source_action = Action(
    name='New DataSource...',
    action='handler.new_data_source_handler(editor, object)')

new_kpi_calculator_action = Action(
    name='New KPI Calculator...',
    action='handler.new_kpi_calculator_handler(editor, object)')

edit_entity_action = Action(
    name='Edit...',
    action='handler.edit_entity_handler(editor, object)'
)

delete_entity_action = Action(
    name='Delete',
    action='handler.delete_entity_handler(editor, object)'
)


class WorkflowElementNode(TreeNode):
    """ Custom TreeNode class for worklow elements """
    def get_icon(self, object, is_expanded):
        return 'icons/valid.png' if object.valid else 'icons/invalid.png'


tree_editor = TreeEditor(
    nodes=[
        # Root node "Workflow"
        WorkflowElementNode(
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
            children='mco_representation',
            label='=MCO',
            view=no_view,
            menu=Menu(new_mco_action),
        ),
        # Node representing the MCO
        WorkflowElementNode(
            node_for=[MCOModelView],
            auto_open=True,
            children='',
            label='label',
            view=no_view,
            menu=Menu(edit_entity_action, delete_entity_action),
        ),
        # Folder node "Parameters" containing the MCO parameters
        TreeNode(
            node_for=[MCOModelView],
            auto_open=True,
            children='mco_parameters_representation',
            label='=Parameters',
            view=no_view,
            menu=Menu(new_parameter_action),
        ),
        #: Node representing an MCO parameter
        WorkflowElementNode(
            node_for=[MCOParameterModelView],
            auto_open=True,
            children='',
            label='label',
            menu=Menu(edit_entity_action, delete_entity_action),
        ),
        # Folder node "Data Sources" containing the DataSources
        TreeNode(
            node_for=[WorkflowModelView],
            auto_open=True,
            children='data_sources_representation',
            label='=Data sources',
            view=no_view,
            menu=Menu(new_data_source_action),
        ),
        #: Node representing a DataSource
        WorkflowElementNode(
            node_for=[DataSourceModelView],
            auto_open=True,
            children='',
            label='label',
            menu=Menu(edit_entity_action, delete_entity_action),
        ),
        # Folder node "KPI Calculators" containing the KPI Calculators
        TreeNode(
            node_for=[WorkflowModelView],
            auto_open=True,
            children='kpi_calculators_representation',
            label='=KPI calculators',
            view=no_view,
            menu=Menu(new_kpi_calculator_action),
        ),
        #: Node representing a KPI Calculator
        WorkflowElementNode(
            node_for=[KPICalculatorModelView],
            auto_open=True,
            children='',
            label='label',
            menu=Menu(edit_entity_action, delete_entity_action),
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

    #: Available KPI calculator factories
    kpi_calculator_factories = List(Instance(
        BaseKPICalculatorFactory))

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
