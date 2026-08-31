import unittest

from proseguard import Linter, Config


def rule_map(text, **kw):
    return {f.rule_id: f for f in Linter(Config(**kw)).lint_text(text).findings}


class StyleTests(unittest.TestCase):
    def test_weasel_word(self):
        self.assertIn("PG400", rule_map("It is basically done."))

    def test_weak_adverb(self):
        self.assertIn("PG401", rule_map("It was very good."))

    def test_passive_voice(self):
        found = rule_map("The ball was thrown by John.")
        self.assertIn("PG402", found)

    def test_active_voice_clean(self):
        self.assertNotIn("PG402", rule_map("John threw the ball far."))

    def test_wordy_phrase(self):
        found = rule_map("In order to win, train hard.")
        self.assertEqual(found["PG403"].replacement, "To")

    def test_long_sentence(self):
        words = " ".join(["word"] * 26)
        found = rule_map(f"{words}.")
        self.assertIn("PG404", found)

    def test_long_sentence_threshold_configurable(self):
        words = " ".join(["word"] * 26)
        found = rule_map(f"{words}.", max_sentence_words=30)
        self.assertNotIn("PG404", found)

    def test_repeated_openers(self):
        text = ("The cat sat. The dog ran. The bird flew away.")
        found = rule_map(text)
        self.assertIn("PG405", found)


if __name__ == "__main__":
    unittest.main()
