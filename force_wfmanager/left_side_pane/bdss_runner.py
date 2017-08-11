from pyface.tasks.api import TraitsDockPane

from traits.api import Button

from traitsui.api import View, UItem


class BDSSRunner(TraitsDockPane):
    """ Side pane which contains the run button for running the BDSS """
    id = 'force_wfmanager.bdss_runner'
    name = 'Run BDSS'

    #: Remove the possibility to close the pane
    closable = False

    #: Run button for running the computation
    run_button = Button('Run')

    traits_view = View(
        UItem('run_button')
    )
