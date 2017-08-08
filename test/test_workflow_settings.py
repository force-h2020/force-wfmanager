import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from envisage.plugin import Plugin

from traits.api import Instance, HasTraits

from force_bdss.core_plugins.dummy.dummy_dakota.dakota_factory import (
    DummyDakotaFactory)
from force_bdss.core_plugins.dummy.csv_extractor.csv_extractor_factory import (
    CSVExtractorFactory)
from force_bdss.core_plugins.dummy.kpi_adder.kpi_adder_factory import (
    KPIAdderFactory)
from force_bdss.api import (BaseMCOModel, BaseMCOFactory,
                            BaseMCOParameter, BaseMCOParameterFactory,
                            BaseDataSourceModel,
                            BaseKPICalculatorModel)
from force_bdss.core.workflow import Workflow

from force_wfmanager.left_side_pane.workflow_model_view import \
    WorkflowModelView
from force_wfmanager.left_side_pane.workflow_settings import (
    WorkflowSettings, WorkflowHandler)
from force_wfmanager.left_side_pane.new_entity_modal import NewEntityModal


NEW_ENTITY_MODAL_PATH = \
    "force_wfmanager.left_side_pane.workflow_settings.NewEntityModal"


def mock_new_modal(*args, **kwargs):
    modal = mock.Mock(NewEntityModal)
    modal.edit_traits = lambda: None
    return modal


class WorkflowSettingsEditor(HasTraits):
    object = Instance(WorkflowSettings)


def get_workflow_settings():
    plugin = mock.Mock(spec=Plugin)
    return WorkflowSettings(
        available_mco_factories=[DummyDakotaFactory(plugin)],
        available_data_source_factories=[CSVExtractorFactory(plugin)],
        available_kpi_calculator_factories=[KPIAdderFactory(plugin)],
        workflow_m=Workflow(),
    )


def get_workflow_model_view():
    mco = mock.Mock(spec=BaseMCOModel)
    mco.factory = mock.Mock(spec=BaseMCOFactory)
    mco.factory.parameter_factories = lambda: [
        mock.Mock(spec=BaseMCOParameterFactory)]
    workflow_mv = WorkflowModelView(
        model=Workflow(
            mco=mco,
            data_sources=[mock.Mock(spec=BaseDataSourceModel),
                          mock.Mock(spec=BaseDataSourceModel)],
            kpi_calculators=[mock.Mock(spec=BaseKPICalculatorModel),
                             mock.Mock(spec=BaseKPICalculatorModel),
                             mock.Mock(spec=BaseKPICalculatorModel)])
    )
    workflow_mv.model.mco.parameters = [mock.Mock(BaseMCOParameter)]
    return workflow_mv


def get_workflow_settings_editor(workflow_model_view):
    return WorkflowSettingsEditor(
        object=WorkflowSettings(
            workflow_mv=workflow_model_view,
            workflow_m=workflow_model_view.model
        )
    )


class TestWorkflowSettings(unittest.TestCase):
    def setUp(self):
        self.workflow_settings = get_workflow_settings()

        self.settings = self.workflow_settings

    def test_ui_initialization(self):
        self.assertIsNone(self.settings.workflow_m.mco)
        self.assertEqual(len(self.settings.workflow_m.data_sources), 0)
        self.assertEqual(len(self.settings.workflow_m.kpi_calculators), 0)

        self.assertEqual(len(self.settings.workflow_mv.mco_representation), 0)
        self.assertEqual(
            len(self.settings.workflow_mv.data_sources_representation), 0)
        self.assertEqual(
            len(self.settings.workflow_mv.kpi_calculators_representation), 0)


class TestTreeEditorHandler(unittest.TestCase):
    def setUp(self):
        self.handler = WorkflowHandler()

        self.workflow = get_workflow_model_view()

        self.workflow_settings_editor = get_workflow_settings_editor(
            self.workflow)

    def test_new_mco(self):
        with mock.patch(NEW_ENTITY_MODAL_PATH) as mock_modal:
            mock_modal.side_effect = mock_new_modal

            self.handler.new_mco_handler(
                self.workflow_settings_editor,
                None)

            mock_modal.assert_called()

    def test_new_mco_parameter(self):
        with mock.patch(NEW_ENTITY_MODAL_PATH) as mock_modal:
            mock_modal.side_effect = mock_new_modal

            self.handler.new_parameter_handler(
                self.workflow_settings_editor,
                None)

            mock_modal.assert_called()

    def test_new_data_source(self):
        with mock.patch(NEW_ENTITY_MODAL_PATH) as mock_modal:
            mock_modal.side_effect = mock_new_modal

            self.handler.new_data_source_handler(
                self.workflow_settings_editor,
                None)

            mock_modal.assert_called()

    def test_new_kpi_calculator(self):
        with mock.patch(NEW_ENTITY_MODAL_PATH) as mock_modal:
            mock_modal.side_effect = mock_new_modal

            self.handler.new_kpi_calculator_handler(
                self.workflow_settings_editor,
                None)

            mock_modal.assert_called()

    def test_edit_entity(self):
        self.handler.edit_entity_handler(
            self.workflow_settings_editor,
            self.workflow.mco_representation[0])

        self.assertEqual(
            self.workflow.model.mco.edit_traits.call_count,
            1
        )

    def test_delete_mco(self):
        self.assertIsNotNone(self.workflow.model.mco)

        self.handler.delete_entity_handler(
            self.workflow_settings_editor,
            self.workflow.mco_representation[0])

        self.assertIsNone(
            self.workflow.model.mco)

    def test_delete_mco_parameter(self):
        self.assertEqual(
            len(self.workflow.model.mco.parameters),
            1
        )

        self.handler.delete_entity_handler(
            self.workflow_settings_editor,
            self.workflow.mco_representation[0].mco_parameters_representation[
                0
            ])

        self.assertEqual(
            len(self.workflow.model.mco.parameters),
            0
        )

    def test_delete_data_source(self):
        first_data_source = self.workflow.data_sources_representation[0]
        first_data_source_id = id(first_data_source)

        self.assertEqual(len(self.workflow.model.data_sources), 2)

        self.handler.delete_entity_handler(
            self.workflow_settings_editor,
            first_data_source)

        self.assertEqual(len(self.workflow.model.data_sources), 1)
        self.assertNotEqual(
            first_data_source_id,
            id(self.workflow.model.data_sources[0]))

    def test_delete_kpi_calculator(self):
        first_kpi_calculator = self.workflow.kpi_calculators_representation[0]
        first_kpi_calculator_id = id(first_kpi_calculator)

        self.assertEqual(len(self.workflow.model.kpi_calculators), 3)

        self.handler.delete_entity_handler(
            self.workflow_settings_editor,
            first_kpi_calculator)

        self.assertEqual(len(self.workflow.model.kpi_calculators), 2)
        self.assertNotEqual(
            first_kpi_calculator_id,
            id(self.workflow.model.kpi_calculators[0]))
