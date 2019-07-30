from traits.api import (
    Property, Instance, Unicode, on_trait_change
)
from traitsui.api import (
    Item, View, InstanceEditor
)

from force_wfmanager.ui.setup.mco.base_mco_options_model_view import \
    BaseMCOOptionsModelView


class KPISpecificationModelView(BaseMCOOptionsModelView):

    # -------------
    #  Properties
    # -------------

    label = Property(Instance(Unicode),
                     depends_on='model.[name,objective]')

    # -----------
    #     View
    # ----------

    # The traits_view only displays possible options for
    # model.name listed in kpi_names. However, it is possible
    # to directly change model.name without updating kpi_names
    traits_view = View(
        Item('selected_variable',
             editor=InstanceEditor(
                 name='available_variables',
                 editable=False)
                     ),
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
    def kpi_model_change(self):
        self.model_change()

    @on_trait_change('selected_variable.name')
    def selected_variable_change(self):
        if self.model is not None:
            self.model.name = self.selected_variable.name
