from traits.api import (
    Bool, Event, Instance, List, Unicode, Either, on_trait_change
)
from traitsui.api import (
    ModelView
)

from force_bdss.api import (
    KPISpecification, BaseMCOParameter
)
from force_wfmanager.utils.variable import (
    Variable
)


class BaseMCOOptionsModelView(ModelView):

    # -------------------
    # Required Attributes
    # -------------------

    #: Either a MCO KPI or parameter model
    model = Either(Instance(KPISpecification),
                   Instance(BaseMCOParameter))

    # ------------------
    # Regular Attributes
    # ------------------

    # Variable selected by the UI to hook model up to
    selected_variable = Instance(Variable)

    #: List of available variables for UI selection
    available_variables = List(selected_variable)

    #: Defines if the KPI/parameter is valid or not. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    #: An error message for issues in this modelview. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    #: Event to request a verification check on the workflow
    #: Listens to: :attr:`model.name <model>` and :attr:`model.type <model>`
    verify_workflow_event = Event

    #: Dummy Variable to use as a default option
    _empty_variable = Instance(Variable)

    def __init__(self, selected_variable=None, available_variables=None,
                 *args, **kwargs):
        super(BaseMCOOptionsModelView, self).__init__(*args, **kwargs)

        if available_variables is not None:
            self.update_available_variables(available_variables)

        if selected_variable is not None:
            self.selected_variable = selected_variable

    # ------------------
    #     Defaults
    # ------------------

    def __empty_variable_default(self):
        """Create an empty Variable object to allow the user to
        manually unhook an mco option"""
        return Variable()

    def _selected_variable_default(self):
        return self._empty_variable

    def _available_variables_default(self):
        """Create a default list containing an empty Variable object"""
        return [self._empty_variable]

    # ------------------
    #     Listeners
    # ------------------

    @on_trait_change('selected_variable,available_variables[]')
    def _check_available_variables(self):
        """Makes sure default _empty_variable or selected_variable
        is in available_variables"""

        if len(self.available_variables) == 0:
            self.update_available_variables(self.available_variables)

        if self.available_variables[0] != self._empty_variable:
            self.update_available_variables(self.available_variables)

        if self.selected_variable not in self.available_variables:
            self.selected_variable = self._selected_variable_default()

    # ------------------
    #   Public Methods
    # ------------------

    def update_available_variables(self, available_variables):
        """Update the available_variables list, whilst keeping the
        default values"""

        self.available_variables = (
            self._available_variables_default() + available_variables
        )
