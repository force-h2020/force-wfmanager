from traits.api import Instance, Str, Bool, on_trait_change, Event

from traitsui.api import View, Item, ModelView

from force_bdss.api import BaseMCOParameter

from .view_utils import get_factory_name


class MCOParameterModelView(ModelView):
    #: MCO parameter model
    model = Instance(BaseMCOParameter, allow_none=False)

    #: The human readable name of the MCO parameter class
    label = Str()

    #: Defines if the MCO parameter is valid or not
    valid = Bool(True)

    #: An error message for issues in this modelview
    error_message = Str

    #: Base view for the MCO parameter
    traits_view = View(
        Item("model.name"),
        Item("model.type"),
        kind="subpanel",
    )

    #: Event to request a verification check on the workflow
    verify_workflow_event = Event

    @on_trait_change('model.name,model.type')
    def parameter_change(self):
        self.verify_workflow_event = True

    def _label_default(self):
        return get_factory_name(self.model.factory)
