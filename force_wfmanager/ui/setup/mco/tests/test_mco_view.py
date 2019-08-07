from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import (
    KPISpecification, OutputSlotInfo, BaseMCOParameter
)

from force_wfmanager.ui.setup.mco.mco_view import \
    MCOView
from force_wfmanager.ui.setup.mco.mco_parameter_view import (
    MCOParameterView
)
from force_wfmanager.ui.setup.mco.kpi_specification_view import (
    KPISpecificationView
)
from force_wfmanager.ui.setup.process.process_view import ProcessView
from force_wfmanager.ui.setup.tests.wfmanager_base_test_case import \
    WfManagerBaseTestCase
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)


class TestMCOView(WfManagerBaseTestCase, UnittestTools):

    def setUp(self):
        super(TestMCOView, self).setUp()
        self.workflow.execution_layers[0].data_sources[0].output_slot_info \
            = [OutputSlotInfo(name='outputA'), OutputSlotInfo(name='outputX')]
        self.workflow.execution_layers[0].data_sources[1].output_slot_info \
            = [OutputSlotInfo(name='outputB')]

        self.mco_model.kpis.append(KPISpecification(
            name='outputA')
        )

        self.process_view = ProcessView(model=self.workflow)
        self.registry = VariableNamesRegistry(
            process_view=self.process_view
        )

        self.mco_view = MCOView(
            model=self.workflow.mco,
            variable_names_registry=self.registry
        )

        self.kpi_view = self.mco_view.kpi_view
        self.parameter_view = self.mco_view.parameter_view

    def test_init_mco_view(self):
        self.assertEqual(2, len(self.mco_view.mco_options))
        self.assertEqual(
            self.mco_view.mco_options[0],
            self.parameter_view
        )
        self.assertEqual(
            self.mco_view.mco_options[1],
            self.kpi_view
        )

        self.assertEqual(1, len(self.kpi_view.model_views))
        self.assertEqual(3, len(self.kpi_view.kpi_name_options))
        self.assertEqual(
            'outputA',
            self.kpi_view.model_views[0].model.name)

        self.assertEqual(2, len(self.parameter_view.model_views))
        self.assertEqual(
            'P1',
            self.parameter_view.model_views[0].model.name)
        self.assertEqual(
            'P2',
            self.parameter_view.model_views[1].model.name)

    def test_label(self):
        self.assertEqual("testmco", self.mco_view.label)

    def test_add_kpi(self):
        kpi_spec = KPISpecification(name='outputB')

        self.kpi_view.add_kpi(kpi_spec)
        self.assertEqual(2, len(self.kpi_view.model_views))
        self.assertEqual(3, len(self.kpi_view.kpi_name_options))
        self.assertEqual(self.kpi_view.model_views[1].model, kpi_spec)
        self.assertEqual(
            'outputB',
            self.kpi_view.model_views[1].model.name)
        self.assertEqual(
            'KPI: outputB (MINIMISE)',
            self.kpi_view.model_views[1].label)

    def test_remove_kpi(self):
        kpi_spec = self.kpi_view.model_views[0].model
        self.kpi_view.remove_kpi(kpi_spec)
        self.assertEqual(0, len(self.kpi_view.model_views))
        self.assertEqual(3, len(self.kpi_view.kpi_name_options))

    def test_add_parameter(self):
        parameter = BaseMCOParameter(None, name='P3', type='PRESSURE')

        self.parameter_view.add_parameter(parameter)
        self.assertEqual(3, len(self.parameter_view.model_views))
        self.assertEqual(3, len(self.kpi_view.kpi_name_options))
        self.assertEqual(
            parameter, self.parameter_view.model_views[2].model)

    def test_remove_parameter(self):
        parameter = self.parameter_view.model_views[1].model
        self.parameter_view.remove_parameter(parameter)
        self.assertEqual(1, len(self.parameter_view.model_views))
        self.assertEqual(3, len(self.kpi_view.kpi_name_options))

    def test_verify_workflow_event(self):
        parameter_model_view = self.parameter_view.model_views[0]

        with self.assertTraitChanges(
                self.mco_view, 'verify_workflow_event', count=1):
            variable = parameter_model_view.available_variables[2]
            parameter_model_view.selected_variable = variable
            self.assertEqual('P2', parameter_model_view.model.name)

        kpi_model_view = self.kpi_view.model_views[0]
        with self.assertTraitChanges(
                self.mco_view, 'verify_workflow_event', count=0):
            variable = kpi_model_view.available_variables[1]
            kpi_model_view.selected_variable = variable
            kpi_model_view.model.name = 'another'
            self.assertNotEqual('another', kpi_model_view.model.name)

    def test_verify(self):

        errors = self.mco_view.verify()
        self.assertEqual(0, len(errors))

        model_view = self.mco_view.parameter_view.model_views[0]
        model_view.selected_variable = model_view.available_variables[2]

        errors = self.mco_view.verify()
        self.assertEqual(1, len(errors))
        self.assertIn(
            'Two or more Parameters have a duplicate name',
            errors[0].local_error,
        )

    def test_sync_mco_options(self):

        old_parameter_view = self.mco_view.parameter_view
        new_parameter_view = MCOParameterView(
            model=self.workflow.mco
        )

        self.mco_view.parameter_view = new_parameter_view

        self.assertEqual(
            new_parameter_view,
            self.mco_view.mco_options[0]
        )
        self.assertNotEqual(
            old_parameter_view,
            self.mco_view.mco_options[0]
        )

        old_kpi_view = self.mco_view.kpi_view
        new_kpi_view = KPISpecificationView(
            model=self.workflow.mco
        )

        self.mco_view.kpi_view = new_kpi_view

        self.assertEqual(
            new_kpi_view,
            self.mco_view.mco_options[1]
        )
        self.assertNotEqual(
            old_kpi_view,
            self.mco_view.mco_options[1]
        )
