import datetime
import os

from utils.registry_utils import load_registry
from utils.registry_utils import PatternRecord
from utils.registry_utils import write_registry

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
registry_path = os.path.join(BASE_DIR, 'registry', 'registry.json')

patterns = load_registry(registry_path)

for pattern in patterns:
    print(pattern.title)

pattern = PatternRecord(
    title="Test Pattern",
    tags=["Testing", "Validation", "Confirmation"],
    filepath="test.txt",
    category="Test",
    created_at=datetime.datetime.now(),
)
pattern_list = [pattern]

pattern2 = PatternRecord(
    title="Test Pattern 2",
    tags=["Testing 2", "Validation 2", "Confirmation 2"],
    filepath="test_2.txt",
    category="Test_2",
    created_at=datetime.datetime.now(),
)

pattern_list.append(pattern2)

write_registry(pattern_list, registry_path)