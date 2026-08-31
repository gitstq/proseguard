"""Deterministic, safe auto-fixer.

Only findings flagged ``autofixable`` with an explicit replacement are
applied. Fixes are performed from the end of the document backwards so that
earlier offsets stay valid. When two fixes overlap, the earlier (lower-offset)
one wins and the overlapping later fix is dropped.
"""

from __future__ import annotations

from .engine import LintResult
from .rules.base import Finding


def plan_fixes(result: LintResult) -> list[Finding]:
    fixes = [f for f in result.findings if f.autofixable and f.replacement is not None]
    fixes.sort(key=lambda f: f.start)
    selected: list[Finding] = []
    cursor = -1
    for fix in fixes:
        if fix.start < cursor:
            continue
        selected.append(fix)
        cursor = fix.end
    # Apply back-to-front.
    return sorted(selected, key=lambda f: f.start, reverse=True)


def apply_fixes(text: str, fixes: list[Finding]) -> str:
    for fix in fixes:
        text = text[:fix.start] + fix.replacement + text[fix.end:]
    return text


def autofix_text(result: LintResult) -> tuple[str, int]:
    fixes = plan_fixes(result)
    return apply_fixes(result.source, fixes), len(fixes)
