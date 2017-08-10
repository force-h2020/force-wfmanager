import os

from pyface.tasks.api import TraitsDockPane

from traits.api import Instance, Button, on_trait_change

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

    @on_trait_change('run_button')
    def run(self):
        self.wfmanager_task.save_workflow()

        if len(self.wfmanager_task.current_file) == 0:
            raise RuntimeError("Can not run if you do not save the workflow")

        os.system("force_bdss {}".format(self.wfmanager_task.current_file))
