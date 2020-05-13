#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from traits.has_traits import HasTraits
from traits.trait_types import Instance


class DummyUI:
    def dispose(self):
        pass


class DummyModelInfo(HasTraits):

    object = Instance(HasTraits)

    ui = Instance(DummyUI)

    def _ui_default(self):
        return DummyUI()
