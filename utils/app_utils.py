import os


def read_pattern_file(filepath):
    if not os.path.exists(filepath):
        return f"ERROR in utils.app_utils.read_pattern_file: \n     File not found at {filepath}."
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"ERROR in utils.app_utils.read_pattern_file: \n     Unable to read file: {e}."