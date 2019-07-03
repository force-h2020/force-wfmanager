import unittest

from force_bdss.api import (
    KPISpecification, Workflow, OutputSlotInfo, ExecutionLayer
)
from force_bdss.tests.probe_classes.mco import (
    ProbeMCOFactory, ProbeMCOModel)
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin

from force_wfmanager.ui.setup.workflow_model_view import \
    WorkflowModelView
from force_wfmanager.utils.variable_names_registry import \
    VariableNamesRegistry
from force_bdss.tests.probe_classes.data_source import ProbeDataSourceFactory
from force_bdss.tests.probe_classes.data_source import (
    ProbeDataSourceModel
)


class TestWorkflowModelView(unittest.TestCase):

    def setUp(self):
        # WorkflowMV for testing
        self.wf_mv = WorkflowModelView(
            model=Workflow())

        self.plugin = ProbeExtensionPlugin()
        self.datasource_models = [ProbeDataSourceModel(
            factory=ProbeDataSourceFactory(plugin=self.plugin))
            for _ in range(2)]
        self.datasource_models[0].output_slot_info \
            = [OutputSlotInfo(name='outputA')]
        self.datasource_models[1].output_slot_info \
            = [OutputSlotInfo(name='outputB')]
        self.execution_layers = [ExecutionLayer(
            data_sources=self.datasource_models)]

        # Add datasources

        workflow = Workflow()
        name_registry = VariableNamesRegistry(workflow)
        self.wf_mv_name_registry = WorkflowModelView(
            model=workflow, variable_names_registry=name_registry
        )
        self.wf_mv_name_registry.set_mco(
            ProbeMCOModel(factory=ProbeMCOFactory(plugin=self.plugin))
        )

    def test_set_mco(self):
        self.wf_mv.set_mco(ProbeMCOFactory(self.plugin).create_model())
        self.assertIsNotNone(self.wf_mv.model.mco, None)

    def test_init_process_model_view(self):
        workflow = Workflow(
            execution_layers=self.execution_layers
        )
        name_registry = VariableNamesRegistry(workflow)
        test_wf = WorkflowModelView(
            model=workflow, variable_names_registry=name_registry
        )
        self.assertEqual(
            len(test_wf.process_model_view.execution_layer_model_views),
            1
        )
        self.assertEqual(
            len(test_wf.process_model_view.execution_layer_model_views[0]\
                .data_source_model_views),
            2
        )

    def test_add_kpi(self):
        # Add a KPI
        self.wf_mv_name_registry.mco_model_view.add_kpi(KPISpecification())
        self.wf_mv_name_registry.mco_model_view.kpi_model_views[0].name = 'outputA'

        self.assertEqual(self.wf_mv_name_registry.kpi_names, ['outputA'])
        self.assertEqual(len(self.wf_mv_name_registry.non_kpi_variables), 1)
        self.assertEqual(self.wf_mv_name_registry.non_kpi_variables[0].name, 'outputB')