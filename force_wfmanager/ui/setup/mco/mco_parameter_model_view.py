from traits.api import (
    cached_property, Property, Instance, Unicode, on_trait_change
)
from traitsui.api import (
    View, Item, InstanceEditor,
    EnumEditor
)

from force_wfmanager.ui.setup.mco.base_mco_options_model_view import \
    BaseMCOOptionsModelView
from force_wfmanager.ui.ui_utils import get_factory_name


class MCOParameterModelView(BaseMCOOptionsModelView):

    # -------------
    #  Properties
    # -------------

    label = Property(Instance(Unicode),
                     depends_on='model.factory')

    # ----------
    #    View
    # ----------

    def default_traits_view(self):
        """Default view containing both traits from the base class and
        any additional user-defined traits"""

        return View(Item('name', object='model',
                         editor=EnumEditor(name='object._combobox_values')),
                    Item('type', object='model'),
                    Item('model',
                         editor=InstanceEditor(),
                         style='custom')
                    )

    #: Defaults
    def _label_default(self):
        """Return a default label corresponding to the MCO parameter factory"""
        return get_factory_name(self.model.factory)

    #: Property getters
    @cached_property
    def _get_label(self):
        """Return a label appending both the parameter name and type to the
        default"""
        if self.model.name == '' and self.model.type == '':
            return self._label_default()
        return self._label_default()+': {type} {name}'.format(
            type=self.model.type, name=self.model.name
        )

    #: Listeners
    @on_trait_change('model.[name,type]')
    def parameter_model_change(self):
        self.model_change()
