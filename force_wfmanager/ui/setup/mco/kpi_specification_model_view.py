#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from traits.api import (
    Property, Str, on_trait_change
)
from traitsui.api import (
    Item, View, EnumEditor
)

from force_wfmanager.ui.setup.mco.base_mco_options_model_view import \
    BaseMCOOptionsModelView


class KPISpecificationModelView(BaseMCOOptionsModelView):

    # -------------
    #  Properties
    # -------------

    label = Property(Str, depends_on='model.[name,objective]')

    # -----------
    #     View
    # ----------

    # The traits_view only displays possible options for
    # model.name listed in kpi_names. However, it is possible
    # to directly change model.name without updating kpi_names
    traits_view = View(
        Item('name', object='model',
             editor=EnumEditor(name='object._combobox_values')),
        Item("objective", object='model'),
        Item("target_value", object='model',
             visible_when='model.objective=="TARGET"'),
        Item("use_bounds", object='model'),
        Item("lower_bound", object='model',
             visible_when='model.use_bounds'),
        Item("upper_bound", object='model',
             visible_when='model.use_bounds'),
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
    @on_trait_change('model.[name,objective,use_bounds,'
                     'lower_bound,upper_bound,target_value]')
    def kpi_model_change(self):
        self.model_change()
