import json
import importlib

from force_bdss.api import DataValue, MCOProgressEvent, BaseDriverEvent


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
            class_module = d["module"]
        except KeyError:
            raise DeserializerError("Could not find module key in json "
                                    "data.")
        try:
            class_name = d["type"]
        except KeyError:
            raise DeserializerError("Could not find type key in json "
                                    "data.")

        try:
            module = importlib.import_module(class_module)
            cls = getattr(module, class_name)
        except AttributeError:
            raise DeserializerError("Unable to deserialize requested "
                                    "type {}".format(class_name))

        if not issubclass(cls, BaseDriverEvent):
            raise DeserializerError("Class {} is not a child of BaseDriverEvent"
                                    " class".format(class_name))

        if "model_data" not in d:
            raise DeserializerError("Unable to find model data for "
                                    "type {}".format(class_name))

        model_data = d["model_data"]
        if cls == MCOProgressEvent:
            model_data["optimal_point"] = [
                DataValue(**data) for data in model_data["optimal_point"]]
            model_data["optimal_kpis"] = [
                DataValue(**data) for data in model_data["optimal_kpis"]]

        return cls(**model_data)
