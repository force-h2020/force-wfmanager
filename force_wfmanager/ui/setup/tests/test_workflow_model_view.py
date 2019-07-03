import unittest

from force_bdss.api import ExecutionLayer, Workflow
from force_bdss.tests.probe_classes.mco import (
    ProbeMCOFactory)
from force_bdss.tests.probe_classes.notification_listener import \
    ProbeNotificationListenerFactory
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin

from force_wfmanager.ui.setup.workflow_model_view import \
    WorkflowModelView
from force_wfmanager.utils.variable_names_registry import \
    VariableNamesRegistry
from force_bdss.tests.probe_classes.data_source import (ProbeDataSourceFactory,
                                                        ProbeDataSourceModel)


class TestWorkflowModelView(unittest.TestCase):

    def setUp(self):
        self.wf_mv = WorkflowModelView(model=Workflow())
        workflow = Workflow()
        name_registry = VariableNamesRegistry(workflow)
        self.wf_mv_name_registry = WorkflowModelView(
            model=workflow, variable_names_registry=name_registry)
        self.plugin = ProbeExtensionPlugin()
        self.datasource_models = [ProbeDataSourceModel(
            factory=ProbeDataSourceFactory(plugin=self.plugin))
            for _ in range(2)]

    def test_set_mco(self):
        self.wf_mv.set_mco(ProbeMCOFactory(self.plugin).create_model())
        #self.assertEqual(len(self.wf_mv.mco_model_view), 1)
        self.assertIsNotNone(self.wf_mv.model.mco, None)

    def test_add_notification_listener(self):
        self.assertEqual(len(self.wf_mv.communication_model_view.notification_listener_model_views), 0)
        self.wf_mv.communication_model_view.add_notification_listener(
            ProbeNotificationListenerFactory(self.plugin).create_model())
        self.assertEqual(len(self.wf_mv.communication_model_view.notification_listener_model_views), 1)

    def test_remove_notification_listener(self):
        model = ProbeNotificationListenerFactory(self.plugin).create_model()
        self.wf_mv.communication_model_view.add_notification_listener(model)
        self.assertEqual(len(self.wf_mv.communication_model_view.notification_listener_model_views), 1)
        self.wf_mv.communication_model_view.remove_notification_listener(model)
        self.assertEqual(len(self.wf_mv.communication_model_view.notification_listener_model_views), 0)

    def test_remove_datasource(self):
        self.wf_mv_name_registry.process_model_view.add_execution_layer(ExecutionLayer())
        self.assertEqual(len(self.wf_mv_name_registry.process_model_view.
                             execution_layer_model_views[0].model.data_sources), 0)
        execution_layer = self.wf_mv_name_registry.process_model_view.execution_layer_model_views[0]
        execution_layer.add_data_source(self.datasource_models[0])
        self.assertEqual(len(execution_layer.model.data_sources), 1)
        self.wf_mv_name_registry.process_model_view.remove_data_source(self.datasource_models[1])
        self.assertEqual(len(execution_layer.model.data_sources), 1)
        self.wf_mv_name_registry.process_model_view.remove_data_source(self.datasource_models[0])
        self.assertEqual(len(execution_layer.model.data_sources), 0)
