from traits.api import HasStrictTraits, List, Str, Tuple, Int


class AnalysisModel(HasStrictTraits):
    #: List of parameter names
    value_names = List(Str)

    #: Evaluation steps, each evalutation step is a tuple of parameter values,
    #: received from the bdss. Each value can be of any type. The order of
    #: the parameters in each evaluation step must match the order of
    #: value_names
    evaluation_steps = List(Tuple())

    #: Selected step, used for highlighting in the table/plot
    selected_step_index = Int(None)
