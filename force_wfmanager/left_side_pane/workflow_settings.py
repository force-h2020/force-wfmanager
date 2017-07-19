from pyface.tasks.api import TraitsDockPane
from traitsui.api import (ListStrEditor, ITreeNodeAdapter, ITreeNode, Tabbed,
                          TreeEditor, TreeNode, UItem, VGroup, View, ModelView)
from traitsui.list_str_adapter import ListStrAdapter
from traits.api import (adapts, Button, Instance, List,
                        on_trait_change, HasTraits, Str)

from force_bdss.mco.base_mco_model import BaseMCOModel
from force_bdss.data_sources.base_data_source_model import BaseDataSourceModel
from force_bdss.kpi.base_kpi_calculator_model import BaseKPICalculatorModel

from force_bdss.mco.i_multi_criteria_optimizer_bundle import (
    IMultiCriteriaOptimizerBundle)
from force_bdss.data_sources.i_data_source_bundle import IDataSourceBundle
from force_bdss.kpi.i_kpi_calculator_bundle import IKPICalculatorBundle


class ListAdapter(ListStrAdapter):
    """ Adapter for the list of available MCOs/Data sources/KPI calculators
    """
    def get_text(self, object, trait, index):
        return self.item.name


class MCOModelView(ModelView):
    name = Str()

    model = Instance(BaseMCOModel)

    view = View(
        UItem('model', style='custom')
    )


class DataSourceModelView(ModelView):
    name = Str()

    model = Instance(BaseDataSourceModel)

    view = View(
        UItem('model', style='custom')
    )


class KPICModelView(ModelView):
    name = Str()

    model = Instance(BaseKPICalculatorModel)

    view = View(
        UItem('model', style='custom')
    )


class McoAdapter(ITreeNodeAdapter):
    """ Adapts the MCO model view to be displayed in the tree
    """
    adapts(MCOModelView, ITreeNode)

    def get_label(self):
        return self.adaptee.name

    def get_view(self):
        return self.adaptee.default_trait_view()


class DataSourceAdapter(ITreeNodeAdapter):
    """ Adapts the Data source model view to be displayed in the tree
    """
    adapts(DataSourceModelView, ITreeNode)

    def get_label(self):
        return self.adaptee.name

    def get_view(self):
        return self.adaptee.default_trait_view()


class KpiCalculatorAdapter(ITreeNodeAdapter):
    """ Adapts the KPI calculator model to be displayed in the tree
    """
    adapts(KPICModelView, ITreeNode)

    def get_label(self):
        return self.adaptee.name

    def get_view(self):
        return self.adaptee.default_trait_view()


class Workflow(HasTraits):
    """ Definition of the workflow
    """
    mco = List(Instance(MCOModelView))
    data_sources = List(Instance(DataSourceModelView))
    kpi_calculators = List(Instance(KPICModelView))


# Create an empty view for objects that have no data to display:
no_view = View()

tree_editor = TreeEditor(
    nodes=[
        TreeNode(node_for=[Workflow],
                 auto_open=True,
                 children='',
                 label='=Workflow',
                 view=no_view
                 ),
        TreeNode(node_for=[Workflow],
                 auto_open=True,
                 children='mco',
                 label='=MCO',
                 ),
        TreeNode(node_for=[Workflow],
                 auto_open=True,
                 children='data_sources',
                 label='=Data sources',
                 view=no_view
                 ),
        TreeNode(node_for=[Workflow],
                 auto_open=True,
                 children='kpi_calculators',
                 label='=KPI calculators',
                 view=no_view
                 ),
    ]
)


class WorkflowSettings(TraitsDockPane):
    """ Side pane which contains the list of available MCOs/Data sources/ KPI
    calculators and the tree editor displaying the Workflow
    """
    id = 'force_wfmanager.workflow_settings'
    name = 'Plugins'

    available_mcos = List()
    available_data_sources = List()
    available_kpi_calculators = List()

    selected_mco = Instance(IMultiCriteriaOptimizerBundle)
    selected_data_source = Instance(IDataSourceBundle)
    selected_kpi_calculator = Instance(IKPICalculatorBundle)

    add_mco_button = Button("Add")
    add_data_source_button = Button("Add")
    add_kpi_calculator_button = Button("Add")

    workflow = Instance(Workflow)

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
        return Workflow()

    @on_trait_change('add_mco_button')
    def add_mco(self):
        self.workflow.mco[0] = MCOModelView(
            name=self.selected_mco.name,
            model=self.selected_mco.create_model()),

    @on_trait_change('add_data_source_button')
    def add_data_source(self):
        self.workflow.data_sources.append(DataSourceModelView(
            name=self.selected_data_source.name,
            model=self.selected_data_source.create_model(),
        ))

    @on_trait_change('add_kpi_calculator_button')
    def add_kpi_calculator(self):
        self.workflow.kpi_calculators.append(KPICModelView(
            name=self.selected_kpi_calculator.name,
            model=self.selected_kpi_calculator.create_model(),
        ))
