import unittest

from force_bdss.tests.probe_classes.mco import ProbeParameterFactory

from force_wfmanager.left_side_pane.mco_parameter_model_view import \
    MCOParameterModelView


class TestMCOParameterModelViewTest(unittest.TestCase):
    def setUp(self):
        self.mco_param_mv = MCOParameterModelView(
            model=ProbeParameterFactory(None).create_model())

    def test_mco_parameter_mv_init(self):
        self.assertEqual(self.mco_param_mv.label, "Undefined parameter")
