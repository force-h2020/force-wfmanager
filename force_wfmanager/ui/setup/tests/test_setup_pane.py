from unittest import TestCase

from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from force_bdss.mco.base_mco_model import BaseMCOModel
from force_bdss.tests.probe_classes.factory_registry import (
    ProbeFactoryRegistry
)

from force_wfmanager.tests.probe_classes import (
    ProbeWfManager
)
from force_wfmanager.ui.setup.workflow_model_view import (
    WorkflowModelView
)
from force_bdss.tests.probe_classes.data_source import (
    ProbeDataSourceFactory
)
from force_bdss.tests.probe_classes.probe_extension_plugin import (
    ProbeExtensionPlugin
)
from force_wfmanager.ui.setup.execution_layers.\
    data_source_model_view import DataSourceModelView


class TestSetupPane(GuiTestAssistant, TestCase):

    def setUp(self):
        super(TestSetupPane, self).setUp()
        self.wfmanager = ProbeWfManager()
        self.wfmanager.run()
        self.setup_pane = self.wfmanager.windows[0].central_pane
        self.workflow_tree = (
            self.wfmanager.windows[0].tasks[0].side_pane.workflow_tree
        )
        self.workflow_tree.workflow_mv = WorkflowModelView()
        self.workflow_tree._factory_registry = ProbeFactoryRegistry()

    def test_sync_selected_mv(self):
        plugin = ProbeExtensionPlugin()
        factory = ProbeDataSourceFactory(plugin=plugin)
        model = factory.create_model()
        registry = self.workflow_tree.workflow_mv.variable_names_registry
        data_source_mv = DataSourceModelView(
            model=model,
            variable_names_registry=registry
        )

        try:
            self.workflow_tree.selected_mv = data_source_mv
        except AttributeError:
            self.fail("ProbeDataSourceModel traits_view not found")

        self.assertEqual(self.setup_pane.selected_model, model)
        self.assertEqual(self.setup_pane.selected_model,
                         self.workflow_tree.selected_mv.model)

    def test_add_entity_button(self):
        self.assertEqual(0, len(self.workflow_tree.workflow_mv.mco_mv))
        self.workflow_tree.on_selection(
            'MCO',
            self.workflow_tree._factory_registry.mco_factories,
            self.workflow_tree.new_mco,
            None,
            self.workflow_tree.workflow_mv
        )
        self.workflow_tree.entity_creator.model = BaseMCOModel(
            factory=self.workflow_tree._factory_registry.mco_factories[0])
        self.setup_pane.add_new_entity_btn = True
        self.assertEqual(1, len(self.workflow_tree.workflow_mv.mco_mv))

    def test_remove_entity_button(self):
        self.assertEqual(
            0, len(self.workflow_tree.workflow_mv.execution_layers_mv))
        self.workflow_tree.on_selection(
            'ExecutionLayer',
            None,
            self.workflow_tree.new_layer,
            None,
            self.workflow_tree.workflow_mv
        )
        self.setup_pane.add_new_entity_btn = True
        self.assertEqual(
            1, len(self.workflow_tree.workflow_mv.execution_layers_mv))

        self.workflow_tree.on_selection(
            'DataSources',
            self.workflow_tree._factory_registry.data_source_factories,
            self.workflow_tree.new_data_source,
            self.workflow_tree.delete_layer,
            self.workflow_tree.workflow_mv.execution_layers_mv[0]
        )
        self.setup_pane.remove_entity_btn = True
        self.assertEqual(0, len(
            self.workflow_tree.workflow_mv.execution_layers_mv))
