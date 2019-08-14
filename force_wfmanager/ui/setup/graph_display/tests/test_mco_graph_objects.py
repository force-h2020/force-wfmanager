from unittest import TestCase

from force_bdss.api import KPISpecification

from force_wfmanager.ui.setup.mco.kpi_specification_view import (
    KPISpecificationView
)
from force_wfmanager.ui.setup.mco.mco_parameter_view import \
    MCOParameterView
from force_wfmanager.ui.setup.graph_display.mco_graph_objects import (
    ParametersBox, KPIsBox
)
from force_wfmanager.utils.variable import Variable
from force_wfmanager.utils.tests.test_variable_names_registry import \
    get_basic_workflow


class TestParametersBox(TestCase):

    def setUp(self):

        self.workflow = get_basic_workflow()
        self.param1 = self.workflow.mco.parameters[0]
        self.param2 = self.workflow.mco.parameters[1]
        self.param3 = self.workflow.mco.parameters[2]
        self.data_source1 = self.workflow.execution_layers[0].data_sources[0]
        self.data_source2 = self.workflow.execution_layers[0].data_sources[1]

        self.param1.name = 'T1'
        self.param1.type = 'PRESSURE'

        self.available_variables = [
            Variable(name='T1', type='PRESSURE'),
            Variable(name='T2', type='PRESSURE')
        ]

        self.parameter_view = MCOParameterView(
            model=self.workflow.mco,
            parameter_name_options=self.available_variables
        )

        self.parameters_box = ParametersBox(
            parameter_view=self.parameter_view
        )

    def test___init__(self):

        self.assertEqual('Parameters', self.parameters_box.text)
        self.assertEqual(3, len(self.parameter_view.model_views))
        self.assertEqual(3, len(self.parameters_box.outputs))

        output_box = self.parameters_box.outputs[0]
        self.assertEqual(self.param1, output_box.model)
        self.assertEqual('T1', output_box.text)
        self.assertEqual('azure', output_box.bgcolor)

        output_box = self.parameters_box.outputs[1]
        self.assertEqual(self.param2, output_box.model)
        self.assertEqual('', output_box.text)
        self.assertEqual('gainsboro', output_box.bgcolor)


class TestKPIsBox(TestCase):

    def setUp(self):
        self.workflow = get_basic_workflow()
        self.param1 = self.workflow.mco.parameters[0]
        self.param2 = self.workflow.mco.parameters[1]
        self.param3 = self.workflow.mco.parameters[2]
        self.data_source1 = self.workflow.execution_layers[0].data_sources[0]
        self.data_source2 = self.workflow.execution_layers[0].data_sources[1]
        self.kpi1 = KPISpecification(name='T1')
        self.kpi2 = KPISpecification()
        self.workflow.mco.kpis.append(self.kpi1)
        self.workflow.mco.kpis.append(self.kpi2)

        self.available_variables = [
            Variable(name='T1', type='PRESSURE')
        ]

        self.kpi_view = KPISpecificationView(
            model=self.workflow.mco,
            kpi_name_options=self.available_variables
        )
        self.kpis_box = KPIsBox(
            kpi_view=self.kpi_view
        )

    def test___init__(self):

        self.assertEqual('KPIs', self.kpis_box.text)
        self.assertEqual(2, len(self.kpi_view.model_views))
        self.assertEqual(2, len(self.kpis_box.inputs))

        input_box = self.kpis_box.inputs[0]
        self.assertEqual(self.kpi1, input_box.model)
        self.assertEqual('T1', input_box.text)
        self.assertEqual('azure', input_box.bgcolor)

        input_box = self.kpis_box.inputs[1]
        self.assertEqual(self.kpi2, input_box.model)
        self.assertEqual('', input_box.text)
        self.assertEqual('salmon', input_box.bgcolor)

