import re
from traits.api import BaseStr


class ZMQSocketURL(BaseStr):
    def validate(self, object, name, value):
        super(ZMQSocketURL, self).validate(object, name, value)
        m = re.match(
            "tcp://(\\d{1,3})\.(\\d{1,3})\.(\\d{1,3})\.(\\d{1,3}):(\\d+)",
            value)
        if m is None:
            self.error(object, name, value)

        a, b, c, d, port = m.groups()

        if not all(map(lambda x: 0 <= int(x) <= 255, (a, b, c, d))):
            self.error(object, name, value)

        if not (1 <= int(port) <= 65535):
            self.error(object, name, value)

        return value
