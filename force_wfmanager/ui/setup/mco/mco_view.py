#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from traits.api import (
    Instance, List, Str, on_trait_change, Bool, Event,
    HasTraits
)
from traitsui.api import View

from force_bdss.api import BaseMCOModel

from force_wfmanager.ui.setup.mco.base_mco_options_view import \
    BaseMCOOptionsView
from force_wfmanager.ui.setup.mco.kpi_specification_view import \
    KPISpecificationView
from force_wfmanager.ui.setup.mco.mco_parameter_view import (
    MCOParameterView
)
from force_wfmanager.ui.ui_utils import get_factory_name
from force_wfmanager.utils.variable_names_registry import \
    VariableNamesRegistry


class MCOView(HasTraits):
    """This class provides a view for the BaseMCOModel"""

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

    #: List of [MCOParameterView, KPISpecificationView] objects to be
    #: displayed in WorkflowTree, containing information on the MCO
    #: options.
    # NOTE: (Has to be a list to be selectable in TreeEditor)
    mco_options = List(Instance(BaseMCOOptionsView))

    #: A view containing all MCO parameters
    parameter_view = Instance(MCOParameterView)

    #: A view containing all MCO KPIs
    kpi_view = Instance(KPISpecificationView)

    #: The label to display in the TreeEditor
    label = Str()

    # This is an empty View, which if not explicitly defined can cause the
    # traits notification handler to raise exceptions during testing.
    traits_view = View()

    # ---------------------
    # Dependent Attributes
    # ---------------------

    #: Event to request a verification check on the workflow
    #: Listens to: :attr:`parameter_view.verify_workflow_event
    #: <MCOParameterView>` and :attr:`kpi_view.verify_workflow_event
    #: <KPISpecificationView>`
    verify_workflow_event = Event()

    #: Defines if the MCO is valid or not. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    #: An error message for issues in this modelview. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Str()

    # -------------------
    #      Defaults
    # -------------------

    def _label_default(self):
        """Return a default label corresponding to the MCO factory"""
        return get_factory_name(self.model.factory)

    def _parameter_view_default(self):
        return MCOParameterView(
            model=self.model,
            variable_names_registry=self.variable_names_registry
        )

    def _kpi_view_default(self):
        return KPISpecificationView(
            model=self.model,
            variable_names_registry=self.variable_names_registry
        )

    def _mco_options_default(self):
        """Return a mco_options containing already constructed objects"""
        return [self.parameter_view, self.kpi_view]

    # -------------------
    #     Listeners
    # -------------------

    # Workflow Verification
    @on_trait_change('parameter_view.verify_workflow_event,'
                     'kpi_view.verify_workflow_event')
    def received_verify_request(self):
        self.verify_workflow_event = True

    @on_trait_change('parameter_view')
    def sync_mco_options_parameter_view(self):
        self.mco_options[0] = self.parameter_view

    @on_trait_change('kpi_view')
    def sync_mco_options_kpi_view(self):
        self.mco_options[1] = self.kpi_view
