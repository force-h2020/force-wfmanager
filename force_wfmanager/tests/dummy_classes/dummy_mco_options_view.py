#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from force_wfmanager.ui.setup.mco.base_mco_options_view import \
    BaseMCOOptionsView


class DummyBaseMCOOptionsView(BaseMCOOptionsView):

    def _model_views_default(self):
        return []
