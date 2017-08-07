import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from force_bdss.api import BaseKPICalculatorModel, BaseKPICalculatorFactory

from force_wfmanager.left_side_pane.kpi_calculator_model_view import \
    KPICalculatorModelView


class TestKPICalculatorModelViewTest(unittest.TestCase):
    def setUp(self):
        mock_model = mock.Mock(spec=BaseKPICalculatorModel)
        mock_model.input_slot_maps = []
        mock_model.output_slot_names = ["T1"]
        mock_model.factory = mock.Mock(spec=BaseKPICalculatorFactory)
        mock_model.factory.name = "baz"

        self.kpi_calc_mv = KPICalculatorModelView(model=mock_model)

    def test_kpi_calculator_model_view_init(self):
        self.assertEqual(self.kpi_calc_mv.label, "baz")
        self.assertEqual(len(self.kpi_calc_mv.input_slot_maps), 0)
        self.assertEqual(len(self.kpi_calc_mv.output_slot_names), 1)

    def test_kpi_calculator_model_view_update(self):
        self.kpi_calc_mv.model.input_slot_maps.append({'name': 'P1'})

        self.assertEqual(len(self.kpi_calc_mv.input_slot_maps), 1)

        self.kpi_calc_mv.model.output_slot_names.append("P2")

        self.assertEqual(len(self.kpi_calc_mv.output_slot_names), 2)
