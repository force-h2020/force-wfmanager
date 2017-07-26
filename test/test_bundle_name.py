import unittest

from traits.api import String

from force_bdss.api import BaseDataSourceBundle

from force_wfmanager.left_side_pane.view_utils import get_bundle_name


class NamedBundle(BaseDataSourceBundle):
    id = String('enthought.test.bundle.named')
    name = String('   Really cool bundle  ')

    def create_data_source(self, application, model):
        pass

    def create_model(self, model_data=None):
        pass


class UnnamedBundle(BaseDataSourceBundle):
    id = String('enthought.test.bundle.unnamed')

    def create_data_source(self, application, model):
        pass

    def create_model(self, model_data=None):
        pass


class BundleNameTest(unittest.TestCase):
    def test_get_bundle_name(self):
        named_bundle = NamedBundle()
        self.assertEqual(
            get_bundle_name(named_bundle), 'Really cool bundle')

        unnamed_bundle = UnnamedBundle()
        self.assertEqual(
            get_bundle_name(unnamed_bundle), 'enthought.test.bundle.unnamed')
