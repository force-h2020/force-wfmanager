from pyface.tasks.api import TraitsDockPane
from traitsui.api import (
    ITreeNodeAdapter, ITreeNode, TreeEditor, TreeNode, UItem, View, Menu,
    Action, Handler)
from traits.api import Instance, List, provides, register_factory

from force_bdss.api import (
    BaseMCOModel, BaseMCOBundle,
    BaseDataSourceModel, BaseDataSourceBundle,
    BaseKPICalculatorModel, BaseKPICalculatorBundle,
    BaseMCOParameter, BaseMCOParameterFactory)
from force_bdss.mco.parameters.core_mco_parameters import all_core_factories

from .view_utils import get_bundle_name
from .new_entity_modal import NewEntityModal
from .workflow_model_view import WorkflowModelView

# Create an empty view and menu for objects that have no data to display:
no_view = View()
no_menu = Menu()


class WorkflowHandler(Handler):
    # Menu actions in the TreeEditor
    def new_mco_handler(self, editor, object):
        """ Opens a dialog for creating a MCO """
        modal = NewEntityModal(
            workflow=editor.object.workflow,
            available_bundles=editor.object.available_mcos)
        modal.configure_traits()

    def new_parameter_handler(self, editor, object):
        """ Opens a dialog for creating a parameter """
        modal = NewEntityModal(
            workflow=editor.object.workflow,
            available_bundles=editor.object.available_parameters)
        modal.configure_traits()

    def new_data_source_handler(self, editor, object):
        """ Opens a dialog for creating a Data Source """
        modal = NewEntityModal(
            workflow=editor.object.workflow,
            available_bundles=editor.object.available_data_sources)
        modal.configure_traits()

    def new_kpi_calculator_handler(self, editor, object):
        """ Opens a dialog for creating a KPI Calculator """
        modal = NewEntityModal(
            workflow=editor.object.workflow,
            available_bundles=editor.object.available_kpi_calculators)
        modal.configure_traits()

    def delete_mco_handler(self, editor, object):
        editor.object.workflow.model.mco = None

    def delete_data_source_handler(self, editor, object):
        editor.object.workflow.model.data_sources.remove(object)

    def delete_kpi_calculator_handler(self, editor, object):
        editor.object.workflow.model.kpi_calculators.remove(object)


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
        return Menu(delete_mco_action, new_parameter_action)

    def allows_children(self):
        return True

    def has_children(self):
        return True

    def get_children(self):
        return self.adaptee.parameters

    def can_auto_open(self):
        return True


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
    available_mcos = List(BaseMCOBundle)

    #: Available parameters factories
    available_parameters = List(Instance(BaseMCOParameterFactory))

    #: Available data source bundles
    available_data_sources = List(BaseDataSourceBundle)

    #: Available KPI calculator bundles
    available_kpi_calculators = List(BaseKPICalculatorBundle)

    #: Selected MCO bundle in the list of MCOs
    selected_mco = Instance(BaseMCOBundle)

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

    def _available_parameters_default(self):
        return all_core_factories()
