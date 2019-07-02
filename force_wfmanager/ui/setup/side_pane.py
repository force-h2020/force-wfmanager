from pyface.tasks.api import TraitsDockPane

from traits.api import (
    Instance, Button, on_trait_change, Bool, Unicode
)
from traitsui.api import View, UItem, VGroup, UReadonly, TextEditor, Group

from force_bdss.api import IFactoryRegistry
from force_wfmanager.ui.setup.execution_layers.process_tree import ProcessTree
from force_wfmanager.model.workflow import Workflow


class SidePane(TraitsDockPane):
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
    #: Collated information about the total workflow
    workflow_model = Instance(Workflow, allow_none=False

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

    #: Tree editor for the Process Model Workflow
    process_tree = Instance(ProcessTree)

    #: Enables or disables the workflow tree.
    ui_enabled = Bool(True)

    #: MCO button for bringin up the MCO options
    mco_button = Button('MCO')

    #: MCO button for bringin up the Notification options
    notification_button = Button('Notifications')

    #: The error message currently displayed in the UI.
    setup_error = Unicode('')

    # ----
    # View
    # ----

    traits_view = View(
        Group(
            VGroup(
                UItem('process_tree',
                      style='custom',
                      enabled_when="ui_enabled"),
                UItem('mco_button'),
                UItem('notification_button')
            ),
            VGroup(
                UReadonly(
                    name='setup_error',
                    editor=TextEditor()
                ),
                label='Workflow Errors',
                show_border=True,
            )
        )
    )

    def _process_tree_default(self):
        print('_process_tree_default called')
        process_tree = ProcessTree(
            model=self.workflow_model.process
        return process_tree

    def _error_message_default(self):
        if self.process_model_view.error_message == '':
            return ERROR_TEMPLATE.format(
                "No errors for current workflow", "")
        else:
            error_list = self.process_model_view.error_message.split('\n')
            body_strings = ''.join([SINGLE_ERROR.format(error)
                                    for error in error_list])
            return ERROR_TEMPLATE.format(
                "Errors for current workflow:", body_strings)

    @on_trait_change('process_model_view', post_init=True)
    def update_process_tree(self):
        print(self.process_model_view, self.factory_registry)
        self.process_tree = self.workflow_model_view.process_model_view

    @on_trait_change("process_tree.selected_error")
    def _sync_setup_error(self):
        self.setup_error = self.process_tree.selected_error

    def _mco_button_fired(self):
        self.process_tree.selected_mv = self.process_model_view.mco_model_view
        self.process_tree.selected_factory_name = 'MCO'

    def _notification_button_fired(self):
        self.process_tree.selected_mv = self.process_model_view.notification_listener_info
        self.process_tree.selected_factory_name = 'Notification Listeners'


ERROR_TEMPLATE = """
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
        <style type="text/css">
            .container{{
                width: 100%;
                font-family: sans-serif;
                display: block;
            }}
        </style>
    </head>
    <body>
    <h4>{}</h4>
        {}
    </body>
    </html>
"""

SINGLE_ERROR = r"""<p>{}<\p>"""
