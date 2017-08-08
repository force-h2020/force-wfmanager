from traits.api import Instance, List, Property, Str
from traitsui.api import ModelView

from force_bdss.api import BaseMCOModel

from .mco_parameter_model_view import MCOParameterModelView
from .view_utils import get_factory_name


class MCOModelView(ModelView):
    #: MCO model (More restrictive than the ModelView model attribute)
    model = Instance(BaseMCOModel)

    #: Label to be used in the TreeEditor
    label = Str()

    #: List of MCO parameters to be displayed in the TreeEditor, it is a
    #: Property so that the list in the editor is synchronized with the actual
    #: list of parameters in the MCO model
    mco_parameters_representation = Property(
        List(Instance(MCOParameterModelView)),
        depends_on="model.parameters"
    )

    def _get_mco_parameters_representation(self):
        return [MCOParameterModelView(model=parameter)
                for parameter in self.model.parameters]

    def _label_default(self):
        return get_factory_name(self.model.factory)
