from envisage.plugin import Plugin

from pyface.api import ImageResource
from traits.api import (
    HasTraits, List, Instance, Unicode, on_trait_change, Bool
)
from traitsui.api import (
    ImageEditor, View, Group, HGroup, UItem, ListStrEditor, VGroup, Spring,
    ModelView, TextEditor, UReadonly
)

from force_bdss.api import Workflow, verify_workflow, InputSlotInfo, OutputSlotInfo

from force_wfmanager.ui.setup.mco.mco_model_view import MCOModelView
from force_wfmanager.ui.setup.process.process_model_view import ProcessModelView
from force_wfmanager.ui.setup.notification_listeners\
    .notification_listeners_info import NotificationListenerInfo
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)

# VerifierError severity constants
_ERROR = "error"
_WARNING = "warning"
_INFO = "information"

# Item positioning shortcuts
def horizontal_centre(item_or_group):
    return HGroup(Spring(), item_or_group, Spring())


class SystemState(HasTraits):

    #: Filename for the current workflow (if any)
    workflow_filename = Unicode()

    #: A list of the loaded plugins
    plugins = List(Plugin)

    #: The factory currently selected in the SetupPane
    selected_factory = Unicode()

    #: The factory currently selected in the SetupPane
    selected_entity_creator = Unicode()


