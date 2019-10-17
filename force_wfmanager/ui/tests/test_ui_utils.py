import unittest

from force_bdss.tests.dummy_classes.extension_plugin import \
    DummyExtensionPlugin
from force_bdss.tests.probe_classes.data_source import \
    ProbeDataSourceModel

from force_wfmanager.ui.ui_utils import (
    class_description, get_factory_name, model_info
)
from force_wfmanager.tests.dummy_classes.dummy_factory import \
    DummyFactory


class HasDescriptionNone(object):
    description = None


class HasShortDescription(object):
    description = "A short description"


class HasLongDescription(object):
    description = "This is a long description"


class HasLongerDescription(object):
    description = "This is actually a pretty long description"


class DescriptionIsLabel(object):
    label = "This is a label"


class TestUiUtils(unittest.TestCase):

    def setUp(self):

        self.plugin = DummyExtensionPlugin()
        self.factory = DummyFactory(self.plugin)
        self.model = ProbeDataSourceModel(self.factory)

    def test_get_factory_name(self):

        self.assertEqual(
            get_factory_name(self.factory),
            'Really cool factory')

    def test_model_info(self):

        self.assertEqual(model_info(None), [])
        self.assertEqual(len(model_info(self.model)), 4)

    def test_class_description(self):

        # Workaround needed if the test is not run from the repository root.
        allclasses = [
            HasDescriptionNone, HasShortDescription, HasLongDescription,
            HasLongerDescription, DescriptionIsLabel
        ]
        for cl in allclasses:
            # This is not a test assertion, but a working assumption. It
            # should never be false.
            assert cl.__module__.endswith("test_ui_utils"), \
                "The test has been invoked in such a way that locally " \
                "defined classes don't appear as belonging to this module!"
            # Fakes a module structure that starts at root
            cl.__module__ = "force_wfmanager.ui.tests.test_ui_utils"

        # Actual test.
        self.assertEqual(
            class_description(HasDescriptionNone),
            "force_wfmanager.ui.tests.test_ui_utils.HasDescriptionNone"
        )
        self.assertEqual(
            class_description(HasShortDescription),
            "A short description (force_wfmanager.ui.tests.test_ui_utils."
            "HasShortDescription)"
        )
        self.assertEqual(
            class_description(HasShortDescription, 35),
            "A short description (force_wfma...)"
        )
        self.assertEqual(
            class_description(HasLongDescription),
            "This is a long description (force_wfmanager.ui..."
            "HasLongDescription)"
        )
        self.assertEqual(
            class_description(HasLongerDescription),
            "This is actually a pretty long description (force_wfmanager....)"
        )
        self.assertEqual(
            class_description(DescriptionIsLabel),
            "force_wfmanager.ui.tests.test_ui_utils.DescriptionIsLabel"
        )
        self.assertEqual(
            class_description(DescriptionIsLabel, desc_attribute="label"),
            "This is a label (force_wfmanager.ui.tests.test_ui_utils."
            "DescriptionIsLabel)"
        )
