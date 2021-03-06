#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from traitsui.api import Item, VGroup

from force_bdss.api import plugin_id, Workflow
from force_bdss.core_plugins.service_offer_plugin import \
    ServiceOfferExtensionPlugin
from force_wfmanager.tests.dummy_classes.dummy_factory import DummyFactory
from force_wfmanager.ui import ContributedUI, IContributedUI


class DummyContributedUI(ContributedUI):

    name = "DummyUI"

    desc = "Dummy UI"

    workflow_data = {
        "mco":
            {"id": "force.bdss.enthought.plugin.test.v0.factory.mco"}
    }


class DummyContributedUI2(ContributedUI):

    name = "DummyUI"

    desc = "Dummy UI 2"

    workflow_data = {
        "mco":
            {"id": "force.bdss.enthought.plugin.uitest.v2.factory.mco"}
    }

    workflow_group = VGroup(Item("name"))

    def create_workflow(self, factory_registry):
        """Return an empty workflow as a placeholder, since the factories
        referenced in workflow_data don't actually exist"""
        return Workflow()


class DummyUIPlugin(ServiceOfferExtensionPlugin):

    id = plugin_id("enthought", "uitest", 2)

    def get_name(self):
        return "Example"

    def get_version(self):
        return 2

    def get_factory_classes(self):
        return [DummyFactory]

    def get_contributed_uis(self):
        return [DummyContributedUI, DummyContributedUI2]

    def get_service_offer_factories(self):
        return [(IContributedUI, self.get_contributed_uis())]


class DummyUIPluginOld(ServiceOfferExtensionPlugin):

    id = plugin_id("enthought", "uitest", 1)

    def get_name(self):
        return "An Older Example"

    def get_version(self):
        return 1

    def get_factory_classes(self):
        return [DummyFactory]

    def get_contributed_uis(self):
        return [DummyContributedUI, DummyContributedUI2]

    def get_service_offer_factories(self):
        return [(IContributedUI, self.get_contributed_uis())]
