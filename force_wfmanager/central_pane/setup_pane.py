from pyface.tasks.api import TraitsTaskPane

from traits.api import Dict

from traitsui.api import View, VGroup, UItem
from traitsui.editors import ShellEditor


class SetupPane(TraitsTaskPane):
    id = 'force_wfmanager.setup_pane'
    name = 'Setup Pane'

    # Namespace for the console
    console_ns = Dict()

    view = View(VGroup(
            UItem("console_ns", label="Console", editor=ShellEditor()),
        ),
    )

    def __init__(self, *args, **kwargs):
        super(SetupPane, self).__init__(*args, **kwargs)

    def _console_ns_default(self):
        namespace = {
            "task": self.task
        }
        try:
            namespace["app"] = self.task.window.application
        except AttributeError:
            namespace["app"] = None

        return namespace
