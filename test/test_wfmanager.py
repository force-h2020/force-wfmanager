import unittest

from force_wfmanager.wfmanager import WfManager


class WfManagerTest(unittest.TestCase):
    def test_wfmanager(self):
        wfmanager = WfManager()
        self.assertEqual(len(wfmanager.default_layout), 1)