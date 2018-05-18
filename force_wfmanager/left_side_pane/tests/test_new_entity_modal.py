import unittest

from traits.api import HasTraits, Instance

from force_bdss.tests.probe_classes.mco import ProbeMCOFactory
from force_bdss.tests.probe_classes.data_source import ProbeDataSourceFactory
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin

from force_wfmanager.left_side_pane.new_entity_modal import (
    ModalHandler, NewEntityModal, ListAdapter)
from force_wfmanager.left_side_pane.workflow_tree import WorkflowModelView


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
        self.plugin = ProbeExtensionPlugin()
        self.mcos = [ProbeMCOFactory(self.plugin)]
        self.data_sources = [ProbeDataSourceFactory(self.plugin)]

        self.workflow_mv = WorkflowModelView()

        self.handler = ModalHandler()

    def _get_dialog(self):
        modal = NewEntityModal(
            factories=self.mcos
        )
        return modal, ModalInfoDummy(object=modal)

    def test_add_entity(self):
        modal, modal_info = self._get_dialog()

        # Simulate pressing add mco button (should do nothing, because no mco
        # is selected)
        self.handler.object_add_button_changed(modal_info)
        self.assertIsNone(modal.current_model)

        # Simulate selecting an mco factory in the list
        modal, modal_info = self._get_dialog()
        modal.selected_factory = modal.factories[0]

        # Simulate pressing add mco button
        self.handler.object_add_button_changed(modal_info)
        self.assertIsNotNone(modal.current_model)

        # Simulate selecting an mco factory in the list
        modal, modal_info = self._get_dialog()
        modal.selected_factory = modal.factories[0]

        # Simulate pressing add mco button again to create a new mco model
        self.handler.object_cancel_button_changed(modal_info)
        self.assertIsNone(modal.current_model)

    def test_caching(self):
        modal, _ = self._get_dialog()
        # Select a factory and
        modal.selected_factory = modal.factories[0]

        self.assertIsNotNone(modal.current_model)
        first_model = modal.current_model

        # Unselect the factory
        modal.selected_factory = None

        self.assertIsNone(modal.current_model)

        # Select the same factory again and check if the model is the same
        modal.selected_factory = modal.factories[0]

        self.assertEqual(id(first_model), id(modal.current_model))

    def test_list_adapter(self):
        adapter = ListAdapter(item=ProbeMCOFactory(self.plugin))
        self.assertEqual(
            adapter.get_text({}, {}, {}),
            'testmco')
