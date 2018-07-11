from traitsui.api import Group, Item
from pyface.qt import QtGui


def get_factory_name(factory):
    """ Returns a factory name, given the factory. This ensure that something
    will be displayed (id or name of the factory) even if no name has been
    specified for the factory """
    name = factory.name.strip()
    if len(name) != 0:
        return name
    else:
        return factory.id


def model_info(model):
    """Returns any interactive view components for a given model"""
    if model is None:
        return []

    current_view = model.trait_view()

    # A list of Items and Groups
    main_group_contents = current_view.content.content

    # Names of all traits with a representation in the view
    view_info = _item_info_from_group(main_group_contents)

    # Remove any non-visible traits
    interactive_view_info = [trait_name for trait_name in view_info
                             if trait_name in model.visible_traits()]

    return interactive_view_info


def _item_info_from_group(group_contents, item_info=None):
    """Gets the item names from a list of groups (group_contents).
    Returns a list of trait names corresponding to the items in the group.
    """
    if item_info is None:
        item_info = []
    for entity in group_contents:
        if isinstance(entity, Group):
            item_info = _item_info_from_group(entity.content, item_info)
        elif isinstance(entity, Item):
            item_info.append(entity.name)
    return item_info


def get_default_background_color():
    """Return the default background color for a Qt Application"""
    palette = QtGui.QPalette()
    rgba_color = palette.window().color().getRgb()
    html_background_color = '#%02x%02x%02x' % (rgba_color[0], rgba_color[1],
                                               rgba_color[2])
    return html_background_color
