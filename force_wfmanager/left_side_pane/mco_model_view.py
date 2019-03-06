from traits.api import Instance, List, Unicode, on_trait_change, Bool, Event

from traitsui.api import ModelView

from force_bdss.api import BaseMCOModel
from force_wfmanager.left_side_pane.kpi_specification_model_view import \
    KPISpecificationModelView
from force_wfmanager.left_side_pane.variable_names_registry import \
    VariableNamesRegistry

from .mco_parameter_model_view import MCOParameterModelView
from .view_utils import get_factory_name


class MCOModelView(ModelView):

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

    #: List of MCO parameters to be displayed in the TreeEditor
    mco_parameters_mv = List(Instance(MCOParameterModelView))

    #: List of the KPISpecificationModelView to be displayed in the TreeEditor
    kpis_mv = List(Instance(KPISpecificationModelView))

    #: Label to be used in the TreeEditor
    label = Unicode()

    # ------------------
    # Dependent Attributes
    # ------------------

    #: Event to request a verification check on the workflow
    verify_workflow_event = Event()

    #: Defines if the MCO is valid or not. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.left_side_pane.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    #: An error message for issues in this modelview. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.left_side_pane.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    # Workflow Verification

    @on_trait_change('mco_parameters_mv.verify_workflow_event,'
                     'kpis_mv.verify_workflow_event')
    def received_verify_request(self):
        self.verify_workflow_event = True

    # Add objects to model

    def add_parameter(self, parameter):
        """Adds a parameter to the MCO model associated with this modelview.

        Parameters
        ----------
        parameter: BaseMCOParameter
            The parameter to be added to the current MCO.
        """
        self.model.parameters.append(parameter)

    def add_kpi(self, kpi):
        """Adds a KPISpecification to the MCO model associated with this
         modelview.

        Parameters
        ----------
        kpi: KPISpecification
            The KPISpecification to be added to the current MCO.
        """
        self.model.kpis.append(kpi)

    # Remove objects from model

    def remove_parameter(self, parameter):
        """Removes a parameter from the MCO model associated with this
        modelview.

        Parameters
        ----------
        parameter: BaseMCOParameter
            The parameter to be removed from the current MCO.
        """
        self.model.parameters.remove(parameter)

    def remove_kpi(self, kpi):
        """Removes a KPISpecification from the MCO model associated with this
        modelview.

        Parameters
        ----------
        kpi: KPISpecification
            The KPISpecification to be added to the current MCO.
        """
        self.model.kpis.remove(kpi)

    # Update modelviews when model changes

    @on_trait_change('model.parameters[]')
    def update_mco_parameters_mv(self):
        """ Update the MCOParameterModelView(s) """
        self.mco_parameters_mv = [
            MCOParameterModelView(model=parameter)
            for parameter in self.model.parameters]

    @on_trait_change('model.kpis[]')
    def update_kpis(self):
        """Updates the KPI modelview according to the new KPIs in the
        model"""
        self.kpis_mv = [
            KPISpecificationModelView(
                variable_names_registry=self.variable_names_registry,
                model=kpi
            )
            for kpi in self.model.kpis
        ]

    # Defaults

    def _label_default(self):
        return get_factory_name(self.model.factory)
