#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from force_bdss.api import MCORuntimeEvent, UIEventMixin


class ProbeUIRuntimeEvent(MCORuntimeEvent, UIEventMixin):

    def serialize(self):
        return {'some_metadata': 0}
