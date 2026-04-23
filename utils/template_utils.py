import os
import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from utils.registry_utils import PatternRecord


@dataclass
class TemplateSection:
    name: str
    questions: List[str] = field(default_factory=list)

@dataclass
class PatternTemplate:
    title: str
    tags: List[str]
    sections: List[TemplateSection]

# HELPER METHODS BELOW
# ----------------------------------------------------------------------------------------------------

def create_file_paths(directory):
    if not os.path.isdir(directory):
        return "ERROR in utils.template_utils.create_file_paths: \n     Directory not found."

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
        print(f"ERROR in utils.template_utils.parse_template: \n    File not found at {file_path}.")
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
        elif line.startswith('?'):
            if current_section:
                current_section.questions.append(line.replace("\n", ""))

        elif line.startswith('!'):
            if current_section:
                current_section.questions.append(line.replace("\n", ""))

    return PatternTemplate(title=title, tags=tags, sections=sections)

def load_templates(directory):
    if not os.path.isdir(directory):
        print("ERROR in utils.template_utils.load_templates: \n     Directory not found.")

    templates = []
    file_paths = create_file_paths(directory)
    for file_path in file_paths:
        template = parse_template(file_path)
        templates.append(template)

    return templates

def create_design_pattern_from_template(template, directory):
    # Prompt user for title, tags, and autogenerate document_content
    print(f"\nCreating new Design Pattern from Template: {template.title}")
    user_title = input("Enter Pattern Title: ").strip()
    raw_tags = input("Enter Tags (comma separated): ")
    user_tags = [t.strip() for t in raw_tags.split(',')]

    # Generate document content from non-template specific information

    document_content = [f"# {user_title}\n", f"Tags: {', '.join(user_tags)}\n",
                        f"Date: {str(datetime.now())}\n", "---"]

    safe_name = user_title.lower().replace(" ", "_")
    filepath = (os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "registry", f"{safe_name}.txt"))
    image_sub_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images", safe_name)

    # loop through each section and each question prompting user and appending the question and answer to document_content
    for section in template.sections:
        print(f"\nNow filling out {section.name}")
        document_content.append(f"## {section.name}\n")

        for question in section.questions:
            if question.startswith('!'):
                label = question[1:].strip()
                img_src = input(f"Enter local path to image for '{label}': ").strip()

                if os.path.exists(img_src):
                    os.makedirs(image_sub_dir, exist_ok=True)
                    ext = os.path.splitext(img_src)[1]
                    img_filename = f"{section.name.replace(' ', '_')}{ext}"
                    dest_path = os.path.join(image_sub_dir, img_filename)

                    # Copy the physical file to the registry assets
                    shutil.copy(img_src, dest_path)
                    document_content.append(f"![{label}](images/{safe_name}/{img_filename})\n")
                else:
                    print(f"Warning: File not found at {img_src}. Skipping image.")

            else:
                # Clean the ? prefix if it exists
                display_q = question[1:].strip() if question.startswith('?') else question
                answer = input(f"{display_q}: ").strip()
                document_content.append(f"### {display_q}\n")
                document_content.append(f"{answer}\n")

    if not os.path.exists(directory):
        print(f"ERROR in utils.registry_utils.create_design_pattern_from_template: \n   Directory not found. Creating new directory at {directory}.")
        os.makedirs(directory)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("\n".join(document_content))

    # Return PatternRecord instance
    return PatternRecord(
        title=user_title,
        tags=user_tags,
        filepath=filepath,
        category=template.title,
        date=str(datetime.now())
    )



