from pyface.tasks.api import TraitsDockPane
from traitsui.api import (
    ListStrEditor, ITreeNodeAdapter, ITreeNode, Tabbed, TreeEditor, TreeNode,
    UItem, VGroup, View, ModelView, VSplit)
from traitsui.list_str_adapter import ListStrAdapter
from traits.api import (Button, Instance, List, provides, register_factory,
                        on_trait_change, Property, property_depends_on)

from force_bdss.api import (
    BaseMCOModel, BaseDataSourceModel, BaseKPICalculatorModel,
    BaseMultiCriteriaOptimizerBundle, BaseDataSourceBundle,
    BaseKPICalculatorBundle)

from force_bdss.workspecs.workflow import Workflow


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


@provides(ITreeNode)
class McoAdapter(ITreeNodeAdapter):
    """ Adapts the MCO model view to be displayed in the tree editor """
    def get_label(self):
        return get_bundle_name(self.adaptee.bundle)

    def get_view(self):
        view = self.adaptee.trait_view()
        view.kind = "subpanel"
        return view


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


@provides(ITreeNode)
class KpiCalculatorAdapter(ITreeNodeAdapter):
    """ Adapts the KPI calculator model to be displayed in the tree editor
    """
    def get_label(self):
        return get_bundle_name(self.adaptee.bundle)

    def get_view(self):
        view = self.adaptee.trait_view()
        view.kind = "subpanel"
        return view


register_factory(McoAdapter, BaseMCOModel, ITreeNode)
register_factory(DataSourceAdapter, BaseDataSourceModel, ITreeNode)
register_factory(KpiCalculatorAdapter, BaseKPICalculatorModel, ITreeNode)


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
    available_mcos = List(Instance(BaseMultiCriteriaOptimizerBundle))

    #: Available data source bundles
    available_data_sources = List(Instance(BaseDataSourceBundle))

    #: Available KPI calculator bundles
    available_kpi_calculators = List(Instance(BaseKPICalculatorBundle))

    #: Selected MCO bundle in the list of MCOs
    selected_mco = Instance(BaseMultiCriteriaOptimizerBundle)

    #: Selected data source bundles in the list of data sources
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
        resizable=True)

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
