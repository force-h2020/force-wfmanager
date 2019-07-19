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


class TestSetupPane(GuiTestAssistant, TestCase):

    def setUp(self):
        super(TestSetupPane, self).setUp()
        self.wfmanager = ProbeWfManager()
        self.wfmanager.run()
        self.setup_pane = self.wfmanager.windows[0].central_pane
        self.side_pane = self.wfmanager.windows[0].tasks[0].side_pane
        self.workflow_tree = (
            self.wfmanager.windows[0].tasks[0].side_pane.workflow_tree
        )
        self.workflow_tree.workflow_mv = WorkflowModelView()
        self.workflow_tree._factory_registry = ProbeFactoryRegistry()

    def tearDown(self):
        for plugin in self.wfmanager:
            self.wfmanager.remove_plugin(plugin)
        self.wfmanager.exit()
        super(TestSetupPane, self).tearDown()

    def test_add_entity_button(self):
        self.assertEqual(0, len(self.workflow_tree.workflow_mv.mco_mv))
        self.workflow_tree.factory(
            self.workflow_tree._factory_registry.mco_factories,
            self.workflow_tree.new_mco,
            'MCO',
            self.workflow_tree.workflow_mv
        )
        self.workflow_tree.entity_creator.model = BaseMCOModel(
            factory=self.workflow_tree._factory_registry.mco_factories[0])
        self.setup_pane.add_new_entity_btn = True
        self.assertEqual(1, len(self.workflow_tree.workflow_mv.mco_mv))

    def test_remove_entity_button(self):
        self.assertEqual(
            0, len(self.workflow_tree.workflow_mv.execution_layers_mv))
        self.workflow_tree.factory(
            None,
            self.workflow_tree.new_layer,
            'ExecutionLayer',
            self.workflow_tree.workflow_mv
        )
        self.setup_pane.add_new_entity_btn = True
        self.assertEqual(
            1, len(self.workflow_tree.workflow_mv.execution_layers_mv))

        self.workflow_tree.factory_instance(
            self.workflow_tree._factory_registry.data_source_factories,
            self.workflow_tree.new_data_source,
            'DataSources',
            self.workflow_tree.delete_layer,
            self.workflow_tree.workflow_mv.execution_layers_mv[0]
        )
        self.setup_pane.remove_entity_btn = True
        self.assertEqual(0, len(
            self.workflow_tree.workflow_mv.execution_layers_mv))
