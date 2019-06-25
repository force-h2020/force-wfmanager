from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin
from traits.api import HasTraits, Instance

from force_bdss.api import (
    BaseDataSourceFactory
)
from force_bdss.tests.dummy_classes.data_source import (
    DummyDataSource, DummyDataSourceModel
)
from force_wfmanager.wfmanager import WfManager


class DummyUI:
    def dispose(self):
        pass


class DummyModalInfo(HasTraits):

    object = Instance(HasTraits)

    ui = Instance(DummyUI)

    def _ui_default(self):
        return DummyUI()


class DummyWfManager(WfManager):

    def __init__(self):

        plugins = [CorePlugin(), TasksPlugin()]
        super(DummyWfManager, self).__init__(plugins=plugins)

    # Requires a docstring to silence Sphinx warnings.
    def run(self):
        """Run the application (dummy class: does nothing in this case)."""
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
