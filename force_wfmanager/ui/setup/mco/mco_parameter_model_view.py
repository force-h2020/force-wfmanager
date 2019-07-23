from traits.api import (
    cached_property, Property, Instance, Unicode, on_trait_change
)
from traitsui.api import (
    View, Item, InstanceEditor, Readonly,
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
                     depends_on='model.[name,type]')

    # ----------
    #    View
    # ----------

    def default_traits_view(self):
        """Default view containing both traits from the base class and
        any additional user-defined traits"""

        return View(Item('name', object='model',
                         editor=EnumEditor(name='object._combobox_values')),
                    Readonly('type', object='model'),
                    Item('model',
                         editor=InstanceEditor(),
                         style='custom')
                    )

    # -------------
    #    Defaults
    # -------------

    def _label_default(self):
        """Return a default label corresponding to the MCO parameter factory"""
        return get_factory_name(self.model.factory)

    # -------------
    #   Listeners
    # -------------

    @cached_property
    def _get_label(self):
        """Return a label appending both the parameter name and type to the
        default"""
        if self.model.name == '' and self.model.type == '':
            return self._label_default()
        return self._label_default()+': {type} {name}'.format(
            type=self.model.type, name=self.model.name
        )

    @on_trait_change('model.[name,type]')
    def parameter_model_change(self):
        if self.model is not None:
            try:
                index = self._combobox_values.index(self.model.name)
                self.model.type = self.available_variables[index][1]
            except ValueError:
                self.model.type = ''

        self.model_change()
