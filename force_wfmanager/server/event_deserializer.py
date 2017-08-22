import json


class DeserializerError(Exception):
    """Raised when the deserialization cannot be performed for any reason."""


class EventDeserializer(object):
    """This is a trivial deserializer for events. It is not made
    for complex hierarchies. It just handles simple events.
    If you want to extend events to contain non-native python
    objects, you must implement a better serializer/deserializer.
    """
    def deserialize(self, data):
        """Deserializes the appropriate object from the given data

        Parameters
        ----------
        data: str
            The string containing the data to deserialize.

        Returns
        -------
        BaseDriverEvent
            A specific instance of the driver event. The resulting class
            must be derived from BaseDriverEvent.

        Raises
        ------
        DeserializerError
        """
        try:
            d = json.loads(data)
        except Exception as e:
            raise DeserializerError("Could not parse json data: {}".format(e))

        try:
            class_name = d["type"]
        except KeyError:
            raise DeserializerError("Could not find type key in json "
                                    "data.")

        from force_bdss import api
        try:
            cls = getattr(api, class_name)
        except AttributeError:
            raise DeserializerError("Unable to deserialize requested "
                                    "type {}".format(class_name))

        if (cls is None or
                not issubclass(cls, api.BaseDriverEvent) or
                cls == api.BaseDriverEvent):

            raise DeserializerError("Unable to deserialize requested "
                                    "type {}".format(class_name))

        if "model_data" not in d:
            raise DeserializerError("Unable to find model data for "
                                    "type {}".format(class_name))

        return cls(**d["model_data"])
