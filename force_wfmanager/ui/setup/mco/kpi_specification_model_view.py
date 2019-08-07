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
    # -----------

    # The traits_view only displays possible options for
    # model.name listed in kpi_names. However, it is possible
    # to directly change model.name without updating kpi_names
    traits_view = View(
        Item('selected_variable',
             editor=InstanceEditor(
                 name='available_variables',
                 editable=False
             )
             ),
        Item("objective", object='model'),
        Item('auto_scale', object='model'),
        Item("scale_factor", object='model',
             visible_when='not model.auto_scale'),
        kind="subpanel",
    )

    # -----------
    #  Listeners
    # -----------

    def _get_label(self):
        """Gets the label from the model object"""
        if self.model.name == '':
            return "KPI"
        return "KPI: {} ({})".format(
            self.model.name, self.model.objective
        )

    @on_trait_change('selected_variable.name', post_init=True)
    def selected_variable_change(self):
        """Syncs the model name with the selected variable name"""

        self.model.name = self.selected_variable.name
        self.verify_workflow_event = True

    @on_trait_change('model:name', post_init=True)
    def model_change(self):
        """Syncs the model name with the selected variable name
        (prevents direct changes to the KPISpecifications model)"""

        if self.model.name != '':
            self.model.name = self.selected_variable.name

    def update_available_variables(self, available_variables):
        """Overloads parent class method to check whether existing
        model can be synced to any variable in available_variables.
        This is required upon instantiation, """

        super().update_available_variables(available_variables)

        # Check whether model can be assigned to a variable
        for variable in self.available_variables:
            if variable.name == self.model.name:
                self.selected_variable = variable
