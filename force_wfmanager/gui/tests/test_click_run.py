import unittest

try:
    import mock
except ImportError:
    from unittest import mock

from click.testing import CliRunner

import force_wfmanager.gui.run


def mock_run_constructor(*args, **kwargs):
    mock_wf_run = mock.Mock(spec=force_wfmanager.gui.run)
    mock_wf_run.main = lambda: None


class TestClickRun(unittest.TestCase):

    def test_click_cli_version(self):
        clirunner = CliRunner()
        clirunner.invoke(force_wfmanager.gui.run.force_wfmanager,
                         args="--version")

    def test_click_cli_main(self):

        with mock.patch('force_wfmanager.gui.run') as mock_run:
            mock_run.side_effect = mock_run_constructor

            force_wfmanager.gui.run.force_wfmanager()

            mock_run.force_wfmanager.assert_called()
