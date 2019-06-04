import unittest
import json

from force_bdss.api import MCOStartEvent
from force_wfmanager.ui.event_serializer import \
    EventSerializer, SerializerError


class TestEventSerializer(unittest.TestCase):
    def test_serialize(self):
        event = MCOStartEvent(
            parameter_names=["a", "b"],
            kpi_names=["c", 'd']
        )

        data = EventSerializer().serialize(event)

        self.assertEqual(
            json.loads(data),
            {
                "type": "MCOStartEvent",
                "model_data": {
                    "parameter_names": ["a", "b"],
                    "kpi_names": ["c", "d"],
                }
            }
        )

    def test_serialize_invalid_entity(self):
        with self.assertRaises(SerializerError):
            EventSerializer().serialize("foo")
