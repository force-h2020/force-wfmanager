import json
import unittest


from force_wfmanager.server.event_deserializer import (
    EventDeserializer,
    DeserializerError,
)

from force_bdss.api import MCOStartEvent, MCOProgressEvent


class TestEventDeserializer(unittest.TestCase):
    def test_instantiation(self):
        data = json.dumps(
            {
                "module": "force_bdss.core_driver_events",
                "type": "MCOStartEvent",
                "model_data": {
                    "parameter_names": ["a", "b"],
                    "kpi_names": ["c", "d"],
                },
            }
        )

        event = EventDeserializer().deserialize(data)
        self.assertIsInstance(event, MCOStartEvent)
        self.assertEqual(event.parameter_names, event.parameter_names)
        self.assertEqual(event.kpi_names, event.kpi_names)

    def test_progress_event_deserialize(self):
        data = json.dumps(
            {
                "module": "force_bdss.core_driver_events",
                "type": "MCOProgressEvent",
                "model_data": {
                    "optimal_point": [{"value": 1.0}, {"value": 2.0}],
                    "optimal_kpis": [{"value": 3.0}],
                    "weights": [1.0],
                },
            }
        )

        event = EventDeserializer().deserialize(data)
        self.assertIsInstance(event, MCOProgressEvent)
        self.assertEqual(len(event.optimal_point), 2)
        self.assertEqual(event.optimal_point[0].value, 1.0)
        self.assertEqual(event.optimal_point[1].value, 2.0)

        self.assertEqual(len(event.optimal_kpis), 1)
        self.assertEqual(event.optimal_kpis[0].value, 3.0)

        self.assertEqual(event.weights, [1.0])

    def test_invalid_cases(self):
        invalid_cases = [
            {
                "type": "Foo",
                "model_data": {
                    "parameter_names": ["a", "b"],
                    "kpi_names": ["c", "d"],
                },
            },
            {
                "module": "force_bdss.core_driver_events",
                "type": "BaseDeviceEvent",
                "model_data": {},
            },
            {
                "module": "force_bdss.core.kpi_specification",
                "type": "KPISpecification",
                "model_data": {},
            },
            {"module": "force_bdss.core.kpi_specification", "model_data": {}},
            {
                "module": "force_bdss.core_driver_events",
                "type": "BaseDriverEvent",
            },
        ]

        for case in invalid_cases:
            with self.assertRaises(DeserializerError):
                EventDeserializer().deserialize(json.dumps(case))

        with self.assertRaises(DeserializerError):
            EventDeserializer().deserialize([])
