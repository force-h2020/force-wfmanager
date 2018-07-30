import unittest
from unittest import mock

from force_wfmanager.gui.run import main
from force_wfmanager.wfmanager import WfManager


def mock_wfmanager_constructor(*args, **kwargs):
    wfmanager = mock.Mock(spec=WfManager)
    wfmanager.run = lambda: None
    return wfmanager


class TestRun(unittest.TestCase):
    def test_main(self):
        with mock.patch('force_wfmanager.gui.run.WfManager') as mock_wfmanager:
            mock_wfmanager.side_effect = mock_wfmanager_constructor

            main()

            mock_wfmanager.assert_called()
