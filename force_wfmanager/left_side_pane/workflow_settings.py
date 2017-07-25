from pyface.tasks.api import TraitsDockPane
from traitsui.api import (
    ITreeNodeAdapter, ITreeNode, TreeEditor, TreeNode, ListStrEditor, VSplit,
    UItem, View, ModelView, Menu, Action, Handler, VGroup, Tabbed, Separator)
from traitsui.list_str_adapter import ListStrAdapter
from traits.api import (Button, Instance, List, provides,
                        register_factory, on_trait_change, Property)

from force_bdss.api import (
    BaseMCOModel, BaseDataSourceModel, BaseKPICalculatorModel,
    BaseMultiCriteriaOptimizerBundle, BaseDataSourceBundle,
    BaseKPICalculatorBundle)

from force_bdss.workspecs.workflow import Workflow

# Create an empty view and menu for objects that have no data to display:
no_view = View()
no_menu = Menu()


def get_bundle_name(bundle):
    """ Returns a bundle name, given the bundle. This ensure that something
    will be displayed (id or name of the bundle) even if no name has been
    specified for the bundle """
    name = bundle.name.strip()
    if len(name) != 0:
        return name
    else:
        return bundle.id


class ListAdapter(ListStrAdapter):
    """ Adapter for the list of available MCOs/Data sources/KPI calculators
    bundles """
    def get_text(self, object, trait, index):
        return get_bundle_name(self.item)


class TreeEditorHandler(Handler):
    def new_mco_handler(self, editor, object):
        """ Opens a dialog for creating the MCO """

    def new_data_source_handler(self, editor, object):
        """ Opens a dialog for creating the Data Source """

    def new_kpi_calculator_handler(self, editor, object):
        """ Opens a dialog for creating the KPI Calculator """

    def delete_mco_handler(self, editor, object):
        object.model.multi_criteria_optimizer = None

    def delete_mco_is_enabled(self, editor, object):
        return object.model.multi_criteria_optimizer is not None

    def delete_data_sources_handler(self, editor, object):
        object.model.data_sources = []

    def delete_data_sources_is_enabled(self, editor, object):
        return len(object.model.data_sources) != 0

    def delete_kpi_calculators_handler(self, editor, object):
        object.model.kpi_calculators = []

    def delete_kpi_calculators_is_enabled(self, editor, object):
        return len(object.model.kpi_calculators) != 0


new_mco_action = Action(
    name='New MCO...',
    action='handler.new_mco_handler(editor, object)')

new_data_source_action = Action(
    name='New DataSource...',
    action='handler.new_data_source_handler(editor, object)')

new_kpi_calculator_action = Action(
    name='New KPI Calculator...',
    action='handler.new_kpi_calculator_handler(editor, object)')

delete_mco_action = Action(
    name='Delete MCO',
    action='handler.delete_mco_handler(editor, object)',
    enabled_when='handler.delete_mco_is_enabled(editor, object)'
)

delete_data_sources_action = Action(
    name='Delete DataSources',
    action='handler.delete_data_sources_handler(editor, object)',
    enabled_when='handler.delete_data_sources_is_enabled(editor, object)'
)

delete_kpi_calculators_action = Action(
    name='Delete KPI Calculators',
    action='handler.delete_kpi_calculators_handler(editor, object)',
    enabled_when='handler.delete_kpi_calculators_is_enabled(editor, object)'
)


@provides(ITreeNode)
class MCOAdapter(ITreeNodeAdapter):
    """ Adapts the MCO model view to be displayed in the tree editor """
    def get_label(self):
        return get_bundle_name(self.adaptee.bundle)

    def get_view(self):
        view = self.adaptee.trait_view()
        view.kind = "subpanel"
        return view

    def get_menu(self):
        return no_menu()


@provides(ITreeNode)
class DataSourceAdapter(ITreeNodeAdapter):
    """ Adapts the Data source model view to be displayed in the tree editor
    """
    def get_label(self):
        return get_bundle_name(self.adaptee.bundle)

    def get_view(self):
        view = self.adaptee.trait_view()
        view.kind = "subpanel"
        return view

    def get_menu(self):
        return no_menu()


@provides(ITreeNode)
class KPICalculatorAdapter(ITreeNodeAdapter):
    """ Adapts the KPI calculator model to be displayed in the tree editor
    """
    def get_label(self):
        return get_bundle_name(self.adaptee.bundle)

    def get_view(self):
        view = self.adaptee.trait_view()
        view.kind = "subpanel"
        return view

    def get_menu(self):
        return no_menu()


