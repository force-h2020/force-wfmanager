from traits.api import (
    List, Property, Unicode, cached_property,
    on_trait_change, Button
)
from traitsui.api import (
    Item, View, ListEditor,
    VGroup, HGroup
)

from force_bdss.api import KPISpecification
from force_wfmanager.ui.setup.mco.base_mco_options_view import \
    BaseMCOOptionsView
from force_wfmanager.ui.setup.mco.kpi_specification_model_view import (
    KPISpecificationModelView
)


class KPISpecificationView(BaseMCOOptionsView):

    # ------------------
    # Regular Attributes
    # ------------------

    #: The human readable name of the KPI View
    label = Unicode('MCO KPIs')

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

    #: Removes selected_model_view from the MCO
    remove_kpi_button = Button('Delete KPI')

    def default_traits_view(self):

        # ListEditor to display model_views
        list_editor = ListEditor(
            page_name='.label',
            use_notebook=True,
            dock_style='tab',
            selected='selected_model_view',
            style='custom'
        )

        traits_view = View(
            VGroup(
                VGroup(
                    Item('model_views',
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
                         enabled_when='selected_model_view '
                                      'is not None'),
                    show_labels=False,
                ),
            ),
            dock='fixed',
            kind="livemodal"
        )

        return traits_view

    # Defaults
    def _model_views_default(self):
        """Creates a list of KPISpecificationModelViews for each
        model.kpi"""
        model_views = []
        if self.model is not None:
            # Update model view list
            model_views += [
                KPISpecificationModelView(
                    model=kpi,
                    _combobox_values=self.kpi_name_options
                )
                for kpi in self.model.kpis
            ]

        return model_views

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
            outputs = self.variable_names_registry.data_source_outputs
            inputs = self.variable_names_registry.data_source_inputs

            kpi_name_options += (
                [output_ for output_ in outputs
                 if output_ not in inputs]
            )

        return kpi_name_options

    #: Listeners
    @on_trait_change('kpi_name_options')
    def update_model_views__combobox(self):
        """Update the KPI model view name options"""
        for kpi_view in self.model_views:
            kpi_view._combobox_values = self.kpi_name_options

    @on_trait_change('model.kpis')
    def update_kpi_model_views(self):
        """ Triggers the base method update_model_views when
        KPISpecifications are updated"""
        self.update_model_views()

    # Workflow Validation
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

    #: Button actions
    def _add_kpi_button_fired(self):
        """Call add_kpi to insert a blank KPI to the model"""
        self.add_kpi(KPISpecification())

        # Highlight new KPI in ListEditor
        self.selected_model_view = self.model_views[-1]

    def _remove_kpi_button_fired(self):
        """Call remove_kpi to delete selected kpi from model"""

        index = self.model_views.index(self.selected_model_view)
        self.remove_kpi(self.selected_model_view.model)

        # Update user selection
        if len(self.model_views) > 0:
            if index == 0:
                self.selected_model_view = self.model_views[index]
            else:
                self.selected_model_view = self.model_views[index-1]

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
