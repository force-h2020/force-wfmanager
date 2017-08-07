import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from force_bdss.api import BaseMCOParameterFactory, BaseMCOParameter

from force_wfmanager.left_side_pane.mco_parameter_model_view import \
    MCOParameterModelView


class TestMCOParameterModelViewTest(unittest.TestCase):
    def setUp(self):
        mock_model = mock.Mock(spec=BaseMCOParameter)
        mock_model.name = "P1"
        mock_model.type = "PRESSURE"
        mock_model.factory = mock.Mock(spec=BaseMCOParameterFactory)
        mock_model.factory.name = "baz"

        self.mco_param_mv = MCOParameterModelView(model=mock_model)

    def test_mco_parameter_mv_init(self):
        self.assertEqual(self.mco_param_mv.name, "P1")
        self.assertEqual(self.mco_param_mv.type, "PRESSURE")
        self.assertEqual(self.mco_param_mv.label, "baz")

    def test_mco_parameter_update(self):
        self.mco_param_mv.name = "T1"
        self.assertEqual(self.mco_param_mv.model.name, "T1")

        self.mco_param_mv.type = "TEMPERATURE"
        self.assertEqual(self.mco_param_mv.model.type, "TEMPERATURE")
