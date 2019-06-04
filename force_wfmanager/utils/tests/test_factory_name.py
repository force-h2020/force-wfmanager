import unittest

from force_bdss.tests.dummy_classes.data_source import DummyDataSource, \
    DummyDataSourceModel
from force_bdss.tests.dummy_classes.extension_plugin import \
    DummyExtensionPlugin

from force_bdss.api import BaseDataSourceFactory

from force_wfmanager.utils.view_utils import get_factory_name


class Factory(BaseDataSourceFactory):
    def get_data_source_class(self):
        return DummyDataSource

    def get_model_class(self):
        return DummyDataSourceModel

    def get_identifier(self):
        return "factory"

    def get_name(self):
        return '   Really cool factory  '


class TestFactoryName(unittest.TestCase):
    def test_get_factory_name(self):
        plugin = DummyExtensionPlugin()

        factory = Factory(plugin)
        self.assertEqual(
            get_factory_name(factory),
            'Really cool factory')
