"""Rule package – aggregators for the default rule registry."""

from .base import Finding, Rule, Document, RuleConfig
from . import spelling, grammar, punctuation, style, readability

ALL_MODULES = (spelling, grammar, punctuation, style, readability)


def all_rules() -> list[Rule]:
    rules: list[Rule] = []
    for module in ALL_MODULES:
        rules.extend(module.RULES)
    return rules


__all__ = [
    "Finding", "Rule", "Document", "RuleConfig",
    "all_rules", "spelling", "grammar", "punctuation", "style", "readability",
]
