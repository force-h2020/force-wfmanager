def get_factory_name(factory):
    """ Returns a factory name, given the factory. This ensure that something
    will be displayed (id or name of the factory) even if no name has been
    specified for the factory """
    name = factory.name.strip()
    if len(name) != 0:
        return name
    else:
        return factory.id


def get_plugin_producer(plugin):
    """
    Extracts the plugin producer from the plugin. For now, this is implemented
    rather horribly, getting it from the id. A better technique is required.
    """
    return plugin.id.split(".")[2].title()
