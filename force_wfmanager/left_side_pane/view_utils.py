def get_factory_name(factory):
    """ Returns a factory name, given the factory. This ensure that something
    will be displayed (id or name of the factory) even if no name has been
    specified for the factory """
    name = factory.name.strip()
    if len(name) != 0:
        return name
    else:
        return factory.id
