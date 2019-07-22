from pyface.qt import QtGui
from traitsui.api import Group, Item


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
    interactive_view_info = [
        trait_name for trait_name in view_info
        if trait_name in model.visible_traits()
    ]

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
    html_background_color = '#{:02x}{:02x}{:02x}'.format(
        rgba_color[0], rgba_color[1], rgba_color[2]
    )
    return html_background_color


def class_description(cl, maxlength=80, desc_attribute="description"):
    """ Returns a short description of a class, based on a
    description class attribute (if present) and the class path:

    Examples (maxlenght = 45)::

        "Short description (path.to.the.class)"
        "This is a longer description (path...class)"

    Parameters
    ----------
    cl : class
        The target class.
    maxlength : int
        Max length of the returned description.
    desc_attribute : str
        Name of the class attribute containing the description.
    """
    length = maxlength

    def shorten(string, maxlength):
        # Helper function that operates the truncation

        if string.startswith("<class '"):

            # Usual str(type) of the form <class 'foo.bar.baz'>:
            # Remove wrapping and truncate, giving precedence to extremes.
            words = string[8:-2].split(".")
            num_words = len(words)
            words_with_priority = [
                # from the out inwards, precedence to the left: 0 2 ... 3 1
                (words[i], min(2*i, 2*num_words - 2*i - 1))
                for i in range(num_words)
            ]
            for threshold in range(num_words, 0, -1):
                string = ".".join(
                    (word if priority < threshold else "")
                    for (word, priority) in words_with_priority
                )
                if len(string) <= maxlength:
                    return string
            # fallback when every dot-based truncation is too long.
            return shorten(words[0], maxlength)

        else:

            # Custom description: just truncate.
            return string if len(string) <= maxlength \
                else string[:maxlength-3]+"..."

    if getattr(cl, desc_attribute, None) is not None:
        description = shorten(getattr(cl, desc_attribute), length)
        # if there's enough room left, add the class name in brackets.
        length -= len(description) + 3
        if length >= 10:
            description += " (" + shorten(str(cl), length) + ")"
    else:
        description = shorten(str(cl), length)
    return description
