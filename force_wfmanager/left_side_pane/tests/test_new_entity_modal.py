import unittest

from traits.api import HasTraits, Instance

from force_bdss.tests.probe_classes.mco import ProbeMCOFactory
from force_bdss.tests.probe_classes.data_source import ProbeDataSourceFactory
from force_bdss.api import (BaseMCOModel, BaseDataSourceModel)

from force_wfmanager.left_side_pane.new_entity_modal import (
    ModalHandler, NewEntityModal, ListAdapter)
from force_wfmanager.left_side_pane.workflow_settings import WorkflowModelView


class UIDummy():
    def dispose(self):
        pass


class ModalInfoDummy(HasTraits):
    object = Instance(NewEntityModal)

    ui = Instance(UIDummy)

    def _ui_default(self):
        return UIDummy()


class TestNewEntityModal(unittest.TestCase):
    def setUp(self):
        self.mcos = [ProbeMCOFactory(None)]
        self.data_sources = [ProbeDataSourceFactory(None)]

        self.workflow_mv = WorkflowModelView()

        self.handler = ModalHandler()

    def _get_new_mco_dialog(self):
        modal = NewEntityModal(
            factories=self.mcos
        )
        return modal, ModalInfoDummy(object=modal)

    def _get_new_data_source_dialog(self):
        modal = NewEntityModal(
            factories=self.data_sources
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
        modal.selected_factory = modal.factories[0]

        # Simulate pressing add mco button
        self.handler.object_add_button_changed(modal_info)
        self.assertIsInstance(self.workflow_mv.model.mco, BaseMCOModel)
        old_mco = self.workflow_mv.model.mco

        # Simulate selecting an mco factory in the list
        modal, modal_info = self._get_new_mco_dialog()
        modal.selected_factory = modal.factories[0]

        # Simulate pressing add mco button again to create a new mco model
        self.handler.object_add_button_changed(modal_info)
        self.assertNotEqual(self.workflow_mv.model.mco, old_mco)

        self.assertEqual(len(self.workflow_mv.mco_mv), 1)

    def test_add_data_source(self):
        modal, modal_info = self._get_new_data_source_dialog()

        # Simulate pressing add data_source button (should do nothing)
        self.handler.object_add_button_changed(modal_info)
        self.assertEqual(
            len(self.workflow_mv.model.execution_layers[0].data_sources), 0)

        # Simulate selecting a data_source factory in the list
        modal, modal_info = self._get_new_data_source_dialog()
        modal.selected_factory = modal.factories[0]

        # Simulate pressing add data_source button
        self.handler.object_add_button_changed(modal_info)
        self.assertIsInstance(
            self.workflow_mv.model.data_sources[0],
            BaseDataSourceModel)

        self.assertEqual(
            len(self.workflow_mv.model.execution_layers.data_sources), 1)

        # Simulate selecting a data_source factory in the list
        modal, modal_info = self._get_new_data_source_dialog()
        modal.selected_factory = modal.factories[0]

        # Simulate pressing add data_source button again
        self.handler.object_add_button_changed(modal_info)
        self.assertIsInstance(
            self.workflow_mv.model.execution_layers[0].data_sources[1],
            BaseDataSourceModel)
        self.assertNotEqual(
            self.workflow_mv.model.execution_layers[0].data_sources[0],
            self.workflow_mv.model.execution_layers[0].data_sources[1])

        self.assertEqual(
            len(self.workflow_mv.execution_layers_mv.data_sources_mv),
            2)

    def test_cancel_button(self):
        modal, modal_info = self._get_new_mco_dialog()

        # Simulate selecting a kpi_calculator factory in the list
        modal.selected_factory = modal.factories[0]

        # Simulate pressing cancel button
        self.handler.object_cancel_button_changed(modal_info)

    def test_selected_factory(self):
        modal, _ = self._get_new_mco_dialog()
        modal.selected_factory = modal.factories[0]

        self.assertIsNotNone(modal.current_model)

        modal.selected_factory = None

        self.assertIsNone(modal.current_model)

    def test_list_adapter(self):
        adapter = ListAdapter(item=ProbeMCOFactory(None))
        self.assertEqual(
            adapter.get_text({}, {}, {}),
            'force.bdss.enthought.factory.test_mco')
