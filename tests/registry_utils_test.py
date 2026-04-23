import unittest
import os
import json
from uuid import uuid4
from datetime import datetime
from unittest.mock import patch, MagicMock, mock_open

from utils.registry_utils import PatternRecord, RegistryManager
from utils.template_utils import create_design_pattern_from_template


class TestPatternRecord(unittest.TestCase):
    def test_serialization(self):
        uid = uuid4()
        original = PatternRecord("Title", ["tag1"], "path/to.txt", "Cat", "2026-04-23", uid)
        as_dict = original.to_dict()

        recovered = PatternRecord.from_dict(as_dict)
        self.assertEqual(str(recovered.record_id), str(uid))
        self.assertEqual(recovered.title, "Title")
        self.assertEqual(recovered.tags, ["tag1"])


class TestRegistryManager(unittest.TestCase):
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="[]")
    def setUp(self, mock_file, mock_exists):
        # Since we use mock files, we prevent the class from looking for real files
        mock_exists.return_value = False
        self.manager = RegistryManager()

        # Manually define paths
        self.manager.directory = "test_dir"
        self.manager.registry_file = "test_dir/registry.json"

        self.sample_record = PatternRecord(
            "Singleton", ["Creational"], "singleton.txt", "Creational", "2026", uuid4()
        )

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='[{"title": "Test"}]')
    def test_load_registry(self, mock_file, mock_exists):
        patterns = self.manager.load_registry()
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0].title, "Test")

    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    def test_write_registry(self, mock_file, mock_exists, mock_makedirs):
        self.manager.patterns = [self.sample_record]
        self.manager.write_registry()

        # Check if json.dump was called via the mock_file
        written_data = "".join(call.args[0] for call in mock_file().write.call_args_list)
        self.assertIn("Singleton", written_data)

    @patch('os.path.exists', return_value=True)
    @patch('os.remove')
    @patch('builtins.open', new_callable=mock_open)
    def test_empty_registry(self, mock_file, mock_remove, mock_exists):
        # Create patterns
        self.manager.patterns = [self.sample_record]

        # Run method
        self.manager.empty_registry()

        # Assert against truth
        mock_remove.assert_called_once_with(self.sample_record.filepath)
        self.assertEqual(len(self.manager.patterns), 0)

    @patch('shutil.rmtree')
    @patch('os.path.isdir', return_value=True)
    @patch('os.path.exists', return_value=True)
    @patch('os.remove')
    @patch('builtins.open', new_callable=mock_open)
    def test_empty_registry_with_images(self, mock_file, mock_remove, mock_exists, mock_isdir, mock_rmtree):
        self.manager.patterns = [self.sample_record]
        self.manager.empty_registry()

        # Assert against truth both were removed
        mock_remove.assert_called()
        mock_rmtree.assert_called()

class TestTemplateInteraction(unittest.TestCase):

    @patch('builtins.input')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=True)
    def test_create_design_pattern_from_template(self, mock_exists, mock_make, mock_file, mock_input):
        mock_template = MagicMock()
        mock_template.title = "Behavioral"

        sec = MagicMock()
        sec.name = "Intent"
        sec.questions = ["Problem?"]
        mock_template.sections = [sec]

        # Create mock input
        mock_input.side_effect = ["Observer", "events", "The state changed"]

        # Run method
        result = create_design_pattern_from_template(mock_template, "dummy_dir")

        # Assert against truth
        self.assertEqual(result.title, "Observer")
        self.assertIn("The state changed", "".join(call.args[0] for call in mock_file().write.call_args_list))

if __name__ == "__main__":
    unittest.main()