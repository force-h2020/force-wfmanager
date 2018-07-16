import unittest

from force_wfmanager.plugin_dialog import htmlformat


class TestPluginDialog(unittest.TestCase):
    def test_htmlformat(self):
        self.assertIn("<h1>xxx</h1>", htmlformat("xxx"))
        self.assertIn("foo", htmlformat(
            title="foo", error_msg="frop", error_tb="woo"))
