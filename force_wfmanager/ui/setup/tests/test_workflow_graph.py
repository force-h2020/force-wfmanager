from unittest import TestCase

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import (
    KPISpecification, OutputSlotInfo, InputSlotInfo
)

from force_wfmanager.ui.setup.mco.mco_view import MCOView
from force_wfmanager.ui.setup.workflow_graph import (
    WorkflowGraph
)
from force_wfmanager.ui.setup.process.process_view import ProcessView
from force_wfmanager.ui.setup.tests.wfmanager_base_test_case import \
    WfManagerBaseTestCase
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)
from force_wfmanager.utils.tests.test_variable_names_registry import (
    get_basic_workflow
)


class TestWorkflowGraph(WfManagerBaseTestCase, UnittestTools):

    def setUp(self):
        super(TestWorkflowGraph, self).setUp()
        self.workflow.execution_layers[0].data_sources[0].output_slot_info \
            = [OutputSlotInfo(name='outputA'), OutputSlotInfo(name='outputX')]
        self.workflow.execution_layers[0].data_sources[1].output_slot_info \
            = [OutputSlotInfo(name='outputB')]

        self.mco_model.kpis.append(KPISpecification(name='outputA'))

        self.process_view = ProcessView(model=self.workflow)
        self.registry = VariableNamesRegistry(
            process_view=self.process_view
        )

        self.mco_view = MCOView(
            model=self.workflow.mco,
            variable_names_registry=self.registry
        )

        self.workflow_graph = WorkflowGraph(
            mco_view=self.mco_view,
            variable_names_registry=self.registry
        )

    def test___init__(self):

        self.assertEqual(self.process_view, self.workflow_graph.process_view)
        self.assertEqual(self.mco_view, self.workflow_graph.mco_view)

        self.assertEqual(3, len(self.workflow_graph.components))
        self.assertEqual(2, len(self.workflow_graph.components[1].components))


class TestDisplay(TestCase):

    def view_display(self):

        from enable.api import Container, Window
        from enable.example_support import DemoFrame, demo_main

        from force_bdss.tests.probe_classes.data_source import (
            ProbeDataSourceFactory
        )
        from force_bdss.tests.probe_classes.probe_extension_plugin import \
            ProbeExtensionPlugin

        class MyFrame(DemoFrame):

            def _create_window(self):

                workflow = get_basic_workflow()

                plugin = ProbeExtensionPlugin()

                data_source_factory = ProbeDataSourceFactory(
                    plugin,
                    input_slots_size=2,
                    output_slots_size=1)

                workflow.execution_layers.remove(workflow.execution_layers[-1])
                workflow.execution_layers[1].data_sources[0] = (
                    data_source_factory.create_model()
                )

                data_source1 = workflow.execution_layers[0].data_sources[0]
                data_source1.input_slot_info = [InputSlotInfo(name='V1')]
                data_source1.output_slot_info = [OutputSlotInfo(name='T1')]

                data_source2 = workflow.execution_layers[0].data_sources[1]
                data_source2.input_slot_info = [InputSlotInfo(name='V2')]
                data_source2.output_slot_info = [OutputSlotInfo(name='T2')]

                data_source3 = workflow.execution_layers[1].data_sources[0]
                data_source3.input_slot_info = [InputSlotInfo(name='T1'),
                                                InputSlotInfo(name='T2')]
                data_source3.output_slot_info = [OutputSlotInfo(name='C1')]

                param1 = workflow.mco.parameters[0]
                param2 = workflow.mco.parameters[1]
                param1.name = 'V1'
                param1.type = 'PRESSURE'
                param2.name = 'V2'
                param2.type = 'PRESSURE'
                kpi1 = KPISpecification(name='C1')
                kpi2 = KPISpecification(name='T1')
                workflow.mco.kpis.append(kpi1)
                workflow.mco.kpis.append(kpi2)

                process_view = ProcessView(model=workflow)
                registry = VariableNamesRegistry(
                    process_view=process_view
                )

                mco_view = MCOView(
                    model=workflow.mco,
                    variable_names_registry=registry
                )

                stack = WorkflowGraph(
                    mco_view=mco_view,
                    variable_names_registry=registry
                )

                print(stack.components)

                stack.outer_bounds = stack.get_preferred_size(stack.components)

                container = Container(bounds=[600, 200])
                container.add(stack)

                return Window(self, -1, component=container)

        demo_main(MyFrame)
