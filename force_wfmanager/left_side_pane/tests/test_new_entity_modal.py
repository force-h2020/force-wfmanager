import unittest

from traits.api import HasTraits, Instance, Int

from force_bdss.tests.probe_classes.mco import ProbeMCOFactory
from force_bdss.tests.probe_classes.data_source import ProbeDataSourceFactory
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin
from force_bdss.tests.dummy_classes.data_source import DummyDataSourceModel
from force_bdss.api import BaseDataSourceModel
from force_wfmanager.left_side_pane.new_entity_modal import (
    ModalHandler, NewEntityModal)
from force_wfmanager.left_side_pane.workflow_tree import WorkflowModelView
from force_wfmanager.left_side_pane.view_utils import model_info


class UIDummy:
    def dispose(self):
        pass


class ModalInfoDummy(HasTraits):
    object = Instance(NewEntityModal)

    ui = Instance(UIDummy)

    def _ui_default(self):
        return UIDummy()


class DataSourceModelDescription(BaseDataSourceModel):

    test_trait = Int(13, desc='Test trait')


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

    def _get_dialog_data(self):
        modal = NewEntityModal(
            factories=self.data_sources
        )
        return modal, ModalInfoDummy(object=modal)

    def test_add_entity(self):
        modal, modal_info = self._get_dialog()

        # Simulate pressing add mco button (should do nothing, because no mco
        # is selected)
        self.handler.close(modal_info, True)
        self.assertIsNone(modal.model)

        # Simulate selecting an mco factory in the list
        modal, modal_info = self._get_dialog()
        modal.selected_factory = modal.factories[0]

        # Simulate pressing add mco button
        self.handler.close(modal_info, True)
        self.assertIsNotNone(modal.model)

        # Simulate selecting an mco factory in the list
        modal, modal_info = self._get_dialog()
        modal.selected_factory = modal.factories[0]

        # Simulate pressing add mco button again to create a new mco model
        self.handler.close(modal_info, False)
        self.assertIsNone(modal.model)

    def test_caching(self):
        modal, _ = self._get_dialog()
        # Select a factory and
        modal.selected_factory = modal.factories[0]

        self.assertIsNotNone(modal.model)
        first_model = modal.model

        # Unselect the factory
        modal.selected_factory = None

        self.assertIsNone(modal.model)

        # Select the same factory again and check if the model is the same
        modal.selected_factory = modal.factories[0]

        self.assertEqual(id(first_model), id(modal.model))

    def test_description_mco_modal(self):

        modal, modal_info = self._get_dialog()

        self.assertFalse(modal.current_model_editable)

        self.assertIn("No Model", modal.model_description_HTML)

        # Select factory
        modal.selected_factory = modal.factories[0]

        self.assertIn("testmco", modal.model_description_HTML)
        self.assertIn("Edit traits", modal.model_description_HTML)

    def test_view_structure(self):

        modal, modal_info = self._get_dialog()

        modal.selected_factory = modal.factories[0]

        self.assertIn("edit_traits_call_count", model_info(
            modal.model))

    def test_plugins_root_default(self):

        modal, modal_info = self._get_dialog()
        root = modal._plugins_root_default()

        self.assertEqual(len(root.plugins), 1)
        self.assertEqual(root.plugins[0].plugin, self.plugin)

    def test_description_editable_data_source(self):
        modal, modal_info = self._get_dialog_data()
        modal.selected_factory = modal.factories[0]
        modal.model = DataSourceModelDescription(
            modal.selected_factory)

        self.assertIn("Test trait",
                      modal.model_description_HTML)

    def test_description_non_editable_datasource(self):

        modal, modal_info = self._get_dialog_data()
        modal.selected_factory = self.data_sources[0]
        # An empty DataSourceModel with no editable traits
        modal.model = DummyDataSourceModel(self.data_sources[0])
        self.assertFalse(modal.current_model_editable)
        self.assertIn("No description available", modal.model_description_HTML)
        self.assertIn("No configuration options available",
                      modal.no_config_options_msg)
