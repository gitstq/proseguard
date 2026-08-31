import unittest

from proseguard import Linter


def rule_map(text):
    result = Linter().lint_text(text)
    return {f.rule_id: f for f in result.findings}


class GrammarTests(unittest.TestCase):
    def test_a_before_consonant(self):
        self.assertNotIn("PG200", rule_map("I saw a cat."))

    def test_an_before_vowel(self):
        found = rule_map("I ate a apple today.")
        self.assertEqual(found["PG200"].replacement, "an")

    def test_consonant_sound_vowel_letter(self):
        found = rule_map("She is an university student.")
        self.assertEqual(found["PG200"].replacement, "a")

    def test_vowel_sound_consonant_letter(self):
        found = rule_map("I waited a hour.")
        self.assertEqual(found["PG200"].replacement, "an")
        self.assertNotIn("PG200", rule_map("I waited an hour."))

    def test_modal_of(self):
        found = rule_map("I should of known.")
        self.assertEqual(found["PG201"].replacement, "have")

    def test_double_comparative(self):
        found = rule_map("This is more easier now.")
        self.assertEqual(found["PG202"].replacement, "easier")

    def test_lowercase_pronoun(self):
        found = rule_map("Tomorrow i will leave.")
        self.assertEqual(found["PG203"].replacement, "I")

    def test_third_person_dont(self):
        found = rule_map("He don't know.")
        self.assertEqual(found["PG204"].replacement, "doesn't")

    def test_sentence_capitalization(self):
        found = rule_map("first we run. Then we stop.")
        self.assertIn("PG205", found)

    def test_clean_sentence_has_no_grammar_findings(self):
        result = Linter().lint_text(
            "The quick brown fox jumps over the lazy dog.")
        grammar = [f for f in result.findings if f.category == "grammar"]
        self.assertEqual(grammar, [])

    def test_article_skips_masked_inline_code_gap(self):
        # The article governs the masked code token, not the following word.
        result = Linter().lint_text(
            "Register a `Rule(...)` in its rules list.")
        self.assertFalse(
            any(f.rule_id == "PG200" for f in result.findings))


if __name__ == "__main__":
    unittest.main()
