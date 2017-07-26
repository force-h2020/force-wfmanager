from pyface.tasks.api import TraitsDockPane
from traitsui.api import (
    ITreeNodeAdapter, ITreeNode, TreeEditor, TreeNode, ListStrEditor, VSplit,
    UItem, View, ModelView, Menu, Action, Handler, VGroup, Tabbed)
from traits.api import (Button, Instance, List, provides,
                        register_factory, on_trait_change, Property)

from force_bdss.api import (
    BaseMCOModel, BaseDataSourceModel, BaseKPICalculatorModel,
    BaseMultiCriteriaOptimizerBundle, BaseDataSourceBundle,
    BaseKPICalculatorBundle)

from force_bdss.workspecs.workflow import Workflow

from .view_utils import get_bundle_name, ListAdapter
from .new_data_source_modal import NewDataSourceModal
from .new_kpi_calculator_modal import NewKPICalculatorModal

# Create an empty view and menu for objects that have no data to display:
no_view = View()
no_menu = Menu()


class WorkflowHandler(Handler):
    new_data_source_modal = Instance(NewDataSourceModal)
    new_kpi_calculator_modal = Instance(NewKPICalculatorModal)

    # Menu actions in the TreeEditor
    def new_mco_handler(self, editor, object):
        """ Opens a dialog for creating a MCO """

    def new_data_source_handler(self, editor, object):
        """ Opens a dialog for creating a Data Source """
        self.new_data_source_modal.configure_traits()

    def new_kpi_calculator_handler(self, editor, object):
        """ Opens a dialog for creating a KPI Calculator """
        self.new_kpi_calculator_modal.configure_traits()

    def delete_mco_handler(self, editor, object):
        editor.object.workflow.model.multi_criteria_optimizer = None

    def delete_data_source_handler(self, editor, object):
        editor.object.workflow.model.data_sources.remove(object)

    def delete_kpi_calculator_handler(self, editor, object):
        editor.object.workflow.model.kpi_calculators.remove(object)

    # On trait changed listeners
    def object_workflow_changed(self, info):
        self.new_data_source_modal.workflow = info.object.workflow.model
        self.new_kpi_calculator_modal.workflow = info.object.workflow.model

    def object_available_data_sources_changed(self, info):
        self.new_data_source_modal.available_data_sources = \
            info.object.available_data_sources

    def object_available_kpi_calculators_changed(self, info):
        self.new_kpi_calculator_modal.available_kpi_calculators = \
            info.object.available_kpi_calculators

    def _new_data_source_modal_default(self):
        return NewDataSourceModal()

    def _new_kpi_calculator_modal_default(self):
        return NewKPICalculatorModal()

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

    add_mco_button = Button("Add")

    workflow = Instance(WorkflowModelView)

    traits_view = View(VSplit(
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
        )),
        width=800,
        height=600,
        resizable=True,
        handler=WorkflowHandler())

    def _workflow_default(self):
        return WorkflowModelView()

    @on_trait_change('add_mco_button')
    def add_mco(self):
        if self.selected_mco is not None:
            self.workflow.model.multi_criteria_optimizer = \
                self.selected_mco.create_model()
