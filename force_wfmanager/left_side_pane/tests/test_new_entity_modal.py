import unittest
try:
    import mock
except:
    from unittest import mock

from envisage.plugin import Plugin


from traits.api import HasTraits, Instance

from force_bdss.core_plugins.dummy.dummy_dakota.dakota_factory import (
    DummyDakotaFactory)
from force_bdss.core_plugins.dummy.csv_extractor.csv_extractor_factory import (
    CSVExtractorFactory)
from force_bdss.core_plugins.dummy.kpi_adder.kpi_adder_factory import (
    KPIAdderFactory)
from force_bdss.core.workflow import Workflow
from force_bdss.api import (BaseMCOModel, BaseDataSourceModel,
                            BaseKPICalculatorModel)

from force_wfmanager.left_side_pane.new_entity_modal import (
    ModalHandler, NewEntityModal, ListAdapter)
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
        plugin = mock.Mock(spec=Plugin)

        self.available_mcos = [DummyDakotaFactory(plugin)]
        self.available_data_sources = [CSVExtractorFactory(plugin)]
        self.available_kpi_calculators = [KPIAdderFactory(plugin)]

        self.workflow_mv = WorkflowModelView(
            model=Workflow()
        )

        self.handler = ModalHandler()

    def _get_new_mco_dialog(self):
        modal = NewEntityModal(
            workflow_mv=self.workflow_mv,
            available_factories=self.available_mcos
        )
        return modal, ModalInfoDummy(object=modal)

    def _get_new_data_source_dialog(self):
        modal = NewEntityModal(
            workflow_mv=self.workflow_mv,
            available_factories=self.available_data_sources
        )
        return modal, ModalInfoDummy(object=modal)

    def _get_new_kpi_calculator_dialog(self):
        modal = NewEntityModal(
            workflow_mv=self.workflow_mv,
            available_factories=self.available_kpi_calculators
        )
        return modal, ModalInfoDummy(object=modal)

    def test_add_mco(self):
        modal, modal_info = self._get_new_mco_dialog()

        # Simulate pressing add mco button (should do nothing, because no mco
        # is selected)
        self.handler.object_add_button_changed(modal_info)
        self.assertIsNone(self.workflow_mv.model.mco)

        # Simulate selecting an mco factory in the list
        modal, modal_info = self._get_new_mco_dialog()
        modal.selected_factory = modal.available_factories[0]

        # Simulate pressing add mco button
        self.handler.object_add_button_changed(modal_info)
        self.assertIsInstance(self.workflow_mv.model.mco, BaseMCOModel)
        old_mco = self.workflow_mv.model.mco

        # Simulate selecting an mco factory in the list
        modal, modal_info = self._get_new_mco_dialog()
        modal.selected_factory = modal.available_factories[0]

        # Simulate pressing add mco button again to create a new mco model
        self.handler.object_add_button_changed(modal_info)
        self.assertNotEqual(self.workflow_mv.model.mco, old_mco)

        self.assertEqual(len(self.workflow_mv.mco_representation), 1)

    def test_add_data_source(self):
        modal, modal_info = self._get_new_data_source_dialog()

        # Simulate pressing add data_source button (should do nothing)
        self.handler.object_add_button_changed(modal_info)
        self.assertEqual(len(self.workflow_mv.model.data_sources), 0)

        # Simulate selecting a data_source factory in the list
        modal, modal_info = self._get_new_data_source_dialog()
        modal.selected_factory = modal.available_factories[0]

        # Simulate pressing add data_source button
        self.handler.object_add_button_changed(modal_info)
        self.assertIsInstance(
            self.workflow_mv.model.data_sources[0],
            BaseDataSourceModel)

        self.assertEqual(len(self.workflow_mv.data_sources_representation), 1)

        # Simulate selecting a data_source factory in the list
        modal, modal_info = self._get_new_data_source_dialog()
        modal.selected_factory = modal.available_factories[0]

        # Simulate pressing add data_source button again
        self.handler.object_add_button_changed(modal_info)
        self.assertIsInstance(
            self.workflow_mv.model.data_sources[1],
            BaseDataSourceModel)
        self.assertNotEqual(
            self.workflow_mv.model.data_sources[0],
            self.workflow_mv.model.data_sources[1])

        self.assertEqual(len(self.workflow_mv.data_sources_representation), 2)

    def test_add_kpi_calculator(self):
        modal, modal_info = self._get_new_kpi_calculator_dialog()

        # Simulate pressing add kpi_calculator button (should do nothing)
        self.handler.object_add_button_changed(modal_info)
        self.assertEqual(len(self.workflow_mv.model.kpi_calculators), 0)

        # Simulate selecting a kpi_calculator factory in the list
        modal, modal_info = self._get_new_kpi_calculator_dialog()
        modal.selected_factory = modal.available_factories[0]

        # Simulate pressing add kpi_calculator button
        self.handler.object_add_button_changed(modal_info)
        self.assertIsInstance(
            self.workflow_mv.model.kpi_calculators[0],
            BaseKPICalculatorModel)

        self.assertEqual(
            len(self.workflow_mv.kpi_calculators_representation), 1)

        # Simulate selecting a kpi_calculator factory in the list
        modal, modal_info = self._get_new_kpi_calculator_dialog()
        modal.selected_factory = modal.available_factories[0]

        # Simulate pressing add kpi_calculator button again
        self.handler.object_add_button_changed(modal_info)
        self.assertIsInstance(
            self.workflow_mv.model.kpi_calculators[1],
            BaseKPICalculatorModel)
        self.assertNotEqual(
            self.workflow_mv.model.kpi_calculators[0],
            self.workflow_mv.model.kpi_calculators[1])

        self.assertEqual(
            len(self.workflow_mv.kpi_calculators_representation), 2)

    def test_cancel_button(self):
        modal, modal_info = self._get_new_mco_dialog()

        # Simulate selecting a kpi_calculator factory in the list
        modal.selected_factory = modal.available_factories[0]

        # Simulate pressing cancel button
        self.handler.object_cancel_button_changed(modal_info)

    def test_selected_factory(self):
        modal, _ = self._get_new_mco_dialog()
        modal.selected_factory = modal.available_factories[0]

        self.assertIsNotNone(modal.current_model)

        modal.selected_factory = None

        self.assertIsNone(modal.current_model)

    def test_list_adapter(self):
        plugin = mock.Mock(spec=Plugin)

        adapter = ListAdapter(item=DummyDakotaFactory(plugin))
        self.assertEqual(adapter.get_text({}, {}, {}), 'Dummy Dakota')
