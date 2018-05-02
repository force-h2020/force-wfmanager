import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from force_bdss.api import BaseMCOModel, BaseMCOFactory, BaseMCOParameter

from force_wfmanager.left_side_pane.mco_model_view import MCOModelView
from force_wfmanager.left_side_pane.mco_parameter_model_view import \
    MCOParameterModelView


class TestMCOModelView(unittest.TestCase):
    def setUp(self):
        mock_model = mock.Mock(spec=BaseMCOModel)
        mock_model.parameters = [mock.Mock(spec=BaseMCOParameter)]
        mock_model.factory = mock.Mock(spec=BaseMCOFactory)
        mock_model.factory.name = "baz"

        self.mco_mv = MCOModelView(model=mock_model)

    def test_mco_parameter_representation(self):
        self.assertEqual(
            len(self.mco_mv.mco_parameters_mv), 1)
        self.assertIsInstance(
            self.mco_mv.mco_parameters_mv[0],
            MCOParameterModelView
        )

    def test_label(self):
        self.assertEqual(self.mco_mv.label, "baz")
