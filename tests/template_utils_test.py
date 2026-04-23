import os
import unittest

from utils.template_utils import parse_template
from utils.template_utils import create_file_paths
from utils.template_utils import PatternTemplate
from utils.template_utils import TemplateSection

file_paths = create_file_paths(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates"))
print(file_paths)


for file_path in file_paths:
    parsed_data = parse_template(file_path)

    print(parsed_data)

# Template Parsing Unit Test
class TestTemplateParser(unittest.TestCase):

    # setUp method defining temporary file to parse
    def setUp(self):
        self.test_file = "test_pattern.txt"
        content = (
            "=Unit Test Pattern\n"
            "*test, validation, assurance\n"
            "#Intent\n"
            "?Problem Definition\n"
            "?Solution Definition\n"
            "#Motivation\n"
            "?Use Case Scenario"
        )
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write(content)

    # Remove temporary file upon completion
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    # Determine accuracy of parser through comparison
    def test_parse_template_accuracy(self):
        expected = PatternTemplate(
            title="Unit Test Pattern",
            tags=["test", "validation", "assurance"],
            sections=[
                TemplateSection(name="Intent", questions=["Problem Definition", "Solution Definition"]),
                TemplateSection(name="Motivation", questions=["Use Case Scenario"])
            ]
        )

        result = parse_template(self.test_file)

        self.assertEqual(result.title, expected.title)
        self.assertEqual(result.tags, expected.tags)

        self.assertEqual(len(result.sections), len(expected.sections))

        for i in range(len(expected.sections)):
            self.assertEqual(result.sections[i].name, expected.sections[i].name)
            self.assertEqual(result.sections[i].questions, expected.sections[i].questions)
