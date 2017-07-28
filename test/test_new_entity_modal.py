import unittest

from traits.api import HasTraits, Instance

from force_bdss.core_plugins.dummy.dummy_dakota.dakota_bundle import (
    DummyDakotaBundle)
from force_bdss.core_plugins.dummy.csv_extractor.csv_extractor_bundle import (
    CSVExtractorBundle)
from force_bdss.core_plugins.dummy.kpi_adder.kpi_adder_bundle import (
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
        self.available_mcos = [DummyDakotaBundle()]
        self.available_data_sources = [CSVExtractorBundle()]
        self.available_kpi_calculators = [KPIAdderBundle()]

        self.workflow = WorkflowModelView(
            model=Workflow()
        )

        self.handler = ModalHandler()

    def _get_new_mco_dialog(self):
        modal = NewEntityModal(
            workflow=self.workflow,
            available_factories=self.available_mcos
        )
        return modal, ModalInfoDummy(object=modal)

    def _get_new_data_source_dialog(self):
        modal = NewEntityModal(
            workflow=self.workflow,
            available_factories=self.available_data_sources
        )
        return modal, ModalInfoDummy(object=modal)

    def _get_new_kpi_calculator_dialog(self):
        modal = NewEntityModal(
            workflow=self.workflow,
            available_factories=self.available_kpi_calculators
        )
        return modal, ModalInfoDummy(object=modal)

    def test_add_mco(self):
        modal, modal_info = self._get_new_mco_dialog()

        # Simulate pressing add mco button (should do nothing, because no mco
        # is selected)
        self.handler.object_add_button_changed(modal_info)
        self.assertIsNone(self.workflow.model.mco)

        # Simulate selecting an mco bundle in the list
        modal, modal_info = self._get_new_mco_dialog()
        modal.selected_factory = modal.available_factories[0]

        # Simulate pressing add mco button
        self.handler.object_add_button_changed(modal_info)
        self.assertIsInstance(self.workflow.model.mco, BaseMCOModel)
        old_mco = self.workflow.model.mco

        # Simulate selecting an mco bundle in the list
        modal, modal_info = self._get_new_mco_dialog()
        modal.selected_factory = modal.available_factories[0]

        # Simulate pressing add mco button again to create a new mco model
        self.handler.object_add_button_changed(modal_info)
        self.assertNotEqual(self.workflow.model.mco, old_mco)

        self.assertEqual(len(self.workflow.mco_representation), 1)

    def test_add_data_source(self):
        modal, modal_info = self._get_new_data_source_dialog()

        # Simulate pressing add data_source button (should do nothing)
        self.handler.object_add_button_changed(modal_info)
        self.assertEqual(len(self.workflow.model.data_sources), 0)

        # Simulate selecting a data_source bundle in the list
        modal, modal_info = self._get_new_data_source_dialog()
        modal.selected_factory = modal.available_factories[0]

        # Simulate pressing add data_source button
        self.handler.object_add_button_changed(modal_info)
        self.assertIsInstance(
            self.workflow.model.data_sources[0],
            BaseDataSourceModel)

        self.assertEqual(len(self.workflow.data_sources_representation), 1)

        # Simulate selecting a data_source bundle in the list
        modal, modal_info = self._get_new_data_source_dialog()
        modal.selected_factory = modal.available_factories[0]

        # Simulate pressing add data_source button again
        self.handler.object_add_button_changed(modal_info)
        self.assertIsInstance(
            self.workflow.model.data_sources[1],
            BaseDataSourceModel)
        self.assertNotEqual(
            self.workflow.model.data_sources[0],
            self.workflow.model.data_sources[1])

        self.assertEqual(len(self.workflow.data_sources_representation), 2)

    def test_add_kpi_calculator(self):
        modal, modal_info = self._get_new_kpi_calculator_dialog()

        # Simulate pressing add kpi_calculator button (should do nothing)
        self.handler.object_add_button_changed(modal_info)
        self.assertEqual(len(self.workflow.model.kpi_calculators), 0)

        # Simulate selecting a kpi_calculator bundle in the list
        modal, modal_info = self._get_new_kpi_calculator_dialog()
        modal.selected_factory = modal.available_factories[0]

        # Simulate pressing add kpi_calculator button
        self.handler.object_add_button_changed(modal_info)
        self.assertIsInstance(
            self.workflow.model.kpi_calculators[0],
            BaseKPICalculatorModel)

        self.assertEqual(len(self.workflow.kpi_calculators_representation), 1)

        # Simulate selecting a kpi_calculator bundle in the list
        modal, modal_info = self._get_new_kpi_calculator_dialog()
        modal.selected_factory = modal.available_factories[0]

        # Simulate pressing add kpi_calculator button again
        self.handler.object_add_button_changed(modal_info)
        self.assertIsInstance(
            self.workflow.model.kpi_calculators[1],
            BaseKPICalculatorModel)
        self.assertNotEqual(
            self.workflow.model.kpi_calculators[0],
            self.workflow.model.kpi_calculators[1])

        self.assertEqual(len(self.workflow.kpi_calculators_representation), 2)

    def test_cancel_button(self):
        modal, modal_info = self._get_new_mco_dialog()

        # Simulate selecting a kpi_calculator bundle in the list
        modal.selected_factory = modal.available_factories[0]

        # Simulate pressing cancel button
        self.handler.object_cancel_button_changed(modal_info)
