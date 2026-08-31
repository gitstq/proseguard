"""Spelling rules (PG100–PG109)."""

from __future__ import annotations

from ..dictionaries import COMMON_MISSPELLINGS, LEGIT_REPEATS
from .base import Document, RuleConfig, Finding, Rule


def _match_case(original: str, suggestion: str) -> str:
    if original.isupper():
        return suggestion.upper()
    if original[:1].isupper():
        return suggestion[:1].upper() + suggestion[1:]
    return suggestion


def check_misspellings(doc: Document, cfg: RuleConfig):
    for sentence in doc.sentences:
        for word in sentence.words:
            token = word.text
            # Skip ALL-CAPS acronyms (NASA, HTTP) and tokens with digits.
            if token.isupper() and len(token) > 1:
                continue
            if any(ch.isdigit() for ch in token):
                continue
            key = token.lower().replace("’", "'")
            if key in cfg.personal_dictionary:
                continue
            replacement = COMMON_MISSPELLINGS.get(key)
            if replacement is None or replacement == key:
                continue
            fixed = _match_case(token, replacement)
            yield Finding(
                rule_id="", severity="", category="",
                message=f"Possible misspelling “{token}”. Did you mean “{fixed}”?",
                start=word.start, end=word.end, replacement=fixed,
            )


def check_repeated_words(doc: Document, cfg: RuleConfig):
    for sentence in doc.sentences:
        words = sentence.words
        for prev, cur in zip(words, words[1:]):
            if prev.lower != cur.lower:
                continue
            if prev.lower in LEGIT_REPEATS:
                continue
            gap = doc.text[prev.end:cur.start]
            # Only direct repetitions separated by a short whitespace/quote run;
            # a wide gap means masked inline code/URLs sat between the words.
            if gap.strip(" \t“”\"'’") or len(gap) > 3:
                continue
            yield Finding(
                rule_id="", severity="", category="",
                message=f"Repeated word “{cur.text}”. Remove the duplicate.",
                start=prev.start, end=cur.end,
                replacement=cur.text,
            )


RULES = [
    Rule(
        id="PG100", severity="error", category="spelling",
        title="Common misspelling",
        description="Flags words from a built-in dictionary of frequently "
                    "misspelled English words and suggests the standard form.",
        check=check_misspellings, autofixable=True,
    ),
    Rule(
        id="PG101", severity="error", category="spelling",
        title="Repeated word",
        description="Detects accidental duplicate words (lexical illusions) "
                    "such as “the the”.",
        check=check_repeated_words, autofixable=True,
    ),
]
