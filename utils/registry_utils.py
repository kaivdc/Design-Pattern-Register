import json
from datetime import datetime
import os
import shutil
import uuid
import io
import zipfile
from uuid import UUID


class PatternRecord:
    def __init__(self, title, tags, filepath, category, date, record_id=None):
        self.record_id = record_id if record_id else uuid.uuid4()
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
        self.directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "registry")
        self.registry_file = os.path.join(self.directory, "registry.json")
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

            # Remove associated image folder
            safe_name = pattern.title.lower().replace(" ", "_")
            image_folder = os.path.join(self.directory, "images", safe_name)
            if os.path.isdir(image_folder):
                shutil.rmtree(image_folder)

        # update patterns to empty list
        self.patterns = []

        # Overwrite registry file with empty json
        self.write_registry()

    def is_valid_uuid(self, value):
        try:
            UUID(str(value))
            return True
        except ValueError:
            return False

    def delete_pattern(self, identifier):
        target_pattern = None

        if isinstance(identifier, PatternRecord):
            target_pattern = identifier

        elif isinstance(identifier, str):
            if self.is_valid_uuid(identifier):
                target_pattern = next((p for p in self.patterns if str(p.record_id) == identifier), None)

            if not target_pattern:
                target_pattern = next((p for p in self.patterns if p.title == identifier), None)

        if not target_pattern:
            print(f"ERROR in utils.registry_utils.delete_pattern: \n    Delete failed: No pattern found matching identifier '{identifier}'.")
            return False

        try:
            if os.path.exists(target_pattern.filepath):
                os.remove(target_pattern.filepath)

            safe_name = target_pattern.title.lower().replace(" ", "_")
            image_dir = os.path.join(self.directory, "images", safe_name)

            if os.path.exists(image_dir):
                shutil.rmtree(image_dir)

            self.patterns = [p for p in self.patterns if p != target_pattern]
            self.write_registry()

            print(f"Successfully deleted pattern: {target_pattern.title}")
            return True

        except Exception as e:
            print(f"ERROR in utils.registry_utils.delete_pattern: \n     During deletion: {e}.")
            return False

    def delete_multiple_patterns(self, identifiers):
        for identifier in identifiers:
            self.delete_pattern(identifier)

    def get_pattern_zip(self, record_id):
        pattern = next((p for p in self.patterns if p.record_id == record_id), None)
        if not pattern:
            return None

        # Create a buffer to hold the ZIP data
        buf = io.BytesIO()

        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.exists(pattern.filepath):
                zf.write(pattern.filepath, arcname=os.path.basename(pattern.filepath))

            safe_name = os.path.splitext(os.path.basename(pattern.filepath))[0]
            image_dir = os.path.join(self.directory, "images", safe_name)

            if os.path.exists(image_dir):
                for root, _, files in os.walk(image_dir):
                    for file in files:
                        img_path = os.path.join(root, file)
                        # Store images in image folder in zipfile
                        zf.write(img_path, arcname=os.path.join("images", file))

        return buf.getvalue()

    def get_multiple_patterns_zip(self, record_ids):
        # Create the in-memory buffer
        buf = io.BytesIO()

        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for rid in record_ids:
                # Find the pattern object
                pattern = next((p for p in self.patterns if str(p.record_id) == str(rid)), None)
                if not pattern:
                    continue

                pattern_folder = pattern.title.lower().replace(" ", "_")

                if os.path.exists(pattern.filepath):
                    zf.write(
                        pattern.filepath,
                        arcname=os.path.join(pattern_folder, os.path.basename(pattern.filepath))
                    )

                safe_name = os.path.splitext(os.path.basename(pattern.filepath))[0]
                image_dir = os.path.join(self.directory, "images", safe_name)

                if os.path.exists(image_dir):
                    for root, _, files in os.walk(image_dir):
                        for file in files:
                            img_path = os.path.join(root, file)
                            zf.write(
                                img_path,
                                arcname=os.path.join(pattern_folder, "images", file)
                            )

        return buf.getvalue()

    def download_pattern(self, identifier):
        target_pattern = None

        if isinstance(identifier, PatternRecord):
            target_pattern = identifier
        elif isinstance(identifier, str):
            if self.is_valid_uuid(identifier):
                target_pattern = next((p for p in self.patterns if str(p.record_id) == identifier), None)
            if not target_pattern:
                target_pattern = next((p for p in self.patterns if p.title == identifier), None)

        if not target_pattern:
            print(f"ERROR: No pattern found matching '{identifier}'.")
            return None

        try:
            if os.path.exists(target_pattern.filepath):
                with open(target_pattern.filepath, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                print(f"ERROR: File not found at {target_pattern.filepath}")
                return None

        except Exception as e:
            print(f"ERROR reading file: {e}")
            return None

    def create_design_pattern_from_ui(self, template, user_title, user_tags, ui_answers):
        base_dir = os.path.abspath("registry")
        safe_name = user_title.lower().replace(" ", "_")
        image_sub_dir = os.path.join(base_dir, "images", safe_name)

        document_content = [
            f"# {user_title}\n",
            f"Tags: {user_tags}\n",
            f"Date: {str(datetime.now())}\n",
            "---"
        ]

        for section in template.sections:
            document_content.append(f"## {section.name}\n")
            for question in section.questions:
                key = f"{section.name}_{question}"
                val = ui_answers.get(key)
                display_question = question.lstrip('?!').strip()

                if question.startswith('!'):

                    document_content.append(f"### {display_question}\n")

                    if val:
                        os.makedirs(image_sub_dir, exist_ok=True)

                        index = 0

                        for uploaded_file in val:
                            if hasattr(uploaded_file, 'name'):
                                ext = os.path.splitext(uploaded_file.name)[1]
                                img_filename = f"{section.name.replace(' ', '_')}_{display_question}_{index}{ext}"
                                index += 1
                                img_path = os.path.join(image_sub_dir, img_filename)

                                with open(img_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())

                                document_content.append(f"![{display_question}-{safe_name}-{img_filename}]({self.directory}\\images\\{safe_name}\\{img_filename})\n")

                # Text case
                elif question.startswith('?'):
                    document_content.append(f"### {display_question}\n")

                    text_value = val if isinstance(val, str) else ""
                    document_content.append(f"{text_value}\n")

        filepath = os.path.join(base_dir, f"{safe_name}.txt")
        os.makedirs(base_dir, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(document_content))

        new_record = PatternRecord(
            record_id=uuid.uuid4(),
            title=user_title,
            tags=[t.strip() for t in user_tags.split(',')],
            filepath=filepath,
            category=template.title,
            date=str(datetime.now())
        )
        self.patterns.append(new_record)
        return new_record