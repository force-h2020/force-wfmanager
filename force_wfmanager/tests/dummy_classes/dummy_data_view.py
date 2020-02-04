from traitsui.group import VGroup
from traitsui.view import View

from force_bdss.tests.dummy_classes.extension_plugin import \
    DummyExtensionPlugin
from force_wfmanager.ui.review.base_data_view import BaseDataView


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
