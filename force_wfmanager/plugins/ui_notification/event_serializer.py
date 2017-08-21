import json
from force_bdss.api import BaseDriverEvent


class SerializerError(Exception):
    """Thrown when the instance cannot be serializer for some reason."""


class EventSerializer(object):
    """Serializer to convert an event into a json string to be sent
    across zmq socket.
    Important: only basic python types are supported. If events start
    carrying more complex instances, this serializer will not be enough.
    """
    def serialize(self, event):
        if not isinstance(event, BaseDriverEvent):
            raise SerializerError("Cannot serialize classes not derived "
                                  "from BaseDriverEvent")
        data = json.dumps(
            {"type": event.__class__.__name__,
             "model_data": event.__getstate__()
             }
        )

        return data
