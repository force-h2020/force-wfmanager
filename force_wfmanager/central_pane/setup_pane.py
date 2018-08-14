from pyface.tasks.api import TraitsTaskPane

from traits.api import Instance, Dict

from traitsui.api import View, VGroup, UItem
from traitsui.editors import ShellEditor

from .analysis_model import AnalysisModel


class SetupPane(TraitsTaskPane):
    id = 'force_wfmanager.setup_pane'
    name = 'Setup Pane'

    #: The model for the analysis part
    analysis_model = Instance(AnalysisModel)

    # Namespace for the console
    console_ns = Dict()

    view = View(VGroup(
            UItem("console_ns", label="Console", editor=ShellEditor()),
    ),
    )

    def __init__(self, analysis_model, *args, **kwargs):
        super(SetupPane, self).__init__(*args, **kwargs)
        self.analysis_model = analysis_model

    def _console_ns_default(self):
        namespace = {
            "task": self.task
        }
        try:
            namespace["app"] = self.task.window.application
        except AttributeError:
            namespace["app"] = None

        return namespace
