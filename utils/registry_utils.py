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

def create_design_pattern_from_template(template, directory):
    # Prompt user for title, tags, and autogenerate document_content
    print(f"\nCreating new Design Pattern from Template: {template.title}")
    user_title = input("Enter Pattern Title: ").strip()
    raw_tags = input("Enter Tags (comma separated): ")
    user_tags = [t.strip() for t in raw_tags.split(',')]

    # Generate document content from non-template specific information

    document_content = [f"TITLE: {user_title}", f"TAGS: {', '.join(user_tags)}",
                        f"DATE: {str(datetime.datetime.now())}\n"]

    # loop through each section and each question prompting user and appending the question and answer to document_content
    for section in template.sections:
        print(f"\nNow filling out {section.name}")
        document_content.append(f"#{section.name}\n")
        document_content.append("=" * len(section.name))

        for question in section.questions:
            answer = input(f"Please fill out the section: {question}: ").strip()
            document_content.append(f"##{question}\n")
            document_content.append(f"{answer}\n")

    if not os.path.exists(directory):
        print(f"ERROR: Directory not found. Creating new directory at {directory}.")
        os.makedirs(directory)

    safe_name = user_title.lower().replace(" ", "_")
    filepath = (os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "registry", f"{safe_name}.txt"))

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("\n".join(document_content))

    # Return PatternRecord instance for read/write to registry/registry.json
    return PatternRecord(
        title=user_title,
        tags=user_tags,
        filepath=filepath,
        category=template.title,
        created_at=datetime.datetime.now().isoformat()
    )
