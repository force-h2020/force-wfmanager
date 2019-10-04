import logging
import click

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin
from stevedore import extension
from stevedore.exception import NoMatches
from traits.api import push_exception_handler

from force_bdss.core_plugins.factory_registry_plugin import (
    FactoryRegistryPlugin
)
from force_wfmanager.version import __version__
from force_wfmanager.wfmanager import WfManager
from force_wfmanager.plugins.wfmanager_plugin import WfManagerPlugin

push_exception_handler(lambda *args: None, reraise_exceptions=True)


@click.command()
@click.version_option(version=__version__)
@click.option(
    '--debug', is_flag=True, default=False,
    help="Prints extra debug information in force_wfmanager.log"
)
@click.option(
    '--profile', is_flag=True, default=False,
    help="Run GUI under cProfile, creating .prof and .pstats "
         "files in the current directory."
)
@click.option(
    '--window-size', nargs=2, type=int,
    help="Sets the initial window size"
)
@click.argument(
    'workflow_file', type=click.Path(exists=True), required=False,
    default=None
)
def force_wfmanager(workflow_file, debug, window_size, profile):
    """Launches the FORCE workflow manager application"""
    if not window_size:
        window_size = None

    main(workflow_file=workflow_file,
         debug=debug,
         window_size=window_size,
         profile=profile)


def main(workflow_file, debug, window_size, profile):
    """Launches the FORCE workflow manager application"""
    if debug is False:
        logging.basicConfig(filename="force_wfmanager.log", filemode="w")
    else:
        logging.basicConfig(filename="force_wfmanager.log", filemode="w",
                            level=logging.DEBUG)

    if profile:
        import cProfile
        import pstats
        profiler = cProfile.Profile()
        profiler.enable()

    log = logging.getLogger(__name__)

    plugins = [CorePlugin(), TasksPlugin(), FactoryRegistryPlugin(),
               WfManagerPlugin(workflow_file=workflow_file)]

    mgr = extension.ExtensionManager(
        namespace='force.bdss.extensions',
        invoke_on_load=True
    )

    def import_extensions(ext):
        log.info("Found extension {}".format(ext.name))
        plugins.append(ext.obj)

    try:
        mgr.map(import_extensions)
    except NoMatches:
        log.info("No extensions found")

    wfmanager = WfManager(plugins=plugins, window_size=window_size)
    wfmanager.run()

    if profile:
        profiler.disable()
        from sys import version_info
        fname = 'force_wfmanager-{}-{}.{}.{}'.format(__version__,
                                                     version_info.major,
                                                     version_info.minor,
                                                     version_info.micro)

        profiler.dump_stats(fname + '.prof')
        with open(fname + '.pstats', 'w') as fp:
            stats = pstats.Stats(profiler, stream=fp).sort_stats('cumulative')
            stats.print_stats()
