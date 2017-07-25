import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from traits.api import String

from force_bdss.core_plugins.dummy_mco.dakota.dakota_bundle import DakotaBundle
from force_bdss.core_plugins.csv_extractor.csv_extractor.csv_extractor_bundle \
    import CSVExtractorBundle
from force_bdss.core_plugins.dummy_kpi.kpi_adder.kpi_adder_bundle import (
    KPIAdderBundle)
from force_bdss.api import (
    BaseMCOModel, BaseDataSourceModel, BaseKPICalculatorModel,
    BaseDataSourceBundle)
from force_bdss.workspecs.workflow import Workflow

from force_wfmanager.left_side_pane.workflow_settings import (
    WorkflowSettings, get_bundle_name, TreeEditorHandler, WorkflowModelView)


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
        self.assertIsNone(self.settings.selected_mco)
        self.assertIsNone(self.settings.selected_data_source)
        self.assertIsNone(self.settings.selected_kpi_calculator)

        self.assertIsNone(self.workflow.multi_criteria_optimizer)
        self.assertEqual(len(self.workflow.data_sources), 0)
        self.assertEqual(len(self.workflow.kpi_calculators), 0)

        self.assertEqual(len(self.settings.workflow.mco_representation), 0)
        self.assertEqual(
            len(self.settings.workflow.data_sources_representation), 0)
        self.assertEqual(
            len(self.settings.workflow.kpi_calculators_representation), 0)

    def test_add_multi_criteria_optimizer(self):
        # Simulate pressing add mco button (should do nothing)
        self.settings.add_mco()
        self.assertIsNone(self.workflow.multi_criteria_optimizer)

        # Simulate selecting an mco bundle in the list
        self.settings.selected_mco = self.settings.available_mcos[0]

        # Simulate pressing add mco button
        self.settings.add_mco()
        self.assertIsInstance(
            self.workflow.multi_criteria_optimizer,
            BaseMCOModel)
        old_mco = self.workflow.multi_criteria_optimizer

        # Simulate pressing add mco button again to create a new mco model
        self.settings.add_mco()
        self.assertNotEqual(
            self.workflow.multi_criteria_optimizer,
            old_mco)

        self.assertEqual(len(self.settings.workflow.mco_representation), 1)

    def test_add_data_source(self):
        # Simulate pressing add data_source button (should do nothing)
        self.settings.add_data_source()
        self.assertEqual(len(self.workflow.data_sources), 0)

        # Simulate selecting a data_source bundle in the list
        self.settings.selected_data_source = \
            self.settings.available_data_sources[0]

        # Simulate pressing add data_source button
        self.settings.add_data_source()
        self.assertIsInstance(
            self.workflow.data_sources[0],
            BaseDataSourceModel)

        self.assertEqual(
            len(self.settings.workflow.data_sources_representation), 1)

        # Simulate pressing add data_source button again
        self.settings.add_data_source()
        self.assertIsInstance(
            self.workflow.data_sources[1],
            BaseDataSourceModel)
        self.assertNotEqual(
            self.workflow.data_sources[0],
            self.workflow.data_sources[1])

        self.assertEqual(
            len(self.settings.workflow.data_sources_representation), 2)

    def test_add_kpi_calculator(self):
        # Simulate pressing add kpi_calculator button (should do nothing)
        self.settings.add_kpi_calculator()
        self.assertEqual(len(self.workflow.kpi_calculators), 0)

        # Simulate selecting a kpi_calculator bundle in the list
        self.settings.selected_kpi_calculator = \
            self.settings.available_kpi_calculators[0]

        # Simulate pressing add kpi_calculator button
        self.settings.add_kpi_calculator()
        self.assertIsInstance(
            self.workflow.kpi_calculators[0],
            BaseKPICalculatorModel)

        self.assertEqual(
            len(self.settings.workflow.kpi_calculators_representation), 1)

        # Simulate pressing add kpi_calculator button again
        self.settings.add_kpi_calculator()
        self.assertIsInstance(
            self.workflow.kpi_calculators[1],
            BaseKPICalculatorModel)
        self.assertNotEqual(
            self.workflow.kpi_calculators[0],
            self.workflow.kpi_calculators[1])

        self.assertEqual(
            len(self.settings.workflow.kpi_calculators_representation), 2)

    def test_get_bundle_name(self):
        named_bundle = NamedBundle()
        self.assertEqual(
            get_bundle_name(named_bundle), 'Really cool bundle')

        unnamed_bundle = UnnamedBundle()
        self.assertEqual(
            get_bundle_name(unnamed_bundle), 'enthought.test.bundle.unnamed')


class TestTreeEditorHandler(unittest.TestCase):
    def setUp(self):
        self.handler = TreeEditorHandler()

        self.emptyWorkflow = WorkflowModelView(
            model=Workflow(
                multi_criteria_optimizer=None,
                data_sources=[],
                kpi_calculators=[])
        )

        self.filledWorkflow = WorkflowModelView(
            model=Workflow(
                multi_criteria_optimizer=mock.Mock(spec=BaseMCOModel),
                data_sources=[mock.Mock(spec=BaseDataSourceModel),
                              mock.Mock(spec=BaseDataSourceModel)],
                kpi_calculators=[mock.Mock(spec=BaseKPICalculatorModel)])
        )

    def test_delete_mco_is_disabled(self):
        self.assertFalse(
            self.handler.delete_mco_is_enabled(None, self.emptyWorkflow)
        )

    def test_delete_mco_is_enabled(self):
        self.assertTrue(
            self.handler.delete_mco_is_enabled(None, self.filledWorkflow)
        )

    def test_delete_data_sources_is_disabled(self):
        self.assertFalse(
            self.handler.delete_data_sources_is_enabled(
                None, self.emptyWorkflow)
        )

    def test_delete_data_sources_is_enabled(self):
        self.assertTrue(
            self.handler.delete_data_sources_is_enabled(
                None, self.filledWorkflow)
        )

    def test_delete_kpi_calculators_is_disabled(self):
        self.assertFalse(
            self.handler.delete_kpi_calculators_is_enabled(
                None, self.emptyWorkflow)
        )

    def test_delete_kpi_calculators_is_enabled(self):
        self.assertTrue(
            self.handler.delete_kpi_calculators_is_enabled(
                None, self.filledWorkflow)
        )

    def test_delete_mco(self):
        self.assertIsNotNone(
            self.filledWorkflow.model.multi_criteria_optimizer)
        self.handler.delete_mco_handler(None, self.filledWorkflow)
        self.assertIsNone(
            self.filledWorkflow.model.multi_criteria_optimizer)

    def test_delete_data_sources(self):
        self.assertNotEqual(
            len(self.filledWorkflow.model.data_sources), 0)
        self.handler.delete_data_sources_handler(None, self.filledWorkflow)
        self.assertEqual(
            len(self.filledWorkflow.model.data_sources), 0)

    def test_delete_kpi_calculators(self):
        self.assertNotEqual(
            len(self.filledWorkflow.model.kpi_calculators), 0)
        self.handler.delete_kpi_calculators_handler(None, self.filledWorkflow)
        self.assertEqual(
            len(self.filledWorkflow.model.kpi_calculators), 0)
