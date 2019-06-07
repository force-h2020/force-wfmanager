from unittest import mock

from force_bdss.api import Workflow, WorkflowReader
from force_bdss.tests.probe_classes.factory_registry import (
    ProbeFactoryRegistry
)

from force_wfmanager.plugins.wfmanager_plugin import WfManagerPlugin
from force_wfmanager.wfmanager_results_task import WfManagerResultsTask
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask
from force_wfmanager.io.workflow_io import load_workflow_file


def mock_create_setup_task(filename):
    def func():
        wf_manager_task = WfManagerSetupTask(
            factory_registry=ProbeFactoryRegistry())
        if filename is not None:
            load_workflow_file(wf_manager_task, filename)
        return wf_manager_task
    return func


def mock_create_results_task():
    def func():
        wf_manager_task = WfManagerResultsTask(
            factory_registry=ProbeFactoryRegistry())
        return wf_manager_task
    return func


def mock_wfmanager_plugin(filename):
    plugin = WfManagerPlugin()
    plugin._create_setup_task = mock_create_setup_task(filename)
    plugin._create_results_task = mock_create_results_task()
    return plugin


def mock_dialog(dialog_class, result, path=''):
    def mock_dialog_call(*args, **kwargs):
        dialog = mock.Mock(spec=dialog_class)
        dialog.open = lambda: result
        dialog.path = path
        return dialog
    return mock_dialog_call


def mock_file_reader(*args, **kwargs):
    def read(*args, **kwargs):
        workflow = Workflow()
        return workflow
    reader = mock.Mock(spec=WorkflowReader)
    reader.read = read
    return reader
