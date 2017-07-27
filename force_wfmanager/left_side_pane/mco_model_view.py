from traits.api import Instance, List, Property, Str
from traitsui.api import ModelView

from force_bdss.api import BaseMCOModel, BaseMCOParameter

from .view_utils import get_bundle_name


class MCOModelView(ModelView):
    model = Instance(BaseMCOModel)

    label = Str()

    mco_parameters_representation = Property(
        List(Instance(BaseMCOParameter)),
        depends_on="model.parameters"
    )

    def _get_mco_parameters_representation(self):
        return self.model.parameters

    def _label_default(self):
        return get_bundle_name(self.model.bundle)
