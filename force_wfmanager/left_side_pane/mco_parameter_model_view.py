from traits.api import Instance, Str, on_trait_change

from traitsui.api import View, Item, ModelView

from force_bdss.api import BaseMCOParameter

from .view_utils import get_factory_name


class MCOParameterModelView(ModelView):
    #: MCO parameter model
    model = Instance(BaseMCOParameter, allow_none=False)

    #: The human readable name of the MCO parameter class
    label = Str()

    #: The user defined name of the MCO parameter
    name = Str()

    #: The type of the MCO parameter
    type = Str()

    #: Base view for the MCO parameter
    traits_view = View(
        Item(name="name"),
        Item(name="type"),
        kind="subpanel",
    )

    @on_trait_change('name')
    def update_name(self):
        self.model.name = self.name

    @on_trait_change('type')
    def update_type(self):
        self.model.type = self.type

    def _label_default(self):
        return get_factory_name(self.model.factory)

    def _name_default(self):
        return self.model.name

    def _type_default(self):
        return self.model.type
