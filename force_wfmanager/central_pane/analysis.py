from pyface.tasks.api import TraitsTaskPane

from traits.api import List, Instance, Int, Any, Str, HasStrictTraits

from traitsui.api import View, HGroup, VGroup, Spring


class Result(HasStrictTraits):
    name = Str()
    value = Any()


class EvaluationStep(HasStrictTraits):
    _step = 0

    @classmethod
    def init_step_count(cls):
        cls._step = 0

    @classmethod
    def get_step(cls):
        cls._step += 1
        return cls._step

    def __init__(self, *args, **kwargs):
        self.step = EvaluationStep.get_step()
        super(EvaluationStep, self).__init__(*args, **kwargs)

    step = Int()
    results = List(Instance(Result))


class Analysis(TraitsTaskPane):
    id = 'force_wfmanager.analysis'
    name = 'Analysis'

    #: Evaluation steps
    evaluation_steps = List(Instance(EvaluationStep))

    #: Selected step in the result table/pareto front
    selected_step = Int()

    view = View(HGroup(
        VGroup(
            Spring(),
            label='Result Table'
        ),
        VGroup(
            Spring(),
            label='Pareto Front'
        )
    ))
