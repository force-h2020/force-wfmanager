from pyface.tasks.api import TraitsTaskPane

from traits.api import Instance, Dict
from traits.has_traits import on_trait_change
from traits.trait_types import String

from traitsui.api import View, VGroup, UItem
from traitsui.editors import ShellEditor, InstanceEditor
from traitsui.handler import ModelView

from .analysis_model import AnalysisModel


class SetupPane(TraitsTaskPane):
    id = 'force_wfmanager.setup_pane'
    name = 'Setup Pane'

    #: The model for the analysis part
    analysis_model = Instance(AnalysisModel)

    # Namespace for the console
    console_ns = Dict()

    selected_mv = Instance(ModelView)

    selected_factory_group = String('Workflow')

    view = View(
        VGroup(
                UItem("selected_mv", editor=InstanceEditor(), style="custom",
                      visible_when="selected_factory_group == 'None'"),
                UItem("console_ns", label="Console", editor=ShellEditor()),
                layout='tabbed'
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

    @on_trait_change('task.side_pane.workflow_tree.selected_factory_group')
    def set_selected_factory_group(self):
        selected = self.task.side_pane.workflow_tree.selected_factory_group
        self.selected_factory_group = selected

    @on_trait_change('task.side_pane.workflow_tree.selected_mv')
    def set_selected_mv(self):
        self.selected_mv = self.task.side_pane.workflow_tree.selected_mv
