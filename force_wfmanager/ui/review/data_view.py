from traits.api import (
    Instance, HasStrictTraits
)

from force_wfmanager.model.analysis_model import AnalysisModel


class BaseDataView(HasStrictTraits):
    """ Base class for contributed UI views of models. """

    # -------------------
    # Required Attributes
    # -------------------

    #: The analysis model containing the results
    analysis_model = Instance(AnalysisModel, allow_none=False)

    # ------------------
    # Regular Attributes
    # ------------------

    #: Short description for the UI selection
    description = "Base Data View"
