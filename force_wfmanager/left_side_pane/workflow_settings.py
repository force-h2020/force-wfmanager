from pyface.tasks.api import TraitsDockPane
from traitsui.api import (ListStrEditor, ITreeNodeAdapter, ITreeNode, Tabbed,
                          TreeEditor, TreeNode, UItem, VGroup, View, ModelView)
from traitsui.list_str_adapter import ListStrAdapter
from traits.api import (adapts, Button, Instance, List,
                        on_trait_change, Property, property_depends_on)

from force_bdss.api import (
    BaseMCOModel, BaseDataSourceModel, BaseKPICalculatorModel,
    IMultiCriteriaOptimizerBundle, IDataSourceBundle, IKPICalculatorBundle
)

from force_bdss.workspecs.workflow import Workflow


def get_bundle_name(bundle):
    try:
        text = bundle.name
    except AttributeError:
        text = bundle.id
    return text


class ListAdapter(ListStrAdapter):
    """ Adapter for the list of available MCOs/Data sources/KPI calculators
    bundles """
    def get_text(self, object, trait, index):
        return get_bundle_name(self.item)


class McoAdapter(ITreeNodeAdapter):
    """ Adapts the MCO model view to be displayed in the tree editor """
    adapts(BaseMCOModel, ITreeNode)

    def get_label(self):
        return get_bundle_name(self.adaptee.bundle)


class DataSourceAdapter(ITreeNodeAdapter):
    """ Adapts the Data source model view to be displayed in the tree editor
    """
    adapts(BaseDataSourceModel, ITreeNode)

    def get_label(self):
        return get_bundle_name(self.adaptee.bundle)


class KpiCalculatorAdapter(ITreeNodeAdapter):
    """ Adapts the KPI calculator model to be displayed in the tree editor
    """
    adapts(BaseKPICalculatorModel, ITreeNode)

    def get_label(self):
        return get_bundle_name(self.adaptee.bundle)


class WorkflowModelView(ModelView):
    model = Instance(Workflow)

    mco_representation = Property(List(Instance(BaseMCOModel)))
    data_sources_representation = Property(List(Instance(
        BaseDataSourceModel)))
    kpi_calculators_representation = Property(List(Instance(
        BaseKPICalculatorModel)))

    @property_depends_on('model.multi_criteria_optimizer', settable=False)
    def _get_mco_representation(self):
        if self.model.multi_criteria_optimizer is not None:
            return [self.model.multi_criteria_optimizer]
        else:
            return []

    @property_depends_on('model.data_sources', settable=False)
    def _get_data_sources_representation(self):
        return self.model.data_sources

    @property_depends_on('model.kpi_calculators', settable=False)
    def _get_kpi_calculators_representation(self):
        return self.model.kpi_calculators

    def _model_default(self):
        return Workflow()


# Create an empty view for objects that have no data to display:
no_view = View()

tree_editor = TreeEditor(
    nodes=[
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='',
                 label='=Workflow',
                 view=no_view
                 ),
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='mco_representation',
                 label='=MCO',
                 view=no_view
                 ),
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='data_sources_representation',
                 label='=Data sources',
                 view=no_view
                 ),
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='kpi_calculators_representation',
                 label='=KPI calculators',
                 view=no_view
                 ),
    ]
)


class WorkflowSettings(TraitsDockPane):
    """ Side pane which contains the list of available MCOs/Data sources/ KPI
    calculators bundles and the tree editor displaying the Workflow """
    id = 'force_wfmanager.workflow_settings'
    name = 'Workflow Settings'

    #: Available MCO bundles
    available_mcos = List(Instance(IMultiCriteriaOptimizerBundle))

    #: Available data source bundles
    available_data_sources = List(Instance(IDataSourceBundle))

    #: Available KPI calculator bundles
    available_kpi_calculators = List(Instance(IKPICalculatorBundle))

    #: Selected MCO bundle in the list of MCOs
    selected_mco = Instance(IMultiCriteriaOptimizerBundle)

    #: Selected data source bundles in the list of data sources
    selected_data_source = Instance(IDataSourceBundle)

    #: Selected KPI calculator bundle in the list of KPI calculators
    selected_kpi_calculator = Instance(IKPICalculatorBundle)

    add_mco_button = Button("Add")
    add_data_source_button = Button("Add")
    add_kpi_calculator_button = Button("Add")

    workflow = Instance(WorkflowModelView)

    view = View(VGroup(
        UItem(name='workflow',
              editor=tree_editor,
              show_label=False),
        Tabbed(
            VGroup(
                UItem(
                    name='add_mco_button'
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
                    name='add_data_source_button'
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
                    name='add_kpi_calculator_button'
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
        resizable=True)

    def _workflow_default(self):
        return WorkflowModelView()

    @on_trait_change('add_mco_button')
    def add_mco(self):
        self.workflow.model.multi_criteria_optimizer = \
            self.selected_mco.create_model()

    @on_trait_change('add_data_source_button')
    def add_data_source(self):
        self.workflow.model.data_sources.append(
            self.selected_data_source.create_model()
        )

    @on_trait_change('add_kpi_calculator_button')
    def add_kpi_calculator(self):
        self.workflow.model.kpi_calculators.append(
            self.selected_kpi_calculator.create_model()
        )
