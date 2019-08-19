import unittest

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from force_bdss.api import plugin_id
from force_bdss.core_plugins.service_offers_plugin import ServiceOffersPlugin
from force_bdss.factory_registry_plugin import FactoryRegistryPlugin

from force_wfmanager.plugins.wfmanager_plugin import WfManagerPlugin
from force_wfmanager.tests.dummy_classes.dummy_factory import DummyFactory
from force_wfmanager.ui import BasePlot, IBasePlot
from force_wfmanager.wfmanager import WfManager


class ExampleUIPlugin(ServiceOffersPlugin):

    id = plugin_id("enthought", "test", 4)

    def get_name(self):
        return "Example"

    def get_version(self):
        return 4

    def get_factory_classes(self):
        return [DummyFactory]

    def get_base_plots(self):
        return [BasePlot, BasePlot]

    def get_service_offer_factories(self):
        return [(IBasePlot, self.get_base_plots())]


class TestServiceOffersPlugin(unittest.TestCase):

    def test_contributes_service(self):
        plugins = [
            CorePlugin(), TasksPlugin(), FactoryRegistryPlugin(),
            WfManagerPlugin(workflow_file=None), ExampleUIPlugin()
        ]
        wfmanager = WfManager(plugins=plugins)
        wfmanager.plugin_manager.start()
        self.assertEqual(len(wfmanager.get_services(IBasePlot)), 2)
