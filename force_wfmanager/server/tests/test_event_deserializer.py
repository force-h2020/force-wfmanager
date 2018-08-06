import json
import unittest


from force_wfmanager.server.event_deserializer import (
    EventDeserializer, DeserializerError)

from force_bdss.api import MCOStartEvent


class TestEventDeserializer(unittest.TestCase):
    def test_instantiation(self):
        data = json.dumps({
            "type": "MCOStartEvent",
            "model_data": {
                "parameter_names": ["a", "b"],
                "kpi_names": ["c", "d"]
            }
        })

        event = EventDeserializer().deserialize(data)
        self.assertIsInstance(event, MCOStartEvent)
        self.assertEqual(event.parameter_names, event.parameter_names)
        self.assertEqual(event.kpi_names, event.kpi_names)

    def test_invalid_cases(self):
        invalid_cases = [
            {
                "type": "Foo",
                "model_data": {
                    "parameter_names": ["a", "b"],
                    "kpi_names": ["c", "d"]
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
                EventDeserializer().deserialize(json.dumps(case))

        with self.assertRaises(DeserializerError):
            EventDeserializer().deserialize([])
