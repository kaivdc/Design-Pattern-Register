import unittest
import os
import json
from uuid import uuid4
from datetime import datetime
from unittest.mock import patch, MagicMock, mock_open

from utils.registry_utils import (
    PatternRecord,
    load_registry,
    write_registry,
    empty_registry,
)
from utils.template_utils import create_design_pattern_from_template


class TestPatternRecord(unittest.TestCase):

    def test_serialization(self):
        uid = uuid4()
        original = PatternRecord("Title", ["tag1"], "path/to.txt", "Cat", "2026-04-23", uid)

        # To Dict
        as_dict = original.to_dict()
        self.assertEqual(as_dict['record_id'], str(uid))
        self.assertEqual(as_dict['title'], "Title")

        # From Dict
        recovered = PatternRecord.from_dict(as_dict)
        self.assertEqual(str(recovered.record_id), str(uid))
        self.assertEqual(recovered.tags, ["tag1"])


class TestRegistryIO(unittest.TestCase):
    def setUp(self):
        self.test_registry_path = "test_data/test_registry.json"
        self.test_dir = "test_data"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

        self.sample = PatternRecord("S", ["t"], "p.txt", "C", "2026", uuid4())

    def tearDown(self):
        if os.path.exists(self.test_registry_path):
            os.remove(self.test_registry_path)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_write_nested_and_single_logic(self):
        # Create single object and attempt to load
        write_registry(self.sample, self.test_registry_path)
        loaded = load_registry(self.test_registry_path)
        self.assertEqual(len(loaded), 1)

        # Create nested list and test against flattened result
        nested = [[self.sample, self.sample]]
        write_registry(nested, self.test_registry_path)
        loaded = load_registry(self.test_registry_path)
        self.assertEqual(len(loaded), 2)

    def test_load_corrupted_and_missing(self):
        # Create invalid json file and assert program detects and rejects
        self.assertEqual(load_registry("missing.json"), [])

        with open(self.test_registry_path, "w") as f:
            f.write("!!!Not JSON!!!")
        self.assertEqual(load_registry(self.test_registry_path), [])

    @patch('os.remove')
    def test_empty_registry(self, mock_remove):
        # Create registry for removal
        write_registry([self.sample], self.test_registry_path)

        # Run empty registry method
        empty_registry(self.test_registry_path)

        # Assert file properly removed
        mock_remove.assert_called_once_with(self.sample.filepath)

        # Assert empty registry against truth
        self.assertEqual(load_registry(self.test_registry_path), [])


class TestTemplateInteraction(unittest.TestCase):

    @patch('builtins.input')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=True)
    def test_create_design_pattern_from_template(self, mock_exists, mock_make, mock_file, mock_input):
        # Create Mock Template
        mock_template = MagicMock()
        mock_template.title = "Behavioral"

        sec = MagicMock()
        sec.name = "Intent"
        sec.questions = ["What is it?"]
        mock_template.sections = [sec]

        # Create mock inputs
        mock_input.side_effect = ["MyPattern", "tagA, tagB", "A useful pattern"]

        # Run method
        result = create_design_pattern_from_template(mock_template, "dummy/dir")

        # Assert record against truth
        self.assertEqual(result.title, "MyPattern")
        self.assertEqual(result.tags, ["tagA", "tagB"])
        self.assertEqual(result.category, "Behavioral")

        # Assert file against truth
        written_data = "".join(call.args[0] for call in mock_file().write.call_args_list)
        self.assertIn("# MyPattern", written_data)
        self.assertIn("A useful pattern", written_data)

if __name__ == "__main__":
    unittest.main()