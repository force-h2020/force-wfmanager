from traits.api import Instance

from force_bdss.api import BaseKPICalculatorModel

from .evaluator_model_view import EvaluatorModelView


class KPICalculatorModelView(EvaluatorModelView):
    #: KPI Calculator model (More restrictive than the ModelView model
    #: attribute)
    model = Instance(BaseKPICalculatorModel, allow_none=False)
