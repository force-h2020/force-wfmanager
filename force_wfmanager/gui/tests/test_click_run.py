import unittest
from unittest import mock

from click.testing import CliRunner

import force_wfmanager.gui.run
from force_wfmanager.wfmanager import WfManager


def mock_run_constructor(*args, **kwargs):
    mock_wf_run = mock.Mock(spec=force_wfmanager.gui.run)
    mock_wf_run.main = lambda: None


class MockWfManager(WfManager):

    def run(self):
        pass


class TestClickRun(unittest.TestCase):

    def test_click_cli_version(self):
        clirunner = CliRunner()
        clirunner.invoke(force_wfmanager.gui.run.force_wfmanager,
                         args="--version")

    def test_click_cli_main(self):

        with mock.patch('force_wfmanager.gui.run') as mock_run:
            mock_run.side_effect = mock_run_constructor

            force_wfmanager.gui.run.force_wfmanager()

            self.assertTrue(mock_run.force_wfmanager.called)

    def test_run_with_debug(self):
        with mock.patch('force_wfmanager.gui.run.WfManager') as mock_wf:
            mock_wf.return_value = MockWfManager()
            force_wfmanager.gui.run.main(window_size=(1650, 1080), debug=True)
            self.log = force_wfmanager.gui.run.logging.getLogger(__name__)
            self.assertEqual(self.log.getEffectiveLevel(), 10)