class WorkflowModelView(HasTraits):
    """A view containing information on certain aspects of the workflow
    state. This includes: Current errors, Available variables, Plugins loaded
    and the current workflow filename."""

    # -----------------------------
    # Required/Dependent Attributes
    # -----------------------------

    #: The Workflow model
    model = Instance(Workflow, allow_none=False)

    # -------------------
    # Required Attributes
    # -------------------

    #: The Variable Names Registry
    variable_names_registry = Instance(VariableNamesRegistry)


    # ------------------
    # Regular Attributes
    # ------------------

    #: List of MCO to be displayed in the TreeEditor
    mco_model_view = Instance(MCOModelView)

    #: List of DataSources to be displayed in the TreeEditor.
    #: Must be a list otherwise the tree editor will not consider it
    #: as a child.
    process_model_view = Instance(ProcessModelView)

    notification_listener_info = Instance(NotificationListenerInfo)

    # ------------------
    # Regular Attributes
    # ------------------

    #: An error message for the entire workflow
    error_message = Unicode()

    #: The force project logo! Stored at images/Force_Logo.png
    image = ImageResource('Force_Logo.png')

    #: A list of plugin names
    plugin_names = List(Unicode)

    #: Message indicating currently loaded file
    workflow_filename_message = Unicode()

    #: Defines if the Workflow is valid or not. Set by the
    #: function verify_tree in process_tree.py
    valid = Bool(True)

    #: A label for the Workflow
    label = Unicode("Workflow")

    # ----
    # View
    # ----

    traits_view = View(
        VGroup(
            horizontal_centre(
                Group(
                    UItem('image',
                          editor=ImageEditor(scale=True,
                                             allow_upscaling=False,
                                             preserve_aspect_ratio=True)),
                    visible_when="selected_factory == 'Workflow'"
                )
            ),
            Group(
                UReadonly('plugin_names',
                          editor=ListStrEditor(editable=False)),
                show_border=True,
                label='Available Plugins',
                visible_when="selected_factory not in ['KPI']"
            ),
            Group(
                UReadonly('workflow_filename_message', editor=TextEditor()),
                show_border=True,
                label='Workflow Filename',
            ),
            Group(
                UReadonly('error_message', editor=TextEditor()),
                show_border=True,
                label='Workflow Errors',
                visible_when="selected_factory == 'Workflow'"
            ),

        )
    )

    # Defaults
    def _model_default(self):
        return Workflow()

    def _variable_names_registry_default(self):
        return VariableNamesRegistry(workflow=self.model)

    def _plugin_names_default(self):
        return [plugin.name for plugin in self.plugins]

    def _workflow_filename_message_default(self):
        if self.workflow_filename == '':
            return 'No File Loaded'
        return 'Current File: ' + self.workflow_filename

    #: Listeners
    @on_trait_change('model.mco')
    def update_mco_model_view(self):
        print('update_mco_model_view called')
        return MCOModelView(
            model=self.model.mco,
            variable_names_registry=self.variable_names_registry)

    @on_trait_change('model.process')
    def update_process_model_view(self):
        print('update_process_model_view called')
        return ProcessModelView(
            model=self.model.process,
            variable_names_registry=self.variable_names_registry)

    @on_trait_change('model.notification_listeners')
    def update_notification_listener_info(self):
        print('update_notification_listener_info called')
        return NotificationListenerInfo(
            model=self.model,
            variable_names_registry=self.variable_names_registry)

    @on_trait_change('mco_model_view.verify_workflow_event,'
                     'process_model_view.verify_workflow_event,'
                     'notification_listener_info.verify_workflow_event')
    def received_verify_request(self):
        self.verify_workflow_event = True

    @on_trait_change("verify_workflow_event")
    def perform_verify_workflow_event(self):
        """Verify the workflow and update error_message traits of
        every ModelView in the workflow"""
        print('perform_verify_workflow_event called')
        errors = verify_workflow(self.model)

        # Communicate the verification errors to each level of the
        # workflow tree
        self.map_verify_workflow(errors)

    def map_verify_workflow(self, errors, start_modelview=None):
        """ Assign the errors generated by verifier.py to the appropriate
        ModelView. This is done recursively, so parent ModelViews also have
        error messages from their child ModelViews.

        Parameters
        ----------
        errors: List(VerifierError)
            A list of the current workflow errors
        start_modelview: ModelView
        """
        # A dictionary with the mappings between modelview lists
        mappings = {
            'WorkflowModelView' : ['process_model_view', 'mco_model_view', 'notification_info'],
            'ProcessModelView': ['execution_layer_model_views'],
            'ExecutionLayerModelView': ['data_source_model_views'],
            'MCOModelView': ['parameters_model_views', 'kpi_model_views'],
            'NotificationListenersInfo' : ['notification_listeners']
        }

        # Begin from top-level WorkflowModelView if nothing specified already
        if start_modelview is None:
            start_modelview = self

        # Get the current modelview's class
        current_modelview_type = start_modelview.__class__.__name__

        # A list of error messages to be displayed in the UI
        message_list = []

        # If the current ModelView has any child modelviews
        # retrieve their error messages by calling self.verify_tree
        if current_modelview_type in mappings:

            for child_modelview_list_name in mappings[current_modelview_type]:
                child_modelview_list = getattr(
                    start_modelview, child_modelview_list_name
                )

                for child_modelview in child_modelview_list:
                    child_modelview_errors = self.verify_tree(
                        errors, start_modelview=child_modelview
                    )

                    # Add any unique error messages to the list
                    for message in child_modelview_errors:
                        if message not in message_list:
                            message_list.append(message)

        # A list of messages to pass to the parent ModelView
        send_to_parent = message_list[:]

        start_modelview.valid = True

        for verifier_error in errors:
            # Check whether this model is the subject of an error. 'warning'
            # or 'information' level messages are only displayed locally and
            # don't invalidate that modelview
            if start_modelview.model == verifier_error.subject:
                message_list.append(verifier_error.local_error)
                # If there are any 'error' level entries, set the modelview
                # as invalid, and communicate these to the parent modelview.
                if verifier_error.severity == _ERROR:
                    send_to_parent.append(verifier_error.global_error)
                    start_modelview.valid = False

            # For errors where the subject is an Input/OutputSlotInfo object,
            # check if this is an attribute of the (DataSource) model
            err_subject_type = type(verifier_error.subject)
            if err_subject_type in [InputSlotInfo, OutputSlotInfo]:
                slots = []
                slots.extend(
                    getattr(start_modelview.model, 'input_slot_info', [])
                )
                slots.extend(
                    getattr(start_modelview.model, 'output_slot_info', [])
                )
                if verifier_error.subject in slots:
                    if verifier_error.local_error not in message_list:
                        message_list.append(verifier_error.local_error)
                    if verifier_error.severity == _ERROR:
                        send_to_parent.append(verifier_error.global_error)
                        start_modelview.valid = False

        # Display message so that errors relevant to this ModelView come first
        start_modelview.error_message = '\n'.join(reversed(message_list))

        # Pass relevant error messages to parent
        return send_to_parent
