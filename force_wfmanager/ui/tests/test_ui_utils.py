import unittest

from force_bdss.tests.dummy_classes.extension_plugin import \
    DummyExtensionPlugin

from force_wfmanager.ui.ui_utils import get_factory_name, model_info
from force_wfmanager.tests.dummy_classes import DummyFactory, DummyModel


class TestUiUtils(unittest.TestCase):

    def setUp(self):

        self.plugin = DummyExtensionPlugin()
        self.factory = DummyFactory(self.plugin)
        self.model = DummyModel(self.factory)

    def test_get_factory_name(self):

        self.assertEqual(
            get_factory_name(self.factory),
            'Really cool factory')

    def test_model_info(self):

        self.assertEqual(model_info(None), [])
        self.assertEqual(model_info(self.model), ['test_trait'])
