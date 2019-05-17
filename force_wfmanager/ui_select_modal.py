from traits.api import (
    Button, Dict, Enum, HasStrictTraits, Instance, List, Str, Unicode,
    on_trait_change
)
from traitsui.api import Item, View, Handler
from traitsui.menu import OKCancelButtons
from force_bdss.api import BaseExtensionPlugin
from force_wfmanager.contributed_ui import ContributedUI


class UISelectHandler(Handler):

    def close(self, info, is_ok):
        if not is_ok:
            info.object.selected_ui = None

        return True


class UISelectModal(HasStrictTraits):

    contributed_uis = List(ContributedUI)
    ui_name_map = Dict(Str, Instance(ContributedUI))
    available_plugins = List(Instance(BaseExtensionPlugin))

    contributed_ui_name = Enum(Unicode, values='_contributed_ui_names')
    _contributed_ui_names = List(Unicode)

    select_ui = Button('Select UI >>')
    selected_ui = Instance(ContributedUI)

    traits_view = View(
        Item("contributed_ui_name"),
        buttons=OKCancelButtons,
        handler=UISelectHandler(),
        kind="livemodal"
    )

    def __contributed_ui_names_default(self):
        return [''] + [ui.name for ui in self.contributed_uis]

    @on_trait_change("contributed_ui_name")
    def show_ui(self):
        if not self.contributed_ui_name:
            self.selected_ui = None
        else:
            self.selected_ui = self.ui_name_map[self.contributed_ui_name]

    def _ui_name_map_default(self):
        return {ui.name: ui for ui in self.contributed_uis}