from unittest import mock

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from pyface.tasks.api import TaskWindow

from force_bdss.api import Workflow
from force_bdss.tests.probe_classes.factory_registry import (
    ProbeFactoryRegistry
)

from force_wfmanager.plugins.wfmanager_plugin import WfManagerPlugin
from force_wfmanager.model.analysis_model import AnalysisModel

from force_wfmanager.wfmanager import WfManager
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


def get_dummy_wfmanager(filename=None):
    plugins = [CorePlugin(), TasksPlugin(),
               mock_wfmanager_plugin(filename)]
    wfmanager = WfManager(plugins=plugins)
    # 'Run' the application by creating windows without an event loop
    wfmanager.run = wfmanager._create_windows
    return wfmanager


def get_dummy_wfmanager_tasks():
    # Returns the Setup and Results Tasks, with a mock TaskWindow and dummy
    # Application which does not have an event loop.

    plugins = [CorePlugin(), TasksPlugin()]
    app = WfManager(plugins=plugins)
    app.run = lambda: None

    analysis_model = AnalysisModel()
    workflow_model = Workflow()
    factory_registry_plugin = ProbeFactoryRegistry()

    setup_task = WfManagerSetupTask(
        analysis_model=analysis_model, workflow_model=workflow_model,
        factory_registry=factory_registry_plugin
    )

    results_task = WfManagerResultsTask(
        analysis_model=analysis_model, workflow_model=workflow_model,
        factory_registry=factory_registry_plugin
    )
    tasks = [setup_task, results_task]

    for task in tasks:
        mock_window = mock.Mock(spec=TaskWindow)
        mock_window.tasks = tasks
        task.window = mock_window
        task.window.application = app
        task.window.application.factory_registry = factory_registry_plugin

        task.create_central_pane()
        task.create_dock_panes()

    return tasks[0], tasks[1]
