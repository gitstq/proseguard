import unittest

from proseguard import Linter
from proseguard.rules.readability import count_syllables, compute_stats
from proseguard.tokenizer import mask_protected, sentence_spans
from proseguard.rules.base import Document


class SyllableTests(unittest.TestCase):
    def test_known_words(self):
        self.assertEqual(count_syllables("dog"), 1)
        self.assertEqual(count_syllables("hello"), 2)
        self.assertEqual(count_syllables("table"), 2)
        self.assertGreaterEqual(count_syllables("beautiful"), 3)

    def test_minimum_one(self):
        self.assertEqual(count_syllables("the"), 1)


class StatsTests(unittest.TestCase):
    def _doc(self, text):
        masked = mask_protected(text)
        return Document(raw=text, text=masked,
                        sentences=sentence_spans(masked))

    def test_simple_text_easier_than_complex(self):
        simple = compute_stats(self._doc("The cat sat. It was warm."))
        complex_text = compute_stats(self._doc(
            "The extraordinarily complicated institutional methodologies "
            "demonstrate fundamental epistemological considerations."
        ))
        self.assertLess(simple.flesch_kincaid_grade,
                        complex_text.flesch_kincaid_grade)

    def test_stats_shapes(self):
        stats = compute_stats(self._doc("Hello world. Goodbye now."))
        self.assertEqual(stats.sentences, 2)
        self.assertEqual(stats.words, 4)
        d = stats.to_dict()
        self.assertIn("gunning_fog", d)

    def test_hard_sentence_rule(self):
        dense = (
            "Methodological considerations fundamentally demonstrate "
            "extraordinary institutional characteristics while simultaneously "
            "investigating interdisciplinary operational complexities."
        )
        ids = {f.rule_id for f in Linter().lint_text(dense).findings}
        self.assertIn("PG500", ids)


if __name__ == "__main__":
    unittest.main()
