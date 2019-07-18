from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import (
    KPISpecification, OutputSlotInfo, ExecutionLayer
)
from force_wfmanager.ui.setup.workflow_view import \
    WorkflowView
from force_wfmanager.ui.setup.tests.wfmanager_base_test_case import (
    WfManagerBaseTestCase
)


class TestWorkflowView(WfManagerBaseTestCase, UnittestTools):

    def setUp(self):
        super(TestWorkflowView, self).setUp()
        self.workflow.execution_layers[0].data_sources[0].output_slot_info \
            = [OutputSlotInfo(name='outputA'), OutputSlotInfo(name='outputX')]
        self.workflow.execution_layers[0].data_sources[1].output_slot_info \
            = [OutputSlotInfo(name='outputB')]

        self.mco_model.kpis.append(KPISpecification(name='outputA'))

        self.workflow_view = WorkflowView(
            model=self.workflow,
            variable_names_registry=self.variable_names_registry
        )

    def test_init_workflow_view(self):
        mco_view = self.workflow_view.mco_view[0]
        process_view = self.workflow_view.process_view[0]
        kpi_view = self.workflow_view.mco_view[0].kpi_view
        parameter_view = self.workflow_view.mco_view[0].parameter_view

        self.assertEqual(
            2, len(mco_view.mco_options))
        self.assertEqual(
            2, len(parameter_view.parameter_model_views))
        self.assertEqual(
            1, len(kpi_view.kpi_names))
        self.assertEqual(
            1, len(kpi_view.kpi_model_views))
        self.assertEqual(
            3, len(kpi_view.kpi_name_options))
        self.assertEqual(
            self.variable_names_registry,
            mco_view.variable_names_registry
        )
        self.assertEqual(
            mco_view.variable_names_registry,
            kpi_view.variable_names_registry
        )
        self.assertEqual(
            self.variable_names_registry,
            kpi_view.variable_names_registry
        )
        self.assertEqual(
            'KPI: outputA (MINIMISE)',
            kpi_view.kpi_model_views[0].label)
        self.assertEqual(
            'outputA',
            kpi_view.kpi_model_views[0].model.name)

        self.assertEqual(
            1,
            len(process_view.execution_layer_views)
        )
        self.assertEqual(
            2,
            len(process_view.execution_layer_views[0]
                .data_source_views)
        )

    def test_set_mco(self):
        mco_model = self.factory_registry.mco_factories[0].create_model()
        self.workflow_view.set_mco(mco_model)

        self.assertIsNotNone(self.workflow_view.model.mco)

        kpi_view = self.workflow_view.mco_view[0].kpi_view
        parameter_view = self.workflow_view.mco_view[0].parameter_view

        self.assertEqual(
            0, len(parameter_view.parameter_model_views))
        self.assertEqual(
            0, len(kpi_view.kpi_model_views))
        self.assertEqual(
            0, len(kpi_view.kpi_names))
        self.assertEqual(
            3, len(kpi_view.kpi_name_options))

    def test_reset_process(self):
        data_source_factory = self.factory_registry.data_source_factories[0]
        execution_layers = [
            ExecutionLayer(
                data_sources=[
                    data_source_factory.create_model(),
                    data_source_factory.create_model()
                ],
            ),
            ExecutionLayer(
                data_sources=[
                    data_source_factory.create_model()
                ],
            )
        ]
        self.workflow.execution_layers = execution_layers

        process_view = self.workflow_view.process_view[0]
        kpi_view = self.workflow_view.mco_view[0].kpi_view

        self.assertEqual(
            2, len(process_view.execution_layer_views))
        self.assertEqual(
            2, len(process_view.execution_layer_views[0]
                   .data_source_views))
        self.assertEqual(
            1, len(process_view.execution_layer_views[1]
                   .data_source_views))
        self.assertEqual(0, len(kpi_view.kpi_name_options))
        self.assertEqual(1, len(kpi_view.kpi_names))

    def test_add_output_variable(self):

        self.assertEqual(
            3, len(self.variable_names_registry.data_source_outputs)
        )

        kpi_view = self.workflow_view.mco_view[0].kpi_view
        self.assertEqual(
            self.variable_names_registry,
            kpi_view.variable_names_registry
        )
        self.assertEqual(
            3, len(kpi_view.kpi_name_options)
        )

        process_view = self.workflow_view.process_view[0]
        execution_layer_view = process_view.execution_layer_views[0]

        data_source = (self.factory_registry.data_source_factories[0]
                       .create_model())
        data_source.output_slot_info = [OutputSlotInfo(name='outputD')]

        with self.assertTraitChanges(
                kpi_view, 'kpi_name_options', count=1):
            execution_layer_view.add_data_source(data_source)

        self.assertEqual(
            3, len(execution_layer_view.data_source_views)
        )
        self.assertEqual(
            4, len(kpi_view.kpi_name_options)
        )
