import unittest

from traits.api import String

from force_bdss.core_plugins.dummy_mco.dakota.dakota_bundle import DakotaBundle
from force_bdss.core_plugins.csv_extractor.csv_extractor.csv_extractor_bundle \
    import CSVExtractorBundle
from force_bdss.core_plugins.dummy_kpi.kpi_adder.kpi_adder_bundle import (
    KPIAdderBundle)

from force_bdss.api import (
    BaseMCOModel, BaseDataSourceModel, BaseKPICalculatorModel,
    BaseDataSourceBundle)

from force_wfmanager.left_side_pane.workflow_settings import (
    WorkflowSettings, get_bundle_name)


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


class TestWorkflowSettings(unittest.TestCase):
    def setUp(self):
        self.workflow_settings = WorkflowSettings(
            available_mcos=[DakotaBundle()],
            available_data_sources=[CSVExtractorBundle()],
            available_kpi_calculators=[KPIAdderBundle()]
        )

        self.settings = self.workflow_settings
        self.workflow = self.settings.workflow.model

    def test_ui_initialization(self):
        self.assertIsNone(self.workflow.multi_criteria_optimizer)
        self.assertEqual(len(self.workflow.data_sources), 0)
        self.assertEqual(len(self.workflow.kpi_calculators), 0)

        self.assertEqual(len(self.settings.workflow.mco_representation), 0)
        self.assertEqual(
            len(self.settings.workflow.data_sources_representation), 0)
        self.assertEqual(
            len(self.settings.workflow.kpi_calculators_representation), 0)

    def test_get_bundle_name(self):
        named_bundle = NamedBundle()
        self.assertEqual(
            get_bundle_name(named_bundle), 'Really cool bundle')

        unnamed_bundle = UnnamedBundle()
        self.assertEqual(
            get_bundle_name(unnamed_bundle), 'enthought.test.bundle.unnamed')
