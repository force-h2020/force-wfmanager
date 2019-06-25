from traits.api import (
    Instance, HasStrictTraits,
)

from force_wfmanager.central_pane.analysis_model import AnalysisModel


class BaseDataView(HasStrictTraits):
    analysis_model = Instance(AnalysisModel, allow_none=False)
