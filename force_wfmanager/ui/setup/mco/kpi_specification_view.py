from traits.api import (
    Bool, Event, Instance, List, Property, Unicode, cached_property,
    on_trait_change, HasTraits, Button
)
from traitsui.api import (
    Item, View, ListEditor,
    VGroup, HGroup, ModelView, EnumEditor
)

from force_bdss.api import KPISpecification, BaseMCOModel
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)


class KPISpecificationModelView(ModelView):

    # -------------------
    # Required Attributes
    # -------------------

    #: KPI model
    model = Instance(KPISpecification)

    # Only display name options for existing KPIs (this isn't perfect and
    # does allow
    _combobox_names = List(Unicode)

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
        Item('name', object='model',
             editor=EnumEditor(name='object._combobox_names')),
        Item("objective", object='model'),
        Item('auto_scale', object='model'),
        Item("scale_factor", object='model',
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
    @on_trait_change('model.[name,objective]')
    def kpi_change(self):
        self.verify_workflow_event = True

    @on_trait_change('model.name,_combobox_names')
    def _check_kpi_name(self):
        if self.model is not None:
            if self._combobox_names is not None:
                if self.model.name not in self._combobox_names + ['']:
                    self.model.name = ''


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
    kpi_names = Property(
        List(Unicode), depends_on='model.kpis.name'
    )

    #: A list names, each representing a variable
    #: that could become a KPI
    kpi_name_options = Property(
        List(Unicode),
        depends_on='variable_names_registry.data_source_outputs'
    )

    # ------------------
    #      Buttons
    # ------------------

    #: Adds a new MCO KPI
    add_kpi_button = Button('New KPI')

    #: Removes selected_kpi from the MCO
    remove_kpi_button = Button('Delete KPI')

    def __init__(self, model=None, *args, **kwargs):
        super(KPISpecificationView, self).__init__(*args, **kwargs)
        if model is not None:
            self.model = model

    def default_traits_view(self):

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
                    Item('add_kpi_button',
                         springy=True),
                    Item('remove_kpi_button',
                         enabled_when='selected_kpi is not None'),
                    show_labels=False,
                ),
            ),
            dock='fixed',
            kind="livemodal"
        )

        return traits_view

    # Defaults
    def _kpi_model_views_default(self):
        """Creates a list of KPISpecificationModelViews for each
        model.kpi"""
        kpi_model_views = []
        if self.model is not None:
            # Update model view list
            kpi_model_views += [
                KPISpecificationModelView(
                    model=kpi,
                    _combobox_names=self.kpi_name_options
                )
                for kpi in self.model.kpis
            ]

        return kpi_model_views

    def _selected_kpi_default(self):
        """Default value for selected_kpi"""
        if len(self.kpi_model_views) > 0:
            return self.kpi_model_views[0]

    #: Property getters
    @cached_property
    def _get_kpi_names(self):
        """Listens to model.kpis to extract model names for display"""
        kpi_names = []
        for kpi in self.model.kpis:
            kpi_names.append(kpi.name)

        return kpi_names

    @cached_property
    def _get_kpi_name_options(self):
        """Listens to variable_names_registry to extract
         possible names for new KPIs"""
        kpi_name_options = []
        if self.variable_names_registry is not None:
            kpi_name_options += (
                self.variable_names_registry.data_source_outputs
            )

        return kpi_name_options

    #: Listeners
    @on_trait_change('kpi_names')
    def _kpi_names_check(self):
        """Reports a validation warning if duplicate KPI names exist
        """
        error_message = ''
        unique_check = True

        for name in self.kpi_names:
            if self.kpi_names.count(name) > 1:
                unique_check = False

        if not unique_check:
            error_message += 'Two or more KPIs have a duplicate name'

        self.valid = (self.valid and unique_check)
        self.error_message = error_message

    @on_trait_change('kpi_name_options')
    def update_kpi_model_views__combobox(self):
        """Update the KPI model view name options"""
        for kpi_view in self.kpi_model_views:
            kpi_view._combobox_names = self.kpi_name_options

    @on_trait_change('model.kpis')
    def update_kpi_model_views(self):
        """Update the list of KPI model views"""
        self.kpi_model_views = self._kpi_model_views_default()

        # Update selected view
        if len(self.kpi_model_views) == 0:
            self.selected_kpi = None

    # Workflow Validation
    @on_trait_change('kpi_model_views.verify_workflow_event')
    def received_verify_request(self):
        """Pass on call for verify_workflow_event"""
        self.verify_workflow_event = True

    @on_trait_change('kpi_model_views.valid')
    def update_validity(self):
        """Pass on kpi_model_views validity"""

        valid_check = True
        for kpi_view in self.kpi_model_views:
            if not kpi_view.valid:
                valid_check = False

        self.valid = (self.valid and valid_check)

    #: Button actions
    def _add_kpi_button_fired(self):
        """Call add_kpi using selected non-kpi variable from table"""
        self.add_kpi(KPISpecification())

        # Highlight new KPI in ListEditor
        self.selected_kpi = self.kpi_model_views[-1]

    def _remove_kpi_button_fired(self):
        """Call remove_kpi to delete selected kpi from list"""

        index = self.kpi_model_views.index(self.selected_kpi)
        self.remove_kpi(self.selected_kpi.model)

        # Update user selection
        if len(self.kpi_model_views) > 0:
            if index == 0:
                self.selected_kpi = self.kpi_model_views[index]
            else:
                self.selected_kpi = self.kpi_model_views[index-1]

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
