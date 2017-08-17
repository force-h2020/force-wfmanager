import unittest
import json

from force_bdss.api import MCOStartEvent
from force_wfmanager.plugins.ui_notification.event_serializer import \
    EventSerializer


class TestEventSerializer(unittest.TestCase):
    def test_serialize(self):
        event = MCOStartEvent(
            input_names=("a", "b"),
            output_names=("c", 'd')
        )

        data = EventSerializer().serialize(event)

        self.assertEqual(
            json.loads(data),
            {"type": "MCOStartEvent",
             "model_data": {
                 "__traits_version__": "4.6.0",
                 "input_names": ["a", "b"],
                 "output_names": ["c", "d"],
             }
            }
        )
