import os
import json

def create_file_paths(directory):
    if directory is None:
        return "ERROR: Directory not found"
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def parse_template(file_path):
    parsed_data = {
            "title": "",
            "tags": [],
            "sections": [],
        }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines:
                return parsed_data

    except:
            return "ERROR: File not found"

    # Strip first line of input file and parse tags from comma seperated strings

    # Clean each line past the first one and check for failure
    current_section = None

    for line in lines[0:]:
        clean_line = line.strip()
        if not clean_line:
            continue

        if clean_line.startswith('#'):
            current_section = {
                "name": line[1:].strip(),
                "questions": []
            }
            parsed_data["sections"].append(current_section)

        elif clean_line.startswith('?') and current_section is not None:
            current_section["questions"].append(line[1:].strip())

        # Parse tags and append them to tag dict
        elif clean_line.startswith('*'):
            content = clean_line[1:].strip()
            parsed_data["tags"] = [tag.strip() for tag in content.split(',')]

        # Parse title and append
        elif clean_line.startswith('='):
            content = clean_line[1:].strip()
            parsed_data["title"] = content

    json_data = json.dumps(parsed_data, indent=4)

    return json_data
