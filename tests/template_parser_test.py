from pathlib import Path
import os
from template_parser import parse_template
from template_parser import create_file_paths

file_paths = create_file_paths(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates"))
print(file_paths)

for file_path in file_paths:
    parsed_data = parse_template(file_path)

    print(parsed_data)