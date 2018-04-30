import unittest

from force_bdss.tests.probe_classes.mco import (
    ProbeParameterFactory, ProbeMCOFactory)
from force_bdss.core.workflow import Workflow

from force_wfmanager.left_side_pane.workflow_model_view import \
    WorkflowModelView

# change
class TestWorkflowModelView(unittest.TestCase):
    def setUp(self):
        self.wf_mv = WorkflowModelView(model=Workflow())

    def test_add_parameter_error(self):
        with self.assertRaisesRegexp(RuntimeError, "no MCO defined"):
            self.wf_mv.add_entity(ProbeParameterFactory(None).create_model())

    def test_add_whatever_error(self):
        with self.assertRaisesRegexp(TypeError, "not supported"):
            self.wf_mv.add_entity(Workflow())

    def test_remove_mco_error(self):
        with self.assertRaisesRegexp(ValueError, "not in the workflow"):
            self.wf_mv.remove_entity(ProbeMCOFactory(None).create_model())

    def test_remove_whatever_error(self):
        with self.assertRaisesRegexp(ValueError, "can not be removed"):
            self.wf_mv.remove_entity(Workflow())
