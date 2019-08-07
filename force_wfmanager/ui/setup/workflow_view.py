from traits.api import (
    HasTraits, List, Instance, Unicode, on_trait_change, Bool, Event
)

from force_bdss.api import Workflow, VerifierError

from force_wfmanager.ui.setup.communicator\
    .communicator_view import CommunicatorView
from force_wfmanager.ui.setup.mco.mco_view import MCOView
from force_wfmanager.ui.setup.process.process_view import (
    ProcessView
)
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)


class WorkflowView(HasTraits):
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

    #: The Variable Names Registry containing all Variable objects
    #: parsed from the DataSource output and input slots
    variable_names_registry = Instance(VariableNamesRegistry)

    # ------------------
    # Regular Attributes
    # ------------------

    #: Process to be displayed in the TreeEditor.
    #: NOTE: (Has to be a list to be selectable in TreeEditor)
    process_view = List(Instance(ProcessView))

    #: MCO to be displayed in the side pane
    #: NOTE: (Has to be a list to be selectable in TreeEditor)
    mco_view = List(Instance(MCOView))

    #: Notification listeners to be displayed in the side pane
    #: NOTE: (Has to be a list to be selectable in TreeEditor)
    communicator_view = List(Instance(CommunicatorView))

    #: Defines if the Workflow is valid or not. Set by the
    #: function verify_tree
    valid = Bool(True)

    #: Event to request a verification check on the workflow
    verify_workflow_event = Event()

    #: An error message for the entire workflow
    error_message = Unicode()

    #: A label for the Workflow
    label = Unicode("Workflow")

    # -------------------
    #     Defaults
    # -------------------

    def _model_default(self):
        return Workflow()

    def _process_view_default(self):
        return [ProcessView(
            model=self.model
        )]

    def _variable_names_registry_default(self):
        return VariableNamesRegistry(
                process_view=self.process_view[0]
            )

    def _mco_view_default(self):
        if self.model.mco is not None:
            return [MCOView(
                model=self.model.mco,
                variable_names_registry=self.variable_names_registry
            )]
        else:
            return []

    def _communicator_view_default(self):
        return [CommunicatorView(
            model=self.model
        )]

    # -------------------
    #     Listeners
    # -------------------

    @on_trait_change('model.execution_layers')
    def update_process_view(self):
        self.process_view = self._process_view_default()

    @on_trait_change('process_view')
    def update_variable_names_registry(self):
        self.variable_names_registry = self._variable_names_registry_default()

    @on_trait_change('model:mco,variable_names_registry')
    def update_mco_view(self):
        self.mco_view = self._mco_view_default()

    @on_trait_change('model')
    def update_communication_view(self):
        self.communicator_view = self._communicator_view_default()

    @on_trait_change('mco_view.verify_workflow_event,'
                     'process_view.verify_workflow_event,'
                     'communicator_view.verify_workflow_event,'
                     'variable_names_registry.verify_workflow_event')
    def received_verify_request(self):
        self.verify_workflow_event = True

    # -------------------
    #   Public Methods
    # -------------------

    def set_mco(self, mco_model):
        """Set the MCO"""
        self.model.mco = mco_model

    def remove_execution_layer(self, layer):
        """Removes the execution layer from the model."""
        self.process_view[0].remove_execution_layer(layer)

    def remove_data_source(self, data_source):
        """Removes the execution layer from the model."""
        self.process_view[0].remove_data_source(data_source)

    def remove_notification_listener(self, notification_listener):
        """Removes the execution layer from the model."""
        self.communicator_view[0].remove_notification_listener(
            notification_listener
        )

    def verify(self):
        """Perform a series of error checks on objects that exist only within the
        force_wfmanager UI. Namely, make sure that:

            - All Variables requiring an MCO Parameter have one assigned
            - Report back any errors from the VariableNamesRegistry
            - Report back any errors from the MCOView, if defined
        """

        errors = []

        # Check Variables requiring an MCO Parameter
        refs = []
        if self.model.mco is not None:
            # Gather MCOOptionView object errors
            errors += self.mco_view[0].verify()

            # Collate MCOParameter name / type combinations
            refs += [
                (parameter.model.name, parameter.model.type)
                for parameter in self.mco_view[0].parameter_view.model_views
            ]

        available_variables = (
            self.variable_names_registry.available_variables
        )
        for variable in available_variables:
            key = (variable.name, variable.type)
            if variable.output_slot_row is None and key not in refs:
                for _, input_slot in variable.input_slot_rows:
                    errors.append(
                        VerifierError(
                            subject=input_slot.model,
                            local_error=('Input slot does not have either a'
                                         ' corresponding Output slot or MCO'
                                         ' Parameter'),
                            global_error=('An Input slot requires a '
                                          'corresponding Output slot or MCO '
                                          'Parameter')
                        )
                    )

        # Gather VariableNamesRegistry errors
        errors += self.variable_names_registry.verify()

        return errors
