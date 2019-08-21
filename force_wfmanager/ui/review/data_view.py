from traits.api import (
    Bool, Instance, HasStrictTraits
)

from force_wfmanager.model.analysis_model import AnalysisModel


class BaseDataView(HasStrictTraits):
    """ Base class for contributed UI views of models. """

    # -------------------
    # Required Attributes
    # -------------------

    #: The analysis model containing the results
    analysis_model = Instance(AnalysisModel, allow_none=False)

    #: Whether this data view is the one being currently visualized
    is_active_view = Bool(False)

    # ------------------
    # Regular Attributes
    # ------------------

    #: Short description for the UI selection (to be overwritten)
    description = "Base Data View"
