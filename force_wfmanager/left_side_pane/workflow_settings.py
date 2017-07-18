from pyface.tasks.api import TraitsDockPane
from traitsui.api import (ListStrEditor, ITreeNodeAdapter, ITreeNode, Tabbed,
                          TreeEditor, TreeNode, UItem, VGroup, View)
from traitsui.list_str_adapter import ListStrAdapter
from traits.api import adapts, Instance, List, HasTraits

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


class McoAdapter(ITreeNodeAdapter):
    """ Adapts the MCO model to be displayed in the tree
    """
    adapts(BaseMCOModel, ITreeNode)

    def get_label(self):
        return self.adaptee.name


class DataSourceAdapter(ITreeNodeAdapter):
    """ Adapts the Data source model to be displayed in the tree
    """
    adapts(BaseDataSourceModel, ITreeNode)

    def get_label(self):
        return self.adaptee.name


class KpiCalculatorAdapter(ITreeNodeAdapter):
    """ Adapts the KPI calculator model to be displayed in the tree
    """
    adapts(BaseKPICalculatorModel, ITreeNode)

    def get_label(self):
        return self.adaptee.name


class Workflow(HasTraits):
    """ Definition of the workflow
    """
    mco = List(Instance(BaseMCOModel))
    data_sources = List(Instance(BaseDataSourceModel))
    kpi_calculators = List(Instance(BaseKPICalculatorModel))


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
                 view=no_view,
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

    workflow = Instance(Workflow)

    view = View(VGroup(
        UItem(name='workflow',
              editor=tree_editor,
              show_label=False),
        Tabbed(
            UItem(
                "available_mcos",
                editor=ListStrEditor(
                    adapter=ListAdapter(),
                    selected="selected_mco"),
                label='MCOs',
            ),
            UItem(
                'available_data_sources',
                editor=ListStrEditor(
                    adapter=ListAdapter(),
                    selected="selected_data_source"),
                label='Data Sources'
            ),
            UItem(
                'available_kpi_calculators',
                editor=ListStrEditor(
                    adapter=ListAdapter(),
                    selected="selected_kpi_calculator"),
                label='KPI Calculators'
            ))
        ),
        width=800,
        height=600,
        resizable=True)

    def _workflow_default(self):
        return Workflow()
