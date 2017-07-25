from pyface.tasks.api import TraitsDockPane
from traitsui.api import (
    ITreeNodeAdapter, ITreeNode, TreeEditor, TreeNode,
    UItem, View, ModelView, Menu, Action, Handler, Separator)
from traits.api import (Instance, List, provides,
                        register_factory, Property)

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


class TreeEditorHandler(Handler):
    def new_mco_handler(self, editor, object):
        print "New multi criteria optimizer !"

    def new_data_source_handler(self, editor, object):
        print "New data source !"

    def new_kpi_calculator_handler(self, editor, object):
        print "New kpi calculator !"

    def delete_mco_handler(self, editor, object):
        print "Delete MCO !"

    def delete_data_sources_handler(self, editor, object):
        print "Delete DataSources !"

    def delete_kpi_calculators_handler(self, editor, object):
        print "Delete KPI Calculators !"

new_mco_action = Action(
    name='New MCO',
    action='handler.new_mco_handler(editor, object)')

new_data_source_action = Action(
    name='New DataSource',
    action='handler.new_data_source_handler(editor, object)')

new_kpi_calculator_action = Action(
    name='New KPI Calculator',
    action='handler.new_kpi_calculator_handler(editor, object)')

delete_mco_action = Action(
    name='Delete MCO',
    action='handler.delete_mco_handler(editor, object)'
)

delete_data_sources_action = Action(
    name='Delete DataSources',
    action='handler.delete_data_sources_handler(editor, object)'
)

delete_kpi_calculators_action = Action(
    name='Delete KPI Calculators',
    action='handler.delete_kpi_calculators_handler(editor, object)'
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
class KPICalculatorAdapter(ITreeNodeAdapter):
    """ Adapts the KPI calculator model to be displayed in the tree editor
    """
    def get_label(self):
        return get_bundle_name(self.adaptee.bundle)

    def get_view(self):
        view = self.adaptee.trait_view()
        view.kind = "subpanel"
        return view


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


# Create an empty view and menu for objects that have no data to display:
no_view = View()
no_menu = Menu()

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
                           Separator(),
                           delete_mco_action),
                 ),
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='data_sources_representation',
                 label='=Data sources',
                 view=no_view,
                 menu=Menu(new_data_source_action,
                           Separator(),
                           delete_data_sources_action),
                 ),
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='kpi_calculators_representation',
                 label='=KPI calculators',
                 view=no_view,
                 menu=Menu(new_kpi_calculator_action,
                           Separator(),
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

    workflow = Instance(WorkflowModelView)

    view = View(
        UItem(name='workflow',
              editor=tree_editor,
              show_label=False),
        handler=TreeEditorHandler())

    def _workflow_default(self):
        return WorkflowModelView()
