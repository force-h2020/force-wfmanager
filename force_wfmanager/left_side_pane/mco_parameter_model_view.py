from traits.api import (
    Instance, Unicode, Bool, on_trait_change, Event, Property)

from traitsui.api import View, Item, ModelView

from force_bdss.api import BaseMCOParameter
from force_wfmanager.api import get_factory_name


class MCOParameterModelView(ModelView):
    #: MCO parameter model
    model = Instance(BaseMCOParameter, allow_none=False)

    #: The human readable name of the MCO parameter class
    label = Property(Unicode(), depends_on="model.name,model.type")

    #: Defines if the MCO parameter is valid or not
    valid = Bool(True)

    #: An error message for issues in this modelview
    error_message = Unicode()

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

    def _get_label(self):
        if self.model.name == '' and self.model.type == '':
            return self._label_default()
        return self._label_default()+': {} {}'.format(self.model.type,
                                                      self.model.name)

    def _label_default(self):
        return get_factory_name(self.model.factory)
