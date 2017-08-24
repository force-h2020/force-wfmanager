from traits.api import Instance, List, Str, on_trait_change, Bool

from traitsui.api import ModelView

from force_bdss.api import BaseMCOModel

from .mco_parameter_model_view import MCOParameterModelView
from .view_utils import get_factory_name


class MCOModelView(ModelView):
    #: MCO model (More restrictive than the ModelView model attribute)
    model = Instance(BaseMCOModel)

    #: Label to be used in the TreeEditor
    label = Str()

    #: List of MCO parameters to be displayed in the TreeEditor
    mco_parameters_representation = List(Instance(MCOParameterModelView))

    #: Defines if the MCO is valid or not
    valid = Bool(True)

    @on_trait_change('model.parameters[]')
    def update_mco_parameters_representation(self):
        """ Update the MCOParameterModelViews """
        self.mco_parameters_representation = [
            MCOParameterModelView(model=parameter)
            for parameter in self.model.parameters]

    def _label_default(self):
        return get_factory_name(self.model.factory)
