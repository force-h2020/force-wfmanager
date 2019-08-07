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
        if self.model.name == '' and self.model.type == '':
            return self._label_default()
        return self._label_default()+': {type} {name}'.format(
            type=self.model.type, name=self.model.name
        )

    @on_trait_change('selected_variable.[name,type]', post_init=True)
    def selected_variable_change(self):
        """Syncs the model name with the selected variable name
        (prevents direct changes to the KPISpecifications model)"""

        self.model.name = self.selected_variable.name
        self.model.type = self.selected_variable.type
        self.verify_workflow_event = True

    @on_trait_change('model:[name,type]', post_init=True)
    def model_change(self):
        """Syncs the model name with the selected variable name
        (prevents direct changes to the KPISpecifications model)"""

        if self.model.name != '':
            self.model.name = self.selected_variable.name
        if self.model.type != '':
            self.model.type = self.selected_variable.type

    def update_available_variables(self, available_variables):
        """Overloads parent class method to update selected_variable
        model selection upon update of available_variables"""

        super(MCOParameterModelView, self).update_available_variables(
            available_variables)

        for variable in self.available_variables:
            name_check = variable.name == self.model.name
            type_check = variable.type == self.model.type
            if name_check and type_check:
                self.selected_variable = variable
