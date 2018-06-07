from traits.api import Instance, Str, Bool, on_trait_change
from traitsui.api import ModelView, View, Item

from force_bdss.core.kpi_specification import KPISpecification


class KPISpecificationModelView(ModelView):
    #: MCO parameter model
    model = Instance(KPISpecification, allow_none=False)

    #: The human readable name of the KPI
    label = Str()

    #: Defines if the KPI is valid or not
    valid = Bool(True)

    #: Base view for the MCO parameter
    traits_view = View(
        Item("model.name"),
        Item("model.objective"),
        kind="subpanel",
    )

    def _label_default(self):
        return _get_label(self.model)


def _get_label(model):
    if model.name == '':
        return "KPI"

    return "KPI: {}".format(model.name)

