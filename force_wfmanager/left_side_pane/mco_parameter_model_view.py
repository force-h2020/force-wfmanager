from traits.api import Instance, Str, on_trait_change

from traitsui.api import View, Item, ModelView

from force_bdss.api import BaseMCOParameter, Identifier

from .view_utils import get_factory_name


class MCOParameterModelView(ModelView):
    #: MCO parameter model
    model = Instance(BaseMCOParameter, allow_none=False)

    #: The human readable name of the MCO parameter class
    label = Str()

    name = Identifier()

    #: Base view for the MCO parameter
    traits_view = View(
        Item("model.name"),
        Item("model.type"),
        kind="subpanel",
    )

    def _label_default(self):
        return get_factory_name(self.model.factory)

    @on_trait_change('model.name')
    def update_name(self):
        self.name = self.model.name
