import os

from traits.etsconfig.api import ETSConfig

from force_wfmanager.wfmanager import WfManager


class ProbeApp(WfManager):
    """ Subclasses the main package's application class to probe the state
    in: ETSconfig.application_home, which depends on the application traits.
    """
    def printe_state_loc(self):
        print(
            os.path.abspath(os.path.join(
                ETSConfig.application_home,
                "tasks", ETSConfig.toolkit,
                "application_memento"
            ))
        )


if __name__ == "__main__":
    probe_app = ProbeApp()
    probe_app.printe_state_loc()
