import unittest

from proseguard.tokenizer import (
    mask_protected, sentence_spans, word_spans, line_col,
)


class MaskTests(unittest.TestCase):
    def test_fenced_code_masked_but_same_length(self):
        text = "before\n```\ndefinately teh\n```\nafter"
        masked = mask_protected(text)
        self.assertEqual(len(masked), len(text))
        self.assertNotIn("definately", masked)
        self.assertTrue(masked.startswith("before"))
        self.assertTrue(masked.rstrip().endswith("after"))

    def test_inline_code_and_url_masked(self):
        text = "see `recieve` at https://example.com/recieve now"
        masked = mask_protected(text)
        self.assertNotIn("recieve", masked)
        self.assertNotIn("https", masked)
        self.assertEqual(len(masked), len(text))
        self.assertIn("see", masked)
        self.assertIn("now", masked)

    def test_newlines_preserved(self):
        text = "```\na\nb\nc\n```"
        masked = mask_protected(text)
        self.assertEqual(masked.count("\n"), text.count("\n"))


class SentenceTests(unittest.TestCase):
    def test_basic_split(self):
        sents = sentence_spans("First sentence. Second one! Third?")
        self.assertEqual(len(sents), 3)
        self.assertEqual(sents[0].text, "First sentence.")

    def test_abbreviation_does_not_split(self):
        sents = sentence_spans("Bring e.g. a laptop. Then leave.")
        self.assertEqual(len(sents), 2)

    def test_word_spans_offsets(self):
        words = word_spans("hello, world!")
        self.assertEqual([w.text for w in words], ["hello", "world"])
        self.assertEqual(words[0].start, 0)
        self.assertEqual(words[1].text, "world")

    def test_line_col(self):
        text = "ab\ncdef"
        self.assertEqual(line_col(text, 0), (1, 1))
        self.assertEqual(line_col(text, 4), (2, 2))


if __name__ == "__main__":
    unittest.main()
