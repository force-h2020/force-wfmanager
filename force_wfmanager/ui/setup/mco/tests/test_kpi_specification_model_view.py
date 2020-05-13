#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import unittest
from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import KPISpecification
from force_wfmanager.ui.setup.mco.kpi_specification_model_view import \
    KPISpecificationModelView


class TestKPISpecificationModelView(unittest.TestCase, UnittestTools):

    def setUp(self):

        self.kpi_model_view = KPISpecificationModelView(
            model=KPISpecification(name='T1'),
            available_variables=[('T1', 'PRESSURE'),
                                 ('T2', 'PRESSURE')]
        )

    def test_kpi_model_view_init(self):
        self.assertEqual(
            "KPI: T1 (MINIMISE)",
            self.kpi_model_view.label
        )
        self.assertTrue(self.kpi_model_view.valid)

    def test_kpi_label(self):
        self.kpi_model_view.model.name = 'T2'
        self.assertEqual(
            "KPI: T2 (MINIMISE)",
            self.kpi_model_view.label
        )

    def test_verify_workflow_event(self):
        with self.assertTraitChanges(
                self.kpi_model_view, 'verify_workflow_event', count=1):
            self.kpi_model_view.model.name = 'T2'
        with self.assertTraitChanges(
                self.kpi_model_view, 'verify_workflow_event', count=2):
            self.kpi_model_view.model.name = 'not_in__combobox'

    def test__check_kpi_name(self):
        self.kpi_model_view.available_variables.remove(
            self.kpi_model_view.available_variables[-1]
        )
        self.assertTrue(self.kpi_model_view.valid)
        self.kpi_model_view.available_variables.remove(
            self.kpi_model_view.available_variables[-1]
        )
        self.assertEqual(
            "KPI",
            self.kpi_model_view.label
        )
        self.assertEqual('', self.kpi_model_view.model.name)
        error_message = self.kpi_model_view.model.verify()
        self.assertIn(
            'KPI is not named',
            error_message[0].local_error
        )
