import re

from traits.api import BaseUnicode, HasStrictTraits, TraitError


class ZMQSocketURL(BaseUnicode):
    """A custom Unicode Trait which is required to be a valid tcp address."""
    #: A basic description of the class
    info_text = "A ZeroMQ Socket URL"

    def validate(self, object, name, value):
        """Checks that this is a valid tcp address """
        super(ZMQSocketURL, self).validate(object, name, value)
        m = re.match(
            "tcp://(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3}):(\\d+)",
            value)
        if m is None:
            self.error(object, name, value)

        a, b, c, d, port = m.groups()

        if not all(map(lambda x: 0 <= int(x) <= 255, (a, b, c, d))):
            self.error(object, name, value)

        if not (1 <= int(port) <= 65535):
            self.error(object, name, value)

        return value


class HasRequiredTraits(HasStrictTraits):
    # TODO: Upgrade version of traits and use in-built HasRequiredTraits
    def __init__(self, **traits):
        for name in self.trait_names(required=True):
            if name not in traits:
                raise TraitError("Required trait {} not found".format(name))

        super(HasRequiredTraits, self).__init__()
