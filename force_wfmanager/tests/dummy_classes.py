from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin
from traits.api import HasTraits, Instance
from traitsui.api import VGroup, View

from force_bdss.api import (
    BaseDataSourceFactory
)
from force_bdss.tests.dummy_classes.data_source import (
    DummyDataSource, DummyDataSourceModel
)
from force_bdss.tests.dummy_classes.extension_plugin import (
    DummyExtensionPlugin
)

from force_wfmanager.ui.review.data_view import BaseDataView
from force_wfmanager.wfmanager import WfManager


class DummyUI:
    def dispose(self):
        pass


class DummyModelInfo(HasTraits):

    object = Instance(HasTraits)

    ui = Instance(DummyUI)

    def _ui_default(self):
        return DummyUI()


class DummyWfManager(WfManager):

    def __init__(self):

        plugins = [CorePlugin(), TasksPlugin()]
        super(DummyWfManager, self).__init__(plugins=plugins)

    def run(self):
        pass


class DummyDataView1(BaseDataView):
    description = "Empty data view with a long description"
    view = View(VGroup())


class DummyDataView2(BaseDataView):
    description = None
    view = View(VGroup())


class DummyDataView3(BaseDataView):
    description = (
        "Empty dummy data view that actually has a even longer description")
    view = View(VGroup())


class DummyExtensionPluginWithDataView(DummyExtensionPlugin):
    def get_data_views(self):
        return [DummyDataView1, DummyDataView2, DummyDataView3]


class DummyWfManagerWithPlugins(WfManager):

    def __init__(self):
        plugins = [
            CorePlugin(),
            TasksPlugin(),
            DummyExtensionPluginWithDataView()
        ]
        super(DummyWfManagerWithPlugins, self).__init__(plugins=plugins)

    def run(self):
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
