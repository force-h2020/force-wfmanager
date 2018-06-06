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

from .version import __version__

push_exception_handler(lambda *args: None, reraise_exceptions=True)


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click.version_option(version=__version__)
def main():

    logging.basicConfig(filename="force_wfmanager.log", filemode="w")
    log = logging.getLogger(__name__)

    plugins = [CorePlugin(), TasksPlugin(), FactoryRegistryPlugin(),
               WfManagerPlugin()]

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
