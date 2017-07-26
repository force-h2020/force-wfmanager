import unittest

from traits.api import HasTraits, Instance

from force_bdss.core_plugins.dummy_mco.dakota.dakota_bundle import DakotaBundle
from force_bdss.core_plugins.csv_extractor.csv_extractor.csv_extractor_bundle \
    import CSVExtractorBundle
from force_bdss.core_plugins.dummy_kpi.kpi_adder.kpi_adder_bundle import (
    KPIAdderBundle)
from force_bdss.workspecs.workflow import Workflow
from force_bdss.api import (BaseMCOModel, BaseDataSourceModel,
                            BaseKPICalculatorModel)

from force_wfmanager.left_side_pane.new_entity_modal import (
    ModalHandler, NewEntityModal)
from force_wfmanager.left_side_pane.workflow_settings import WorkflowModelView


class UIDummy():
    def dispose(self, bool):
        return bool


class ModalInfoDummy(HasTraits):
    object = Instance(NewEntityModal)

    ui = Instance(UIDummy)

    def _ui_default(self):
        return UIDummy()


class NewEntityModalTest(unittest.TestCase):
    def setUp(self):
        self.modal = NewEntityModal()

        self.available_mcos = [DakotaBundle()]
        self.available_data_sources = [CSVExtractorBundle()]
        self.available_kpi_calculators = [KPIAdderBundle()]

        self.workflow = WorkflowModelView(
            model=Workflow()
        )

        self.modal.workflow = self.workflow

        self.modal_info = ModalInfoDummy(object=self.modal)

        self.handler = ModalHandler()

    def test_add_multi_criteria_optimizer(self):
        self.modal.available_bundles = self.available_mcos

        # Simulate pressing add mco button (should do nothing, because no mco
        # is selected)
        self.handler.object_add_button_changed(self.modal_info)
        self.assertIsNone(self.workflow.model.multi_criteria_optimizer)

        # Simulate selecting an mco bundle in the list
        self.modal.selected_bundle = self.modal.available_bundles[0]

        # Simulate pressing add mco button
        self.handler.object_add_button_changed(self.modal_info)
        self.assertIsInstance(
            self.workflow.model.multi_criteria_optimizer,
            BaseMCOModel)
        old_mco = self.workflow.model.multi_criteria_optimizer

        # Simulate selecting an mco bundle in the list
        self.modal.selected_bundle = self.modal.available_bundles[0]

        # Simulate pressing add mco button again to create a new mco model
        self.handler.object_add_button_changed(self.modal_info)
        self.assertNotEqual(
            self.workflow.model.multi_criteria_optimizer,
            old_mco)

        self.assertEqual(len(self.workflow.mco_representation), 1)

    def test_add_data_source(self):
        self.modal.available_bundles = self.available_data_sources

        # Simulate pressing add data_source button (should do nothing)
        self.handler.object_add_button_changed(self.modal_info)
        self.assertEqual(len(self.workflow.model.data_sources), 0)

        # Simulate selecting a data_source bundle in the list
        self.modal.selected_bundle = self.modal.available_bundles[0]

        # Simulate pressing add data_source button
        self.handler.object_add_button_changed(self.modal_info)
        self.assertIsInstance(
            self.workflow.model.data_sources[0],
            BaseDataSourceModel)

        self.assertEqual(len(self.workflow.data_sources_representation), 1)

        # Simulate selecting a data_source bundle in the list
        self.modal.selected_bundle = self.modal.available_bundles[0]

        # Simulate pressing add data_source button again
        self.handler.object_add_button_changed(self.modal_info)
        self.assertIsInstance(
            self.workflow.model.data_sources[1],
            BaseDataSourceModel)
        self.assertNotEqual(
            self.workflow.model.data_sources[0],
            self.workflow.model.data_sources[1])

        self.assertEqual(len(self.workflow.data_sources_representation), 2)

    def test_add_kpi_calculator(self):
        self.modal.available_bundles = self.available_kpi_calculators

        # Simulate pressing add kpi_calculator button (should do nothing)
        self.handler.object_add_button_changed(self.modal_info)
        self.assertEqual(len(self.workflow.model.kpi_calculators), 0)

        # Simulate selecting a kpi_calculator bundle in the list
        self.modal.selected_bundle = self.modal.available_bundles[0]

        # Simulate pressing add kpi_calculator button
        self.handler.object_add_button_changed(self.modal_info)
        self.assertIsInstance(
            self.workflow.model.kpi_calculators[0],
            BaseKPICalculatorModel)

        self.assertEqual(len(self.workflow.kpi_calculators_representation), 1)

        # Simulate selecting a kpi_calculator bundle in the list
        self.modal.selected_bundle = self.modal.available_bundles[0]

        # Simulate pressing add kpi_calculator button again
        self.handler.object_add_button_changed(self.modal_info)
        self.assertIsInstance(
            self.workflow.model.kpi_calculators[1],
            BaseKPICalculatorModel)
        self.assertNotEqual(
            self.workflow.model.kpi_calculators[0],
            self.workflow.model.kpi_calculators[1])

        self.assertEqual(len(self.workflow.kpi_calculators_representation), 2)

    def test_cancel_button(self):
        self.modal.available_bundles = self.available_kpi_calculators

        # Simulate selecting a kpi_calculator bundle in the list
        self.modal.selected_bundle = self.modal.available_bundles[0]

        # Simulate pressing cancel button
        self.handler.object_cancel_button_changed(self.modal_info)

        self.assertEqual(self.modal._models, {})
        self.assertIsNone(self.modal.current_model)
        self.assertIsNone(self.modal.selected_bundle)
