import unittest

from force_bdss.api import (
    Workflow, ExecutionLayer, KPISpecification, OutputSlotInfo
)
from force_bdss.tests.probe_classes.data_source import ProbeDataSourceModel, \
    ProbeDataSourceFactory
from force_bdss.tests.probe_classes.factory_registry_plugin import \
    ProbeFactoryRegistryPlugin
from force_bdss.tests.probe_classes.mco import ProbeMCOModel, ProbeMCOFactory
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin
from force_wfmanager.left_side_pane.variable_names_registry import \
    VariableNamesRegistry
from force_wfmanager.left_side_pane.workflow_info import WorkflowInfo
from force_wfmanager.left_side_pane.workflow_model_view import \
    WorkflowModelView
from force_wfmanager.left_side_pane.workflow_tree import WorkflowTree


class TestWorkflowInfo(unittest.TestCase):

    def setUp(self):

        # WorkflowMV for testing
        workflow = Workflow()
        name_registry = VariableNamesRegistry(workflow)
        self.plugin = ProbeExtensionPlugin()
        self.datasource_models = [ProbeDataSourceModel(
            factory=ProbeDataSourceFactory(plugin=self.plugin))
            for _ in range(2)]

        self.wf_mv_name_registry = WorkflowModelView(
            model=workflow, variable_names_registry=name_registry
        )
        self.wf_mv_name_registry.set_mco(
            ProbeMCOModel(factory=ProbeMCOFactory(plugin=self.plugin))
        )

        # Add datasources
        self.wf_mv_name_registry.add_execution_layer(ExecutionLayer())
        execution_layer = self.wf_mv_name_registry.execution_layers_mv[0]
        execution_layer.add_data_source(self.datasource_models[0])
        execution_layer.add_data_source(self.datasource_models[1])
        execution_layer.data_sources_mv[0].model.output_slot_info \
            = [OutputSlotInfo(name='outputA')]
        execution_layer.data_sources_mv[1].model.output_slot_info \
            = [OutputSlotInfo(name='outputB')]

        # WorkflowInfo for testing
        self.other_plugin = ProbeExtensionPlugin()
        self.other_plugin.name = 'A different Probe extension'
        plugin_list = [self.plugin, self.other_plugin]
        self.wf_info = WorkflowInfo(
            plugins=plugin_list, workflow_mv=self.wf_mv_name_registry,
            workflow_filename='workflow.json', selected_factory='Workflow'
        )

    def test_init(self):
        self.assertEqual(len(self.wf_info.plugin_names), 2)
        self.assertEqual(len(self.wf_info.non_kpi_variables_rep), 2)

    def test_plugin_list(self):
        self.assertEqual(self.wf_info.plugin_names,
                         ['Probe extension', 'A different Probe extension'])

    def test_add_kpi(self):
        # Add a KPI
        self.wf_mv_name_registry.mco_mv[0].add_kpi(KPISpecification())
        self.wf_mv_name_registry.mco_mv[0].kpis_mv[0].name = 'outputA'
        self.assertEqual(self.wf_info.kpi_names, ['outputA'])
        self.assertEqual(len(self.wf_info.non_kpi_variables_rep), 1)
        self.assertEqual(self.wf_info.non_kpi_variables_rep[0].name, 'outputB')

    def test_workflow_filename(self):
        self.assertEqual(self.wf_info.workflow_filename_message,
                         'Current File: workflow.json')

    def test_error_messaging(self):
        self.wf_tree = WorkflowTree(
            _factory_registry=ProbeFactoryRegistryPlugin(),
            model=self.wf_mv_name_registry.model
        )
        self.assertIsNotNone(self.wf_tree.workflow_mv.error_message)
