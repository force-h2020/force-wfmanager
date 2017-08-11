import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from force_bdss.core.workflow import Workflow
from force_bdss.api import BaseMCOParameter, BaseMCOModel

from force_wfmanager.left_side_pane.workflow_model_view import \
    WorkflowModelView


class TestWorkflowModelView(unittest.TestCase):
    def setUp(self):
        self.wf_mv = WorkflowModelView(model=Workflow())

    def test_add_parameter_error(self):
        with self.assertRaisesRegexp(RuntimeError, "no MCO defined"):
            self.wf_mv.add_entity(mock.Mock(spec=BaseMCOParameter))

    def test_add_whatever_error(self):
        with self.assertRaisesRegexp(TypeError, "not supported"):
            self.wf_mv.add_entity(Workflow())

    def test_remove_mco_error(self):
        with self.assertRaisesRegexp(ValueError, "not in the workflow"):
            self.wf_mv.remove_entity(mock.Mock(spec=BaseMCOModel))

    def test_remove_whatever_error(self):
        with self.assertRaisesRegexp(ValueError, "can not be removed"):
            self.wf_mv.remove_entity(Workflow())
