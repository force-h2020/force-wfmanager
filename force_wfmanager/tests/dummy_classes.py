from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from force_bdss.api import (
    BaseDataSourceFactory)

from force_bdss.tests.dummy_classes.data_source import DummyDataSource, \
    DummyDataSourceModel

from force_wfmanager.wfmanager import WfManager


class DummyWfManager(WfManager):

    def __init__(self):

        plugins = [CorePlugin(), TasksPlugin()]
        super(DummyWfManager, self).__init__(plugins=plugins)
        self.run = lambda: None


class DummyFactory(BaseDataSourceFactory):
    def get_data_source_class(self):
        return DummyDataSource

    def get_model_class(self):
        return DummyDataSourceModel

    def get_identifier(self):
        return "factory"

    def get_name(self):
        return '   Really cool factory  '
