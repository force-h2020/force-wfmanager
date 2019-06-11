from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from traits.api import Int

from force_bdss.api import (
    BaseDataSourceFactory, BaseDataSourceModel)

from force_bdss.tests.dummy_classes.data_source import DummyDataSource, \
    DummyDataSourceModel

from force_wfmanager.wfmanager_results_task import WfManagerResultsTask
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask
from force_wfmanager.wfmanager import WfManager

from .mock_methods import mock_wfmanager_plugin


class DummyWfManager(WfManager):

    def __init__(self, filename=None, mode=0):

        plugins = [CorePlugin(), TasksPlugin()]
        if mode == 0:
            plugins += [mock_wfmanager_plugin(filename)]

        super(DummyWfManager, self).__init__(plugins=plugins)

        if mode == 0:
            # 'Run' the application by creating windows without an event loop
            self.run = self._create_windows
        else:
            self.run = lambda: None


class DummyWfManagerSetupTask(WfManagerSetupTask):
    pass


class DummyWfManagerResultsTask(WfManagerResultsTask):
    pass


class DummyFactory(BaseDataSourceFactory):
    def get_data_source_class(self):
        return DummyDataSource

    def get_model_class(self):
        return DummyDataSourceModel

    def get_identifier(self):
        return "factory"

    def get_name(self):
        return '   Really cool factory  '


class DummyModel(BaseDataSourceModel):

    test_trait = Int(1)
