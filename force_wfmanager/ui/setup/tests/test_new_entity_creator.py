import unittest

from traits.api import Int

from force_bdss.api import BaseDataSourceModel
from force_bdss.tests.dummy_classes.data_source import DummyDataSourceModel
from force_bdss.tests.probe_classes.mco import ProbeMCOFactory, ProbeMCOModel
from force_bdss.tests.probe_classes.data_source import (
    ProbeDataSourceFactory, ProbeDataSourceModel
)
from force_bdss.tests.probe_classes.probe_extension_plugin import (
    ProbeExtensionPlugin
)

from force_wfmanager.tests.dummy_classes import DummyModelInfo
from force_wfmanager.ui.setup.new_entity_creator import (
     NewEntityCreator
)
from force_wfmanager.ui.setup.workflow_tree import WorkflowView
from force_wfmanager.ui.ui_utils import model_info


class DataSourceModelDescription(BaseDataSourceModel):

    test_trait = Int(13, desc='Test trait')


class TestNewEntityModel(unittest.TestCase):
    def setUp(self):
        self.plugin = ProbeExtensionPlugin()
        self.mcos = [ProbeMCOFactory(self.plugin)]
        self.data_sources = [ProbeDataSourceFactory(self.plugin)]

        self.workflow_mv = WorkflowView()

    def _get_mco_selector(self):
        model = NewEntityCreator(
            factories=self.mcos
        )
        return model, DummyModelInfo(object=model)

    def _get_data_selector(self):
        model = NewEntityCreator(
            factories=self.data_sources
        )
        return model, DummyModelInfo(object=model)

    def test_select_factory(self):
        # Simulate selecting an mco factory in the panel
        model, _ = self._get_mco_selector()
        model.selected_factory = model.factories[0]
        self.assertIsInstance(model.model, ProbeMCOModel)

        # Simulate selecting a datasource factory in the panel
        model, _ = self._get_data_selector()
        model.selected_factory = model.factories[0]
        self.assertIsInstance(model.model, ProbeDataSourceModel)

    def test_caching(self):
        model, _ = self._get_mco_selector()
        # Select a factory and
        model.selected_factory = model.factories[0]

        self.assertIsNotNone(model.model)
        first_model = model.model

        # Unselect the factory
        model.selected_factory = None

        self.assertIsNone(model.model)

        # Select the same factory again and check if the model is the same
        model.selected_factory = model.factories[0]

        self.assertEqual(id(first_model), id(model.model))

    def test_description_mco_model(self):

        model, _ = self._get_mco_selector()

        self.assertFalse(model._current_model_editable)

        self.assertIn("No Model", model.model_description_HTML)

        # Select factory
        model.selected_factory = model.factories[0]

        self.assertIn("testmco", model.model_description_HTML)
        self.assertIn("Edit traits", model.model_description_HTML)

    def test_view_structure(self):

        model, _ = self._get_mco_selector()

        model.selected_factory = model.factories[0]

        self.assertIn("edit_traits_call_count",
                      model_info(model.model))

    def test_plugins_root_default(self):

        model, _ = self._get_mco_selector()
        root = model._plugins_root_default()

        self.assertEqual(len(root.plugins), 1)
        self.assertEqual(root.plugins[0].plugin, self.plugin)

    def test_description_editable_data_source(self):
        model, _ = self._get_data_selector()
        model.selected_factory = model.factories[0]
        model.model = DataSourceModelDescription(
            model.selected_factory)

        self.assertIn("Test trait",
                      model.model_description_HTML)

    def test_description_non_editable_datasource(self):

        model, _ = self._get_data_selector()
        model.selected_factory = self.data_sources[0]
        # An empty DataSourceModel with no editable traits
        model.model = DummyDataSourceModel(self.data_sources[0])
        self.assertFalse(model._current_model_editable)
        self.assertIn("No description available",
                      model.model_description_HTML)
        self.assertIn("No configuration options available",
                      model._no_config_options_msg)

    def test_view_header(self):
        model, _ = self._get_mco_selector()

        self.assertEqual(
            "Available Factories",
            model.view_header
        )

        model.factory_name = 'MCO'

        self.assertEqual(
            "Available MCO Factories",
            model.view_header
        )
