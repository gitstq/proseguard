"""Grammar rules (PG200–PG209)."""

from __future__ import annotations

from ..dictionaries import (
    CONSONANT_SOUND_WORDS, VOWEL_SOUND_WORDS, LOWERCASE_BRANDS,
)
from .base import Document, RuleConfig, Finding, Rule

_COMPARATIVES = frozenset({
    "easier", "better", "faster", "simpler", "clearer", "safer", "stronger",
    "bigger", "smaller", "quicker", "harder", "nicer", "older", "newer",
    "cheaper", "brighter", "darker", "smarter", "larger", "longer",
    "shorter", "louder", "weaker", "cleaner", "deeper", "richer", "poorer",
    "wider", "narrower", "closer", "fuller", "thinner", "thicker",
    "smoother", "softer", "tougher", "gentler", "calmer", "slower", "lower",
    "higher", "happier", "heavier", "lighter",
})
_MODALS = frozenset({"could", "should", "would", "must", "might", "may", "cant", "can't"})
_THIRD_PERSON = frozenset({"he", "she", "it"})
_VOWELS = frozenset("aeiou")


def _tight(gap: str) -> bool:
    """True only when two words sit next to each other in plain prose.

    A wider gap means masked inline code/URLs sat between the words, so the
    grammatical relation does not hold.
    """
    return len(gap.strip(" \t\"'“”’")) == 0 and len(gap) <= 1


def _expected_article(next_word: str) -> str:
    w = next_word.lower().strip("'\"“”")
    if not w:
        return ""
    first = w[0]
    if first in _VOWELS:
        # "a university", "a euro..." – consonant sound wins.
        for exception in CONSONANT_SOUND_WORDS:
            if w == exception or w.startswith(exception):
                return "a"
        return "an"
    # Consonant letter but vowel sound: "an hour", "an MBA".
    if w in VOWEL_SOUND_WORDS:
        return "an"
    return "a"


def check_articles(doc: Document, cfg: RuleConfig):
    for sentence in doc.sentences:
        words = sentence.words
        for i, word in enumerate(words[:-1]):
            if word.lower not in {"a", "an"}:
                continue
            gap = doc.text[word.end:words[i + 1].start]
            if not _tight(gap):
                continue
            expected = _expected_article(words[i + 1].text)
            if not expected or expected == word.lower:
                continue
            fixed = expected.upper() if word.text.isupper() else expected
            yield Finding(
                rule_id="", severity="", category="",
                message=f"Use “{fixed}” rather than “{word.text}” before "
                        f"“{words[i + 1].text}”.",
                start=word.start, end=word.end, replacement=fixed,
            )


def check_modal_of(doc: Document, cfg: RuleConfig):
    for sentence in doc.sentences:
        words = sentence.words
        for i, word in enumerate(words[:-1]):
            if word.lower in _MODALS and words[i + 1].lower == "of":
                if not _tight(doc.text[word.end:words[i + 1].start]):
                    continue
                target = words[i + 1]
                yield Finding(
                    rule_id="", severity="", category="",
                    message="Modal verbs are followed by “have”, not “of”.",
                    start=target.start, end=target.end, replacement="have",
                )


def check_double_comparative(doc: Document, cfg: RuleConfig):
    for sentence in doc.sentences:
        words = sentence.words
        for i, word in enumerate(words[:-1]):
            if word.lower not in {"more", "less"}:
                continue
            nxt = words[i + 1]
            if not _tight(doc.text[word.end:nxt.start]):
                continue
            if nxt.lower in _COMPARATIVES:
                yield Finding(
                    rule_id="", severity="", category="",
                    message=f"Double comparative “{word.text} {nxt.text}”. "
                            f"Use “{nxt.text}” alone.",
                    start=word.start, end=nxt.end, replacement=nxt.text,
                )


def check_first_person_pronoun(doc: Document, cfg: RuleConfig):
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.text == "i":
                yield Finding(
                    rule_id="", severity="", category="",
                    message="The first-person pronoun must be capitalized: “I”.",
                    start=word.start, end=word.end, replacement="I",
                )


def check_third_person_dont(doc: Document, cfg: RuleConfig):
    for sentence in doc.sentences:
        words = sentence.words
        for i, word in enumerate(words[:-1]):
            if word.lower in _THIRD_PERSON and words[i + 1].lower in {"dont", "don't"}:
                if not _tight(doc.text[word.end:words[i + 1].start]):
                    continue
                nxt = words[i + 1]
                yield Finding(
                    rule_id="", severity="", category="",
                    message=f"Third-person singular needs “doesn't” "
                            f"(after “{word.text}”).",
                    start=nxt.start, end=nxt.end, replacement="doesn't",
                )


def check_sentence_capitalization(doc: Document, cfg: RuleConfig):
    for sentence in doc.sentences:
        first = sentence.first_word
        if first is None:
            continue
        if first.text in LOWERCASE_BRANDS:
            continue
        # Already capitalized or contains internal capitals (camelCase).
        if first.text[:1].isupper() or any(c.isupper() for c in first.text[1:]):
            continue
        yield Finding(
            rule_id="", severity="", category="",
            message="Sentences should begin with a capital letter.",
            start=first.start, end=first.end,
            replacement=first.text[:1].upper() + first.text[1:],
        )


RULES = [
    Rule("PG200", "error", "grammar", "Article agreement (a/an)",
         "Checks that “a”/“an” agrees with the following word's sound, "
         "including silent-h and consonant-sounding-vowel exceptions.",
         check_articles, autofixable=True),
    Rule("PG201", "error", "grammar", "“could of” → “could have”",
         "Catches the common “would of / should of / could of” mistake.",
         check_modal_of, autofixable=True),
    Rule("PG202", "error", "grammar", "Double comparative",
         "Flags redundant forms such as “more easier” or “more faster”.",
         check_double_comparative, autofixable=True),
    Rule("PG203", "error", "grammar", "Lowercase pronoun “i”",
         "Capitalizes the standalone first-person singular pronoun.",
         check_first_person_pronoun, autofixable=True),
    Rule("PG204", "error", "grammar", "Third-person “don't”",
         "Requires “doesn't” after he/she/it.",
         check_third_person_dont, autofixable=True),
    Rule("PG205", "suggestion", "grammar", "Sentence capitalization",
         "Suggests an uppercase letter at the start of each sentence.",
         check_sentence_capitalization, autofixable=True),
]
