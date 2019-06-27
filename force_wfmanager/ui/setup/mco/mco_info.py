from traits.api import (
    Instance, List, Unicode, on_trait_change, Bool, Event,
    HasTraits, Button
)
from traitsui.api import (
    ModelView, View, Item, InstanceEditor, Action, ToolBar,
    ActionGroup, MenuBar, Menu, VGroup, HGroup, VSplit, UItem,
    ButtonEditor, ListEditor, HSplit
)
from force_bdss.api import BaseMCOModel, BaseMCOParameter
from force_wfmanager.ui.setup.mco.kpi_specification_model_view import \
    KPISpecificationModelView
from force_wfmanager.utils.variable_names_registry import \
    VariableNamesRegistry

from .mco_parameter_model_view import MCOParameterModelView
from force_wfmanager.ui.ui_utils import get_factory_name


class MCOInfo(HasTraits):

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
    mco_parameters = List(Instance(MCOParameterModelView))

    #: List of the KPISpecificationModelView to be displayed in the TreeEditor
    mco_kpis = List(Instance(KPISpecificationModelView))

    #: Buttons

    add_parameter_button = Button('New Parameter')
    remove_parameter_button = Button('Delete Parameter')

    add_kpi_button = Button('New KPI')
    remove_kpi_button = Button('Delete KPI')

    #: Label to be used in the TreeEditor
    label = Unicode()

    # ------------------
    # Dependent Attributes
    # ------------------

    #: Event to request a verification check on the workflow
    verify_workflow_event = Event()

    #: Defines if the MCO is valid or not. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.models.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    #: An error message for issues in this modelview. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.models.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    mco_editor = ListEditor(
        page_name='.label',
        use_notebook=True,
        dock_style='tab')

    traits_view = View(
        VSplit(
            VGroup(
                Item('mco_parameters',
                     editor=mco_editor,
                     show_label=False,
                     style='custom',
                     ),
                show_labels=False,
                show_border=True
            ),
            VGroup(
                Item('mco_kpis',
                     editor=mco_editor,
                     show_label=False,
                     style='custom',
                     ),
                show_labels=False,
                show_border=True
            )
        ),
        dock='fixed',
        kind="livemodal"
    )

    # Workflow Verification

    @on_trait_change('mco_parameters.verify_workflow_event,'
                     'mco_kpis.verify_workflow_event')
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
    def update_mco_parameters(self):
        """ Update the MCOParameterModelView(s) """

        self.mco_parameters = [
           MCOParameterModelView(model=parameter)
           for parameter in self.model.parameters]

    @on_trait_change('model.kpis[]')
    def update_kpis(self):
        """Updates the KPI modelview according to the new KPIs in the
        model"""

        self.mco_kpis = [
            KPISpecificationModelView(
                variable_names_registry=self.variable_names_registry,
                model=kpi
            )
            for kpi in self.model.kpis
        ]

    # Defaults

    def _label_default(self):
        return get_factory_name(self.model.factory)
