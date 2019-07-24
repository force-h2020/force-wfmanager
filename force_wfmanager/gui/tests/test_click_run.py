import unittest
import sys
import os
from unittest import mock

from click.testing import CliRunner

import force_wfmanager.gui.run
from force_wfmanager.tests.dummy_classes.dummy_wfmanager import \
    DummyWfManager
from force_wfmanager.version import __version__


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

            self.assertTrue(mock_run.force_wfmanager.called)

    def test_run_with_debug(self):
        with mock.patch('force_wfmanager.gui.run.WfManager') as mock_wf:
            mock_wf.return_value = DummyWfManager()
            force_wfmanager.gui.run.main(
                window_size=(1650, 1080),
                debug=True,
                profile=False,
                workflow_file=None
            )
            self.log = force_wfmanager.gui.run.logging.getLogger(__name__)
            self.assertEqual(self.log.getEffectiveLevel(), 10)

    def test_run_with_profile(self):
        with mock.patch('force_wfmanager.gui.run.WfManager') as mock_wf:
            mock_wf.return_value = DummyWfManager()
            force_wfmanager.gui.run.main(
                window_size=(1650, 1080), debug=False,
                profile=True, workflow_file=None
            )
            root = ('force_wfmanager-{}-{}.{}.{}'
                    .format(__version__,
                            sys.version_info.major,
                            sys.version_info.minor,
                            sys.version_info.micro))
            exts = ['.pstats', '.prof']
            files_exist = [False] * len(exts)
            for ind, ext in enumerate(exts):
                files_exist[ind] = os.path.isfile(root + ext)
                os.remove(root + ext)
            self.assertTrue(all(files_exist))
