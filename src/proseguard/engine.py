"""Core linting engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .config import Config
from .rules import all_rules, Document, RuleConfig, Finding, Rule
from .rules.readability import ReadabilityStats, compute_stats
from .tokenizer import mask_protected, sentence_spans


@dataclass
class LintResult:
    source: str
    findings: list[Finding] = field(default_factory=list)
    stats: ReadabilityStats | None = None
    path: str | None = None

    @property
    def error_count(self) -> int:
        return sum(f.severity == "error" for f in self.findings)

    @property
    def warning_count(self) -> int:
        return sum(f.severity == "warning" for f in self.findings)

    @property
    def suggestion_count(self) -> int:
        return sum(f.severity == "suggestion" for f in self.findings)

    def by_severity(self) -> dict[str, list[Finding]]:
        groups = {"error": [], "warning": [], "suggestion": []}
        for finding in self.findings:
            groups[finding.severity].append(finding)
        return groups


class Linter:
    """Stateless linter bound to a :class:`Config`."""

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        catalog = {rule.id: rule for rule in all_rules()}
        requested = self.config.enable | self.config.disable
        unknown = sorted(rid for rid in requested if rid not in catalog)
        if unknown:
            valid = ", ".join(sorted(catalog))
            raise ValueError(
                f"unknown rule id(s): {', '.join(unknown)}. "
                f"Valid ids: {valid}"
            )
        self.rules: list[Rule] = [
            rule for rid, rule in sorted(catalog.items())
            if self.config.is_enabled(rid)
        ]

    @staticmethod
    def catalog() -> list[dict[str, str]]:
        return [
            {
                "id": r.id, "severity": r.severity, "category": r.category,
                "title": r.title, "description": r.description,
                "autofixable": r.autofixable,
            }
            for r in sorted(all_rules(), key=lambda r: r.id)
        ]

    def _rule_config(self) -> RuleConfig:
        return RuleConfig(
            max_sentence_words=self.config.max_sentence_words,
            long_sentence_hard=self.config.long_sentence_hard,
            readability_grade=self.config.readability_grade,
            personal_dictionary=frozenset(self.config.personal_dictionary),
        )

    def lint_text(self, text: str, path: str | None = None,
                  with_stats: bool = True) -> LintResult:
        masked = mask_protected(text)
        doc = Document(raw=text, text=masked,
                       sentences=sentence_spans(masked), path=path)
        rule_cfg = self._rule_config()
        # Prefix count of protected positions: character-level rules scan the
        # masked text, but a finding is only valid when its whole span maps
        # onto untouched (non-protected) characters of the raw document. This
        # guarantees that --fix can never erase code spans or URLs.
        protected_prefix = [0] * (len(text) + 1)
        for i, (raw_ch, masked_ch) in enumerate(zip(text, masked)):
            protected_prefix[i + 1] = protected_prefix[i] + (
                raw_ch != masked_ch)

        def is_clean_span(start: int, end: int) -> bool:
            return protected_prefix[end] - protected_prefix[start] == 0

        findings: list[Finding] = []
        for rule in self.rules:
            for finding in rule.run(doc, rule_cfg):
                if is_clean_span(finding.start, finding.end):
                    findings.append(finding)
        findings.sort(key=lambda f: (f.start, f.rule_id))
        stats = compute_stats(doc) if with_stats else None
        return LintResult(source=text, findings=findings, stats=stats, path=path)

    def lint_file(self, path: str | Path, encoding: str = "utf-8") -> LintResult:
        p = Path(path)
        text = p.read_text(encoding=encoding)
        return self.lint_text(text, path=str(p))
