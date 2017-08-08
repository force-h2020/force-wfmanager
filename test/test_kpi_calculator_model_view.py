import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from force_bdss.api import BaseKPICalculatorModel, BaseKPICalculatorFactory

from force_wfmanager.left_side_pane.kpi_calculator_model_view import \
    KPICalculatorModelView


class KPICalculatorModelViewTest(unittest.TestCase):
    def setUp(self):
        mock_model = mock.Mock(spec=BaseKPICalculatorModel)
        mock_model.input_slot_maps = []
        mock_model.output_slot_names = ["T1"]
        mock_model.factory = mock.Mock(spec=BaseKPICalculatorFactory)
        mock_model.factory.name = "baz"

        self.kpi_calc_mv = KPICalculatorModelView(model=mock_model)

    def test_kpi_calculator_model_view_init(self):
        self.assertEqual(self.kpi_calc_mv.label, "baz")
