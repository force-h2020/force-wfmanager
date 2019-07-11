from traits.api import (
    Instance, List, Unicode, on_trait_change, Bool, Event,
    HasTraits, Either
)
from traitsui.api import View

from force_bdss.api import BaseMCOModel
from force_wfmanager.ui.setup.mco.kpi_specification_view import \
    KPISpecificationView
from force_wfmanager.utils.variable_names_registry import \
    VariableNamesRegistry

from .mco_parameter_view import MCOParameterView
from force_wfmanager.ui.ui_utils import get_factory_name


class MCOView(HasTraits):

    # -------------------
    # Required Attributes
    # -------------------

    #: MCO model (More restrictive than the ModelView model attribute)
    model = Instance(BaseMCOModel)

    #: Registry of the available variables
    variable_names_registry = Instance(VariableNamesRegistry)

    # ------------------
    # Regular Attributes
    # ------------------

    #: List of MCO parameters and KPIs to be displayed in the TreeEditor
    #: NOTE: (Has to be a list to be selectable in TreeEditor)
    mco_options = List(Either(Instance(MCOParameterView),
                              Instance(KPISpecificationView)))

    #: List of MCO parameters to be displayed in the TreeEditor
    #: NOTE: (Has to be a list to be selectable in TreeEditor)
    parameter_view = List(Instance(MCOParameterView))

    #: List of the MCO KPIs to be displayed in the TreeEditor
    #: NOTE: (Has to be a list to be selectable in TreeEditor)
    kpi_view = List(Instance(KPISpecificationView))

    #: The label to display in the TreeEditor
    label = Unicode()

    # ------------------
    # Dependent Attributes
    # ------------------

    #: Event to request a verification check on the workflow
    verify_workflow_event = Event

    #: Defines if the MCO is valid or not. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.models.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    #: An error message for issues in this modelview. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.models.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    # ------------------
    #       View
    # ------------------

    traits_view = View()

    # Defaults
    def _label_default(self):
        return get_factory_name(self.model.factory)

    def _parameter_view_default(self):
        return [MCOParameterView(
            model=self.model
        )]

    def _kpi_view_default(self):
        return [KPISpecificationView(
            model=self.model,
            variable_names_registry=self.variable_names_registry
        )]

    def _mco_options_default(self):
        return [MCOParameterView(
            model=self.model
            ),
            KPISpecificationView(
            model=self.model,
            variable_names_registry=self.variable_names_registry
        )]

    #: Listeners
    # Workflow Verification
    @on_trait_change('parameter_view.verify_workflow_event,'
                     'kpi_view.verify_workflow_event')
    def received_verify_request(self):
        self.verify_workflow_event = True
