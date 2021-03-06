#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

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

            main(workflow_file=None,
                 debug=False,
                 profile=False,
                 window_size=(1680, 1050))

            self.assertTrue(mock_wfmanager.called)
