import json
import tempfile
from testfixtures import LogCapture
from unittest import mock, TestCase

from traits.trait_errors import TraitError

from force_wfmanager.model.analysis_model import AnalysisModel


class TestAnalysisModel(TestCase):
    def setUp(self):
        self.model = AnalysisModel()

    def test_initialize(self):
        self.assertEqual(tuple(), self.model.header)
        self.assertFalse(self.model.export_enabled)
        self.assertFalse(self.model._export_enabled)
        self.assertEqual([], self.model.evaluation_steps)
        self.assertEqual([], self.model._evaluation_steps)
        self.assertDictEqual(self.model._row_data, {})

    def test__add_header(self):
        header = ("a", "b", "c")
        self.model._add_header(header)
        self.assertTupleEqual(self.model.header, header)
        self.assertDictEqual(self.model._row_data, dict.fromkeys(header))

        wrong_header = 1
        log_error = (
            f"The Header of the AnalysisModel can't be defined by "
            f"the {wrong_header}. A list or tuple of strings is required."
        )
        with LogCapture() as capture:
            with self.assertRaises(TraitError):
                self.model._add_header(wrong_header)
        capture.check(
            ("force_wfmanager.model.analysis_model", "ERROR", log_error)
        )

    def test_header_update(self):
        header = ("a", "b", "c")
        data = ((1, 2, 3), (4, 5, 6))
        state_dict = {"header": header, "1": data[0], "2": data[1]}
        self.model.from_json(state_dict)

        self.assertTupleEqual(self.model.header, header)
        self.model.header = ("new", )
        self.assertTupleEqual(self.model.header, ("new", ))
        self.assertEqual([], self.model.evaluation_steps)

    def test__add_cell(self):
        header = ("a", "b", "c")
        self.model._add_header(header)

        self.model._add_cell(label="a", value="1")
        self.assertEqual("1", self.model._row_data["a"])
        self.assertIsNone(self.model._row_data["b"])
        self.assertIsNone(self.model._row_data["c"])

        label, value = "d", "2"
        log_warning = (
            f"The AnalysisModel does not have the {label} column."
            f"The value {value} has not been added to the table."
        )
        with LogCapture() as capture:
            self.model._add_cell(label=label, value=value)
        capture.check(
            (
                "force_wfmanager.model.analysis_model",
                "WARNING",
                log_warning,
            )
        )
        self.assertEqual("1", self.model._row_data["a"])
        self.assertIsNone(self.model._row_data["b"])
        self.assertIsNone(self.model._row_data["c"])

    def test__add_cells(self):
        header = ("a", "b", "c")
        self.model._add_header(header)

        data = []
        self.model._add_cells(data)
        self.assertIsNone(self.model._row_data["a"])
        self.assertIsNone(self.model._row_data["b"])
        self.assertIsNone(self.model._row_data["c"])

        data = (1, 2)
        self.model._add_cells(data)
        self.assertEqual(1, self.model._row_data["a"])
        self.assertEqual(2, self.model._row_data["b"])
        self.assertIsNone(self.model._row_data["c"])

        data = (1, 2, 3, 4)
        self.model._add_cells(data)
        self.assertEqual(1, self.model._row_data["a"])
        self.assertEqual(2, self.model._row_data["b"])
        self.assertEqual(3, self.model._row_data["c"])

    def test_finalize_row(self):
        header = ("a", "b", "c")
        self.model._add_header(header)
        data = (1, 2, 3)
        self.model._add_cells(data)

        self.model._finalize_row()
        self.assertEqual(1, len(self.model.evaluation_steps))
        self.assertTupleEqual(self.model.evaluation_steps[0], data)
        self.assertDictEqual(
            self.model._row_data, self.model._row_data_default()
        )

        data = (1, 2)
        self.model._add_cells(data)

        self.model._finalize_row()
        self.assertEqual(2, len(self.model.evaluation_steps))
        self.assertTupleEqual(self.model.evaluation_steps[1], (1, 2, None))
        self.assertDictEqual(
            self.model._row_data, self.model._row_data_default()
        )

    def test__add_data(self):
        with mock.patch.object(AnalysisModel, "_add_cell") as mock_cell:
            model = AnalysisModel()
            model._add_data({"name": "value"})
        mock_cell.assert_called_with("name", "value")

        with mock.patch.object(
            AnalysisModel, "_add_cells"
        ) as mock_cells, mock.patch.object(AnalysisModel, "_finalize_row"):
            model = AnalysisModel()

            model._add_data(["data", "entries"])
        mock_cells.assert_called_with(["data", "entries"])

        header = ("a", "b", "c")
        self.model._add_header(header)
        self.model._add_data({"a": 1})
        self.model._add_data({"c": 2})
        self.model._add_data([3, 4])
        self.assertEqual(1, len(self.model.evaluation_steps))
        self.assertTupleEqual(self.model.evaluation_steps[0], (3, 4, 2))
        self.assertDictEqual(
            self.model._row_data, self.model._row_data_default()
        )

    def test__add_evaluation_step(self):
        with self.assertRaisesRegex(
            ValueError, "Cannot add evaluation step to an empty Analysis model"
        ):
            self.model._add_evaluation_step(None)

        self.model.notify(["column"])
        step = (1, 2)
        error = (
            "Size of evaluation step is incompatible with the length of "
            "the header."
        )
        with self.assertRaisesRegex(ValueError, error):
            self.model._add_evaluation_step(step)

        step = (1,)
        self.model._add_evaluation_step(step)
        self.assertEqual(1, len(self.model.evaluation_steps))
        self.assertTupleEqual(self.model.evaluation_steps[0], step)
        self.assertTrue(self.model.export_enabled)

    def test_notify(self):
        with mock.patch.object(AnalysisModel, "_add_header") as mock_header:
            model = AnalysisModel()
            model.notify(None)
        mock_header.assert_called_once()

        with mock.patch.object(
            AnalysisModel, "_add_header"
        ) as mock_header, mock.patch.object(
            AnalysisModel, "_add_data"
        ) as mock_data:
            model = AnalysisModel()
            model.notify(None)
            # This line is necessary because the header must be set
            # in order to add data to the model.
            model.header = ("",)
            model.notify(None)
        mock_header.assert_called_once()
        mock_data.assert_called_once()

    def test_column(self):
        header = ("a", "b", "c")
        data = ((1, 2, 3), (4, 5, 6))
        state_dict = {"header": header, "1": data[0], "2": data[1]}
        self.model.from_json(state_dict)

        column_by_id = self.model.column(0)
        column_by_label = self.model.column("a")
        self.assertListEqual(column_by_id, column_by_label)
        self.assertListEqual(column_by_label, [1, 4])

        column_by_id = self.model.column(-1)
        column_by_label = self.model.column("c")
        self.assertListEqual(column_by_id, column_by_label)
        self.assertListEqual(column_by_label, [3, 6])

        error = (
            "Column of the AnalysisModel with label 2"
            " doesn't exist. The label must be a string or int."
        )
        with self.assertRaisesRegex(ValueError, error):
            self.model.column("2")

        error = (
            "Column of the AnalysisModel with label 100"
            " doesn't exist. The label must be a string or int."
        )
        with self.assertRaisesRegex(ValueError, error):
            self.model.column(100)

    def test_is_empty(self):
        self.assertTrue(self.model.is_empty)

        header = ("a", "b", "c")
        data = ((1, 2, 3), (4, 5, 6))
        state_dict = {"header": header, "1": data[0], "2": data[1]}
        self.model.from_json(state_dict)

        self.assertFalse(self.model.is_empty)

    def test___getstate__(self):
        header = ("a", "b", "c")
        data = ((1, 2, 3), (4, 5, 6))
        state_dict = {"header": header, 1: data[0], 2: data[1]}
        self.model.notify(header)
        for entry in data:
            self.model.notify(entry)

        state = self.model.__getstate__()
        self.assertDictEqual(state, state_dict)

        with mock.patch.object(AnalysisModel, "__getstate__") as mock_getstate:
            AnalysisModel().to_json()
        mock_getstate.assert_called_once()

    def test_json(self):
        header = ("a", "b", "c")
        data = ((1, 2, 3), (4, 5, 6))
        state_dict = {"header": header, "1": data[0], "2": data[1]}

        error = (
            "AnalysisModel can't be instantiated from a data dictionary"
            " that does not contain a header."
        )
        with LogCapture() as capture:
            with self.assertRaisesRegex(KeyError, error):
                AnalysisModel().from_json({"1": data[0], "2": data[1]})
        capture.check(
            (
                "force_wfmanager.model.analysis_model",
                "ERROR",
                "AnalysisModel can't be instantiated from a data dictionary "
                "that does not contain a header.",
            )
        )

        with mock.patch.object(AnalysisModel, "clear") as mock_clear:
            model = AnalysisModel()
            model.from_json(state_dict)
        mock_clear.assert_called_once()

        self.model.from_json(state_dict)
        self.assertTupleEqual(self.model.header, header)
        self.assertEqual(2, len(self.model.evaluation_steps))
        self.assertTupleEqual(self.model.evaluation_steps[0], data[0])
        self.assertTupleEqual(self.model.evaluation_steps[1], data[1])

        tmp_file = tempfile.NamedTemporaryFile()
        filename = tmp_file.name
        self.model.dump_json(filename)
        with open(filename) as f:
            json_data = json.load(f)
        self.assertDictEqual(
            json_data,
            {"header": list(header), "1": list(data[0]), "2": list(data[1])},
        )

        self.model._export_enabled = False
        self.assertFalse(self.model.dump_json(None))

        header = ("a", "b", "c")
        data = ((1, 2, 3), (4, 5, 6))
        state_dict = {"header": header, "1": data[0], "3": data[1]}
        with LogCapture() as capture:
            AnalysisModel().from_json(state_dict)
        capture.check(
            (
                "force_wfmanager.model.analysis_model",
                "WARNING",
                "Can't find a row with index 2. This index will "
                "be skipped in the AnalysisModel.",
            )
        )

    def test_write_csv(self):
        header = ("a", "b", "c")
        data = ((1, 2, 3), (4, 5, 6))
        state_dict = {"header": header, "1": data[0], "2": data[1]}
        self.model.from_json(state_dict)
        tmp_file = tempfile.NamedTemporaryFile()
        filename = tmp_file.name
        self.model.dump_csv(filename)

        with open(filename) as f:
            csv_data = f.read()
        self.assertEqual("a,b,c\n1,2,3\n4,5,6\n", csv_data)

        self.model._export_enabled = False
        self.assertFalse(self.model.dump_csv(None))

    def test_write(self):
        with mock.patch.object(AnalysisModel, "dump_csv") as mock_csv:
            AnalysisModel().write("filename.csv")
        mock_csv.assert_called_with("filename.csv", mode="w")

        with mock.patch.object(AnalysisModel, "dump_json") as mock_json:
            AnalysisModel().write("filename.json")
        mock_json.assert_called_with("filename.json", mode="w")

        with self.assertRaises(IOError):
            AnalysisModel().write("filename.format")

    def test_clear(self):
        header = ("a", "b", "c")
        data = ((1, 2, 3), (4, 5, 6))
        self.model.notify(header)
        for entry in data:
            self.model.notify(entry)

        self.model.clear_steps()
        self.assertFalse(self.model.export_enabled)
        self.assertEqual([], self.model.evaluation_steps)
        self.assertTupleEqual(self.model.header, header)

        self.model.notify(header)
        for entry in data:
            self.model.notify(entry)

        self.model.clear()
        self.assertFalse(self.model.export_enabled)
        self.assertEqual([], self.model.evaluation_steps)
        self.assertTupleEqual(self.model.header, ())

    def test_selected_step_indices(self):
        self.assertIsNone(self.model.selected_step_indices)

        header = ("a", "b", "c")
        data = ((1, 2, 3), (4, 5, 6))
        self.model.notify(header)
        for entry in data:
            self.model.notify(entry)

        self.assertIsNone(self.model.selected_step_indices)
        self.model.selected_step_indices = [1]
        self.assertListEqual(self.model.selected_step_indices, [1])
        self.model.selected_step_indices = [1, 2]
        self.assertListEqual(self.model.selected_step_indices, [1, 2])
        error = (
            "Invalid value for selection index 3. "
            "It must be a positive Int less or equal to 1"
        )
        with self.assertRaisesRegex(ValueError, error):
            self.model.selected_step_indices = [1, 3]
        error = (
            "Invalid value for selection index -1. "
            "It must be a positive Int less or equal to 1"
        )
        with self.assertRaisesRegex(ValueError, error):
            self.model.selected_step_indices = [-1]
