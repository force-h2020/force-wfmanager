from traits.api import (
    Instance, List, Unicode, on_trait_change, Bool, Event,
    HasTraits, Button
)
from traitsui.api import (
    View, Item, VGroup, HGroup, ObjectColumn,
    TableEditor, ListEditor, HSplit, UReadonly
)
from force_bdss.api import BaseMCOModel, BaseMCOParameter
from force_wfmanager.ui.setup.mco.kpi_specification_model_view import \
    KPISpecificationModelView
from force_wfmanager.utils.variable_names_registry import \
    VariableNamesRegistry

from .mco_parameter_model_view import MCOParameterModelView
from force_wfmanager.ui.ui_utils import get_factory_name


class TableRow(HasTraits):
    """A representation of a variable in the workflow. Instances of TableRow
    are displayed in a table using the TableEditor."""

    #: The variable's type
    type = Unicode()

    #: The variable's name
    name = Unicode()


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

    #: The names of the KPIs in the Workflow
    kpi_names = List(Unicode)

    #: A list of TableRow instances, each representing a variable
    non_kpi_variables_rep = List(TableRow)

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

    table_edit = TableEditor(
        columns=[
            ObjectColumn(name="name", label="name", resize_mode="stretch"),
            ObjectColumn(name="type", label="type", resize_mode="stretch")
        ],
        auto_size=False,
    )

    traits_view = View(
        HSplit(
            VGroup(
                VGroup(
                    Item('mco_parameters',
                         editor=mco_editor,
                         show_label=False,
                         style='custom',
                         ),
                    show_labels=False,
                    show_border=True
                ),
                HGroup(
                    Item('add_parameter_button',
                         springy=True),
                    Item('remove_parameter_button'),
                    show_labels=False,
                ),
            ),
            VGroup(
                VGroup(
                    Item('mco_kpis',
                         editor=mco_editor,
                         show_label=False,
                         style='custom',
                         ),
                    show_labels=False,
                    show_border=True
                ),
                HGroup(
                    UReadonly('non_kpi_variables_rep',
                              editor=table_edit),
                    show_border=True,
                    label='Non-KPI Variables'
                ),
                HGroup(
                    Item('add_kpi_button',
                         springy=True),
                    Item('remove_kpi_button'),
                    show_labels=False,
                )
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
        self.verify_workflow_event = True

    def remove_kpi(self, kpi):
        """Removes a KPISpecification from the MCO model associated with this
        modelview.

        Parameters
        ----------
        kpi: KPISpecification
            The KPISpecification to be added to the current MCO.
        """
        self.model.kpis.remove(kpi)
        self.verify_workflow_event = True

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

    def _non_kpi_variables_rep_default(self):
        non_kpi = []
        if self.variable_names_registry is None:
            return non_kpi
        var_stack = self.variable_names_registry.available_variables_stack
        for exec_layer in var_stack:
            for variable in exec_layer:
                if variable[0] not in self.kpi_names:
                    variable_rep = TableRow(name=variable[0], type=variable[1])
                    non_kpi.append(variable_rep)
        return non_kpi

    def _kpi_names_default(self):
        kpi_names = []
        if self.variable_names_registry is None:
            return kpi_names
        for kpi in self.mco_kpis:
            kpi_names.append(kpi.name)

        return kpi_names
