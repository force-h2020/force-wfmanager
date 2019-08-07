from traits.api import (
    List, Unicode, on_trait_change, Button
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
from force_wfmanager.utils.variable import Variable


class KPISpecificationView(BaseMCOOptionsView):

    # ------------------
    # Regular Attributes
    # ------------------

    #: The human readable name of the KPI View
    name = Unicode('KPIs')

    #: A list names, each representing a variable
    #: that could become a KPI
    kpi_name_options = List(Variable)

    # ------------------
    #      Buttons
    # ------------------

    #: Adds a new MCO KPI
    add_kpi_button = Button('New KPI')

    #: Removes selected_model_view from the MCO
    remove_kpi_button = Button('Delete KPI')

    # -------------------
    #        View
    # -------------------

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

    # -------------------
    #      Defaults
    # -------------------

    def _model_views_default(self):
        """Creates a list of KPISpecificationModelViews for each
        model.kpi"""
        model_views = []

        if self.model is not None:
            # Add all MCO KPIs as ModelViews
            for kpi in self.model.kpis:
                model_view = self._create_model_view(kpi)
                model_views.append(model_view)

        return model_views

    # -------------------
    #     Listeners
    # -------------------

    @on_trait_change('model.kpis')
    def update_kpi_model_views(self):
        """Triggers the base method update_model_views when
        KPISpecifications are updated"""
        if self.model is not None:
            self.update_model_views(self.model.kpis)
        else:
            self.update_model_views()

    @on_trait_change('kpi_name_options[]')
    def update_model_views_available_variables(self):
        """Updates all model_view available_variables when kpi_name_options
         is updated"""

        # Update the model_views with the new kpi_name_options
        for model_view in self.model_views:
            model_view.update_available_variables(self.kpi_name_options)

    def _add_kpi_button_fired(self):
        """Call add_kpi to insert a blank KPI to the model"""
        self.add_kpi(KPISpecification())

        # Highlight new KPI in ListEditor
        self.selected_model_view = self.model_views[-1]

    def _remove_kpi_button_fired(self):
        """Call remove_kpi to delete selected kpi from model"""
        self._remove_button_action(self.remove_kpi)

    # -------------------
    #   Private Methods
    # -------------------

    def _create_model_view(self, kpi):
        """Overloaded method to create a MCOParameterModelView from a
        MCOParameter"""

        model_view = KPISpecificationModelView(
            model=kpi,
            available_variables=self.kpi_name_options
        )

        for variable in model_view.available_variables:
            if model_view.check_variable(variable):
                model_view.selected_variable = variable

        return model_view

    # -------------------
    #   Public methods
    # -------------------

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
