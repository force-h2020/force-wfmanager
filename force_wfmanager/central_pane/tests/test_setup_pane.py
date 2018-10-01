import unittest
from force_bdss.mco.base_mco_model import BaseMCOModel

from force_bdss.tests.probe_classes.factory_registry_plugin import \
    ProbeFactoryRegistryPlugin
from force_wfmanager.left_side_pane.workflow_model_view import \
    WorkflowModelView

from force_wfmanager.wfmanager import WfManager
from force_wfmanager.wfmanager_plugin import WfManagerPlugin

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant


def dummy_wfmanager():
    plugins = [CorePlugin(), TasksPlugin(), WfManagerPlugin()]
    wfmanager = WfManager(plugins=plugins)
    wfmanager.run = wfmanager._create_windows
    return wfmanager


class TestSetupPane(GuiTestAssistant, unittest.TestCase):

    def setUp(self):
        super(TestSetupPane, self).setUp()
        self.wfmanager = dummy_wfmanager()
        self.wfmanager.run()
        self.setup_pane = self.wfmanager.windows[0].central_pane
        self.workflow_tree = \
            self.wfmanager.windows[0].tasks[0].side_pane.workflow_tree
        self.workflow_tree.workflow_mv = WorkflowModelView()
        self.workflow_tree._factory_registry = ProbeFactoryRegistryPlugin()

    def test_add_entity_button(self):
        self.assertEqual(0, len(self.workflow_tree.workflow_mv.mco_mv))
        self.workflow_tree.mco_factory_selected(self.workflow_tree.workflow_mv)
        self.workflow_tree.current_modal.model = BaseMCOModel(
            factory=self.workflow_tree._factory_registry.mco_factories[0])
        self.setup_pane.add_new_entity = True
        self.assertEqual(1, len(self.workflow_tree.workflow_mv.mco_mv))

    def test_remove_entity_button(self):
        self.assertEqual(
            0, len(self.workflow_tree.workflow_mv.execution_layers_mv))
        self.workflow_tree.execution_layer_factory_selected(
            self.workflow_tree.workflow_mv
        )
        self.setup_pane.add_new_entity = True
        self.assertEqual(
            1, len(self.workflow_tree.workflow_mv.execution_layers_mv))

        self.workflow_tree.datasource_factory_exec_instance_selected(
            self.workflow_tree.workflow_mv.execution_layers_mv[0]
        )
        self.setup_pane.remove_entity = True
        self.assertEqual(0, len(
            self.workflow_tree.workflow_mv.execution_layers_mv))
