import unittest

from force_bdss.tests.dummy_classes.extension_plugin import \
    DummyExtensionPlugin
from force_bdss.tests.probe_classes.data_source import \
    ProbeDataSourceModel

from force_wfmanager.ui.ui_utils import get_factory_name, model_info
from force_wfmanager.tests.dummy_classes import DummyFactory


class TestUiUtils(unittest.TestCase):

    def setUp(self):

        self.plugin = DummyExtensionPlugin()
        self.factory = DummyFactory(self.plugin)
        self.model = ProbeDataSourceModel(self.factory)

    def test_get_factory_name(self):

        self.assertEqual(
            get_factory_name(self.factory),
            'Really cool factory')

    def test_model_info(self):

        self.assertEqual(model_info(None), [])
        self.assertEqual(len(model_info(self.model)), 4)
