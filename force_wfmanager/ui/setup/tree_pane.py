from pyface.tasks.api import TraitsDockPane
from traits.api import (
    Bool, Button, Dict, Enum, Instance, List, on_trait_change)
from traitsui.api import EnumEditor, UItem, VGroup, View

from force_bdss.api import IFactoryRegistry, Workflow

from force_wfmanager.ui.setup.workflow_tree import WorkflowTree


class TreePane(TraitsDockPane):
    """ Side pane which contains a visualisation of the workflow (via a
    TraitsUI TreeEditor) along with a button to run the workflow.
    """

    # -----------------------------
    # Required/Dependent Attributes
    # -----------------------------

    #: The Workflow model. Updated when
    #: :attr:`WfManagerSetupTask.workflow_model <force_wfmanager.\
    # wfmanager_setup_task.WfManagerSetupTask.workflow_model>` changes.
    #: Listens to: :attr:`WfManagerSetupTask.workflow_model <force_wfmanager.\
    #: wfmanager_setup_task.WfManagerSetupTask.workflow_model>`
    #:
    workflow_model = Instance(Workflow)

    # -------------------
    # Required Attributes
    # -------------------

    #: The factory registry containing all the factories
    factory_registry = Instance(IFactoryRegistry)

    # ------------------
    # Regular Attributes
    # ------------------

    #: An internal identifier for this pane
    id = 'force_wfmanager.tree_pane'

    #: Name displayed as the title of this pane
    name = 'Workflow'

    #: Remove the possibility to close the pane
    closable = False

    #: Remove the possibility to detach the pane from the GUI
    floatable = False

    #: Remove the possibility to move the pane in the GUI
    movable = False

    #: Make the pane visible by default
    visible = True

    #: Tree editor for the Workflow
    workflow_tree = Instance(WorkflowTree)

    #: Run button for running the computation
    run_button = Button('Run')

    #: Enables or disables the workflow tree.
    ui_enabled = Bool(True)

    #: Enable or disable the run button.
    run_enabled = Bool(True)

    #: Available data views contributed by the plugins
    plugin_data_views = List

    #: Human readable descriptions of each data view, for the UI
    data_view_descriptions = Dict

    #: Selection
    selected_data_view = Enum(values='plugin_data_views')

    # ----
    # View
    # ----

    traits_view = View(VGroup(
        UItem('workflow_tree', style='custom', enabled_when="ui_enabled"),
        UItem('run_button', enabled_when="run_enabled"),
        VGroup(
            UItem(
                'selected_data_view',
                enabled_when='ui_enabled',
                editor=EnumEditor(name='data_view_descriptions')),
            label="Arrange results using layout:",
            show_border=True,
        ),
    ))

    def _workflow_tree_default(self):
        wf_tree = WorkflowTree(
            _factory_registry=self.factory_registry,
            model=self.workflow_model
        )
        self.run_enabled = wf_tree.workflow_mv.valid
        return wf_tree

    def _plugin_data_views_changed(self, new):
        """Update the data_view descriptions upon load/change.
        """

        def shorten(string, maxlength):
            if string.startswith("<class '"):

                # Usual str(type) of the form <class 'foo.bar.baz'>:
                # Remove wrapping and truncate, giving precedence to extremes.
                words = string[8:-2].split(".")
                num_words = len(words)
                word_priority = [
                    # from the out inwards, precedence to the left: 0 2 ... 3 1
                    min(2*i, 2*num_words - 2*i - 1) for i in range(num_words)]
                for threshold in range(num_words, -1, -1):
                    string = ""
                    for i, word in enumerate(words):
                        string += word if word_priority[i] < threshold else ""
                        string += "."
                    if len(string) <= maxlength + 1:
                        return string[:-1]
                # fallback when every dot-based truncation is too long.
                return shorten(words[0])

            else:

                # Custom description: just truncate.
                return string if len(string) <= maxlength \
                    else string[:maxlength-3]+"..."

        descriptions = []
        for item in self.plugin_data_views:
            length = 70
            if hasattr(item, "description") and item.description is not None:
                item_description = shorten(item.description, length)
                # if there's enough room left, add the class name in brackets.
                length -= len(item_description) + 3
                if length >= 10:
                    item_description += " (" + shorten(str(item), length) + ")"
            else:
                item_description = shorten(str(item), length)
            descriptions.append((item, item_description))

        self.data_view_descriptions = dict(descriptions)

    @on_trait_change('workflow_tree.workflow_mv.valid')
    def update_run_btn_status(self):
        """Enables/Disables the run button if the workflow is valid/invalid"""
        self.run_enabled = (
            self.workflow_tree.workflow_mv.valid and self.ui_enabled
        )

    @on_trait_change('workflow_model', post_init=True)
    def update_workflow_tree(self, *args, **kwargs):
        """Synchronises :attr:`workflow_tree.model <workflow_tree>`
        with :attr:`workflow_model`"""
        self.workflow_tree.model = self.workflow_model
