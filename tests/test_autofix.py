import unittest

from proseguard import Linter
from proseguard.autofix import autofix_text, plan_fixes


class AutofixTests(unittest.TestCase):
    def test_fixes_misspelling(self):
        linter = Linter()
        result = linter.lint_text("This is definately wrong.")
        fixed, n = autofix_text(result)
        self.assertIn("definitely", fixed)
        self.assertNotIn("definately", fixed)
        self.assertGreaterEqual(n, 1)

    def test_fix_is_idempotent(self):
        linter = Linter()
        text = ("This is definately wrong,  and you should of known. "
                "It was more easier then.")
        once = autofix_text(linter.lint_text(text))[0]
        twice = autofix_text(linter.lint_text(once))[0]
        self.assertEqual(once, twice)

    def test_no_overlapping_fixes(self):
        linter = Linter()
        result = linter.lint_text("definately,  recieve")
        fixes = plan_fixes(result)
        for a, b in zip(fixes, fixes[1:]):
            self.assertGreaterEqual(a.start, b.end)

    def test_non_fixable_rules_left_untouched(self):
        linter = Linter()
        result = linter.lint_text("It is basically very passive text.")
        _, n = autofix_text(result)
        self.assertEqual(n, 0)

    def test_fix_never_erases_protected_code_or_links(self):
        text = (
            "This is definately wrong.\n\n"
            "```python\n"
            "def definately_not_linted():\n"
            "    return 'teh teh'\n"
            "```\n\n"
            "See `recieve` and [site](https://example.com/recieve)."
        )
        linter = Linter()
        fixed, n = autofix_text(linter.lint_text(text))
        self.assertGreaterEqual(n, 1)
        self.assertIn("definitely", fixed)          # outside code fixed
        self.assertIn("def definately_not_linted", fixed)  # code preserved
        self.assertIn("'teh teh'", fixed)
        self.assertIn("`recieve`", fixed)
        self.assertIn("https://example.com/recieve", fixed)
        # No protected span is collapsed into whitespace artifacts.
        self.assertIn("```python", fixed)


if __name__ == "__main__":
    unittest.main()
