"""Punctuation & typography rules (PG300–PG309)."""

from __future__ import annotations

import re

from .base import Document, RuleConfig, Finding, Rule

_MULTI_SPACE = re.compile(r"(?<=\S) {2,}(?=\S)")
_SPACE_BEFORE = re.compile(r"[ \t]+([,.;:!?])")
_MISSING_AFTER = re.compile(r"([,;:])([^\s,.;:!?)\]}'\"”’])")
_REPEATED = re.compile(r"([,;:.!?])\1+")
_TRAILING = re.compile(r"[ \t]+$", re.MULTILINE)


def check_multiple_spaces(doc: Document, cfg: RuleConfig):
    for m in _MULTI_SPACE.finditer(doc.text):
        yield Finding(
            rule_id="", severity="", category="",
            message=f"Multiple spaces ({len(m.group(0))}) found; use one.",
            start=m.start(), end=m.end(), replacement=" ",
        )


def check_space_before_punct(doc: Document, cfg: RuleConfig):
    for m in _SPACE_BEFORE.finditer(doc.text):
        punct = m.group(1)
        # Tolerate ellipses.
        if punct == "." and doc.text[m.end():m.end() + 2] == "..":
            continue
        yield Finding(
            rule_id="", severity="", category="",
            message=f"No space before “{punct}”.",
            start=m.start(), end=m.end(), replacement=punct,
        )


def check_missing_space_after(doc: Document, cfg: RuleConfig):
    for m in _MISSING_AFTER.finditer(doc.text):
        punct, following = m.group(1), m.group(2)
        # Numbers: 1,000 / 12:30.
        before = doc.text[m.start() - 1] if m.start() > 0 else ""
        if punct in {",", ":"} and before.isdigit() and following.isdigit():
            continue
        yield Finding(
            rule_id="", severity="", category="",
            message=f"Add a space after “{punct}”.",
            start=m.start(1), end=m.end(1), replacement=f"{punct} ",
        )


def check_repeated_punctuation(doc: Document, cfg: RuleConfig):
    for m in _REPEATED.finditer(doc.text):
        run = m.group(0)
        # Ellipsis is legitimate punctuation.
        if set(run) == {"."}:
            continue
        yield Finding(
            rule_id="", severity="", category="",
            message=f"Repeated punctuation “{run}”. Collapse to “{m.group(1)}”.",
            start=m.start(), end=m.end(), replacement=m.group(1),
        )


def check_trailing_whitespace(doc: Document, cfg: RuleConfig):
    for m in _TRAILING.finditer(doc.text):
        yield Finding(
            rule_id="", severity="", category="",
            message="Trailing whitespace at end of line.",
            start=m.start(), end=m.end(), replacement="",
        )


RULES = [
    Rule("PG300", "warning", "punctuation", "Multiple spaces",
         "Flags runs of two or more spaces between words.",
         check_multiple_spaces, autofixable=True),
    Rule("PG301", "warning", "punctuation", "Space before punctuation",
         "Removes stray whitespace immediately before , . ; : ! ?.",
         check_space_before_punct, autofixable=True),
    Rule("PG302", "warning", "punctuation", "Missing space after punctuation",
         "Inserts the missing space after commas, semicolons and colons "
         "(numbers such as 1,000 or 12:30 are ignored).",
         check_missing_space_after, autofixable=True),
    Rule("PG303", "suggestion", "punctuation", "Repeated punctuation",
         "Collapses doubled punctuation such as “??” or “,,”.",
         check_repeated_punctuation, autofixable=True),
    Rule("PG304", "warning", "punctuation", "Trailing whitespace",
         "Removes spaces and tabs at the end of each line.",
         check_trailing_whitespace, autofixable=True),
]
