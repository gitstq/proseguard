import unittest

from proseguard import Linter


def rule_map(text):
    return {f.rule_id: f for f in Linter().lint_text(text).findings}


class PunctuationTests(unittest.TestCase):
    def test_multiple_spaces(self):
        found = rule_map("one  two")
        self.assertIn("PG300", found)
        self.assertEqual(found["PG300"].replacement, " ")

    def test_space_before_punct(self):
        found = rule_map("Hello , world.")
        self.assertIn("PG301", found)

    def test_missing_space_after(self):
        found = rule_map("hello,world")
        self.assertIn("PG302", found)
        self.assertEqual(found["PG302"].replacement, ", ")

    def test_numbers_not_flagged(self):
        found = rule_map("It costs 1,000 at 12:30.")
        self.assertNotIn("PG302", found)

    def test_repeated_punct(self):
        found = rule_map("Really??")
        self.assertIn("PG303", found)

    def test_ellipsis_allowed(self):
        found = rule_map("Wait...")
        self.assertNotIn("PG303", found)

    def test_trailing_whitespace(self):
        result = Linter().lint_text("hello   \nworld")
        ids = {f.rule_id for f in result.findings}
        self.assertIn("PG304", ids)


if __name__ == "__main__":
    unittest.main()
