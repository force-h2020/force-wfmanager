import unittest

from unittest import mock
import subprocess

from pyface.tasks.api import TaskLayout, TaskWindow

from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from force_bdss.tests.probe_classes.factory_registry_plugin import \
    ProbeFactoryRegistryPlugin
from force_bdss.api import WorkflowWriter, Workflow

from force_wfmanager.wfmanager import WfManager
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask
from force_wfmanager.wfmanager_results_task import WfManagerResultsTask
from force_wfmanager.left_side_pane.tree_pane import TreePane
from force_wfmanager.left_side_pane.workflow_tree import WorkflowTree
from force_wfmanager.central_pane.analysis_model import AnalysisModel

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

FILE_DIALOG_PATH = 'force_wfmanager.wfmanager.FileDialog'
INFORMATION_PATH = 'force_wfmanager.wfmanager.information'
CONFIRM_PATH = 'force_wfmanager.wfmanager_setup_task.confirm'
FILE_OPEN_PATH = 'force_wfmanager.wfmanager.open'
WORKFLOW_WRITER_PATH = 'force_wfmanager.wfmanager.WorkflowWriter'
WORKFLOW_READER_PATH = 'force_wfmanager.wfmanager.WorkflowReader'
ERROR_PATH = 'force_wfmanager.wfmanager_setup_task.error'
SUBPROCESS_PATH = 'force_wfmanager.wfmanager_setup_task.subprocess'
OS_REMOVE_PATH = 'force_wfmanager.wfmanager_setup_task.os.remove'
ZMQSERVER_SETUP_SOCKETS_PATH = \
    'force_wfmanager.wfmanager.ZMQServer._setup_sockets'


def get_wfmanager_task(task_name):
    # Returns the specified Task, with a mock TaskWindow and dummy Application
    # which does not have an event loop.

    if task_name == "Setup":
        wfmanager_task = WfManagerSetupTask(analysis_m=AnalysisModel(),
                                            workflow_m=Workflow())
    elif task_name == "Results":
        wfmanager_task = WfManagerResultsTask(analysis_m=AnalysisModel(),
                                              workflow_m=Workflow())
    else:
        raise ValueError
    wfmanager_task.window = mock.Mock(spec=TaskWindow)
    wfmanager_task.window.application = dummy_wfmanager()

    wfmanager_task.window.application.factory_registry = \
        ProbeFactoryRegistryPlugin()
    wfmanager_task.window.application.exit = mock.Mock()

    wfmanager_task.create_central_pane()
    wfmanager_task.create_dock_panes()

    return wfmanager_task


def mock_file_writer(*args, **kwargs):
    def write(*args, **kwargs):
        return ''
    writer = mock.Mock(spec=WorkflowWriter)
    writer.write = write
    return writer


def mock_confirm_function(result):
    def mock_conf(*args, **kwargs):
        return result
    return mock_conf


def mock_dialog(dialog_class, result, path=''):
    def mock_dialog_call(*args, **kwargs):
        dialog = mock.Mock(spec=dialog_class)
        dialog.open = lambda: result
        dialog.path = path
        return dialog
    return mock_dialog_call


def mock_subprocess(*args, **kwargs):
    def check_call(*args, **kwargs):
        return
    mock_subprocess_module = mock.Mock(spec=subprocess)
    mock_subprocess_module.check_call = check_call
    return mock_subprocess_module


def mock_show_error(*args, **kwargs):
    return args


def dummy_wfmanager():

    plugins = [CorePlugin(), TasksPlugin()]
    wfmanager = WfManager(plugins=plugins, workflow_file=None)
    wfmanager.run = lambda: None
    return wfmanager


class TestWFManagerTasks(GuiTestAssistant, unittest.TestCase):
    def setUp(self):
        super(TestWFManagerTasks, self).setUp()
        self.wfmanager_setup_task = get_wfmanager_task("Setup")
        self.wfmanager_results_task = get_wfmanager_task("Results")

    def test_init(self):
        self.assertEqual(len(self.wfmanager_setup_task.create_dock_panes()), 1)
        self.assertIsInstance(self.wfmanager_setup_task.side_pane, TreePane)
        self.assertIsInstance(
            self.wfmanager_setup_task.side_pane.workflow_tree, WorkflowTree)
        self.assertIsInstance(self.wfmanager_setup_task.default_layout,
                              TaskLayout)
