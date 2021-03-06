#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from force_bdss.tests.probe_classes.factory_registry import (
    ProbeFactoryRegistry
)
from force_wfmanager.ui import BasePlot

from force_wfmanager.wfmanager import WfManager
from force_wfmanager.plugins.wfmanager_plugin import WfManagerPlugin
from force_wfmanager.wfmanager_review_task import WfManagerReviewTask
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask


class ProbeWfManagerPlugin(WfManagerPlugin):

    def __init__(self, filename):
        self.filename = filename
        super(ProbeWfManagerPlugin, self).__init__()

    def _create_setup_task(self):
        wf_manager_task = WfManagerSetupTask(
            factory_registry=ProbeFactoryRegistry())
        if self.filename is not None:
            wf_manager_task.load_workflow(self.filename)
        return wf_manager_task

    def _create_review_task(self):
        wf_manager_task = WfManagerReviewTask(
            factory_registry=ProbeFactoryRegistry())
        return wf_manager_task


class ProbeWfManager(WfManager):

    def __init__(self, filename=None):

        plugins = [CorePlugin(), TasksPlugin(),
                   ProbeWfManagerPlugin(filename)]

        super(ProbeWfManager, self).__init__(plugins=plugins)

        # 'Run' the application by creating windows without an event loop
        self.run = self._create_windows


class ProbePlot(BasePlot):

    def customize_plot(self, plot):
        dummy_plot = plot.plot(('x', 'y'))[0]
        self._axis = dummy_plot
