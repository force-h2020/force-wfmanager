import unittest

from force_wfmanager.left_side_pane.workflow_settings import WorkflowSettings

from force_bdss.core_plugins.dummy_mco.dakota.dakota_bundle import DakotaBundle
from force_bdss.core_plugins.csv_extractor.csv_extractor.csv_extractor_bundle \
    import CSVExtractorBundle
from force_bdss.core_plugins.dummy_kpi.kpi_adder.kpi_adder_bundle import (
    KPIAdderBundle)
from force_bdss.api import (BaseMCOModel, BaseDataSourceModel,
                            BaseKPICalculatorModel)


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

    def test_add_multi_criteria(self):
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

        # Simulate selecting an data_source bundle in the list
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

        # Simulate selecting an kpi_calculator bundle in the list
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
