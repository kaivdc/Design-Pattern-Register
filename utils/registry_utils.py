import json
import datetime
import os
import uuid

class PatternRecord:
    def __init__(self, title, tags, filepath, category, date, record_id=uuid.uuid4()):
        self.record_id = record_id
        self.title = title
        self.tags = tags
        self.filepath = filepath
        self.category = category
        self.date = date

    @classmethod
    def from_dict(cls, data):
        return cls(
            record_id=data.get('record_id'),
            title=data.get('title'),
            tags=data.get('tags', []),
            filepath=data.get('filepath'),
            category=data.get('category'),
            date=data.get('date')
        )

    def to_dict(self):
        return {
            "record_id": str(self.record_id),
            'title': self.title,
            'tags': self.tags,
            'filepath': self.filepath,
            'category': self.category,
            'date': str(self.date)
        }

class RegistryManager:
    def __init__(self):
        self.directory = os.path.dirname(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "registry"))
        self.registry_file = f"{self.directory}/registry.json"
        self.patterns = self.load_registry()

    def load_registry(self):
        if not os.path.exists(self.registry_file):
            return []

        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

                # Check if list
                if isinstance(raw_data, dict):
                    raw_data = [raw_data]

                return [PatternRecord.from_dict(pattern) for pattern in raw_data]

        except (json.JSONDecodeError, TypeError):
            print("Error in utils.registry_utils.load_registry: \n    registry.json is corrupted or invalid.")
            return []

    def write_registry(self):
        directory = self.directory
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        patterns = self.patterns
        # Ensure we are dealing with a list of objects
        if not isinstance(patterns, list):
            patterns = [patterns]

        dumpable_list = []
        for item in patterns:

            # Check if the item is a list and process internal lists in event of nested lists
            if isinstance(item, list):
                for sub_item in item:
                    dumpable_list.append(sub_item.to_dict() if hasattr(sub_item, 'to_dict') else sub_item)

            # Check if we are iterating over our correct object
            elif hasattr(item, 'to_dict'):
                dumpable_list.append(item.to_dict())

            # If already formatted as a dict, append without formatting
            else:
                dumpable_list.append(item)

        # Dump final records list
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(dumpable_list, f, indent=4)

    def empty_registry(self):
        # Iterate through patterns and remove each associated file if it exists
        for pattern in self.patterns:
            if os.path.exists(pattern.filepath):
                os.remove(pattern.filepath)

        # update patterns to empty list
        self.patterns = []

        # Overwrite registry file with empty json
        self.write_registry()