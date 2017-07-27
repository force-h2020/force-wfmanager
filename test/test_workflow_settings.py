import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from traits.api import Instance, HasTraits

from force_bdss.core_plugins.dummy.dummy_dakota.dakota_bundle import (
    DummyDakotaBundle)
from force_bdss.core_plugins.dummy.csv_extractor.csv_extractor_bundle import (
    CSVExtractorBundle)
from force_bdss.core_plugins.dummy.kpi_adder.kpi_adder_bundle import (
    KPIAdderBundle)
from force_bdss.api import (BaseMCOModel, BaseDataSourceModel,
                            BaseKPICalculatorModel)
from force_bdss.workspecs.workflow import Workflow

from force_wfmanager.left_side_pane.workflow_settings import (
    WorkflowSettings, WorkflowHandler, WorkflowModelView)


class WorkflowSettingsEditor(HasTraits):
    object = Instance(WorkflowSettings)


def get_workflow_settings():
    return WorkflowSettings(
        available_mcos=[DummyDakotaBundle()],
        available_data_sources=[CSVExtractorBundle()],
        available_kpi_calculators=[KPIAdderBundle()]
    )


def get_workflow_model_view():
    return WorkflowModelView(
        model=Workflow(
            mco=mock.Mock(spec=BaseMCOModel),
            data_sources=[mock.Mock(spec=BaseDataSourceModel),
                          mock.Mock(spec=BaseDataSourceModel)],
            kpi_calculators=[mock.Mock(spec=BaseKPICalculatorModel),
                             mock.Mock(spec=BaseKPICalculatorModel),
                             mock.Mock(spec=BaseKPICalculatorModel)])
    )


def get_workflow_settings_editor(workflow):
    return WorkflowSettingsEditor(
        object=WorkflowSettings(
            workflow=workflow
        )
    )


class TestWorkflowSettings(unittest.TestCase):
    def setUp(self):
        self.workflow_settings = get_workflow_settings()

        self.settings = self.workflow_settings
        self.workflow = self.settings.workflow.model

    def test_ui_initialization(self):
        self.assertIsNone(self.workflow.mco)
        self.assertEqual(len(self.workflow.data_sources), 0)
        self.assertEqual(len(self.workflow.kpi_calculators), 0)

        self.assertEqual(len(self.settings.workflow.mco_representation), 0)
        self.assertEqual(
            len(self.settings.workflow.data_sources_representation), 0)
        self.assertEqual(
            len(self.settings.workflow.kpi_calculators_representation), 0)


class TestTreeEditorHandler(unittest.TestCase):
    def setUp(self):
        self.handler = WorkflowHandler()

        self.workflow = get_workflow_model_view()

        self.workflow_settings_editor = get_workflow_settings_editor(
            self.workflow)

    def test_delete_mco(self):
        self.assertIsNotNone(
            self.workflow.model.mco)

        self.handler.delete_mco_handler(
            self.workflow_settings_editor,
            self.workflow.model.mco)

        self.assertIsNone(
            self.workflow.model.mco)

    def test_delete_data_source(self):
        first_data_source = self.workflow.model.data_sources[0]
        first_data_source_id = id(first_data_source)

        self.assertEqual(len(self.workflow.model.data_sources), 2)

        self.handler.delete_data_source_handler(
            self.workflow_settings_editor,
            first_data_source)

        self.assertEqual(len(self.workflow.model.data_sources), 1)
        self.assertNotEqual(
            first_data_source_id,
            id(self.workflow.model.data_sources[0]))

    def test_delete_kpi_calculator(self):
        first_kpi_calculator = self.workflow.model.kpi_calculators[0]
        first_kpi_calculator_id = id(first_kpi_calculator)

        self.assertEqual(len(self.workflow.model.kpi_calculators), 3)

        self.handler.delete_kpi_calculator_handler(
            self.workflow_settings_editor,
            first_kpi_calculator)

        self.assertEqual(len(self.workflow.model.kpi_calculators), 2)
        self.assertNotEqual(
            first_kpi_calculator_id,
            id(self.workflow.model.kpi_calculators[0]))
