import unittest
from click.testing import CliRunner

from force_wfmanager.run import force_wfmanager


class TestClickRun(unittest.TestCase):
    def test_click_main(self):
        """Test if the command force_wfmanager works"""

        clirunner = CliRunner()

        clirunner.invoke(force_wfmanager, args="--version")
