import json
import unittest

from proseguard import Linter
from proseguard import report


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.results = [
            Linter().lint_text("This is definately wrong.", path="a.md"),
            Linter().lint_text("Clean sentence here.", path="b.md"),
        ]

    def test_json_is_valid_and_structured(self):
        payload = json.loads(report.format_json(self.results))
        self.assertEqual(len(payload["files"]), 2)
        self.assertIn("summary", payload)
        finding = payload["files"][0]["findings"][0]
        self.assertEqual(finding["rule_id"], "PG100")
        self.assertEqual(finding["start_line"], 1)

    def test_markdown_contains_rule(self):
        md = report.format_markdown(self.results)
        self.assertIn("PG100", md)
        self.assertIn("a.md", md)

    def test_html_self_contained(self):
        html = report.format_html(self.results)
        self.assertTrue(html.lstrip().startswith("<!DOCTYPE html>"))
        self.assertNotIn("src=\"http", html)
        self.assertNotIn("<link", html)
        self.assertIn("PG100", html)

    def test_text_clean_message(self):
        clean = [Linter().lint_text("A perfectly clean sentence.")]
        text = report.format_text(clean, color=False)
        self.assertIn("No problems found", text)

    def test_text_color_codes(self):
        plain = report.format_text(self.results, color=False)
        colored = report.format_text(self.results, color=True)
        self.assertNotIn("\033[", plain)
        self.assertIn("\033[", colored)


if __name__ == "__main__":
    unittest.main()
