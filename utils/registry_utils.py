import json
import datetime
import os
import uuid

class PatternRecord:
    def __init__(self, title, tags, filepath, category, created_at, record_id=uuid.uuid4()):
        self.record_id = record_id
        self.title = title
        self.tags = tags
        self.filepath = filepath
        self.category = category
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data):
        return cls(
            record_id=data.get('record_id'),
            title=data.get('title'),
            tags=data.get('tags', []),
            filepath=data.get('filepath'),
            category=data.get('category'),
            created_at=data.get('created_at')
        )

    def to_dict(self):
        return {
            "record_id": str(self.record_id),
            'title': self.title,
            'tags': self.tags,
            'filepath': self.filepath,
            'category': self.category,
            'created_at': str(self.created_at)
        }


def load_registry(file_path):
    if not os.path.exists(file_path):
        print("Registry file not found. Starting with an empty list.")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

            patterns = [PatternRecord.from_dict(item) for item in raw_data]

            return patterns

    except json.JSONDecodeError:
        print("Error: registry.json is corrupted or using invalid formatting.")
        return []


def write_registry(patterns, file_path):
    # Create the directory if it doesn't exist
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Convert all patterns in the list to dictionaries
    dumpable_list = [pattern.to_dict() for pattern in patterns]

    # Write the list of dicts to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(dumpable_list, f, indent=4)
