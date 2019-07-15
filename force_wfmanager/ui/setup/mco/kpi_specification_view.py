from traits.api import (
    Bool, Event, Instance, List, Property, Unicode, cached_property,
    on_trait_change, HasTraits, Button
)
from traitsui.api import (
    Item, View, ListEditor, TableEditor, ObjectColumn,
    VGroup, HGroup, UReadonly, ModelView
)

from force_bdss.api import KPISpecification, BaseMCOModel
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)


class TableRow(HasTraits):
    """A representation of a variable in the workflow. Instances of TableRow
    are displayed in a table using the TableEditor."""

    #: The variable's type
    type = Unicode()

    #: The variable's name
    name = Unicode()


class KPISpecificationModelView(ModelView):

    # -------------------
    # Required Attributes
    # -------------------

    #: KPI model
    model = Instance(KPISpecification)

    # ------------------
    # Regular Attributes
    # ------------------

    #: Defines if the KPI is valid or not. Set by the function
    #: map_verify_workflow in workflow_view.py
    valid = Bool(True)

    #: An error message for issues in this modelview. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    #: Event to request a verification check on the workflow
    #: Listens to: :attr:`model.name <model>` and :attr:`model.type <model>`
    verify_workflow_event = Event

    # ------------------
    #     Properties
    # ------------------

    #: Human readable label for ModelView
    label = Property(Instance(Unicode),
                     depends_on='model:[name,objective]')

    # ------------------
    #     View
    # ------------------

    # The traits_view only displays possible options for
    # model.name listed in kpi_names. However, it is possible
    # to directly change model.name without updating kpi_names
    traits_view = View(
        UReadonly('model.name'),
        Item("model.objective"),
        Item('model.auto_scale'),
        Item("model.scale_factor",
             visible_when='not model.auto_scale'),
        kind="subpanel",
    )

    #: Property getters
    def _get_label(self):
        """Gets the label from the model object"""
        if self.model.name == '':
            return "KPI"
        return "KPI: {} ({})".format(self.model.name, self.model.objective)

    #: Listeners
    @on_trait_change('model.[name,type]')
    def kpi_change(self):
        self.verify_workflow_event = True


class KPISpecificationView(HasTraits):

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

    #: List of kpi ModelViews to display in ListEditor notebook
    kpi_model_views = List(Instance(KPISpecificationModelView))

    #: The human readable name of the KPI View
    label = Unicode('MCO KPIs')

    # ------------------
    # Dependent Attributes
    # ------------------

    #: The selected KPI in kpi_model_views
    selected_kpi = Instance(KPISpecificationModelView)

    #: The selected non-KPI in non_kpi_variables
    selected_non_kpi = Instance(TableRow)

    #: Defines if the KPI is valid or not. Set by the function
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    #: An error message for issues in this modelview. Set by the function
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    #: Event to request a verification check on the workflow
    #: Listens to: `model.name`,`model.objective`
    verify_workflow_event = Event()

    # ------------------
    #     Properties
    # ------------------

    #: The names of the KPIs in the Workflow.
    kpi_names = Property(List(Unicode),
                         depends_on='model.kpis[]')

    #: A list of TableRow instances, each representing a variable
    #: that could become a KPI
    non_kpi_variables = Property(
        List(TableRow),
        depends_on='variable_names_registry.data_source_outputs,'
                   'kpi_names'
    )

    # ------------------
    #      Buttons
    # ------------------

    #: Adds selected_non_kpi variable as a new MCO KPI
    add_kpi_button = Button('New KPI')

    #: Removes selected_kpi from the MCO
    remove_kpi_button = Button('Delete KPI')

    # ------------------
    #       View
    # ------------------

    def default_traits_view(self):

        # TableEditor to display non_kpi_variables
        table_editor = TableEditor(
            columns=[
                ObjectColumn(name="name",
                             label="name",
                             resize_mode="stretch"),
                ObjectColumn(name="type",
                             label="type",
                             resize_mode="stretch")
            ],
            auto_size=False,
            selected='selected_non_kpi'
        )

        # ListEditor to display kpi_model_views
        list_editor = ListEditor(
            page_name='.label',
            use_notebook=True,
            dock_style='tab',
            selected='selected_kpi',
            style='custom'
        )

        traits_view = View(
            VGroup(
                VGroup(
                    Item('kpi_model_views',
                         editor=list_editor,
                         show_label=False,
                         style='custom',
                         ),
                    show_labels=False,
                    show_border=True
                ),
                HGroup(
                    UReadonly(
                        'non_kpi_variables',
                        editor=table_editor
                    ),
                    show_border=True,
                    label='Non-KPI Variables'
                ),
                HGroup(
                    Item('add_kpi_button',
                         springy=True),
                    Item('remove_kpi_button'),
                    show_labels=False,
                ),
            ),
            dock='fixed',
            kind="livemodal"
        )

        return traits_view

    #: Property getters
    @cached_property
    def _get_kpi_names(self):
        """Listens to model.kpis to extract model names for display"""
        kpi_names = []

        for kpi in self.model.kpis:
            kpi_names.append(kpi.name)

        return kpi_names

    @cached_property
    def _get_non_kpi_variables(self):
        """Listens to variable_names_registry to extract names
         able to be assigned to kpis"""
        non_kpi = []

        if self.variable_names_registry is not None:
            variables_stack = (self.variable_names_registry
                               .available_variables_stack)
            for execution_layer in variables_stack:
                for variable in execution_layer:
                    # Each KPI must refer to a unique variable
                    kpi_check = variable[0] not in self.kpi_names
                    # Each KPI must refer to an output variable
                    variable_check = (
                            variable[0] in self.variable_names_registry
                            .data_source_outputs
                    )
                    if kpi_check and variable_check:
                        variable_rep = TableRow(name=variable[0],
                                                type=variable[1])
                        non_kpi.append(variable_rep)

        return non_kpi

    #: Listeners
    @on_trait_change('model.kpis[]')
    def update_kpi_model_views(self):
        """Update the list of existing KPI names"""
        self.kpi_model_views = [
            KPISpecificationModelView(
                model=kpi)
            for kpi in self.model.kpis
        ]

    # Workflow Validation
    @on_trait_change('kpi_model_views.verify_workflow_event')
    def received_verify_request(self):
        """Pass on call for verify_workflow_event"""
        self.verify_workflow_event = True

    #: Button actions
    def _add_kpi_button_fired(self):
        """Call add_kpi using selected non-kpi variable from table"""
        if self.selected_non_kpi is not None:
            self.add_kpi(
                KPISpecification(
                    name=self.selected_non_kpi.name
                )
            )

    def _remove_kpi_button_fired(self):
        """Call remove_kpi to delete selected kpi from list"""
        if self.selected_kpi is not None:
            self.remove_kpi(self.selected_kpi.model)

    #: Public methods
    def add_kpi(self, kpi):
        """Adds a KPISpecification to the MCO model associated with this
         modelview.

        Parameters
        ----------
        kpi: KPISpecification
            The KPISpecification to be added to the current MCO.
        """
        self.model.kpis.append(kpi)

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
