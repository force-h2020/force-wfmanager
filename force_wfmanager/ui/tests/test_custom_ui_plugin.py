#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import unittest

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from force_bdss.api import plugin_id
from force_bdss.core_plugins.service_offer_plugin import \
    ServiceOfferExtensionPlugin
from force_bdss.core_plugins.factory_registry_plugin import \
    FactoryRegistryPlugin

from force_wfmanager.plugins.wfmanager_plugin import WfManagerPlugin
from force_wfmanager.tests.dummy_classes.dummy_factory import DummyFactory
from force_wfmanager.ui import (
    ContributedUI, IContributedUI, IDataView)
from force_wfmanager.wfmanager import WfManager
from force_wfmanager.tests.probe_classes import ProbePlot


class ExampleCustomUIPlugin(ServiceOfferExtensionPlugin):

    id = plugin_id("enthought", "test", 4)

    def get_name(self):
        return "Example Custom UI"

    def get_version(self):
        return 4

    def get_factory_classes(self):
        return [DummyFactory]

    def get_contributed_uis(self):
        return [ContributedUI, ContributedUI]

    def get_base_plots(self):
        return [ProbePlot, ProbePlot]

    def get_service_offer_factories(self):
        return [
            (IDataView, self.get_base_plots()),
            (IContributedUI, self.get_contributed_uis())
        ]


class TestContributedUIPlugin(unittest.TestCase):

    def test_contributes_service(self):
        plugins = [
            CorePlugin(), TasksPlugin(), FactoryRegistryPlugin(),
            WfManagerPlugin(workflow_file=None), ExampleCustomUIPlugin()
        ]
        wfmanager = WfManager(plugins=plugins)
        wfmanager.plugin_manager.start()

        self.assertEqual(len(wfmanager.get_services(IContributedUI)), 2)
        self.assertEqual(len(wfmanager.get_services(IDataView)), 2)
