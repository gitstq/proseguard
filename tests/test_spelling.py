import unittest

from proseguard import Linter, Config


def ids_for(text, **cfg_kw):
    linter = Linter(Config(**cfg_kw))
    result = linter.lint_text(text)
    return {f.rule_id: f for f in result.findings}


class MisspellingTests(unittest.TestCase):
    def test_basic_misspelling(self):
        found = ids_for("This is definately wrong.")
        self.assertIn("PG100", found)
        self.assertEqual(found["PG100"].replacement, "definitely")

    def test_case_preserved(self):
        found = ids_for("Definately broken.")
        self.assertEqual(found["PG100"].replacement, "Definitely")

    def test_acronyms_and_digits_skipped(self):
        linter = Linter()
        result = linter.lint_text("HTTP connects on port 8080.")
        self.assertFalse(
            any(f.rule_id == "PG100" for f in result.findings))

    def test_personal_dictionary(self):
        found = ids_for("proseguard is here.",
                        personal_dictionary={"proseguard"})
        # "proseguard" is not in misspelling map anyway; ensure no crash and
        # no PG100 for a dictionary word that happens to be listed.
        self.assertNotIn("PG100", found)

    def test_dictionary_has_no_self_maps(self):
        from proseguard.dictionaries import COMMON_MISSPELLINGS
        bad = [k for k, v in COMMON_MISSPELLINGS.items() if k == v]
        self.assertEqual(bad, [])


class RepeatedWordTests(unittest.TestCase):
    def test_duplicate_flagged(self):
        found = ids_for("I went to the the store.")
        self.assertIn("PG101", found)
        self.assertEqual(found["PG101"].replacement, "the")

    def test_legit_repeat_allowed(self):
        found = ids_for("If I had had time, I would come.")
        self.assertNotIn("PG101", found)


if __name__ == "__main__":
    unittest.main()
