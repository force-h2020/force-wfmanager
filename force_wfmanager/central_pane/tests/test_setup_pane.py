import unittest
from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from force_bdss.mco.base_mco_model import BaseMCOModel
from force_bdss.tests.probe_classes.factory_registry_plugin import (
    ProbeFactoryRegistryPlugin
)
from force_wfmanager.left_side_pane.workflow_model_view import (
    WorkflowModelView
)
from force_wfmanager.wfmanager import WfManager
from force_wfmanager.wfmanager_plugin import WfManagerPlugin
from force_wfmanager.wfmanager_results_task import WfManagerResultsTask
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask


def dummy_wfmanager(filename=None):
    plugins = [CorePlugin(), TasksPlugin(),
               mock_wfmanager_plugin(filename)]
    wfmanager = WfManager(plugins=plugins)
    # 'Run' the application by creating windows without an event loop
    wfmanager.run = wfmanager._create_windows
    return wfmanager


def mock_wfmanager_plugin(filename):
    plugin = WfManagerPlugin()
    plugin._create_setup_task = mock_create_setup_task(filename)
    plugin._create_results_task = mock_create_results_task()
    return plugin


def mock_create_setup_task(filename):
    def func():
        wf_manager_task = WfManagerSetupTask(
            factory_registry=ProbeFactoryRegistryPlugin())
        if filename is not None:
            wf_manager_task.open_workflow_file(filename)
        return wf_manager_task
    return func


def mock_create_results_task():
    def func():
        wf_manager_task = WfManagerResultsTask(
            factory_registry=ProbeFactoryRegistryPlugin())
        return wf_manager_task
    return func


class TestSetupPane(GuiTestAssistant, unittest.TestCase):

    def setUp(self):
        super(TestSetupPane, self).setUp()
        self.wfmanager = dummy_wfmanager()
        self.wfmanager.run()
        self.setup_pane = self.wfmanager.windows[0].central_pane
        self.workflow_tree = (
            self.wfmanager.windows[0].tasks[0].side_pane.workflow_tree
        )
        self.workflow_tree.workflow_mv = WorkflowModelView()
        self.workflow_tree._factory_registry = ProbeFactoryRegistryPlugin()

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
