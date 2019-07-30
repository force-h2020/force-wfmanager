from traits.api import (
    cached_property, Property, Instance, Unicode, on_trait_change
)
from traitsui.api import (
    View, Item, InstanceEditor, Readonly
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

        return View(Item('selected_variable',
                         editor=InstanceEditor(
                             name='available_variables',
                             editable=False)
                         ),
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
        if self.model is None:
            return self._label_default()
        if self.selected_variable is None:
            return self._label_default()
        return self._label_default()+': {type} {name}'.format(
            type=self.model.type, name=self.model.name
        )

    @on_trait_change('model.[name,type],'
                     'selected_variable.[name,type]')
    def selected_variable_change(self):
        """Syncs the model name and type with the selected variable name
        and type (prevents direct changes to the MCOParameter model)"""
        if self.model is not None:
            if self.selected_variable is not None:
                self.model.name = self.selected_variable.name
                self.model.type = self.selected_variable.type
            self.model_change()
