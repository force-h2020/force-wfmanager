from traits.api import Instance

from force_bdss.api import BaseDataSourceModel

from .evaluator_model_view import EvaluatorModelView


class DataSourceModelView(EvaluatorModelView):
    #: DataSource model (More restrictive than the ModelView model attribute)
    model = Instance(BaseDataSourceModel, allow_none=False)
