"""Rule primitives shared by every rule module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Any

from ..tokenizer import Sentence, line_col

SEVERITIES = ("error", "warning", "suggestion")
CATEGORIES = ("spelling", "grammar", "punctuation", "style", "readability")


@dataclass
class Finding:
    rule_id: str
    severity: str
    category: str
    message: str
    start: int
    end: int
    replacement: str | None = None
    autofixable: bool = False
    excerpt: str = ""

    def position(self, source: str) -> tuple[int, int, int, int]:
        sl, sc = line_col(source, self.start)
        el, ec = line_col(source, self.end)
        return sl, sc, el, ec

    def to_dict(self, source: str, path: str | None = None) -> dict[str, Any]:
        sl, sc, el, ec = self.position(source)
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "path": path,
            "start_line": sl,
            "start_column": sc,
            "end_line": el,
            "end_column": ec,
            "replacement": self.replacement,
            "autofixable": self.autofixable,
            "excerpt": self.excerpt,
        }


@dataclass
class Document:
    raw: str
    text: str                      # masked text (same length as raw)
    sentences: list[Sentence]
    path: str | None = None


@dataclass
class RuleConfig:
    max_sentence_words: int = 25
    long_sentence_hard: int = 40
    readability_grade: float = 12.0
    personal_dictionary: frozenset[str] = field(default_factory=frozenset)
    options: dict[str, Any] = field(default_factory=dict)


# A check receives (Document, RuleConfig) and yields Findings.
CheckFn = Callable[[Document, RuleConfig], Iterable[Finding]]


@dataclass
class Rule:
    id: str
    severity: str
    category: str
    title: str
    description: str
    check: CheckFn
    autofixable: bool = False

    def run(self, doc: Document, cfg: RuleConfig) -> list[Finding]:
        findings = list(self.check(doc, cfg))
        for f in findings:
            # Normalize: rule metadata wins for severity/category/id.
            f.rule_id = self.id
            f.severity = self.severity
            f.category = self.category
            f.autofixable = self.autofixable and f.replacement is not None
            if not f.excerpt:
                f.excerpt = doc.raw[f.start:f.end]
        return findings
