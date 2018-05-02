import unittest

from force_bdss.core.execution_layer import ExecutionLayer
from force_bdss.core.workflow import Workflow
from force_bdss.tests.probe_classes.mco import (
    ProbeMCOFactory)
from force_wfmanager.left_side_pane.workflow_model_view import \
    WorkflowModelView


# change
class TestWorkflowModelView(unittest.TestCase):
    def setUp(self):
        self.wf_mv = WorkflowModelView(model=Workflow())

    def test_add_execution_layer(self):
        self.assertEqual(len(self.wf_mv.execution_layers_mv), 0)
        self.wf_mv.add_execution_layer(ExecutionLayer())
        self.assertEqual(len(self.wf_mv.model.execution_layers), 1)
        self.assertEqual(len(self.wf_mv.execution_layers_mv), 1)
        self.assertEqual(self.wf_mv.execution_layers_mv[0].model,
                         self.wf_mv.model.execution_layers[0])

    def test_remove_execution_layer(self):
        self.wf_mv.add_execution_layer(ExecutionLayer())
        layer = self.wf_mv.model.execution_layers[0]
        self.wf_mv.remove_execution_layer(layer)

        self.assertEqual(len(self.wf_mv.model.execution_layers), 0)
        self.assertEqual(len(self.wf_mv.execution_layers_mv), 0)

    def test_set_mco(self):
        self.wf_mv.set_mco(ProbeMCOFactory(None).create_model())
        self.assertEqual(len(self.wf_mv.mco_mv), 1)
        self.assertIsNotNone(self.wf_mv.model.mco, None)
