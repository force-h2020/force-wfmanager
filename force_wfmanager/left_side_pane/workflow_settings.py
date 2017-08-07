from pyface.tasks.api import TraitsDockPane

from traitsui.api import (
    ITreeNodeAdapter, ITreeNode, TreeEditor, TreeNode, UItem, View, Menu,
    Action, Handler)
from traits.api import (Instance, List, provides, register_factory, Property,
                        on_trait_change)

from force_bdss.api import (
    BaseMCOFactory,
    BaseDataSourceModel, BaseDataSourceFactory,
    BaseKPICalculatorModel, BaseKPICalculatorFactory,
    BaseMCOParameter, BaseMCOParameterFactory)
from force_bdss.core.workflow import Workflow

from .view_utils import get_factory_name
from .new_entity_modal import NewEntityModal
from .workflow_model_view import WorkflowModelView
from .mco_model_view import MCOModelView

# Create an empty view and menu for objects that have no data to display:
no_view = View()
no_menu = Menu()


class WorkflowHandler(Handler):
    """ Handler for the Workflow editor, this handler will take care of events
    on the tree editor (e.g. right click on a tree element) """
    def new_mco_handler(self, editor, object):
        """ Opens a dialog for creating a MCO """
        modal = NewEntityModal(
            workflow_mv=editor.object._workflow_mv,
            available_factories=editor.object.available_mco_factories)
        modal.configure_traits()

    def new_parameter_handler(self, editor, object):
        """ Opens a dialog for creating a parameter """
        modal = NewEntityModal(
            workflow_mv=editor.object._workflow_mv,
            available_factories=editor.object.available_mco_parameter_factories
        )
        modal.configure_traits()

    def new_data_source_handler(self, editor, object):
        """ Opens a dialog for creating a Data Source """
        modal = NewEntityModal(
            workflow_mv=editor.object._workflow_mv,
            available_factories=editor.object.available_data_source_factories)
        modal.configure_traits()

    def new_kpi_calculator_handler(self, editor, object):
        """ Opens a dialog for creating a KPI Calculator """
        obj = editor.object
        modal = NewEntityModal(
            workflow_mv=obj._workflow_mv,
            available_factories=obj.available_kpi_calculator_factories)
        modal.configure_traits()

    def delete_mco_handler(self, editor, object):
        """ Delete the MCO from the workflow """
        editor.object.workflow_m.mco = None

    def delete_mco_parameter_handler(self, editor, object):
        """ Delete one parameter from the MCO """
        workflow_m = editor.object.workflow_m
        workflow_m.mco.parameters.remove(object)

    def delete_data_source_handler(self, editor, object):
        """ Delete a DataSource from the workflow """
        workflow_m = editor.object.workflow_m
        workflow_m.data_sources.remove(object)

    def delete_kpi_calculator_handler(self, editor, object):
        """ Delete a KPI Calculator from the workflow """
        workflow_m = editor.object.workflow_m
        workflow_m.kpi_calculators.remove(object)


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

delete_mco_action = Action(
    name='Delete',
    action='handler.delete_mco_handler(editor, object)'
)

delete_mco_parameter_action = Action(
    name='Delete',
    action='handler.delete_mco_parameter_handler(editor, object)'
)

delete_data_source_action = Action(
    name='Delete',
    action='handler.delete_data_source_handler(editor, object)'
)

delete_kpi_calculator_action = Action(
    name='Delete',
    action='handler.delete_kpi_calculator_handler(editor, object)'
)


@provides(ITreeNode)
class MCOParameterAdapter(ITreeNodeAdapter):
    """ Adapts the MCO parameter model to be displayed in the tree editor """
    def get_label(self):
        return get_factory_name(self.adaptee.factory)

    def get_view(self):
        view = self.adaptee.trait_view()
        view.kind = "subpanel"
        return view

    def get_menu(self):
        return Menu(delete_mco_parameter_action)


@provides(ITreeNode)
class DataSourceAdapter(ITreeNodeAdapter):
    """ Adapts the Data source model to be displayed in the tree editor """
    def get_label(self):
        return get_factory_name(self.adaptee.factory)

    def get_view(self):
        view = self.adaptee.trait_view()
        view.kind = "subpanel"
        return view

    def get_menu(self):
        return Menu(delete_data_source_action)


@provides(ITreeNode)
class KPICalculatorAdapter(ITreeNodeAdapter):
    """ Adapts the KPI calculator model to be displayed in the tree editor """
    def get_label(self):
        return get_factory_name(self.adaptee.factory)

    def get_view(self):
        view = self.adaptee.trait_view()
        view.kind = "subpanel"
        return view

    def get_menu(self):
        return Menu(delete_kpi_calculator_action)


register_factory(MCOParameterAdapter, BaseMCOParameter, ITreeNode)
register_factory(DataSourceAdapter, BaseDataSourceModel, ITreeNode)
register_factory(KPICalculatorAdapter, BaseKPICalculatorModel, ITreeNode)

tree_editor = TreeEditor(
    nodes=[
        # Root node "Workflow"
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='',
                 label='=Workflow',
                 view=no_view,
                 menu=no_menu,
                 ),
        # Folder node "MCO" containing the MCO
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='mco_representation',
                 label='=MCO',
                 view=no_view,
                 menu=Menu(new_mco_action),
                 ),
        # Node representing the MCO
        TreeNode(node_for=[MCOModelView],
                 auto_open=True,
                 children='',
                 label='label',
                 view=View(UItem('model', style="custom"), kind="subpanel"),
                 menu=Menu(delete_mco_action),
                 ),
        # Folder node "Parameters" containing the MCO parameters
        TreeNode(node_for=[MCOModelView],
                 auto_open=True,
                 children='mco_parameters_representation',
                 label='=Parameters',
                 view=no_view,
                 menu=Menu(new_parameter_action),
                 ),
        # Folder node "Data Sources" containing the DataSources
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='data_sources_representation',
                 label='=Data sources',
                 view=no_view,
                 menu=Menu(new_data_source_action),
                 ),
        # Folder node "KPI Calculators" containing the KPI Calculators
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='kpi_calculators_representation',
                 label='=KPI calculators',
                 view=no_view,
                 menu=Menu(new_kpi_calculator_action),
                 ),
    ]
)


class WorkflowSettings(TraitsDockPane):
    """ Side pane which contains the tree editor displaying the Workflow """

    id = 'force_wfmanager.workflow_settings'
    name = 'Workflow Settings'

    #: Available MCO factories
    available_mco_factories = List(Instance(BaseMCOFactory))

    #: Available parameters factories
    available_mco_parameter_factories = Property(
        List(Instance(BaseMCOParameterFactory)),
        depends_on='workflow_m.mco')

    #: Available data source factories
    available_data_source_factories = List(Instance(BaseDataSourceFactory))

    #: Available KPI calculator factories
    available_kpi_calculator_factories = List(Instance(
        BaseKPICalculatorFactory))

    #: The workflow model view
    _workflow_mv = Instance(WorkflowModelView, allow_none=False)

    #: The workflow model
    workflow_m = Instance(Workflow, allow_none=False)

    traits_view = View(
        UItem(name='_workflow_mv',
              editor=tree_editor,
              show_label=False),
        width=800,
        height=600,
        resizable=True,
        handler=WorkflowHandler())

    def __workflow_mv_default(self):
        return WorkflowModelView(
            model=self.workflow_m
        )

    @on_trait_change('workflow_m')
    def update_model_view(self):
        self._workflow_mv.model = self.workflow_m

    def _get_available_mco_parameter_factories(self):
        mco_factory = self.workflow_m.mco.factory
        return mco_factory.parameter_factories()
