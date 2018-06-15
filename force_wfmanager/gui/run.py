import logging
import click

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from stevedore import extension
from stevedore.exception import NoMatches

from force_bdss.factory_registry_plugin import FactoryRegistryPlugin

from force_wfmanager.wfmanager import WfManager
from force_wfmanager.wfmanager_plugin import WfManagerPlugin

from traits.api import push_exception_handler

from force_wfmanager.version import __version__

push_exception_handler(lambda *args: None, reraise_exceptions=True)


@click.command()
@click.version_option(version=__version__)
@click.option('--file', default='', type=click.Path())
def force_wfmanager(file):
    """Launches the FORCE workflow manager application"""
    kwargs = {'workflow_file': file}
    main(**kwargs)


def main(workflow_file):
    """Launches the FORCE workflow manager application"""
    logging.basicConfig(filename="force_wfmanager.log", filemode="w")
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
