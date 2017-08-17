import json
import unittest


from force_wfmanager.server.event_deserializer import (
    EventDeserializer, DeserializerError)

try:
    import mock
except ImportError:
    from unittest import mock

from force_bdss.api import MCOStartEvent


class TestEventDeserializer(unittest.TestCase):
    def test_instantiation(self):
        data = json.dumps({
            "type": "MCOStartEvent",
            "model_data": {
                "input_names": ["a", "b"],
                "output_names": ["c", "d"]
            }
        })

        event = EventDeserializer().deserialize(data)
        self.assertIsInstance(event, MCOStartEvent)
        self.assertEqual(event.input_names, event.input_names)
        self.assertEqual(event.output_names, event.output_names)

    def test_invalid_cases(self):
        invalid_cases = [
            {
                "type": "Foo",
                "model_data": {
                    "input_names": ["a", "b"],
                    "output_names": ["c", "d"]
                }
            },
            {
                "type": "BaseDeviceEvent",
                "model_data": {
                }
            },
            {
                "model_data": {
                }
            },
            {
                "type": "MCOStartEvent"
            },
            {
                "type": "MCOStartEvent"
            }]

        for case in invalid_cases:
            with self.assertRaises(DeserializerError):
                event = EventDeserializer().deserialize(json.dumps(case))

        with self.assertRaises(DeserializerError):
            event = EventDeserializer().deserialize([])

