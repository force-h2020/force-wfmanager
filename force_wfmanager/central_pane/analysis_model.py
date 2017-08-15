from traits.api import (
    HasStrictTraits, List, Str, Tuple, Int, on_trait_change, TraitError,
)


class AnalysisModel(HasStrictTraits):
    #: List of parameter names
    value_names = List(Str)

    #: Evaluation steps, each evaluation step is a tuple of parameter values,
    #: received from the bdss. Each value can be of any type. The order of
    #: the parameters in each evaluation step must match the order of
    #: value_names
    evaluation_steps = List(Tuple())

    #: Selected step, used for highlighting in the table/plot
    selected_step_index = Int()

    @on_trait_change("evaluation_steps[]")
    def _verify_evaluation_steps(self, name, new):
        if name.endswith("_items"):
            for entry in new:
                if len(entry) != len(self.value_names):
                    raise TraitError("evaluation_steps_items")

    @on_trait_change("value_names")
    def _clear_evaluation_steps(self):
        self.evaluation_steps[:] = []

