import unittest

from unittest import mock

from force_wfmanager.central_pane.graph_pane import GraphPane
from force_wfmanager.central_pane.setup_pane import SetupPane
from pyface.tasks.api import TaskWindow

from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from force_bdss.tests.probe_classes.factory_registry_plugin import \
    ProbeFactoryRegistryPlugin
from force_bdss.api import Workflow

from force_wfmanager.wfmanager import WfManager
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask
from force_wfmanager.wfmanager_results_task import WfManagerResultsTask
from force_wfmanager.left_side_pane.tree_pane import TreePane
from force_wfmanager.left_side_pane.results_pane import ResultsPane
from force_wfmanager.central_pane.analysis_model import AnalysisModel

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin


def get_wfmanager_tasks():
    # Returns the Setup and Results Tasks, with a mock TaskWindow and dummy
    # Application which does not have an event loop.
    app = dummy_wfmanager()
    analysis_m = app.analysis_m
    workflow_m = app.workflow_m
    factory_registry_plugin = ProbeFactoryRegistryPlugin()
    setup_task = WfManagerSetupTask(
        analysis_m=analysis_m, workflow_m=workflow_m,
        factory_registry=factory_registry_plugin
    )
    results_task = WfManagerResultsTask(
        analysis_m=analysis_m, workflow_m=workflow_m,
        factory_registry=factory_registry_plugin
    )
    tasks = [setup_task, results_task]

    for task in tasks:
        task.window = mock.Mock(spec=TaskWindow)
        task.window.application = app
        task.window.application.factory_registry = factory_registry_plugin

        task.create_central_pane()
        task.create_dock_panes()

    return tasks[0], tasks[1]


def dummy_wfmanager():
    plugins = [CorePlugin(), TasksPlugin()]
    wfmanager = WfManager(plugins=plugins, workflow_file=None)
    wfmanager.run = lambda: None
    return wfmanager


class TestWFManagerTasks(GuiTestAssistant, unittest.TestCase):
    def setUp(self):
        super(TestWFManagerTasks, self).setUp()
        self.setup_task, self.results_task = get_wfmanager_tasks()

    def test_init(self):
        self.assertIsInstance(self.setup_task.create_central_pane(),
                              SetupPane)
        self.assertEqual(len(self.setup_task.create_dock_panes()), 1)
        self.assertIsInstance(self.setup_task.side_pane, TreePane)

        self.assertEqual(len(self.results_task.create_dock_panes()),
                         1)
        self.assertIsInstance(self.results_task.side_pane,
                              ResultsPane)
        self.assertIsInstance(self.results_task.create_central_pane(),
                              GraphPane)

    def test_app_property_sync(self):
        # Check if shared properties track each other properly

        old_workflow = self.setup_task.app.workflow_m
        self.assertTrue(self.object_consistent('workflow_m'))
        self.setup_task.app.workflow_m = Workflow()
        self.assertTrue(self.object_consistent('workflow_m'))
        self.assertNotEqual(old_workflow, self.setup_task.app.workflow_m)

        old_analysismodel = self.setup_task.app.analysis_m
        self.assertTrue(self.object_consistent('analysis_m'))
        self.setup_task.app.analysis_m = AnalysisModel()
        self.assertTrue(self.object_consistent('analysis_m'))
        self.assertNotEqual(old_analysismodel, self.setup_task.app.analysis_m)

        old_registry = self.setup_task.app.factory_registry
        self.assertTrue(self.object_consistent('factory_registry'))
        self.setup_task.app.factory_registry = ProbeFactoryRegistryPlugin()
        self.assertTrue(self.object_consistent('factory_registry'))
        self.assertNotEqual(old_registry, self.setup_task.app.factory_registry)

        self.assertFalse((self.setup_task.app.run_enabled and
                          self.setup_task.run_enabled and
                          self.results_task.run_enabled))
        self.setup_task.run_enabled = True
        self.assertTrue((self.setup_task.app.run_enabled and
                         self.setup_task.run_enabled and
                         self.results_task.run_enabled))

        self.setup_task.app.computation_running = True
        self.assertFalse(self.setup_task.save_load_enabled and
                         self.results_task.save_load_enabled)

    def test_app_calls(self):
        self.app_calls(self.setup_task)
        self.app_calls(self.results_task)

    def app_calls(self, task):
        task.app.open_workflow = mock.Mock()
        task.open_workflow()
        self.assertTrue(task.app.open_workflow.called)

        task.app.save_workflow = mock.Mock()
        task.save_workflow()
        self.assertTrue(task.app.save_workflow.called)

        task.app.save_workflow_as = mock.Mock()
        task.save_workflow_as()
        self.assertTrue(task.app.save_workflow_as.called)

        task.app.open_plugins = mock.Mock()
        task.open_plugins()
        self.assertTrue(task.app.open_plugins.called)

        task.app.open_about = mock.Mock()
        task.open_about()
        self.assertTrue(task.app.open_about.called)

        task.app.run_bdss = mock.Mock()
        task.run_bdss()
        self.assertTrue(task.app.run_bdss.called)

        task.app.exit = mock.Mock()
        task.exit()
        self.assertTrue(task.app.exit.called)

    def object_consistent(self, object_name):

        setup_app = getattr(self.setup_task.app, object_name)
        setup_local = getattr(self.setup_task, object_name)
        results_app = getattr(self.results_task.app, object_name)
        results_local = getattr(self.results_task, object_name)

        check_setup = (setup_app == setup_local)
        check_results = (results_app == results_local)
        check_cross = (results_local == setup_local)

        return check_results and check_setup and check_cross
