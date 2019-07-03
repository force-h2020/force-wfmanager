from traits.api import (
    HasTraits, List, Instance, Unicode, on_trait_change, Bool, Event
)
from traitsui.api import ModelView

from force_bdss.api import Workflow, verify_workflow, InputSlotInfo, OutputSlotInfo

from force_wfmanager.ui.setup.mco.mco_model_view import MCOModelView
from force_wfmanager.ui.setup.process.process_model_view import ProcessModelView
from force_wfmanager.ui.setup.communication\
    .communication_model_view import CommunicationModelView
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)

# VerifierError severity constants
_ERROR = "error"
_WARNING = "warning"
_INFO = "information"


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

    #: List of Processes to be displayed in the TreeEditor.
    process_model_view = Instance(ProcessModelView)

    #: MCO to be displayed in the side pane
    mco_model_view = Instance(MCOModelView)

    #: Notification listeners to be displayed in the side pane
    communication_model_view = Instance(CommunicationModelView)

    #: Defines if the Workflow is valid or not. Set by the
    #: function map_verify_workflow
    valid = Bool(True)

    #: Event to request a verification check on the workflow
    verify_workflow_event = Event()

    #: An error message for the entire workflow
    error_message = Unicode()

    #: A label for the Workflow
    label = Unicode("Workflow")

    # Defaults
    def _variable_names_registry_default(self):
        return VariableNamesRegistry(workflow=self.model)

    def _process_model_view_default(self):
        return ProcessModelView(
            model=self.model,
            variable_names_registry=self.variable_names_registry)

    def _mco_model_view_default(self):
        return MCOModelView(
            model=self.model.mco,
            variable_names_registry=self.variable_names_registry)

    def _communication_model_view_default(self):
        return CommunicationModelView(
            model=self.model,
            variable_names_registry=self.variable_names_registry)

    #: Listeners
    @on_trait_change('model.execution_layers')
    def update_process_model_view(self):
        self.process_model_view = ProcessModelView(
            model=self.model,
            variable_names_registry=self.variable_names_registry)

    @on_trait_change('model.mco')
    def update_mco_model_view(self):
        self.mco_model_view = MCOModelView(
            model=self.model.mco,
            variable_names_registry=self.variable_names_registry)

    @on_trait_change('model.communication')
    def update_notification_listener_info(self):
        self.communication_model_view = CommunicationModelView(
            model=self.model,
            variable_names_registry=self.variable_names_registry)

    @on_trait_change('mco_model_view.verify_workflow_event,'
                     'process_model_view.verify_workflow_event,'
                     'communication_model_view.verify_workflow_event')
    def received_verify_request(self):
        self.verify_workflow_event = True

    @on_trait_change("verify_workflow_event")
    def perform_verify_workflow_event(self):
        """Verify the workflow and update error_message traits of
        every ModelView in the workflow"""
        print('workflow_model_view perform_verify_workflow_event called')
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
            'WorkflowModelView' : ['process_model_view', 'mco_model_view',
                                   'communication_model_view'],
            'ProcessModelView': ['execution_layer_model_views'],
            'ExecutionLayerModelView': ['data_source_model_views'],
            'MCOModelView': ['parameter_model_views', 'kpi_model_views'],
            'CommunicationModelView' : ['notification_listeners']
        }

        # Begin from top-level WorkflowModelView if nothing specified already
        if start_modelview is None:
            start_modelview = self

        # Get the current modelview's class
        current_modelview_type = start_modelview.__class__.__name__

        # A list of error messages to be displayed in the UI
        message_list = []

        # If the current ModelView has any child modelviews
        # retrieve their error messages by calling self.map_verify_workflow
        if current_modelview_type in mappings:
            for child_modelview_list_name in mappings[current_modelview_type]:
                child_modelview_list = getattr(
                    start_modelview, child_modelview_list_name
                )
                try:
                    for child_modelview in child_modelview_list:
                        child_modelview_errors = self.map_verify_workflow(
                            errors, start_modelview=child_modelview
                        )

                        # Add any unique error messages to the list
                        for message in child_modelview_errors:
                            if message not in message_list:
                                message_list.append(message)
                except TypeError:
                    child_modelview_errors = self.map_verify_workflow(
                        errors, start_modelview=child_modelview_list
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


# HTML Formatting Templates
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
