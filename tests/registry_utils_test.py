import unittest
import os
import json
from uuid import uuid4
from datetime import datetime

from utils.registry_utils import PatternRecord, load_registry, write_registry

class TestRegistryLoadWrite(unittest.TestCase):

    # Create temporary file and directory with patterns
    def setUp(self):
        self.test_registry_path = "test_data/test_registry.json"
        self.test_dir = "test_data"

        self.sample_pattern = PatternRecord(
            title="Singleton",
            tags=["Creational", "Shared"],
            filepath="records/singleton.txt",
            category="Creational",
            created_at=str(datetime.now()),
            record_id=uuid4()
        )

    # Remove temporary files and directories
    def tearDown(self):
        if os.path.exists(self.test_registry_path):
            os.remove(self.test_registry_path)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    # Write patterns to file and then attempt to load them to ensure data is conserved
    def test_write_and_load(self):
        patterns_to_write = [self.sample_pattern]

        write_registry(patterns_to_write, self.test_registry_path)

        self.assertTrue(os.path.exists(self.test_registry_path))

        loaded_patterns = load_registry(self.test_registry_path)

        self.assertEqual(len(loaded_patterns), 1)
        self.assertEqual(loaded_patterns[0].title, self.sample_pattern.title)
        self.assertEqual(loaded_patterns[0].category, self.sample_pattern.category)
        self.assertEqual(str(loaded_patterns[0].record_id), str(self.sample_pattern.record_id))

    # Load a file that doesn't exist and ensure we receive a empty dict
    def test_load_non_existent_file(self):
        result = load_registry("imaginary_file.json")
        self.assertEqual(result, [])

    # Create a corrupted/invalid file and an
    def test_load_corrupted_json(self):
        os.makedirs(self.test_dir, exist_ok=True)
        with open(self.test_registry_path, "w") as f:
            f.write("{ invalid json: [")

        result = load_registry(self.test_registry_path)
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()