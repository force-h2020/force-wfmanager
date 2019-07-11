from force_bdss.api import (
    KPISpecification, OutputSlotInfo, ExecutionLayer, InputSlotInfo
)
from force_wfmanager.ui.setup.workflow_view import \
    WorkflowView
from force_wfmanager.ui.setup.tests.template_test_case import BaseTest


class TestWorkflowView(BaseTest):

    def setUp(self):
        super(TestWorkflowView, self).setUp()
        self.workflow.execution_layers[0].data_sources[0].output_slot_info \
            = [OutputSlotInfo(name='outputA'), OutputSlotInfo(name='outputX')]
        self.workflow.execution_layers[0].data_sources[1].output_slot_info \
            = [OutputSlotInfo(name='outputB')]

        self.mco_model.kpis.append(KPISpecification(name='outputA'))

        self.workflow_view = WorkflowView(
            model=self.workflow
        )

    def test_init_workflow_view(self):
        mco_view = self.workflow_view.mco_view[0]
        process_view = self.workflow_view.process_view[0]
        kpi_view = self.workflow_view.mco_view[0].kpi_view[0]
        parameter_view = self.workflow_view.mco_view[0].parameter_view[0]

        self.assertEqual(
            1, len(mco_view.parameter_view))
        self.assertEqual(
            2, len(parameter_view.parameter_model_views))
        self.assertEqual(
            1, len(mco_view.kpi_view))
        self.assertEqual(
            1, len(kpi_view.kpi_names))
        self.assertEqual(
            1, len(kpi_view.kpi_model_views))
        self.assertEqual(
            2, len(kpi_view.non_kpi_variables))
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

        kpi_view = self.workflow_view.mco_view[0].kpi_view[0]
        parameter_view = self.workflow_view.mco_view[0].parameter_view[0]

        self.assertEqual(
            0, len(parameter_view.parameter_model_views))
        self.assertEqual(
            0, len(kpi_view.kpi_model_views))
        self.assertEqual(
            0, len(kpi_view.kpi_names))
        self.assertEqual(
            3, len(kpi_view.non_kpi_variables))

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
        kpi_view = self.workflow_view.mco_view[0].kpi_view[0]

        self.assertEqual(
            2, len(process_view.execution_layer_views))
        self.assertEqual(
            2, len(process_view.execution_layer_views[0]
                   .data_source_views))
        self.assertEqual(
            1, len(process_view.execution_layer_views[1]
                   .data_source_views))
        self.assertEqual(0, len(kpi_view.non_kpi_variables))
        self.assertEqual(1, len(kpi_view.kpi_names))

    def WIP_test_error_messaging(self):

        default_message = ''
        global_message = "An input slot is not named"
        local_message = "Input slot is not named"

        print(self.workflow_view.error_message)

        self.assertIn(
            global_message, self.workflow_view.error_message
        )
        self.assertIn(
            global_message, self.workflow_view.process_view.error_message
        )
        self.assertIn(
            global_message,
            (self.workflow_view.process_view.execution_layer_views[0]
             .error_message)
        )
        self.assertIn(
            local_message,
            (self.workflow_view.process_view.execution_layer_views[0]
             .data_source_views[0].error_message)
        )

        (self.workflow_view.process_view.execution_layer_views[0]
            .data_source_views[0].model.input_slot_info) = (
            [InputSlotInfo(name='P1')]
        )
        self.assertNotIn(
            local_message,
            (self.workflow_view.process_view.execution_layer_views[0]
             .data_source_views[0].error_message)
        )
        (self.workflow_view.process_view.execution_layer_views[0]
         .data_source_views[1].model.input_slot_info) = (
            [InputSlotInfo(name='P2')]
        )
        self.assertNotIn(
            global_message,
            (self.workflow_view.process_view.execution_layer_views[0]
             .error_message)
        )
        self.assertEqual('', self.workflow_view.process_view.error_message)
        self.assertEqual(default_message, self.workflow_view.error_message)

        """
        self.workflow_tree.selected_view = self.workflow_tree.process_view

        ds_mv = (
            self.workflow_tree.process_view.execution_layer_views[1]
                .data_source_views[1]
        )

        print(self.variable_names_registry.available_variables_stack.__dict__)
        print(ds_mv.model.output_slot_info[0].__dict__)
        ds_mv.model.output_slot_info[0].name = 'something'
        print(ds_mv.model.output_slot_info[0].__dict__)
        self.workflow_tree.selected_view = ds_mv

        self.assertIn(
            "An output variable has an undefined name",
            self.workflow_tree.selected_error
        )
        """