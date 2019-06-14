from unittest import mock

from force_bdss.api import Workflow, WorkflowReader, WorkflowWriter
from force_bdss.tests.probe_classes.factory_registry import (
    ProbeFactoryRegistry
)

from force_wfmanager.plugins.wfmanager_plugin import WfManagerPlugin
from force_wfmanager.wfmanager_review_task import WfManagerReviewTask
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask


def mock_create_setup_task(filename):
    def func():
        wf_manager_task = WfManagerSetupTask(
            factory_registry=ProbeFactoryRegistry())
        if filename is not None:
            wf_manager_task.load_workflow(filename)
        return wf_manager_task
    return func


def mock_create_review_task():
    def func():
        wf_manager_task = WfManagerReviewTask(
            factory_registry=ProbeFactoryRegistry())
        return wf_manager_task
    return func


def mock_wfmanager_plugin(filename):
    plugin = WfManagerPlugin()
    plugin._create_setup_task = mock_create_setup_task(filename)
    plugin._create_review_task = mock_create_review_task()
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


def mock_file_writer(*args, **kwargs):
    def write(*args, **kwargs):
        return ''
    writer = mock.Mock(spec=WorkflowWriter)
    writer.write = write
    return writer
