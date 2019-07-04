import unittest

from force_bdss.api import (DataValue, ExecutionLayer,
                            Workflow,)
from force_bdss.tests.probe_classes.data_source import \
    ProbeDataSourceFactory
from force_bdss.tests.probe_classes.mco import ProbeMCOFactory, ProbeParameter
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin
from force_wfmanager.utils.variable_names_registry import \
    VariableNamesRegistry


def get_run_function(nb_outputs):
    def run(*args, **kwargs):
        return [DataValue() for _ in range(nb_outputs)]
    return run


class TestProcess(unittest.TestCase):

    def setUp(self):
        #: Create 2 data source factories and models
        self.plugin = ProbeExtensionPlugin()
        self.factory_1 = ProbeDataSourceFactory(
            self.plugin,
            input_slots_size=1,
            output_slots_size=2,
            run_function=get_run_function(2))
        self.factory_2 = ProbeDataSourceFactory(
            self.plugin,
            input_slots_size=1,
            output_slots_size=1,
            run_function=get_run_function(1))

        self.model_1 = self.factory_1.create_model()
        self.model_2 = self.factory_2.create_model()

        #: Store these data source models in an exectution layer
        self.data_sources = [self.model_1, self.model_2]
        self.execution_layer = ExecutionLayer(
            data_sources=self.data_sources
        )

        #: Create MCO model to store some variables
        factory = ProbeMCOFactory(self.plugin)
        mco_model = factory.create_model()
        mco_model.parameters.append(ProbeParameter(None, name='P1',
                                                   type='PRESSURE'))
        mco_model.parameters.append(ProbeParameter(None, name='P2',
                                                   type='PRESSURE'))

        #: Set up workflow containing 1 execution layer with 2
        #: data sources and 2 MCO parameters
        self.workflow = Workflow(
            mco=mco_model,
            execution_layers=[self.execution_layer]
        )
        self.variable_names_registry = VariableNamesRegistry(
            workflow=self.workflow)
