from pyface.tasks.api import TraitsDockPane
from traitsui.api import (
    ITreeNodeAdapter, ITreeNode, TreeEditor, TreeNode, UItem, View, Menu,
    Action, Handler)
from traits.api import Instance, List, provides, register_factory

from force_bdss.api import (
    BaseMCOModel, BaseDataSourceModel, BaseKPICalculatorModel,
    BaseMultiCriteriaOptimizerBundle, BaseDataSourceBundle,
    BaseKPICalculatorBundle)

from .view_utils import get_bundle_name
from .new_entity_modal import NewEntityModal
from .workflow_model_view import WorkflowModelView

# Create an empty view and menu for objects that have no data to display:
no_view = View()
no_menu = Menu()


class WorkflowHandler(Handler):
    new_entity_modal = Instance(NewEntityModal)

    # Menu actions in the TreeEditor
    def new_mco_handler(self, editor, object):
        """ Opens a dialog for creating a MCO """
        self.new_entity_modal.available_bundles = editor.object.available_mcos
        self.new_entity_modal.configure_traits()

    def new_data_source_handler(self, editor, object):
        """ Opens a dialog for creating a Data Source """
        self.new_entity_modal.available_bundles = \
            editor.object.available_data_sources
        self.new_entity_modal.configure_traits()

    def new_kpi_calculator_handler(self, editor, object):
        """ Opens a dialog for creating a KPI Calculator """
        self.new_entity_modal.available_bundles = \
            editor.object.available_kpi_calculators
        self.new_entity_modal.configure_traits()

    def delete_mco_handler(self, editor, object):
        editor.object.workflow.model.multi_criteria_optimizer = None

    def delete_data_source_handler(self, editor, object):
        editor.object.workflow.model.data_sources.remove(object)

    def delete_kpi_calculator_handler(self, editor, object):
        editor.object.workflow.model.kpi_calculators.remove(object)

    # On trait changed listeners
    def object_workflow_changed(self, info):
        self.new_entity_modal.workflow = info.object.workflow

    def _new_entity_modal_default(self):
        return NewEntityModal()


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
    name='Delete',
    action='handler.delete_mco_handler(editor, object)'
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
class MCOAdapter(ITreeNodeAdapter):
    """ Adapts the MCO model view to be displayed in the tree editor """
    def get_label(self):
        return get_bundle_name(self.adaptee.bundle)

    def get_view(self):
        view = self.adaptee.trait_view()
        view.kind = "subpanel"
        return view

    def get_menu(self):
        return Menu(delete_mco_action)


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
        return Menu(delete_data_source_action)


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
        return Menu(delete_kpi_calculator_action)


register_factory(MCOAdapter, BaseMCOModel, ITreeNode)
register_factory(DataSourceAdapter, BaseDataSourceModel, ITreeNode)
register_factory(KPICalculatorAdapter, BaseKPICalculatorModel, ITreeNode)

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
                 menu=Menu(new_mco_action),
                 ),
        TreeNode(node_for=[WorkflowModelView],
                 auto_open=True,
                 children='data_sources_representation',
                 label='=Data sources',
                 view=no_view,
                 menu=Menu(new_data_source_action),
                 ),
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

    workflow = Instance(WorkflowModelView)

    traits_view = View(
        UItem(name='workflow',
              editor=tree_editor,
              show_label=False),
        width=800,
        height=600,
        resizable=True,
        handler=WorkflowHandler())

    def _workflow_default(self):
        return WorkflowModelView()
