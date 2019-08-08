import unittest

from force_bdss.api import (
    DataValue, ExecutionLayer, Workflow, InputSlotInfo
)
from force_bdss.tests.probe_classes.data_source import \
    ProbeDataSourceFactory
from force_bdss.tests.probe_classes.factory_registry import (
    ProbeFactoryRegistry
)
from force_bdss.tests.probe_classes.mco import ProbeParameter
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin

from force_wfmanager.utils.variable_names_registry import \
    VariableNamesRegistry


def get_run_function(nb_outputs):
    def run(*args, **kwargs):
        return [DataValue() for _ in range(nb_outputs)]
    return run


class WfManagerBaseTestCase(unittest.TestCase):

    def setUp(self):
        #: Create 2 data source factories and models
        self.plugin = ProbeExtensionPlugin()
        self.factory_registry = ProbeFactoryRegistry(
            plugin=self.plugin
        )
        factory = ProbeDataSourceFactory(
            self.plugin,
            input_slots_size=1,
            output_slots_size=2,
            run_function=get_run_function(2))
        self.factory_registry.data_source_factories.append(factory)
        self.model_1 = factory.create_model()

        factory = ProbeDataSourceFactory(
            self.plugin,
            input_slots_size=1,
            output_slots_size=1,
            run_function=get_run_function(1))
        self.factory_registry.data_source_factories.append(factory)
        self.model_2 = factory.create_model()

        factory = ProbeDataSourceFactory(
            self.plugin,
            input_slots_size=2,
            output_slots_size=3
        )
        self.factory_registry.data_source_factories.append(factory)

        self.model_1.input_slot_info = [InputSlotInfo(name='P1')]
        self.model_2.input_slot_info = [InputSlotInfo(name='P2')]

        #: Store these data source models in an exectution layer
        self.data_sources = [self.model_1, self.model_2]
        self.execution_layer = ExecutionLayer(
            data_sources=self.data_sources
        )

        #: Create MCO model to store some variables
        mco_factory = self.factory_registry.mco_factories[0]
        self.mco_model = mco_factory.create_model()
        self.mco_model.parameters.append(ProbeParameter(
            None, name='P1', type='PRESSURE')
        )
        self.mco_model.parameters.append(ProbeParameter(
            None, name='P2', type='PRESSURE')
        )

        #: Create a notification listener
        nl_factory = self.factory_registry.notification_listener_factories[0]
        self.notification_listener = nl_factory.create_model()

        #: Set up workflow containing 1 execution layer with 2
        #: data sources, 2 MCO parameters and 1 listener
        self.workflow = Workflow(
            mco=self.mco_model,
            execution_layers=[self.execution_layer],
            notification_listeners=[self.notification_listener]
        )
        self.variable_names_registry = VariableNamesRegistry(
            workflow=self.workflow)
