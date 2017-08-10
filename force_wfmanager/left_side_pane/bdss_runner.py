from pyface.tasks.api import TraitsDockPane

from traits.api import Instance, Button

from traitsui.api import View, UItem


class BDSSRunner(TraitsDockPane):
    """ Side pane which contains the run button for running the BDSS """

    id = 'force_wfmanager.bdss_runner'
    name = 'Run BDSS'

    wfmanager_task = Instance('force_wfmanager.wfmanager_task.WfManagerTask')

    run_button = Button('Run')

    traits_view = View(
        UItem('run_button')
    )