register_factory(MCOAdapter, BaseMCOModel, ITreeNode)
register_factory(DataSourceAdapter, BaseDataSourceModel, ITreeNode)
register_factory(KPICalculatorAdapter, BaseKPICalculatorModel, ITreeNode)


class WorkflowModelView(ModelView):
    model = Instance(Workflow)

    mco_representation = Property(
        List(BaseMCOModel),
        depends_on='model.multi_criteria_optimizer')
    data_sources_representation = Property(
        List(BaseDataSourceModel),
        depends_on='model.data_sources')
    kpi_calculators_representation = Property(
        List(BaseKPICalculatorModel),
        depends_on='model.kpi_calculators')

    def _get_mco_representation(self):
        if self.model.multi_criteria_optimizer is not None:
            return [self.model.multi_criteria_optimizer]
        else:
            return []

    def _get_data_sources_representation(self):
        return self.model.data_sources

    def _get_kpi_calculators_representation(self):
        return self.model.kpi_calculators

    def _model_default(self):
        return Workflow()


tree_editor = TreeEditor(
    nodes=[
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='',
                 label='=Workflow',
                 view=no_view,
                 menu=no_menu,
                 ),
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='mco_representation',
                 label='=MCO',
                 view=no_view,
                 menu=Menu(new_mco_action,
                           delete_mco_action),
                 ),
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='data_sources_representation',
                 label='=Data sources',
                 view=no_view,
                 menu=Menu(new_data_source_action,
                           delete_data_sources_action),
                 ),
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='kpi_calculators_representation',
                 label='=KPI calculators',
                 view=no_view,
                 menu=Menu(new_kpi_calculator_action,
                           delete_kpi_calculators_action),
                 ),
    ]
)


class WorkflowSettings(TraitsDockPane):
    """ Side pane which contains the list of available MCOs/Data sources/ KPI
    calculators bundles and the tree editor displaying the Workflow """

    id = 'force_wfmanager.workflow_settings'
    name = 'Workflow Settings'

    #: Available MCO bundles
    available_mcos = List(BaseMultiCriteriaOptimizerBundle)

    #: Available data source bundles
    available_data_sources = List(BaseDataSourceBundle)

    #: Available KPI calculator bundles
    available_kpi_calculators = List(BaseKPICalculatorBundle)

    #: Selected MCO bundle in the list of MCOs
    selected_mco = Instance(BaseMultiCriteriaOptimizerBundle)

    #: Selected data source bundle in the list of data sources
    selected_data_source = Instance(BaseDataSourceBundle)

    #: Selected KPI calculator bundle in the list of KPI calculators
    selected_kpi_calculator = Instance(BaseKPICalculatorBundle)

    add_mco_button = Button("Add")
    add_data_source_button = Button("Add")
    add_kpi_calculator_button = Button("Add")

    workflow = Instance(WorkflowModelView)

    view = View(VSplit(
        UItem(name='workflow',
              editor=tree_editor,
              show_label=False),
        Tabbed(
            VGroup(
                UItem(
                    name='add_mco_button',
                    enabled_when="selected_mco is not None"
                ),
                UItem(
                    "available_mcos",
                    editor=ListStrEditor(
                        adapter=ListAdapter(),
                        selected="selected_mco"),
                ),
                label='MCOs',
            ),
            VGroup(
                UItem(
                    name='add_data_source_button',
                    enabled_when="selected_data_source is not None"
                ),
                UItem(
                    "available_data_sources",
                    editor=ListStrEditor(
                        adapter=ListAdapter(),
                        selected="selected_data_source"),
                ),
                label='Data Sources',
            ),
            VGroup(
                UItem(
                    name='add_kpi_calculator_button',
                    enabled_when="selected_kpi_calculator is not None"
                ),
                UItem(
                    'available_kpi_calculators',
                    editor=ListStrEditor(
                        adapter=ListAdapter(),
                        selected="selected_kpi_calculator")
                ),
                label='KPI Calculators'
            ),
        )),
        width=800,
        height=600,
        resizable=True,
        handler=TreeEditorHandler())

    def _workflow_default(self):
        return WorkflowModelView()

    @on_trait_change('add_mco_button')
    def add_mco(self):
        if self.selected_mco is not None:
            self.workflow.model.multi_criteria_optimizer = \
                self.selected_mco.create_model()

    @on_trait_change('add_data_source_button')
    def add_data_source(self):
        if self.selected_data_source is not None:
            self.workflow.model.data_sources.append(
                self.selected_data_source.create_model()
            )

    @on_trait_change('add_kpi_calculator_button')
    def add_kpi_calculator(self):
        if self.selected_kpi_calculator is not None:
            self.workflow.model.kpi_calculators.append(
                self.selected_kpi_calculator.create_model()
            )
