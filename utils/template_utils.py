import os
import json
from dataclasses import dataclass, field
from typing import List


@dataclass
class TemplateSection:
    name: str
    questions: List[str] = field(default_factory=list)

@dataclass
class PatternTemplate:
    title: str
    tags: List[str]
    sections: List[TemplateSection]

def create_file_paths(directory):
    if directory is None:
        return "ERROR: Directory not found"
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def parse_template(file_path):
    title = ""
    tags = []
    sections = []
    current_section = None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"ERROR: File not found at {file_path}")
        return None

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        # Title (=)
        if clean_line.startswith('='):
            title = clean_line[1:].strip()

        # Tags (*)
        elif clean_line.startswith('*'):
            content = clean_line[1:].strip()
            tags = [tag.strip() for tag in content.split(',')]

        # Section (#)
        elif clean_line.startswith('#'):
            current_section = TemplateSection(name=clean_line[1:].strip())
            sections.append(current_section)

        # Question (?)
        elif clean_line.startswith('?') and current_section is not None:
            current_section.questions.append(clean_line[1:].strip())

    return PatternTemplate(title=title, tags=tags, sections=sections)

def load_templates(directory):
    file_paths = create_file_paths(directory)
    for file_path in file_paths:
        parsed_data = parse_template(file_path)

def create_design_pattern_from_template(json_data):
    data = json.loads(json_data)
    new_data = {}
    for section in data["sections"]:
        print(f"Now filling out section {section['name']}")
        for question in section["questions"]:
            input(f"Please enter the contents for the {question['name']} section : \n")