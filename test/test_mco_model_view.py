import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from force_bdss.api import BaseMCOModel, BaseMCOFactory

from force_wfmanager.left_side_pane.mco_model_view import MCOModelView


class MCOModelViewTest(unittest.TestCase):
    def setUp(self):
        mock_model = mock.Mock(spec=BaseMCOModel)
        mock_model.parameters = ["foo", "bar"]
        mock_model.factory = mock.Mock(spec=BaseMCOFactory)
        mock_model.factory.name = "baz"

        self.mco_mv = MCOModelView(model=mock_model)

    def test_mco_parameter_representation(self):
        self.assertEqual(
            self.mco_mv.mco_parameters_representation, ["foo", "bar"])

    def test_label(self):
        self.assertEqual(self.mco_mv.label, "baz")
