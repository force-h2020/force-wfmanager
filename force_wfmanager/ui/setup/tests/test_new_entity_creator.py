import unittest

from traits.api import Int

from force_bdss.tests.probe_classes.mco import ProbeMCOFactory, ProbeMCOModel
from force_bdss.tests.probe_classes.data_source import (
    ProbeDataSourceFactory, ProbeDataSourceModel
)
from force_bdss.tests.probe_classes.probe_extension_plugin import (
    ProbeExtensionPlugin
)
from force_bdss.tests.dummy_classes.data_source import DummyDataSourceModel
from force_bdss.api import BaseDataSourceModel
from force_wfmanager.ui.setup.new_entity_creator import (
     NewEntityCreator
)
from force_wfmanager.ui.setup.workflow_tree import WorkflowModelView
from force_wfmanager.ui.ui_utils import model_info
from force_wfmanager.tests.dummy_classes import DummyModalInfo


class DataSourceModelDescription(BaseDataSourceModel):

    test_trait = Int(13, desc='Test trait')


class TestNewEntityModal(unittest.TestCase):
    def setUp(self):
        self.plugin = ProbeExtensionPlugin()
        self.mcos = [ProbeMCOFactory(self.plugin)]
        self.data_sources = [ProbeDataSourceFactory(self.plugin)]

        self.workflow_mv = WorkflowModelView()

    def _get_mco_selector(self):
        modal = NewEntityCreator(
            factories=self.mcos
        )
        return modal, DummyModalInfo(object=modal)

    def _get_data_selector(self):
        modal = NewEntityCreator(
            factories=self.data_sources
        )
        return modal, DummyModalInfo(object=modal)

    def test_select_factory(self):
        # Simulate selecting an mco factory in the panel
        modal, modal_info = self._get_mco_selector()
        modal.selected_factory = modal.factories[0]
        self.assertIsInstance(modal.model, ProbeMCOModel)

        # Simulate selecting a datasource factory in the panel
        modal, modal_info = self._get_data_selector()
        modal.selected_factory = modal.factories[0]
        self.assertIsInstance(modal.model, ProbeDataSourceModel)

    def test_caching(self):
        modal, _ = self._get_mco_selector()
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

        modal, modal_info = self._get_mco_selector()

        self.assertFalse(modal._current_model_editable)

        self.assertIn("No Model", modal.model_description_HTML)

        # Select factory
        modal.selected_factory = modal.factories[0]

        self.assertIn("testmco", modal.model_description_HTML)
        self.assertIn("Edit traits", modal.model_description_HTML)

    def test_view_structure(self):

        modal, modal_info = self._get_mco_selector()

        modal.selected_factory = modal.factories[0]

        self.assertIn("edit_traits_call_count", model_info(
            modal.model))

    def test_plugins_root_default(self):

        modal, modal_info = self._get_mco_selector()
        root = modal._plugins_root_default()

        self.assertEqual(len(root.plugins), 1)
        self.assertEqual(root.plugins[0].plugin, self.plugin)

    def test_description_editable_data_source(self):
        modal, modal_info = self._get_data_selector()
        modal.selected_factory = modal.factories[0]
        modal.model = DataSourceModelDescription(
            modal.selected_factory)

        self.assertIn("Test trait",
                      modal.model_description_HTML)

    def test_description_non_editable_datasource(self):

        modal, modal_info = self._get_data_selector()
        modal.selected_factory = self.data_sources[0]
        # An empty DataSourceModel with no editable traits
        modal.model = DummyDataSourceModel(self.data_sources[0])
        self.assertFalse(modal._current_model_editable)
        self.assertIn("No description available", modal.model_description_HTML)
        self.assertIn("No configuration options available",
                      modal._no_config_options_msg)
