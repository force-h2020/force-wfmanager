import click
import logging

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin
from stevedore import extension
from stevedore.exception import NoMatches
from traits.api import push_exception_handler

from force_bdss.api import FactoryRegistryPlugin
from force_wfmanager.version import __version__
from force_wfmanager.wfmanager import WfManager
from force_wfmanager.wfmanager_plugin import WfManagerPlugin

push_exception_handler(lambda *args: None, reraise_exceptions=True)


@click.command()
@click.version_option(version=__version__)
@click.option('--debug', is_flag=True, default=False,
              help="Prints extra debug information in force_wfmanager.log")
@click.argument('workflow_file', type=click.Path(exists=True), required=False,
                default=None,)
def force_wfmanager(workflow_file, debug):
    """Launches the FORCE workflow manager application"""
    main(workflow_file=workflow_file, debug=debug)


def main(workflow_file=None, debug=False):
    """Launches the FORCE workflow manager application"""
    if debug is False:
        logging.basicConfig(filename="force_wfmanager.log", filemode="w")
    else:
        logging.basicConfig(filename="force_wfmanager.log", filemode="w",
                            level=logging.DEBUG)
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

    wfmanager = WfManager(plugins=plugins)
    wfmanager.run()
