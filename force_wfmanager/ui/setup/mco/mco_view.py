from traits.api import (
    Instance, List, Unicode, on_trait_change, Bool, Event,
    HasTraits, Button
)
from traitsui.api import (
    View, Item, VGroup, HGroup, ObjectColumn,
    TableEditor, ListEditor, HSplit, UReadonly, InstanceEditor
)
from force_bdss.api import BaseMCOModel, BaseMCOParameter, KPISpecification
from force_wfmanager.ui.setup.mco.kpi_specification_view import \
    KPISpecificationView
from force_wfmanager.utils.variable_names_registry import \
    VariableNamesRegistry

from .mco_parameter_view import MCOParameterView
from force_wfmanager.ui.ui_utils import get_factory_name
from force_wfmanager.ui.setup.new_entity_creator import NewEntityCreator


class TableRow(HasTraits):
    """A representation of a variable in the workflow. Instances of TableRow
    are displayed in a table using the TableEditor."""

    #: The variable's type
    type = Unicode()

    #: The variable's name
    name = Unicode()


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

    #: List of MCO parameters to be displayed in the TreeEditor
    parameter_views = List(Instance(MCOParameterView))

    #: List of the KPISpecificationModelView to be displayed in the TreeEditor
    kpi_views = List(Instance(KPISpecificationView))

    # ------------------
    # Dependent Attributes
    # ------------------

    #: The names of the KPIs in the Workflow
    kpi_names = List(Unicode)

    #: A list of TableRow instances, each representing a variable
    #: that could become a KPI
    non_kpi_variables = List(TableRow)

    #: The selected parameter
    selected_parameter = Instance(MCOParameterView)

    #: The selected KPI
    selected_kpi = Instance(KPISpecificationView)

    #: The selected non-KPI
    selected_non_kpi = Instance(TableRow)

    #: Creates new instances of MCO Parameters
    entity_creator = Instance(NewEntityCreator)

    #: Label for the Model View
    label = Unicode()

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
    #        View
    # ------------------

    #: Buttons
    add_parameter_button = Button('New Parameter')
    remove_parameter_button = Button('Delete Parameter')

    add_kpi_button = Button('New KPI')
    remove_kpi_button = Button('Delete KPI')

    parameter_editor = ListEditor(
        page_name='.label',
        use_notebook=True,
        dock_style='tab',
        selected='selected_parameter')

    kpi_editor = ListEditor(
        page_name='.label',
        use_notebook=True,
        dock_style='tab',
        selected='selected_kpi')

    table_edit = TableEditor(
        columns=[
            ObjectColumn(name="name", label="name", resize_mode="stretch"),
            ObjectColumn(name="type", label="type", resize_mode="stretch")
        ],
        auto_size=False,
        selected='selected_non_kpi'
    )

    traits_view = View(
        HSplit(
            VGroup(
                VGroup(
                    Item('parameter_views',
                         editor=parameter_editor,
                         show_label=False,
                         style='custom',
                         ),
                    show_labels=False,
                    show_border=True
                ),
                HGroup(
                    Item(
                        "entity_creator", editor=InstanceEditor(),
                        style="custom",
                        show_label=False
                    ),
                    springy=True,
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
                    Item('kpi_views',
                         editor=kpi_editor,
                         show_label=False,
                         style='custom',
                         ),
                    show_labels=False,
                    show_border=True
                ),
                HGroup(
                    UReadonly('non_kpi_variables',
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

    # Defaults
    def _label_default(self):
        return get_factory_name(self.model.factory)

    def _kpi_names_default(self):
        return self.lookup_kpi_names()

    def _entity_creator_default(self):
        visible_factories = [
            f for f in self.parameter_factories() if f.ui_visible
        ]

        entity_creator = NewEntityCreator(
            factories=visible_factories,
            dclick_function=self.add_parameter
        )
        return entity_creator

    #: Listeners
    @on_trait_change('variable_names_registry,kpi_names,kpi_views[]')
    def update_non_kpi_variables(self):
        print('update_non_kpi_variables called')
        non_kpi = []
        if self.variable_names_registry is None:
            return non_kpi

        var_stack = self.variable_names_registry.available_variables_stack
        for exec_layer in var_stack:
            for variable in exec_layer:
                kpi_check = variable[0] not in self.kpi_names
                variable_check = variable[0] in self.variable_names_registry\
                    .data_source_outputs
                if kpi_check and variable_check:
                    variable_rep = TableRow(name=variable[0], type=variable[1])
                    non_kpi.append(variable_rep)
        self.non_kpi_variables = non_kpi

    # Workflow Verification
    @on_trait_change('parameter_views.verify_workflow_event,'
                     'kpi_views.verify_workflow_event')
    def received_verify_request(self):
        self.verify_workflow_event = True

    # Update modelviews when model changes
    @on_trait_change('model.parameters[]')
    def update_parameter_model_views(self):
        """ Update the MCOParameterModelView(s) """

        self.parameter_views = [
            MCOParameterView(model=parameter)
            for parameter in self.model.parameters
        ]

    @on_trait_change('model.kpis[]')
    def update_kpi_model_views(self):
        """Updates the KPI modelview according to the new KPIs in the
        model"""
        self.kpi_views = [
            KPISpecificationView(
                model=kpi,
                variable_names_registry=self.variable_names_registry
            )
            for kpi in self.model.kpis
        ]

    #: Class Methods
    def lookup_kpi_names(self):
        kpi_names = []
        if self.variable_names_registry is None:
            return kpi_names
        for kpi in self.kpi_views:
            kpi_names.append(kpi.name)

        return kpi_names

    def parameter_factories(self):
        """Returns the list of parameter factories for the current MCO."""
        if self.model is not None:
            parameter_factories = (
                self.model.factory.parameter_factories
            )
            return parameter_factories
        return None

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

    #: Button actions
    def _add_parameter_button_fired(self):
        """Call add_parameter to create a new empty parameter"""
        self.add_parameter(self.entity_creator.model)
        self.entity_creator.reset_model()

    def _add_kpi_button_fired(self):
        """Call add_kpi using selected non-kpi variable from table"""
        if self.selected_non_kpi is not None:
            self.add_kpi(
                KPISpecification(
                    name=self.selected_non_kpi.name
                )
            )
            self.kpi_names = self.lookup_kpi_names()

    def _remove_parameter_button_fired(self):
        """Call remove_parameter to delete selected_parameter from list"""
        self.remove_parameter(self.selected_parameter.model)

    def _remove_kpi_button_fired(self):
        """Call remove_kpi to delete selected kpi from list"""
        self.remove_kpi(self.selected_kpi.model)
        self.kpi_names = self.lookup_kpi_names()
