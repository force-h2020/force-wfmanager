import unittest
try:
    import mock
except:
    from unittest import mock

from envisage.plugin import Plugin

from traits.api import String

from force_bdss.api import BaseDataSourceFactory

from force_wfmanager.left_side_pane.view_utils import get_factory_name


class NamedFactory(BaseDataSourceFactory):
    id = String('enthought.test.factory.named')
    name = String('   Really cool factory  ')

    def create_data_source(self, application, model):
        pass

    def create_model(self, model_data=None):
        pass


class UnnamedFactory(BaseDataSourceFactory):
    id = String('enthought.test.factory.unnamed')

    def create_data_source(self, application, model):
        pass

    def create_model(self, model_data=None):
        pass


class FactoryNameTest(unittest.TestCase):
    def test_get_factory_name(self):
        plugin = mock.Mock(spec=Plugin)

        named_factory = NamedFactory(plugin)
        self.assertEqual(
            get_factory_name(named_factory),
            'Really cool factory')

        unnamed_factory = UnnamedFactory(plugin)
        self.assertEqual(
            get_factory_name(unnamed_factory),
            'enthought.test.factory.unnamed')
