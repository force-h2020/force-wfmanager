import unittest

from force_bdss.core.kpi_specification import KPISpecification
from force_wfmanager.left_side_pane.kpi_specification_model_view import \
    KPISpecificationModelView


class TestKPISpecificationModelViewTest(unittest.TestCase):
    def setUp(self):
        self.kpi_specification_mv = KPISpecificationModelView(
            model=KPISpecification())

    def test_kpi_specification_mv_init(self):
        self.assertEqual(self.kpi_specification_mv.label, "KPI")
