from traits.api import Instance, List, Str, on_trait_change
from traitsui.api import ModelView

from force_bdss.api import BaseMCOModel, Identifier

from .mco_parameter_model_view import MCOParameterModelView
from .view_utils import get_factory_name


class MCOModelView(ModelView):
    #: MCO model (More restrictive than the ModelView model attribute)
    model = Instance(BaseMCOModel)

    #: Label to be used in the TreeEditor
    label = Str()

    #: List of MCO parameters to be displayed in the TreeEditor
    mco_parameters_representation = List(Instance(MCOParameterModelView))

    #: List of MCO parameter names
    mco_parameters_names = List(Identifier)

    @on_trait_change('model.parameters[]')
    def update_mco_parameters_representation(self):
        """ Update the MCOParameterModelViews """
        self.mco_parameters_representation = [
            MCOParameterModelView(model=parameter)
            for parameter in self.model.parameters]

    @on_trait_change('mco_parameters_representation.model.name')
    def update_mco_parameter_names(self):
        """ Update the available paramter names """
        self.mco_parameters_names = [
            p.model.name
            for p in self.mco_parameters_representation
            if len(p.model.name) != 0
        ]

    def _label_default(self):
        return get_factory_name(self.model.factory)
