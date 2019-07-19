from force_wfmanager.ui.setup.mco.base_mco_options_model_view import\
    BaseMCOOptionsModelView
from force_wfmanager.ui.setup.mco.base_mco_options_view import \
    BaseMCOOptionsView


class DummyBaseMCOOptionsView(BaseMCOOptionsView):

    def _model_views_default(self):
        return []


class DummyBaseMCOOptionsModelView(BaseMCOOptionsModelView):

    def _get_label(self):
        return
