from force_wfmanager.central_pane.analysis_model import AnalysisModel

from traits.api import (
    Button, Bool, Dict, Enum, HasStrictTraits, Instance, List, Property, Tuple,
    on_trait_change
)

class BaseDataView(HasStrictTraits):
    analysis_model = Instance(AnalysisModel, allow_none=False)
